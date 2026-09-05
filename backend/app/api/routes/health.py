from fastapi import APIRouter


router = APIRouter()


@router.get("")
def health_check() -> dict[str, str]:
    """
    Backend sanity check
    """
    return {
        "status": "ok",
        "service": "MaBaN API",
    }
