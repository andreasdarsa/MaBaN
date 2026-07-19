from typing import Any

from .common import DatasetSummaryResponse

from pydantic import BaseModel, Field

from app.core.enums import (
    DatasetFormat,
    MiningAlgorithm,
    RuleMetric,
)


class TransactionInput(BaseModel):
    transaction_id: str
    items: list[str] = Field(min_length=1)


class AnalysisRequest(BaseModel):
    transactions: list[TransactionInput] = Field(
        min_length=1,
    )

    dataset_format: DatasetFormat = DatasetFormat.BASKET

    algorithm: MiningAlgorithm = MiningAlgorithm.APRIORI

    min_support: float = Field(
        default=0.05,
        gt=0,
        le=1,
    )

    max_len: int | None = Field(
        default=None,
        ge=1,
    )

    rule_metric: RuleMetric = RuleMetric.CONFIDENCE

    rule_threshold: float = Field(
        default=0.5,
        ge=0,
    )

    top_n: int = Field(
        default=10,
        ge=1,
    )


class MiningStatisticsResponse(BaseModel):
    num_transactions: int
    num_items: int
    num_frequent_itemsets: int


class RuleStatisticsResponse(BaseModel):
    num_rules: int
    num_unique_antecedents: int
    num_unique_consequents: int


class InsightStatisticsResponse(BaseModel):
    num_frequent_itemsets: int
    num_rules: int
    num_unique_items: int
    avg_rule_confidence: float | None
    avg_rule_lift: float | None


class AnalysisResponse(BaseModel):
    dataset_summary: DatasetSummaryResponse

    mining_statistics: MiningStatisticsResponse
    mining_execution_time: float

    rule_statistics: RuleStatisticsResponse
    rule_execution_time: float

    frequent_itemsets: list[dict[str, Any]]
    rules: list[dict[str, Any]]

    insight_statistics: InsightStatisticsResponse
    top_items: list[dict[str, Any]]
    top_itemsets: list[dict[str, Any]]
    top_rules: list[dict[str, Any]]
    item_role_summary: list[dict[str, Any]]
