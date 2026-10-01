import pandas as pd
import streamlit as st

from bootstrap import PROJECT_ROOT
from api_client import (
    APIClientError,
    get_api_client,
)
from styles import apply_styles

st.set_page_config(
    page_title="MaBaN - Upload dataset",
    page_icon="📊",
    layout="wide",
)

st.title("Upload Dataset")

st.write(
    "Upload a CSV transaction dataset and configure its structure."
)

apply_styles()

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"],
)


if uploaded_file is None:
    st.info("Choose a CSV file to continue.")
    st.stop()


try:
    df = pd.read_csv(uploaded_file)

except Exception as exc:
    st.error(
        f"Could not read the CSV file: {exc}"
    )
    st.stop()


if df.empty:
    st.error(
        "The uploaded CSV file is empty."
    )
    st.stop()


st.success(
    f"Dataset loaded: {uploaded_file.name}"
)


st.subheader("Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True,
)


col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Rows",
        len(df),
    )

with col2:
    st.metric(
        "Columns",
        len(df.columns),
    )


st.subheader("Dataset Structure")


dataset_type = st.radio(
    "Dataset type",
    options=[
        "long",
        "basket",
    ],
    format_func=lambda value: (
        "Long / invoice-item"
        if value == "long"
        else "Basket per row"
    ),
    horizontal=True,
)


columns = df.columns.tolist()


transaction_col = st.selectbox(
    "Transaction / basket ID column",
    options=columns,
)


if dataset_type == "long":

    item_col = st.selectbox(
        "Item column",
        options=columns,
    )

    valid_config = (
        transaction_col != item_col
    )

    basket_item_cols = None

else:

    item_col = None

    st.caption(
        "Select the columns containing product names."
    )

    basket_item_cols = st.multiselect(
        "Item columns",
        options=[
            column
            for column in columns
            if column != transaction_col
        ],
    )

    valid_config = bool(
        basket_item_cols
    )

    if not basket_item_cols:
        st.warning(
            "Select at least one item column."
        )


st.divider()


if st.button(
    "Connect Dataset",
    type="primary",
    disabled=not valid_config,
):

    client = get_api_client()

    try:

        upload_response = (
            client.upload_dataset(
                file_bytes=uploaded_file.getvalue(),
                filename=uploaded_file.name,
                dataset_format=dataset_type,
                transaction_col=transaction_col,
                item_col=item_col,
            )
        )

    except APIClientError as exc:

        st.error(str(exc))
        st.stop()


    st.session_state["raw_dataset"] = df

    st.session_state["dataset_filename"] = (
        uploaded_file.name
    )

    st.session_state["column_mapping"] = {
        "dataset_format": dataset_type,
        "transaction_col": transaction_col,
        "item_col": item_col,
        "basket_item_cols": (
            basket_item_cols
            if dataset_type == "basket"
            else None
        ),
    }

    st.session_state["upload_response"] = (
        upload_response
    )

    # Old analysis results are no longer valid.
    st.session_state.pop(
        "analysis",
        None,
    )

    st.session_state.pop(
        "analysis_config",
        None,
    )

    st.success(
        "Dataset connected to the MaBaN API."
    )

    with st.expander(
        "API upload response"
    ):
        st.json(upload_response)