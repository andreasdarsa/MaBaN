from fastapi import FastAPI

from .api.router import api_router


app = FastAPI(
    title="MaBaN API",
    description=(
        "API for market basket analysis, association rules, "
        "recommendations and analytical insights."
    ),
    version="0.1.0",
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
