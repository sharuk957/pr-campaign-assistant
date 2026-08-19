from fastapi import APIRouter

from app.api.routes import analysis, campaigns, health, journalists, pitches

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(campaigns.router)
api_router.include_router(journalists.router)
api_router.include_router(analysis.router)
api_router.include_router(pitches.router)
