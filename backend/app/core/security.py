from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
