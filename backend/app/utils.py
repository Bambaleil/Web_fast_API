from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Optional

import aiofiles
from PIL import Image, ImageEnhance
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

project_root = Path(__file__).resolve().parents[2]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_image(img_name: str) -> Optional[Path]:
    img_path: Path = get_project_root() / "img" / img_name
    return None if not img_path.is_file() else img_path


def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash: str = pwd_context.hash(password)
    return password_hash


async def add_watermark_with_photo(avatar: Optional[bytes] = None,
                                   watermark_path: Optional[str] = None,
                                   opacity: float = 0.1) -> bytes:
    if watermark_path is None:
        watermark_path = get_image("watermark.jpg")
    # if avatar is None:
    #     avatar_path = get_image("default_avatar.jpeg")
    #     async with aiofiles.open(avatar_path, "rb") as f:
    #         avatar = await f.read()

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
