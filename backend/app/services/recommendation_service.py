from typing import Any

import pandas as pd

from app.core.recommendations import generate_recommendations
from app.schemas.recommendations import RecommendationRequest


def rules_to_dataframe(
    request: RecommendationRequest,
) -> pd.DataFrame:
    records = []

    for rule in request.rules:
        records.append(
            {
                "antecedents": frozenset(rule.antecedents),
                "consequents": frozenset(rule.consequents),
                "support": rule.support,
                "confidence": rule.confidence,
                "lift": rule.lift,
            }
        )

    return pd.DataFrame.from_records(
        records,
        columns=[
            "antecedents",
            "consequents",
            "support",
            "confidence",
            "lift",
        ],
    )


def dataframe_to_records(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    if dataframe.empty:
        return []

    serialized = dataframe.where(
        pd.notna(dataframe),
        None,
    )

    return serialized.to_dict(orient="records")


def run_recommendations(
    request: RecommendationRequest,
) -> dict[str, Any]:
    rules_dataframe = rules_to_dataframe(request)

    result = generate_recommendations(
        rules=rules_dataframe,
        basket=request.basket,
        top_n=request.top_n,
        ranking_metric=request.ranking_metric,
    )

    return {
        "basket": list(result.parameters.basket),
        "ranking_metric": result.parameters.ranking_metric,
        "top_n": result.parameters.top_n,
        "execution_time": result.execution_time,
        "statistics": {
            "num_matching_rules": (
                result.statistics.num_matching_rules
            ),
            "num_candidate_items": (
                result.statistics.num_candidate_items
            ),
            "num_recommendations": (
                result.statistics.num_recommendations
            ),
        },
        "recommendations": dataframe_to_records(
            result.recommendations
        ),
    }
