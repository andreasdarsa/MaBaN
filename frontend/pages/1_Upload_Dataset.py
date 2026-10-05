import pandas as pd
import streamlit as st

from api_client import APIClientError, get_api_client
from styles import apply_styles

st.set_page_config(page_title="MaBaN | Upload Dataset", page_icon="🛒", layout="wide")
apply_styles()

st.markdown('<div class="maban-kicker">STEP 1</div>', unsafe_allow_html=True)
st.title("Upload Dataset")
st.markdown('<div class="maban-subtitle">Connect a CSV transaction dataset and describe its structure.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file is None:
    st.info("Upload a CSV file to continue.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Could not read the CSV file: {exc}")
    st.stop()

if df.empty:
    st.error("The uploaded CSV file is empty.")
    st.stop()

m1, m2, m3 = st.columns(3)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", len(df.columns))
m3.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")

with st.expander("Preview dataset", expanded=True):
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

st.markdown("### Dataset structure")
dataset_type = st.radio(
    "Dataset type",
    ["long", "basket"],
    format_func=lambda v: "Long / invoice-item" if v == "long" else "Basket per row",
    horizontal=True,
)
columns = df.columns.tolist()
transaction_col = st.selectbox("Transaction / basket ID column", columns)

if dataset_type == "long":
    item_col = st.selectbox("Item column", columns)
    basket_item_cols = None
    valid_config = transaction_col != item_col
else:
    item_col = None
    basket_item_cols = st.multiselect(
        "Item columns",
        [c for c in columns if c != transaction_col],
    )
    valid_config = bool(basket_item_cols)

if st.button("Connect Dataset", type="primary", disabled=not valid_config, use_container_width=True):
    try:
        response = get_api_client().upload_dataset(
            file_bytes=uploaded_file.getvalue(),
            filename=uploaded_file.name,
            dataset_format=dataset_type,
            transaction_col=transaction_col,
            item_col=item_col,
        )
    except APIClientError as exc:
        st.error(str(exc))
        st.stop()

    st.session_state["raw_dataset"] = df
    st.session_state["dataset_filename"] = uploaded_file.name
    st.session_state["column_mapping"] = {
        "dataset_format": dataset_type,
        "transaction_col": transaction_col,
        "item_col": item_col,
        "basket_item_cols": basket_item_cols if dataset_type == "basket" else None,
    }
    st.session_state["upload_response"] = response
    st.session_state.pop("analysis", None)
    st.session_state.pop("analysis_config", None)
    st.session_state.pop("recommendations", None)

    st.success("Dataset connected. Move to Analysis.")
