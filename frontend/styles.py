from __future__ import annotations

import streamlit as st


# ============================================================
# MaBaN Dark Theme
# Based on the existing MaBaN logo palette.
# ============================================================

# Brand colors
NAVY = "#0E3447"
GREEN = "#296639"
GREEN_DARK = "#144B2C"
ORANGE = "#EE5F2C"
ORANGE_LIGHT = "#F18130"
TEAL = "#4E9F92"
BLUE = "#1D648D"

# Semantic colors
YELLOW = "#F6C343"
RED = "#EF4444"

# Dark UI neutrals
BACKGROUND = "#081117"
SURFACE = "#111827"
SURFACE_ALT = "#1A2332"
SURFACE_ELEVATED = "#202C3B"
BORDER = "#2A3748"

# Text
TEXT = "#E5E7EB"
TEXT_SECONDARY = "#CBD5E1"
TEXT_MUTED = "#94A3B8"
TEXT_DISABLED = "#64748B"

# Semantic backgrounds
SUCCESS_BG = "#0D2E1D"
WARNING_BG = "#342A08"
ERROR_BG = "#351417"
INFO_BG = "#0A2535"


def apply_styles() -> None:
    """Apply the shared MaBaN dark visual system to the current Streamlit page."""

    st.markdown(
        f"""
        <style>
            :root {{
                --maban-navy: {NAVY};
                --maban-green: {GREEN};
                --maban-green-dark: {GREEN_DARK};
                --maban-orange: {ORANGE};
                --maban-orange-light: {ORANGE_LIGHT};
                --maban-teal: {TEAL};
                --maban-blue: {BLUE};
                --maban-yellow: {YELLOW};
                --maban-red: {RED};

                --maban-background: {BACKGROUND};
                --maban-surface: {SURFACE};
                --maban-surface-alt: {SURFACE_ALT};
                --maban-surface-elevated: {SURFACE_ELEVATED};
                --maban-border: {BORDER};

                --maban-text: {TEXT};
                --maban-text-secondary: {TEXT_SECONDARY};
                --maban-text-muted: {TEXT_MUTED};
                --maban-text-disabled: {TEXT_DISABLED};

                --maban-success-bg: {SUCCESS_BG};
                --maban-warning-bg: {WARNING_BG};
                --maban-error-bg: {ERROR_BG};
                --maban-info-bg: {INFO_BG};
            }}

            .stApp {{
                background:
                    radial-gradient(
                        circle at top right,
                        rgba(41, 102, 57, 0.10),
                        transparent 28%
                    ),
                    var(--maban-background);
                color: var(--maban-text);
            }}

            [data-testid="stAppViewContainer"] {{
                background: transparent;
            }}

            [data-testid="stMainBlockContainer"] {{
                max-width: 1400px;
                padding-top: 4rem;
                padding-bottom: 3rem;
            }}

            [data-testid="stHeader"] {{
                background: transparent;
            }}

            [data-testid="stSidebar"] {{
                background: var(--maban-surface);
                border-right: 1px solid var(--maban-border);
            }}

            [data-testid="stSidebar"] > div:first-child {{
                background: var(--maban-surface);
            }}

            [data-testid="stSidebar"] * {{
                color: var(--maban-text);
            }}

            [data-testid="stSidebarNav"] {{
                padding-top: 1rem;
            }}

            [data-testid="stSidebarNav"] span {{
                color: var(--maban-text-secondary);
            }}

            [data-testid="stSidebarNav"] a:hover {{
                background: var(--maban-surface-alt);
                border-radius: 10px;
            }}

            [data-testid="stSidebarNav"] a[aria-current="page"] {{
                background: rgba(41, 102, 57, 0.18);
                border-left: 3px solid var(--maban-green);
                border-radius: 0 10px 10px 0;
            }}

            [data-testid="stSidebarNav"] a[aria-current="page"] span {{
                color: #A7F3D0;
                font-weight: 700;
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: var(--maban-text) !important;
                letter-spacing: -0.02em;
            }}

            h1 {{
                font-weight: 750;
            }}

            h2, h3 {{
                font-weight: 700;
            }}

            p,
            label,
            [data-testid="stMarkdownContainer"] {{
                color: var(--maban-text);
            }}

            [data-testid="stCaptionContainer"] {{
                color: var(--maban-text-muted);
            }}

            .stButton > button {{
                border-radius: 10px;
                border: 1px solid var(--maban-green);
                background: var(--maban-green);
                color: white;
                font-weight: 700;
                padding: 0.55rem 1rem;
                transition:
                    background 120ms ease-in-out,
                    border-color 120ms ease-in-out,
                    transform 120ms ease-in-out;
            }}

            .stButton > button:hover {{
                background: var(--maban-green-dark);
                border-color: var(--maban-green-dark);
                color: white;
                transform: translateY(-1px);
            }}

            .stButton > button:focus {{
                box-shadow: 0 0 0 0.2rem rgba(41, 102, 57, 0.25);
            }}

            .stButton > button:disabled {{
                background: var(--maban-surface-elevated);
                border-color: var(--maban-border);
                color: var(--maban-text-disabled);
            }}

            [data-testid="stDownloadButton"] button {{
                border-radius: 10px;
                border: 1px solid var(--maban-blue);
                background: transparent;
                color: #7DD3FC;
                font-weight: 650;
            }}

            [data-testid="stDownloadButton"] button:hover {{
                background: rgba(29, 100, 141, 0.16);
                border-color: var(--maban-teal);
                color: white;
            }}

            [data-testid="metric-container"] {{
                background: linear-gradient(
                    145deg,
                    var(--maban-surface),
                    var(--maban-surface-alt)
                );
                border: 1px solid var(--maban-border);
                border-radius: 14px;
                padding: 1rem 1.1rem;
                box-shadow: 0 8px 22px rgba(0, 0, 0, 0.16);
            }}

            [data-testid="metric-container"]
            [data-testid="stMetricLabel"] {{
                color: var(--maban-text-muted);
                font-weight: 600;
            }}

            [data-testid="metric-container"]
            [data-testid="stMetricValue"] {{
                color: var(--maban-text);
                font-weight: 750;
            }}

            [data-testid="metric-container"]
            [data-testid="stMetricDelta"] {{
                color: #86EFAC;
            }}

            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"] > div {{
                background: var(--maban-surface) !important;
                border: 1px solid var(--maban-border) !important;
                border-radius: 10px !important;
                color: var(--maban-text) !important;
            }}

            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea,
            div[data-baseweb="select"] input {{
                color: var(--maban-text) !important;
            }}

            div[data-baseweb="input"] > div:hover,
            div[data-baseweb="select"] > div:hover,
            div[data-baseweb="textarea"] > div:hover {{
                border-color: #3D4D61 !important;
            }}

            div[data-baseweb="input"]:focus-within > div,
            div[data-baseweb="select"]:focus-within > div,
            div[data-baseweb="textarea"]:focus-within > div {{
                border-color: var(--maban-teal) !important;
                box-shadow: 0 0 0 1px var(--maban-teal) !important;
            }}

            [data-baseweb="popover"] {{
                background: var(--maban-surface) !important;
                border: 1px solid var(--maban-border) !important;
            }}

            [role="option"] {{
                background: var(--maban-surface) !important;
                color: var(--maban-text) !important;
            }}

            [role="option"]:hover {{
                background: var(--maban-surface-alt) !important;
            }}

            [data-testid="stFileUploader"] {{
                background: var(--maban-surface);
                border: 1px dashed #3D4D61;
                border-radius: 14px;
                padding: 0.4rem;
            }}

            [data-testid="stFileUploaderDropzone"] {{
                background: var(--maban-surface);
                border-radius: 12px;
            }}

            [data-testid="stFileUploader"] small {{
                color: var(--maban-text-muted) !important;
            }}

            [data-testid="stDataFrame"] {{
                border: 1px solid var(--maban-border);
                border-radius: 12px;
                overflow: hidden;
            }}

            [data-testid="stAlert"] {{
                border-radius: 12px;
            }}

            hr {{
                border-color: var(--maban-border);
            }}

            a {{
                color: #67E8F9;
                text-decoration: none;
            }}

            a:hover {{
                color: #A7F3D0;
                text-decoration: underline;
            }}

            [data-testid="stExpander"] {{
                background: var(--maban-surface);
                border: 1px solid var(--maban-border);
                border-radius: 12px;
            }}

            [data-testid="stExpander"] summary {{
                color: var(--maban-text);
            }}

            [data-testid="stCheckbox"] label,
            [data-testid="stRadio"] label {{
                color: var(--maban-text);
            }}

            [data-testid="stProgressBar"] > div > div {{
                background: linear-gradient(
                    90deg,
                    var(--maban-green),
                    var(--maban-teal)
                );
            }}

            ::-webkit-scrollbar {{
                width: 9px;
                height: 9px;
            }}

            ::-webkit-scrollbar-track {{
                background: var(--maban-background);
            }}

            ::-webkit-scrollbar-thumb {{
                background: #334155;
                border-radius: 999px;
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: #475569;
            }}

            /* Optional custom components for later dashboard work. */
            .maban-card {{
                background: linear-gradient(
                    145deg,
                    var(--maban-surface),
                    var(--maban-surface-alt)
                );
                border: 1px solid var(--maban-border);
                border-radius: 14px;
                padding: 1.1rem;
                box-shadow: 0 8px 22px rgba(0, 0, 0, 0.14);
            }}

            .maban-card-accent-green {{
                border-left: 4px solid var(--maban-green);
            }}

            .maban-card-accent-orange {{
                border-left: 4px solid var(--maban-orange);
            }}

            .maban-card-accent-yellow {{
                border-left: 4px solid var(--maban-yellow);
            }}

            .maban-card-accent-red {{
                border-left: 4px solid var(--maban-red);
            }}

            .maban-card-accent-teal {{
                border-left: 4px solid var(--maban-teal);
            }}

            .maban-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.28rem 0.65rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                border: 1px solid var(--maban-border);
                background: var(--maban-surface-alt);
                color: var(--maban-text-secondary);
            }}

            .maban-badge-success {{
                border-color: rgba(41, 102, 57, 0.7);
                background: var(--maban-success-bg);
                color: #86EFAC;
            }}

            .maban-badge-warning {{
                border-color: rgba(246, 195, 67, 0.65);
                background: var(--maban-warning-bg);
                color: #FDE68A;
            }}

            .maban-badge-danger {{
                border-color: rgba(239, 68, 68, 0.65);
                background: var(--maban-error-bg);
                color: #FCA5A5;
            }}

            .maban-badge-info {{
                border-color: rgba(29, 100, 141, 0.7);
                background: var(--maban-info-bg);
                color: #7DD3FC;
            }}

            .maban-kicker {{
                color: var(--maban-text-muted);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }}

            .maban-title {{
                color: var(--maban-text);
                font-size: 1.75rem;
                font-weight: 750;
                letter-spacing: -0.03em;
            }}

            .maban-subtitle {{
                color: var(--maban-text-muted);
                font-size: 0.98rem;
            }}

            .maban-recommendation .item {{
                color: #F8FAFC;
                font-size: 1.15rem;
                font-weight: 800 !important;
                letter-spacing: -0.01em;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
