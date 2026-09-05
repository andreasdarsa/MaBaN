from fastapi import APIRouter, HTTPException, status

from app.schemas.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import (
    run_recommendations,
)


router = APIRouter()


@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
)
def recommend_items(
    request: RecommendationRequest,
) -> RecommendationResponse:
    try:
        result = run_recommendations(request)

        return RecommendationResponse.model_validate(result)

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
