from fastapi import APIRouter

from app.api.routes import analysis, campaigns, health, journalists

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(campaigns.router)
api_router.include_router(journalists.router)
api_router.include_router(analysis.router)
