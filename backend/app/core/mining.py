from time import perf_counter

import mlxtend
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth

from .enums import MiningAlgorithm
from .models import MiningParameters, MiningResult, MiningStatistics


def validate_mining_inputs(
    encoded_df: pd.DataFrame,
    algorithm: str | MiningAlgorithm,
    min_support: float,
    max_len: int | None = None,
) -> MiningAlgorithm:
    if encoded_df is None:
        raise ValueError("encoded_df cannot be None.")

    try:
        validated_algorithm = MiningAlgorithm(algorithm)
    except (ValueError, TypeError) as exc:
        supported = ", ".join(
            mining_algorithm.value
            for mining_algorithm in MiningAlgorithm
        )

        raise ValueError(
            f"Unsupported mining algorithm '{algorithm}'. "
            f"Supported algorithms: {supported}."
        ) from exc

    if (
        isinstance(min_support, bool)
        or not isinstance(min_support, (int, float))
    ):
        raise ValueError("min_support must be a number.")

    if not 0 < float(min_support) <= 1:
        raise ValueError("min_support must be in the range (0, 1].")

    if max_len is not None:
        if isinstance(max_len, bool) or not isinstance(max_len, int):
            raise ValueError("max_len must be an integer or None.")

        if max_len < 1:
            raise ValueError(
                "max_len must be greater than or equal to 1."
            )

    return validated_algorithm


def run_apriori(
    encoded_df: pd.DataFrame,
    min_support: float,
    max_len: int | None = None,
) -> pd.DataFrame:
    return apriori(
        encoded_df,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len,
    )


def run_fpgrowth(
    encoded_df: pd.DataFrame,
    min_support: float,
    max_len: int | None = None,
) -> pd.DataFrame:
    return fpgrowth(
        encoded_df,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len,
    )


def generate_mining_statistics(
    encoded_df: pd.DataFrame,
    frequent_itemsets: pd.DataFrame,
) -> MiningStatistics:
    return MiningStatistics(
        num_transactions=len(encoded_df),
        num_items=len(encoded_df.columns),
        num_frequent_itemsets=len(frequent_itemsets),
    )


def mine_patterns(
    encoded_df: pd.DataFrame,
    algorithm: str | MiningAlgorithm,
    min_support: float,
    max_len: int | None = None,
) -> MiningResult:
    validated_algorithm = validate_mining_inputs(
        encoded_df=encoded_df,
        algorithm=algorithm,
        min_support=min_support,
        max_len=max_len,
    )

    parameters = MiningParameters(
        algorithm=validated_algorithm,
        min_support=float(min_support),
        max_len=max_len,
    )

    start_time = perf_counter()

    if validated_algorithm == MiningAlgorithm.APRIORI:
        frequent_itemsets = run_apriori(
            encoded_df=encoded_df,
            min_support=parameters.min_support,
            max_len=parameters.max_len,
        )

    elif validated_algorithm == MiningAlgorithm.FP_GROWTH:
        frequent_itemsets = run_fpgrowth(
            encoded_df=encoded_df,
            min_support=parameters.min_support,
            max_len=parameters.max_len,
        )

    else:
        raise RuntimeError(
            f"Mining algorithm '{validated_algorithm}' "
            "has not been implemented."
        )

    execution_time = perf_counter() - start_time

    statistics = generate_mining_statistics(
        encoded_df=encoded_df,
        frequent_itemsets=frequent_itemsets,
    )

    return MiningResult(
        parameters=parameters,
        statistics=statistics,
        execution_time=execution_time,
        frequent_itemsets=frequent_itemsets,
        engine="mlxtend",
        engine_version=mlxtend.__version__,
    )
