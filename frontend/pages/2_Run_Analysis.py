from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from bootstrap import PROJECT_ROOT
from api_client import (
    APIClientError,
    get_api_client,
)


st.title("Run Analysis")


if (
    "raw_dataset" not in st.session_state
    or "column_mapping" not in st.session_state
):

    st.info(
        "Upload and connect a dataset first."
    )

    st.stop()


df: pd.DataFrame = (
    st.session_state["raw_dataset"]
)


config: dict[str, Any] = (
    st.session_state["column_mapping"]
)


st.caption(
    f"Dataset: "
    f"{st.session_state.get(
        'dataset_filename',
        'Uploaded CSV'
    )}"
)


st.subheader("Analysis Settings")


algorithm = st.selectbox(
    "Algorithm",
    options=[
        "apriori",
        "fpgrowth",
    ],
    format_func=lambda value: (
        "FP-Growth"
        if value == "fpgrowth"
        else "Apriori"
    ),
)


min_support = st.number_input(
    "Minimum support",
    min_value=0.001,
    max_value=1.0,
    value=0.05,
    step=0.01,
    format="%.3f",
)


max_len = st.number_input(
    "Maximum itemset length",
    min_value=1,
    value=3,
    step=1,
)


rule_metric = st.selectbox(
    "Rule metric",
    options=[
        "confidence",
        "lift",
        "leverage",
        "conviction",
        "zhangs_metric",
    ],
)


rule_threshold = st.number_input(
    "Rule threshold",
    min_value=0.0,
    value=0.5,
    step=0.05,
)


top_n = st.number_input(
    "Top N",
    min_value=1,
    value=10,
    step=1,
)


def build_transactions() -> list[dict[str, Any]]:
    transaction_col = (
        config["transaction_col"]
    )

    # -----------------------------
    # LONG FORMAT
    # -----------------------------

    if config["dataset_format"] == "long":

        item_col = config["item_col"]

        work = (
            df[
                [
                    transaction_col,
                    item_col,
                ]
            ]
            .dropna()
        )

        grouped = (
            work
            .groupby(
                transaction_col,
                sort=False,
            )[item_col]
            .apply(list)
        )

        transactions = []

        for transaction_id, items in (
            grouped.items()
        ):

            cleaned_items = list(
                dict.fromkeys(
                    str(item).strip()
                    for item in items
                    if str(item).strip()
                )
            )

            if cleaned_items:

                transactions.append(
                    {
                        "transaction_id": str(
                            transaction_id
                        ),
                        "items": cleaned_items,
                    }
                )

        return transactions

    # -----------------------------
    # BASKET FORMAT
    # -----------------------------

    item_columns = (
        config["basket_item_cols"]
        or []
    )

    transactions = []

    for row_index, row in df.iterrows():

        items = []

        for column in item_columns:

            value = row[column]

            if (
                pd.notna(value)
                and str(value).strip()
            ):

                items.append(
                    str(value).strip()
                )

        items = list(
            dict.fromkeys(items)
        )

        if not items:
            continue

        transactions.append(
            {
                "transaction_id": str(
                    row[transaction_col]
                ),
                "items": items,
            }
        )

    return transactions


st.divider()


if st.button(
    "Run Analysis",
    type="primary",
):

    try:

        transactions = (
            build_transactions()
        )

    except Exception as exc:

        st.error(
            "Could not prepare the "
            f"transaction payload: {exc}"
        )

        st.stop()


    if len(transactions) < 2:

        st.error(
            "At least two valid transactions "
            "are required for analysis."
        )

        st.stop()


    payload = {
        "transactions": transactions,
        "algorithm": algorithm,
        "min_support": min_support,
        "max_len": max_len,
        "rule_metric": rule_metric,
        "rule_threshold": rule_threshold,
        "top_n": top_n,
    }


    with st.spinner(
        "Running market basket analysis..."
    ):

        try:

            analysis = (
                get_api_client()
                .run_analysis(payload)
            )

        except APIClientError as exc:

            st.error(str(exc))
            st.stop()


    st.session_state["analysis"] = (
        analysis
    )

    st.session_state[
        "analysis_config"
    ] = payload

    st.success(
        "Analysis completed."
    )


analysis = st.session_state.get(
    "analysis"
)


if analysis is None:

    st.info(
        "Configure the analysis and click "
        "'Run Analysis' to generate results."
    )

    st.stop()


st.divider()

st.subheader("Analysis Results")


summary = analysis["dataset_summary"]

mining = analysis["mining_statistics"]

insights = analysis["insight_statistics"]


m1, m2, m3, m4 = st.columns(4)


m1.metric(
    "Transactions",
    summary["num_transactions"],
)

m2.metric(
    "Unique items",
    summary["num_unique_items"],
)

m3.metric(
    "Frequent itemsets",
    mining["num_frequent_itemsets"],
)

m4.metric(
    "Association rules",
    insights["num_rules"],
)


m5, m6, m7 = st.columns(3)


m5.metric(
    "Avg. basket size",
    f"{summary['avg_basket_size']:.2f}",
)


m6.metric(
    "Avg. confidence",
    (
        "—"
        if insights["avg_rule_confidence"] is None
        else f"{insights['avg_rule_confidence']:.3f}"
    ),
)


m7.metric(
    "Avg. lift",
    (
        "—"
        if insights["avg_rule_lift"] is None
        else f"{insights['avg_rule_lift']:.3f}"
    ),
)


st.subheader("Top Rules")


top_rules = pd.DataFrame(
    analysis.get(
        "top_rules",
        [],
    )
)


if top_rules.empty:

    st.info(
        "No rules matched the selected thresholds."
    )

else:

    st.dataframe(
        top_rules,
        use_container_width=True,
    )


st.subheader("Top Itemsets")


top_itemsets = pd.DataFrame(
    analysis.get(
        "top_itemsets",
        [],
    )
)


if top_itemsets.empty:

    st.info(
        "No frequent itemsets matched "
        "the selected support."
    )

else:

    st.dataframe(
        top_itemsets,
        use_container_width=True,
    )