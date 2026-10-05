import streamlit as st

from api_client import APIClientError, get_api_client
from styles import apply_styles

st.set_page_config(page_title="MaBaN", page_icon="🛒", layout="wide")
apply_styles()

st.markdown('<div class="maban-kicker">MARKET BASKET ANALYSIS</div>', unsafe_allow_html=True)
st.title("MaBaN")
st.markdown(
    '<div class="maban-subtitle">Discover product relationships, purchasing patterns, recommendations, and actionable insights.</div>',
    unsafe_allow_html=True,
)
st.markdown("")

try:
    health = get_api_client().health()
    st.markdown(
        '<div class="maban-card maban-card-accent-green"><strong>API connected</strong><br>'
        '<span class="maban-subtitle">MaBaN API is ready for analysis.</span></div>',
        unsafe_allow_html=True,
    )
except APIClientError as exc:
    st.markdown(
        '<div class="maban-card maban-card-accent-red"><strong>Backend offline</strong><br>'
        f'<span class="maban-subtitle">{exc}</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("### Workflow")
cols = st.columns(4)
steps = [
    ("01", "Upload", "Connect a CSV dataset."),
    ("02", "Configure", "Map the transaction structure."),
    ("03", "Analyze", "Mine itemsets and association rules."),
    ("04", "Recommend", "Turn rules into product suggestions."),
]
for col, (number, title, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="maban-card"><div class="maban-kicker">{number}</div>'
            f'<div style="font-size:1.05rem;font-weight:750;margin:.35rem 0">{title}</div>'
            f'<div class="maban-subtitle">{desc}</div></div>',
            unsafe_allow_html=True,
        )
