import streamlit as st
import pandas as pd
from backend.app.core.preprocessing import preprocess_dataset

st.title("Upload Dataset")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Structure")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")
    st.write(list(df.columns))

    dataset_type = st.radio(
        "Select dataset type",
        options=["long", "basket"],
        format_func=lambda x: "Long / invoice-item" if x == "long" else "Basket per row"
    )

    column_mapping = {"dataset_type": dataset_type}

    if dataset_type == "long":
        transaction_col = st.selectbox(
            "Transaction column",
            options=df.columns
        )

        item_col = st.selectbox(
            "Item column",
            options=df.columns
        )

        column_mapping.update({
            "transaction_col": transaction_col,
            "item_col": item_col,
            "basket_item_cols": None
        })

    else:
        basket_item_cols = st.multiselect(
            "Item columns",
            options=df.columns
        )

        transaction_col_option = st.selectbox(
            "Optional transaction/id column",
            options=["None"] + list(df.columns)
        )

        transaction_col = (
            None if transaction_col_option == "None"
            else transaction_col_option
        )

        column_mapping.update({
            "transaction_col": transaction_col,
            "item_col": None,
            "basket_item_cols": basket_item_cols
        })

    if st.button("Save dataset configuration"):
        st.session_state["raw_dataset"] = df
        st.session_state["column_mapping"] = column_mapping

        st.success("Dataset configuration saved.")
        st.json(column_mapping)

if st.button("Test preprocessing"):
    try:
        result = preprocess_dataset(
            df=df,
            **column_mapping
        )

        st.success("Preprocessing completed.")
        st.write(result["summary"])
        st.dataframe(result["encoded_df"].head())

    except ValueError as e:
        st.error(str(e))
