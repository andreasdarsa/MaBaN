import pandas as pd
import streamlit as st

from styles import apply_styles

st.set_page_config(page_title="MaBaN | Rules", page_icon="🛒", layout="wide")
apply_styles()

st.markdown('<div class="maban-kicker">STEP 3</div>', unsafe_allow_html=True)
st.title("Association Rules")
analysis = st.session_state.get("analysis")
if analysis is None:
    st.info("Run an analysis first.")
    st.stop()

rules = pd.DataFrame(analysis.get("rules", []))
if rules.empty:
    st.info("No association rules were generated with the current thresholds.")
    st.stop()


def format_rule(row: pd.Series) -> str:
    left = ", ".join(sorted(map(str, row["antecedents"])))
    right = ", ".join(sorted(map(str, row["consequents"])))
    return f"{left} → {right}"

rules["Rule"] = rules.apply(format_rule, axis=1)

c1, c2, c3 = st.columns(3)
with c1:
    min_confidence = st.slider("Minimum confidence", 0.0, 1.0, 0.0, 0.05)
with c2:
    min_lift = st.number_input("Minimum lift", 0.0, 100.0, 0.0, 0.1)
with c3:
    sort_by = st.selectbox("Sort by", ["lift", "confidence", "support"])

filtered = rules[(rules["confidence"] >= min_confidence) & (rules["lift"] >= min_lift)].sort_values(sort_by, ascending=False)

if filtered.empty:
    st.warning("No rules match the selected filters.")
else:
    display = filtered[["Rule", "support", "confidence", "lift"]].copy()
    for column in ["support", "confidence", "lift"]:
        display[column] = display[column].map(lambda x: f"{x:.3f}")
    st.dataframe(
        display.rename(columns={"support": "Support", "confidence": "Confidence", "lift": "Lift"}),
        use_container_width=True,
        hide_index=True,
    )

st.download_button(
    "Download all rules as CSV",
    data=pd.DataFrame(analysis.get("rules", [])).to_csv(index=False).encode("utf-8"),
    file_name="maban_rules.csv",
    mime="text/csv",
)
