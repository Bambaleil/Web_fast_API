from fastapi import APIRouter

from .routes import clients

api_router = APIRouter()

api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
