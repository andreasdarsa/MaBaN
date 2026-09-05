from time import perf_counter

import pandas as pd

from .models import (
    InsightParameters,
    InsightStatistics,
    InsightsResult,
)


REQUIRED_ITEMSET_COLUMNS = {
    "support",
    "itemsets",
}

REQUIRED_RULE_COLUMNS = {
    "antecedents",
    "consequents",
    "support",
    "confidence",
    "lift",
}


def validate_insight_inputs(
    frequent_itemsets: pd.DataFrame,
    rules: pd.DataFrame,
    top_n: int,
) -> None:
    if frequent_itemsets is None:
        raise ValueError("frequent_itemsets cannot be None.")

    if not isinstance(frequent_itemsets, pd.DataFrame):
        raise TypeError(
            "frequent_itemsets must be a pandas DataFrame."
        )

    missing_itemset_columns = (
        REQUIRED_ITEMSET_COLUMNS
        - set(frequent_itemsets.columns)
    )

    if missing_itemset_columns:
        raise ValueError(
            "frequent_itemsets is missing required columns: "
            f"{sorted(missing_itemset_columns)}"
        )

    if rules is None:
        raise ValueError("rules cannot be None.")

    if not isinstance(rules, pd.DataFrame):
        raise TypeError("rules must be a pandas DataFrame.")

    missing_rule_columns = (
        REQUIRED_RULE_COLUMNS
        - set(rules.columns)
    )

    if missing_rule_columns:
        raise ValueError(
            "rules is missing required columns: "
            f"{sorted(missing_rule_columns)}"
        )

    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise ValueError("top_n must be an integer.")

    if top_n < 1:
        raise ValueError(
            "top_n must be greater than or equal to 1."
        )


def format_itemset(itemset: object) -> str:
    return ", ".join(
        sorted(str(item) for item in itemset)
    )


def generate_top_items(
    frequent_itemsets: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    singleton_mask = frequent_itemsets["itemsets"].apply(
        lambda itemset: len(itemset) == 1
    )

    singleton_itemsets = (
        frequent_itemsets
        .loc[singleton_mask, ["itemsets", "support"]]
        .copy()
    )

    if singleton_itemsets.empty:
        return pd.DataFrame(
            columns=["item", "support"]
        )

    singleton_itemsets["item"] = (
        singleton_itemsets["itemsets"]
        .apply(lambda itemset: str(next(iter(itemset))))
    )

    return (
        singleton_itemsets[
            ["item", "support"]
        ]
        .sort_values(
            by="support",
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def generate_top_itemsets(
    frequent_itemsets: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    multi_item_mask = frequent_itemsets["itemsets"].apply(
        lambda itemset: len(itemset) > 1
    )

    top_itemsets = (
        frequent_itemsets
        .loc[
            multi_item_mask,
            ["itemsets", "support"],
        ]
        .copy()
    )

    if top_itemsets.empty:
        return pd.DataFrame(
            columns=[
                "itemset",
                "itemset_size",
                "support",
            ]
        )

    top_itemsets["itemset"] = (
        top_itemsets["itemsets"].apply(format_itemset)
    )

    top_itemsets["itemset_size"] = (
        top_itemsets["itemsets"].apply(len)
    )

    return (
        top_itemsets[
            [
                "itemset",
                "itemset_size",
                "support",
            ]
        ]
        .sort_values(
            by=[
                "support",
                "itemset_size",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def generate_top_rules(
    rules: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    output_columns = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
    ]

    if rules.empty:
        return pd.DataFrame(columns=output_columns)

    top_rules = rules[output_columns].copy()

    top_rules["antecedents"] = (
        top_rules["antecedents"].apply(format_itemset)
    )

    top_rules["consequents"] = (
        top_rules["consequents"].apply(format_itemset)
    )

    return (
        top_rules
        .sort_values(
            by=[
                "lift",
                "confidence",
                "support",
            ],
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def generate_item_role_summary(
    rules: pd.DataFrame,
) -> pd.DataFrame:
    output_columns = [
        "item",
        "antecedent_count",
        "consequent_count",
        "total_rule_count",
    ]

    if rules.empty:
        return pd.DataFrame(columns=output_columns)

    antecedent_items = (
        rules[["antecedents"]]
        .explode("antecedents")
        .rename(
            columns={"antecedents": "item"}
        )
    )

    consequent_items = (
        rules[["consequents"]]
        .explode("consequents")
        .rename(
            columns={"consequents": "item"}
        )
    )

    antecedent_counts = (
        antecedent_items["item"]
        .value_counts()
        .rename("antecedent_count")
    )

    consequent_counts = (
        consequent_items["item"]
        .value_counts()
        .rename("consequent_count")
    )

    item_role_summary = (
        pd.concat(
            [
                antecedent_counts,
                consequent_counts,
            ],
            axis=1,
        )
        .fillna(0)
        .astype(int)
        .reset_index()
        .rename(columns={"index": "item"})
    )

    item_role_summary["item"] = (
        item_role_summary["item"].astype(str)
    )

    item_role_summary["total_rule_count"] = (
        item_role_summary["antecedent_count"]
        + item_role_summary["consequent_count"]
    )

    return (
        item_role_summary[
            output_columns
        ]
        .sort_values(
            by=[
                "total_rule_count",
                "consequent_count",
                "antecedent_count",
            ],
            ascending=False,
        )
        .reset_index(drop=True)
    )


def generate_insight_statistics(
    frequent_itemsets: pd.DataFrame,
    rules: pd.DataFrame,
) -> InsightStatistics:
    unique_items: set[str] = set()

    for itemset in frequent_itemsets["itemsets"]:
        unique_items.update(
            str(item) for item in itemset
        )

    avg_rule_confidence = (
        float(rules["confidence"].mean())
        if not rules.empty
        else None
    )

    avg_rule_lift = (
        float(rules["lift"].mean())
        if not rules.empty
        else None
    )

    return InsightStatistics(
        num_frequent_itemsets=len(frequent_itemsets),
        num_rules=len(rules),
        num_unique_items=len(unique_items),
        avg_rule_confidence=avg_rule_confidence,
        avg_rule_lift=avg_rule_lift,
    )


def generate_insights(
    frequent_itemsets: pd.DataFrame,
    rules: pd.DataFrame,
    top_n: int = 10,
) -> InsightsResult:
    validate_insight_inputs(
        frequent_itemsets=frequent_itemsets,
        rules=rules,
        top_n=top_n,
    )

    parameters = InsightParameters(
        top_n=top_n,
    )

    start_time = perf_counter()

    top_items = generate_top_items(
        frequent_itemsets=frequent_itemsets,
        top_n=top_n,
    )

    top_itemsets = generate_top_itemsets(
        frequent_itemsets=frequent_itemsets,
        top_n=top_n,
    )

    top_rules = generate_top_rules(
        rules=rules,
        top_n=top_n,
    )

    item_role_summary = generate_item_role_summary(
        rules=rules,
    )

    statistics = generate_insight_statistics(
        frequent_itemsets=frequent_itemsets,
        rules=rules,
    )

    execution_time = perf_counter() - start_time

    return InsightsResult(
        parameters=parameters,
        statistics=statistics,
        execution_time=execution_time,
        top_items=top_items,
        top_itemsets=top_itemsets,
        top_rules=top_rules,
        item_role_summary=item_role_summary,
    )
