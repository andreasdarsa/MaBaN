from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from api_client import APIClientError, get_api_client
from styles import apply_styles

st.set_page_config(page_title="MaBaN | Analysis", page_icon="🛒", layout="wide")
apply_styles()


def build_transactions(df: pd.DataFrame, config: dict[str, Any]) -> list[dict[str, Any]]:
    transaction_col = config["transaction_col"]
    if config["dataset_format"] == "long":
        work = df[[transaction_col, config["item_col"]]].dropna()
        grouped = work.groupby(transaction_col, sort=False)[config["item_col"]].apply(list)
        return [
            {"transaction_id": str(tid), "items": list(dict.fromkeys(str(x).strip() for x in items if str(x).strip()))}
            for tid, items in grouped.items()
            if items
        ]

    transactions = []
    for _, row in df.iterrows():
        items = [
            str(row[col]).strip()
            for col in (config["basket_item_cols"] or [])
            if pd.notna(row[col]) and str(row[col]).strip()
        ]
        items = list(dict.fromkeys(items))
        if items:
            transactions.append({"transaction_id": str(row[transaction_col]), "items": items})
    return transactions


def format_rule_part(values: object) -> str:
    if isinstance(values, str):
        return values

    return ", ".join(
        sorted(str(item) for item in values)
    )


def rule_text(row: dict[str, Any]) -> str:
    left = format_rule_part(
        row.get("antecedents", [])
    )

    right = format_rule_part(
        row.get("consequents", [])
    )

    return f"{left} → {right}"

if "raw_dataset" not in st.session_state or "column_mapping" not in st.session_state:
    st.info("Upload and connect a dataset first.")
    st.stop()

df = st.session_state["raw_dataset"]
config = st.session_state["column_mapping"]

st.markdown('<div class="maban-kicker">STEP 2</div>', unsafe_allow_html=True)
st.title("Analysis")
st.markdown(
    f'<span class="maban-badge maban-badge-info">Dataset · {st.session_state.get("dataset_filename", "Uploaded CSV")}</span>',
    unsafe_allow_html=True,
)

with st.expander("Analysis configuration", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        algorithm = st.selectbox("Algorithm", ["apriori", "fpgrowth"], format_func=lambda v: "FP-Growth" if v == "fpgrowth" else "Apriori")
        min_support = st.number_input("Minimum support", 0.001, 1.0, 0.05, 0.01, format="%.3f")
    with c2:
        max_len = st.number_input("Maximum itemset length", 1, 20, 3, 1)
        rule_metric = st.selectbox("Rule metric", ["confidence", "lift", "leverage", "conviction", "zhangs_metric"])
    with c3:
        rule_threshold = st.number_input("Rule threshold", 0.0, 10.0, 0.5, 0.05)
        top_n = st.number_input("Top N", 1, 100, 10, 1)

    if st.button("Run Analysis", type="primary", use_container_width=True):
        transactions = build_transactions(df, config)
        if len(transactions) < 2:
            st.error("At least two valid transactions are required.")
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
        with st.spinner("Running market basket analysis..."):
            try:
                analysis = get_api_client().run_analysis(payload)
            except APIClientError as exc:
                st.error(str(exc))
                st.stop()
        st.session_state["analysis"] = analysis
        st.session_state["analysis_config"] = payload
        st.session_state.pop("recommendations", None)
        st.success("Analysis completed.")

analysis = st.session_state.get("analysis")
if analysis is None:
    st.info("Configure the analysis and click Run Analysis.")
    st.stop()

summary = analysis["dataset_summary"]
mining = analysis["mining_statistics"]
insights = analysis["insight_statistics"]

st.markdown("### Results")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Transactions", f"{summary['num_transactions']:,}")
m2.metric("Unique items", f"{summary['num_unique_items']:,}")
m3.metric("Frequent itemsets", f"{mining['num_frequent_itemsets']:,}")
m4.metric("Association rules", f"{insights['num_rules']:,}")

m5, m6, m7 = st.columns(3)
m5.metric("Avg. basket size", f"{summary['avg_basket_size']:.2f}")
m6.metric("Avg. confidence", "—" if insights["avg_rule_confidence"] is None else f"{insights['avg_rule_confidence']:.3f}")
m7.metric("Avg. lift", "—" if insights["avg_rule_lift"] is None else f"{insights['avg_rule_lift']:.3f}")

st.markdown("### Key insights")
left, right = st.columns(2)
with left:
    st.markdown('<div class="maban-card maban-card-accent-orange"><strong>Top association rules</strong><br><span class="maban-subtitle">Highest-lift rules from the analysis.</span></div>', unsafe_allow_html=True)
    top_rules = analysis.get("top_rules", [])
    if not top_rules:
        st.info("No rules matched the selected thresholds.")
    for row in top_rules[:5]:
        st.markdown(
            f'<div class="maban-rule"><div class="rule">{rule_text(row)}</div><div class="metrics">Support {row["support"]:.3f} · Confidence {row["confidence"]:.3f} · Lift {row["lift"]:.3f}</div></div>',
            unsafe_allow_html=True,
        )
with right:
    st.markdown('<div class="maban-card maban-card-accent-teal"><strong>Top items</strong><br><span class="maban-subtitle">Most frequent singleton itemsets.</span></div>', unsafe_allow_html=True)
    top_items = pd.DataFrame(analysis.get("top_items", []))
    if top_items.empty:
        st.info("No singleton itemsets matched the support threshold.")
    else:
        top_items["support"] = top_items["support"].map(lambda x: f"{x:.3f}")
        st.dataframe(top_items.rename(columns={"item": "Item", "support": "Support"}), use_container_width=True, hide_index=True)

st.markdown("### Top itemsets")
top_itemsets = pd.DataFrame(analysis.get("top_itemsets", []))
if top_itemsets.empty:
    st.info("No multi-item itemsets matched the selected support.")
else:
    top_itemsets["support"] = top_itemsets["support"].map(lambda x: f"{x:.3f}")
    st.dataframe(
        top_itemsets.rename(columns={"itemset": "Itemset", "itemset_size": "Size", "support": "Support"}),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    f"Mining {analysis['mining_execution_time']:.3f}s · Rules {analysis['rule_execution_time']:.3f}s"
)
