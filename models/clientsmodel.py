from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Optional

import aiofiles
from PIL import Image, ImageEnhance
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, EmailStr, field_validator

current_file_path = Path(__file__).resolve()


async def add_watermark_with_photo(avatar: bytes, watermark_path: Optional[str] = None, opacity: float = 0.5) -> bytes:
    if watermark_path is None:
        watermark_path = current_file_path.parent.parent / "watermark.jpg"

    async with aiofiles.open(watermark_path, "rb") as f:
        watermark_bytes = await f.read()

    watermark = Image.open(BytesIO(watermark_bytes)).convert("RGBA")
    avatar_image = Image.open(BytesIO(avatar)).convert("RGBA")

    watermark = watermark.resize(avatar_image.size, Image.Resampling.LANCZOS)

    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)

    avatar_image.paste(watermark, (0, 0), watermark)

    output = BytesIO()
    avatar_image.save(output, format="PNG")
    result_image = output.getvalue()

    return result_image


class SexEnum(str, Enum):
    male: str = "мужской"
    female: str = "женский"


class ClientsModelAdd(BaseModel):
    password: str
    name: str
    surname: str
    sex: SexEnum
    email: EmailStr
    avatar: Optional[UploadFile] = None

    @field_validator("avatar")
    def validate_avatar(cls, value: Optional[UploadFile]) -> Optional[UploadFile]:
        if value:
            if value.size > 1024 * 1024 * 1024:  # Не больше 5 мб
                raise HTTPException(416, "The file size is over 5 mb")
            if not value.headers.get("content-type").startswith("image"):
                raise HTTPException(415, "Invalid file type")
        return value


class ClientsModel(ClientsModelAdd):
    id: int
