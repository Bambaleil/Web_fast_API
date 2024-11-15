from fastapi import APIRouter

from .routes import clients, likes

api_router = APIRouter()

api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(likes.router, prefix="/likes", tags=["likes"])
