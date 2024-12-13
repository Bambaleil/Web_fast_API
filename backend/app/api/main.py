from fastapi import APIRouter

from .routes import clients, likes, login, utils

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(likes.router, prefix="/likes", tags=["likes"])
