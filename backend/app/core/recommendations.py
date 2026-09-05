from time import perf_counter

import pandas as pd

from .enums import RecommendationRanking
from .models import (
    RecommendationParameters,
    RecommendationResult,
    RecommendationStatistics,
)


REQUIRED_RULE_COLUMNS = {
    "antecedents",
    "consequents",
    "support",
    "confidence",
    "lift",
}


def clean_basket_item(item: object) -> str:
    return str(item).strip().lower()


def validate_recommendation_inputs(
    rules: pd.DataFrame,
    basket: list[str],
    top_n: int,
    ranking_metric: str | RecommendationRanking,
) -> RecommendationRanking:
    if rules is None:
        raise ValueError("rules cannot be None.")

    if not isinstance(rules, pd.DataFrame):
        raise TypeError("rules must be a pandas DataFrame.")

    missing_columns = REQUIRED_RULE_COLUMNS - set(rules.columns)

    if missing_columns:
        raise ValueError(
            "rules is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if basket is None:
        raise ValueError("basket cannot be None.")

    if not isinstance(basket, list):
        raise TypeError("basket must be a list of item names.")

    if not basket:
        raise ValueError("basket cannot be empty.")

    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise ValueError("top_n must be an integer.")

    if top_n < 1:
        raise ValueError("top_n must be greater than or equal to 1.")

    try:
        validated_ranking_metric = RecommendationRanking(
            ranking_metric
        )
    except (ValueError, TypeError) as exc:
        supported = ", ".join(
            metric.value
            for metric in RecommendationRanking
        )

        raise ValueError(
            f"Unsupported recommendation ranking metric "
            f"'{ranking_metric}'. Supported metrics: {supported}."
        ) from exc

    return validated_ranking_metric


def normalize_basket(
    basket: list[str],
) -> list[str]:
    cleaned_items = [
        clean_basket_item(item)
        for item in basket
        if pd.notna(item)
    ]

    cleaned_items = [
        item
        for item in cleaned_items
        if item
    ]

    return list(dict.fromkeys(cleaned_items))


def find_matching_rules(
    rules: pd.DataFrame,
    basket: list[str],
) -> pd.DataFrame:
    basket_set = set(basket)

    matching_mask = rules["antecedents"].apply(
        lambda antecedent: set(antecedent).issubset(basket_set)
    )

    return rules.loc[matching_mask].copy()


def extract_recommendation_candidates(
    matching_rules: pd.DataFrame,
    basket: list[str],
) -> pd.DataFrame:
    basket_set = set(basket)
    candidates: list[dict] = []

    for _, rule in matching_rules.iterrows():
        antecedents = set(rule["antecedents"])
        consequents = set(rule["consequents"])

        new_items = consequents - basket_set

        for item in new_items:
            candidates.append(
                {
                    "item": item,
                    "antecedents": frozenset(antecedents),
                    "support": float(rule["support"]),
                    "confidence": float(rule["confidence"]),
                    "lift": float(rule["lift"]),
                }
            )

    return pd.DataFrame(
        candidates,
        columns=[
            "item",
            "antecedents",
            "support",
            "confidence",
            "lift",
        ],
    )


def aggregate_candidates(
    candidates: pd.DataFrame,
    ranking_metric: RecommendationRanking,
) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=[
                "item",
                "score",
                "support",
                "confidence",
                "lift",
                "matching_rule_count",
            ]
        )

    aggregated = (
        candidates
        .groupby("item", as_index=False)
        .agg(
            support=("support", "max"),
            confidence=("confidence", "max"),
            lift=("lift", "max"),
            matching_rule_count=("item", "size"),
        )
    )

    aggregated["score"] = aggregated[ranking_metric.value]

    return aggregated[
        [
            "item",
            "score",
            "support",
            "confidence",
            "lift",
            "matching_rule_count",
        ]
    ]


def rank_recommendations(
    candidates: pd.DataFrame,
    ranking_metric: RecommendationRanking,
    top_n: int,
) -> pd.DataFrame:
    aggregated = aggregate_candidates(
        candidates=candidates,
        ranking_metric=ranking_metric,
    )

    if aggregated.empty:
        return aggregated

    return (
        aggregated
        .sort_values(
            by=[
                "score",
                "confidence",
                "lift",
                "support",
            ],
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def generate_recommendation_statistics(
    matching_rules: pd.DataFrame,
    candidates: pd.DataFrame,
    recommendations: pd.DataFrame,
) -> RecommendationStatistics:
    return RecommendationStatistics(
        num_matching_rules=len(matching_rules),
        num_candidate_items=(
            candidates["item"].nunique()
            if not candidates.empty
            else 0
        ),
        num_recommendations=len(recommendations),
    )


def generate_recommendations(
    rules: pd.DataFrame,
    basket: list[str],
    top_n: int = 5,
    ranking_metric: (
        str | RecommendationRanking
    ) = RecommendationRanking.CONFIDENCE,
) -> RecommendationResult:
    validated_ranking_metric = validate_recommendation_inputs(
        rules=rules,
        basket=basket,
        top_n=top_n,
        ranking_metric=ranking_metric,
    )

    normalized_basket = normalize_basket(basket)

    if not normalized_basket:
        raise ValueError(
            "basket contains no valid item names after cleaning."
        )

    parameters = RecommendationParameters(
        basket=tuple(normalized_basket),
        top_n=top_n,
        ranking_metric=validated_ranking_metric,
    )

    start_time = perf_counter()

    matching_rules = find_matching_rules(
        rules=rules,
        basket=normalized_basket,
    )

    candidates = extract_recommendation_candidates(
        matching_rules=matching_rules,
        basket=normalized_basket,
    )

    recommendations = rank_recommendations(
        candidates=candidates,
        ranking_metric=validated_ranking_metric,
        top_n=top_n,
    )

    execution_time = perf_counter() - start_time

    statistics = generate_recommendation_statistics(
        matching_rules=matching_rules,
        candidates=candidates,
        recommendations=recommendations,
    )

    return RecommendationResult(
        parameters=parameters,
        statistics=statistics,
        execution_time=execution_time,
        recommendations=recommendations,
    )
