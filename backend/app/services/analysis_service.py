from typing import Any

import pandas as pd

from app.core.enums import DatasetFormat
from app.core.insights import generate_insights
from app.core.mining import mine_patterns
from app.core.preprocessing import preprocess_dataset
from app.core.rules import generate_association_rules
from app.schemas.analysis import AnalysisRequest


def transactions_to_long_dataframe(
    request: AnalysisRequest,
) -> pd.DataFrame:
    records: list[dict[str, str]] = []

    for transaction in request.transactions:
        for item in transaction.items:
            records.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "item": item,
                }
            )

    return pd.DataFrame.from_records(
        records,
        columns=["transaction_id", "item"],
    )
# API accepts transactions as {"transaction_id":..., "items":...}, therefore we should focus on converting
# transactions list to long dataset format


def serialize_collection(value: Any) -> Any:
    if isinstance(value, (set, frozenset, tuple)):
        return sorted(str(item) for item in value)

    return value


def dataframe_to_records(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    if dataframe.empty:
        return []

    serialized = dataframe.copy()

    for column in serialized.columns:
        serialized[column] = serialized[column].apply(
            serialize_collection
        )

    serialized = serialized.astype(object).where(
        pd.notna(serialized),
        None,
    )

    return serialized.to_dict(orient="records")


def run_analysis(
    request: AnalysisRequest,
) -> dict[str, Any]:
    dataframe = transactions_to_long_dataframe(request)

    preprocessing_result = preprocess_dataset(
        df=dataframe,
        dataset_format=DatasetFormat.LONG,  # no need to adapt core, service is used for that
        transaction_col="transaction_id",
        item_col="items",
    )

    mining_result = mine_patterns(
        encoded_df=preprocessing_result.encoded_df,
        algorithm=request.algorithm,
        min_support=request.min_support,
        max_len=request.max_len,
    )

    rule_result = generate_association_rules(
        frequent_itemsets=mining_result.frequent_itemsets,
        metric=request.rule_metric,
        min_threshold=request.rule_threshold,
    )

    insights_result = generate_insights(
        frequent_itemsets=mining_result.frequent_itemsets,
        rules=rule_result.rules,
        top_n=request.top_n,
    )

    return {
        "dataset_summary": {
            "num_transactions": (
                preprocessing_result.summary.num_transactions
            ),
            "num_unique_items": (
                preprocessing_result.summary.num_unique_items
            ),
            "avg_basket_size": (
                preprocessing_result.summary.avg_basket_size
            ),
        },
        "mining_statistics": {
            "num_transactions": (
                mining_result.statistics.num_transactions
            ),
            "num_items": (
                mining_result.statistics.num_items
            ),
            "num_frequent_itemsets": (
                mining_result.statistics.num_frequent_itemsets
            ),
        },
        "mining_execution_time": (
            mining_result.execution_time
        ),
        "rule_statistics": {
            "num_rules": (
                rule_result.statistics.num_rules
            ),
            "num_unique_antecedents": (
                rule_result.statistics.num_unique_antecedents
            ),
            "num_unique_consequents": (
                rule_result.statistics.num_unique_consequents
            ),
        },
        "rule_execution_time": rule_result.execution_time,
        "frequent_itemsets": dataframe_to_records(
            mining_result.frequent_itemsets
        ),
        "rules": dataframe_to_records(
            rule_result.rules
        ),
        "insight_statistics": {
            "num_frequent_itemsets": (
                insights_result.statistics.num_frequent_itemsets
            ),
            "num_rules": (
                insights_result.statistics.num_rules
            ),
            "num_unique_items": (
                insights_result.statistics.num_unique_items
            ),
            "avg_rule_confidence": (
                insights_result.statistics.avg_rule_confidence
            ),
            "avg_rule_lift": (
                insights_result.statistics.avg_rule_lift
            ),
        },
        "top_items": dataframe_to_records(
            insights_result.top_items
        ),
        "top_itemsets": dataframe_to_records(
            insights_result.top_itemsets
        ),
        "top_rules": dataframe_to_records(
            insights_result.top_rules
        ),
        "item_role_summary": dataframe_to_records(
            insights_result.item_role_summary
        ),
    }
