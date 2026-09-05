from time import perf_counter

import pandas as pd
from mlxtend.frequent_patterns import association_rules

from .enums import RuleMetric
from .models import RuleParameters, RuleResult, RuleStatistics


def validate_rule_inputs(
    frequent_itemsets: pd.DataFrame,
    metric: str | RuleMetric,
    min_threshold: float,
) -> RuleMetric:
    # Έλεγχος για το αν η λίστα συχνών στοιχειοσυνόλων είναι κενή
    if frequent_itemsets is None:
        raise ValueError("frequent_itemsets cannot be None.")

    # Έλεγχος για το αν υπάρχουν οι σωστές στήλες
    required_columns = {"support", "itemsets"}

    missing_columns = required_columns - set(frequent_itemsets.columns)

    if missing_columns:
        raise ValueError(
            "frequent_itemsets is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    try:
        validated_metric = RuleMetric(metric)
    except (ValueError, TypeError) as exc:
        supported = ", ".join(
            rule_metric.value
            for rule_metric in RuleMetric
        )

        raise ValueError(
            f"Unsupported rule metric '{metric}'. "
            f"Supported metrics: {supported}."
        ) from exc

    if (
        isinstance(min_threshold, bool)
        or not isinstance(min_threshold, (int, float))
    ):
        raise ValueError("min_threshold must be a number.")

    if float(min_threshold) < 0:
        raise ValueError(
            "min_threshold must be greater than or equal to 0."
        )

    return validated_metric


def run_association_rules(
    frequent_itemsets: pd.DataFrame,
    metric: RuleMetric,
    min_threshold: float,
) -> pd.DataFrame:
    return association_rules(
        frequent_itemsets,
        metric=metric.value,
        min_threshold=min_threshold,
    )


def generate_rule_statistics(
    rules: pd.DataFrame,
) -> RuleStatistics:
    if rules.empty:
        return RuleStatistics(
            num_rules=0,
            num_unique_antecedents=0,
            num_unique_consequents=0,
        )

    return RuleStatistics(
        num_rules=len(rules),
        num_unique_antecedents=rules["antecedents"].nunique(),
        num_unique_consequents=rules["consequents"].nunique(),
    )


def generate_association_rules(
    frequent_itemsets: pd.DataFrame,
    metric: str | RuleMetric = RuleMetric.CONFIDENCE,
    min_threshold: float = 0.5,
) -> RuleResult:
    validated_metric = validate_rule_inputs(
        frequent_itemsets=frequent_itemsets,
        metric=metric,
        min_threshold=min_threshold,
    )

    parameters = RuleParameters(
        metric=validated_metric,
        min_threshold=float(min_threshold),
    )

    start_time = perf_counter()

    rules = run_association_rules(
        frequent_itemsets=frequent_itemsets,
        metric=parameters.metric,
        min_threshold=parameters.min_threshold,
    )

    execution_time = perf_counter() - start_time

    statistics = generate_rule_statistics(rules)

    return RuleResult(
        parameters=parameters,
        statistics=statistics,
        execution_time=execution_time,
        rules=rules,
    )
