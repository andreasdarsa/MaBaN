import streamlit as st

from bootstrap import PROJECT_ROOT


st.title("Recommendations")


if "analysis" not in st.session_state:

    st.info(
        "Run an analysis first."
    )

    st.stop()


st.info(
    "Recommendation API integration "
    "will be added next."
)


st.caption(
    "Analysis results are already available "
    "in Streamlit session state."
)