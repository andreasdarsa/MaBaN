from fastapi import APIRouter

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.api.routes.recommendations import (
    router as recommendations_router,
)


api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    analysis_router,
    prefix="/analysis",
    tags=["Analysis"],
)

api_router.include_router(
    recommendations_router,
    prefix="/recommendations",
    tags=["Recommendations"],
)