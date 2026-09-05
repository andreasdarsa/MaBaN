from fastapi import APIRouter, HTTPException, status

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
)
from app.services.analysis_service import run_analysis


router = APIRouter()


@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_market_basket(
    request: AnalysisRequest,
) -> AnalysisResponse:
    try:
        result = run_analysis(request)
        return AnalysisResponse.model_validate(result)

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
