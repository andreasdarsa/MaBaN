from enum import Enum


class DatasetFormat(str, Enum):
    LONG = "long"
    BASKET = "basket"
    ONEHOT = "onehot"


class MiningAlgorithm(str, Enum):
    APRIORI = "apriori"
    FP_GROWTH = "fpgrowth"


class RuleMetric(str, Enum):
    CONFIDENCE = "confidence"
    LIFT = "lift"
    LEVERAGE = "leverage"
    CONVICTION = "conviction"
    ZHANGS_METRIC = "zhangs_metric"


class RecommendationRanking(str, Enum):
    CONFIDENCE = "confidence"
    LIFT = "lift"
    SUPPORT = "support"
