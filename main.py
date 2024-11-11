from fastapi import FastAPI

from models.usermodel import UserModel

app = FastAPI()


@app.post("/user/")
async def create_user(user: UserModel) -> UserModel:
    return user
