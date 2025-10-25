from fastapi import APIRouter
from app.api.v1.endpoints import health, game

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(game.router, prefix="/game", tags=["game"])

# Add more routers here as you create new endpoints
# api_router.include_router(users.router, prefix="/users", tags=["users"])
