import logging
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Optional, Any
import emails
from jinja2 import Template
import aiofiles
from PIL import Image, ImageEnhance
from fastapi.security import OAuth2PasswordBearer

from .core.config import settings

project_root = Path(__file__).resolve().parents[2]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SexEnum(str, Enum):
    male = "мужской"
    female = "женский"


# Все что связанно с редером и отправкой имейла новому пользователю
# @dataclass
# class EmailData:
#     html_content: str
#     subject: str
#
#
# def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
#     template_str = (
#             Path(__file__).parent / "email-templates" / "build" / template_name
#     ).read_text()
#     html_content = Template(template_str).render(context)
#     return html_content
#
#
# def send_email(
#         *,
#         email_to: str,
#         subject: str = "",
#         html_content: str = "",
# ) -> None:
#     assert settings.emails_enabled, "no provided configuration for email variables"
#     message = emails.Message(
#         subject=subject,
#         html=html_content,
#         mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
#     )
#     smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
#     if settings.SMTP_TLS:
#         smtp_options["tls"] = True
#     elif settings.SMTP_SSL:
#         smtp_options["ssl"] = True
#     if settings.SMTP_USER:
#         smtp_options["user"] = settings.SMTP_USER
#     if settings.SMTP_PASSWORD:
#         smtp_options["password"] = settings.SMTP_PASSWORD
#     response = message.send(to=email_to, smtp=smtp_options)
#     logger.info(f"send email result: {response}")
#
#
# def generate_new_account_email(
#         email_to: str, client_name: str, password: str
# ) -> EmailData:
#     project_name = settings.PROJECT_NAME
#     subject = f"{project_name} - New account for client {client_name}"
#     html_content = render_email_template(
#         template_name="new_account.html",
#         context={
#             "project_name": settings.PROJECT_NAME,
#             "username": client_name,
#             "password": password,
#             "email": email_to,
#             "link": settings.FRONTEND_HOST,
#         },
#     )
#     return EmailData(html_content=html_content, subject=subject)

def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_image(img_name: str) -> Optional[Path]:
    img_path: Path = get_project_root() / "img" / img_name
    return None if not img_path.is_file() else img_path


async def add_watermark_with_photo(avatar: Optional[bytes] = None,
                                   watermark_path: Optional[str] = None,
                                   opacity: float = 0.1) -> bytes:
    if watermark_path is None:
        watermark_path = get_image("watermark.jpg")

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
