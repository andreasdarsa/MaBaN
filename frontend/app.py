import streamlit as st

from bootstrap import PROJECT_ROOT
from api_client import (
    APIClientError,
    get_api_client,
)
from styles import apply_styles


st.set_page_config(
    page_title="MaBaN",
    page_icon="📊",
    layout="wide",
)

apply_styles()

st.title("MaBaN")
st.subheader("Market Basket Analysis")

st.write(
    "Discover product relationships, purchasing patterns, "
    "recommendations, and actionable business insights."
)


st.divider()


st.markdown("### Workflow")

st.markdown(
    """
    1. Upload your transaction dataset
    2. Configure the dataset structure
    3. Run the market basket analysis
    4. Explore rules, itemsets, and recommendations
    """
)


st.divider()


client = get_api_client()


try:
    health = client.health()

    st.success(
        f"Backend connected — "
        f"{health.get('service', 'MaBaN API')}"
    )

except APIClientError as exc:

    st.warning(str(exc))

    st.caption(
        "Start the FastAPI backend before running an analysis. "
        "Default API URL: http://localhost:8000/api/v1"
    )