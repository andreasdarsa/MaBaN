from __future__ import annotations

import pandas as pd
import streamlit as st

from api_client import APIClientError, get_api_client
from styles import apply_styles

st.set_page_config(page_title="MaBaN | Recommendations", page_icon="🛒", layout="wide")
apply_styles()

st.markdown('<div class="maban-kicker">STEP 4</div>', unsafe_allow_html=True)
st.title("Recommendations")
st.markdown('<div class="maban-subtitle">Select products already in a basket and let MaBaN rank what to recommend next.</div>', unsafe_allow_html=True)

analysis = st.session_state.get("analysis")
if analysis is None:
    st.info("Run an analysis first.")
    st.stop()

rules = pd.DataFrame(analysis.get("rules", []))
if rules.empty:
    st.info("No association rules are available. Lower the analysis thresholds and rerun.")
    st.stop()

items = set()
for column in ("antecedents", "consequents"):
    for values in rules[column]:
        items.update(map(str, values))
available_items = sorted(items, key=str.lower)

c1, c2 = st.columns([2, 1])
with c1:
    basket = st.multiselect("Current basket", available_items)
with c2:
    ranking_metric = st.selectbox("Rank by", ["confidence", "lift", "support"])

top_n = st.slider("Number of recommendations", 1, 10, 5)

if not basket:
    st.markdown('<div class="maban-card maban-card-accent-yellow"><strong>Select at least one item.</strong><br><span class="maban-subtitle">MaBaN will find rules whose antecedents match the basket.</span></div>', unsafe_allow_html=True)
    st.stop()

if st.button("Generate Recommendations", type="primary", use_container_width=True):
    payload = {
        "rules": rules.to_dict(orient="records"),
        "basket": basket,
        "top_n": top_n,
        "ranking_metric": ranking_metric,
    }
    with st.spinner("Ranking recommendations..."):
        try:
            result = get_api_client().recommend(payload)
        except APIClientError as exc:
            st.error(str(exc))
            st.stop()
    st.session_state["recommendations"] = result

result = st.session_state.get("recommendations")
if result is None:
    st.info("Generate recommendations to see ranked products.")
    st.stop()

stats = result["statistics"]
s1, s2, s3 = st.columns(3)
s1.metric("Matching rules", stats["num_matching_rules"])
s2.metric("Candidate items", stats["num_candidate_items"])
s3.metric("Recommendations", stats["num_recommendations"])

recommendations = result.get("recommendations", [])
if not recommendations:
    st.warning("No recommendations were found for this basket.")
    st.stop()

st.markdown("### Ranked recommendations")
cols = st.columns(min(3, len(recommendations)))
for index, rec in enumerate(recommendations):
    with cols[index % len(cols)]:
        st.markdown(
            f'<div class="maban-recommendation">'
            f'<div class="maban-kicker">#{index + 1}</div>'
            f'<div class="item">{rec["item"]}</div>'
            f'<div class="score">{rec["score"]:.3f}</div>'
            f'<div class="meta">{ranking_metric.title()} score</div>'
            f'<div class="meta">Confidence {rec["confidence"]:.3f} · Lift {rec["lift"]:.3f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.caption(f"Execution time: {result.get('execution_time', 0):.4f}s")
