import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="MaBaN",
    page_icon="📊",
    layout="wide",
)


st.title("MaBaN")
st.subheader("Market Basket Analysis")

st.write(
    "Discover product relationships, purchasing patterns, "
    "recommendations, and actionable business insights."
)


st.header("Dataset")

uploaded_file = st.file_uploader(
    "Upload your transactional dataset",
    type=["csv"],
)


if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)

    st.success(
        f"Dataset loaded: {uploaded_file.name}"
    )

    st.write("### Dataset Preview")
    st.dataframe(
        dataframe.head(),
        use_container_width=True,
    )

    dataset_format = st.selectbox(
        "Dataset format",
        options=["long", "basket", "onehot"],
    )

    st.write("### Column Mapping")

    columns = dataframe.columns.tolist()

    transaction_col = st.selectbox(
        "Transaction ID column",
        options=columns,
    )

    if dataset_format == "long":
        item_col = st.selectbox(
            "Item column",
            options=columns,
        )

    elif dataset_format == "basket":
        item_col = st.selectbox(
            "Items column",
            options=columns,
        )

    else:
        item_col = None


st.header("Analysis Settings")

algorithm = st.selectbox(
    "Algorithm",
    options=["apriori", "fpgrowth"],
)

min_support = st.number_input(
    "Minimum support",
    min_value=0.001,
    max_value=1.0,
    value=0.05,
    step=0.01,
)

max_len = st.number_input(
    "Maximum itemset length",
    min_value=1,
    value=3,
    step=1,
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


run_analysis = st.button(
    "Run Analysis",
    type="primary",
)


if run_analysis:
    if uploaded_file is None:
        st.error("Please upload a CSV file first.")
    else:
        st.info("API integration will be added next.")