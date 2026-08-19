from fastapi import APIRouter

from app.api.routes import campaigns, health, journalists

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(campaigns.router)
api_router.include_router(journalists.router)
