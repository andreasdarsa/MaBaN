from dataclasses import dataclass

import pandas as pd

from .enums import DatasetFormat, MiningAlgorithm, RuleMetric, RecommendationRanking


@dataclass(frozen=True)
class DatasetSummary:
    num_transactions: int
    num_unique_items: int
    avg_basket_size: float


@dataclass
class PreprocessingResult:
    dataset_format: DatasetFormat
    encoded_df: pd.DataFrame
    summary: DatasetSummary
    transactions: list[list[str]] | None = None


@dataclass(frozen=True)
class MiningParameters:
    algorithm: MiningAlgorithm
    min_support: float
    max_len: int | None = None


@dataclass(frozen=True)
class MiningStatistics:
    num_transactions: int
    num_items: int
    num_frequent_itemsets: int
    largest_itemset_size: int


@dataclass
class MiningResult:
    """
        DataClass that keeps info about mining results
            - parameters: algorithm used, minimum support and maximum length
            - statistics: number of transactions - items - frequent itemsets mined
            - frequent_itemsets: dataframe of all frequent itemsets mined by the selected algorithm
            - execution_time: time (in sec) needed to produce mining results
            - engine: engine/library providing the algorithm (mlxtend by default)
            - engine_version: version of the selected engine
    """
    parameters: MiningParameters
    statistics: MiningStatistics
    execution_time: float
    frequent_itemsets: pd.DataFrame
    engine: str = "mlxtend"
    engine_version: str | None = None


@dataclass(frozen=True)
class RuleParameters:
    metric: RuleMetric
    min_threshold: float


@dataclass(frozen=True)
class RuleStatistics:
    num_rules: int
    num_unique_antecedents: int
    num_unique_consequents: int


@dataclass
class RuleResult:
    parameters: RuleParameters
    statistics: RuleStatistics
    execution_time: float
    rules: pd.DataFrame


@dataclass(frozen=True)
class RecommendationParameters:
    basket: tuple[str, ...]
    top_n: int
    ranking_metric: RecommendationRanking


@dataclass(frozen=True)
class RecommendationStatistics:
    num_matching_rules: int
    num_candidate_items: int
    num_recommendations: int


@dataclass
class RecommendationResult:
    parameters: RecommendationParameters
    statistics: RecommendationStatistics
    execution_time: float
    recommendations: pd.DataFrame


@dataclass(frozen=True)
class InsightParameters:
    top_n: int


@dataclass(frozen=True)
class InsightStatistics:
    num_frequent_itemsets: int
    num_rules: int
    num_unique_items: int
    avg_rule_confidence: float | None
    avg_rule_lift: float | None


@dataclass
class InsightsResult:
    parameters: InsightParameters
    statistics: InsightStatistics
    execution_time: float
    top_items: pd.DataFrame
    top_itemsets: pd.DataFrame
    top_rules: pd.DataFrame
    item_role_summary: pd.DataFrame
