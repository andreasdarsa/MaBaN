import pandas as pd
import streamlit as st

from bootstrap import PROJECT_ROOT

from styles import apply_styles

apply_styles()

st.set_page_config(
    page_title="MaBaN - Rules",
    page_icon="📊",
    layout="wide",
)

st.title("Association Rules")


analysis = st.session_state.get(
    "analysis"
)


if analysis is None:

    st.info(
        "Run an analysis first."
    )

    st.stop()


rules = pd.DataFrame(
    analysis.get(
        "rules",
        [],
    )
)


if rules.empty:

    st.info(
        "No association rules were generated "
        "with the current thresholds."
    )

    st.stop()


st.write(
    f"Showing {len(rules)} generated rules."
)


preferred_columns = [
    column
    for column in [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction",
        "zhangs_metric",
    ]
    if column in rules.columns
]


if preferred_columns:

    display_df = rules[
        preferred_columns
    ]

else:

    display_df = rules


st.dataframe(
    display_df,
    use_container_width=True,
)


csv_data = (
    rules
    .to_csv(index=False)
    .encode("utf-8")
)


st.download_button(
    "Download rules as CSV",
    data=csv_data,
    file_name="maban_rules.csv",
    mime="text/csv",
)