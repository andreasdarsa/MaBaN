from pydantic import BaseModel, Field

from app.core.enums import RecommendationRanking


class AssociationRuleInput(BaseModel):
    antecedents: list[str] = Field(min_length=1)
    consequents: list[str] = Field(min_length=1)

    support: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    lift: float = Field(ge=0)


class RecommendationRequest(BaseModel):
    rules: list[AssociationRuleInput] = Field(min_length=1)

    basket: list[str] = Field(min_length=1)

    top_n: int = Field(
        default=5,
        ge=1,
    )

    ranking_metric: RecommendationRanking = (
        RecommendationRanking.CONFIDENCE
    )


class RecommendationItemResponse(BaseModel):
    item: str
    score: float
    support: float
    confidence: float
    lift: float
    matching_rule_count: int


class RecommendationStatisticsResponse(BaseModel):
    num_matching_rules: int
    num_candidate_items: int
    num_recommendations: int


class RecommendationResponse(BaseModel):
    basket: list[str]
    ranking_metric: RecommendationRanking
    top_n: int
    execution_time: float

    statistics: RecommendationStatisticsResponse
    recommendations: list[RecommendationItemResponse]