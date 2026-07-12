import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Dark tech background */
        .stApp {
            background: linear-gradient(135deg, #0a0e17 0%, #0f1419 50%, #0a0e17 100%);
            color: #e2e8f0;
        }

        /* Sidebar - deep slate */
        section[data-testid="stSidebar"] {
            background: #0d1117;
            border-right: 1px solid #1f2937;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #94a3b8 !important;
            font-weight: 500;
        }

        /* Headers - electric accent gradient */
        h1 {
            background: linear-gradient(90deg, #00d4ff, #7c3aed, #00ffa3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            font-size: 2.8rem !important;
            letter-spacing: -0.5px;
        }

        h2 {
            color: #00d4ff !important;
            font-weight: 700 !important;
            border-left: 4px solid #00d4ff;
            padding-left: 12px;
        }

        h3 {
            color: #a78bfa !important;
            font-weight: 600 !important;
        }

        p, li, .stMarkdown {
            color: #cbd5e1;
        }

        /* Metric cards - glassmorphism */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(0, 212, 255, 0.2);
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.08);
            backdrop-filter: blur(10px);
        }

        div[data-testid="stMetricValue"] {
            color: #00d4ff !important;
            font-weight: 700 !important;
            font-family: 'JetBrains Mono', monospace;
        }

        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 1px;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            color: #0a0e17;
            border-radius: 8px;
            border: none;
            font-weight: 700;
            padding: 0.5rem 1.5rem;
            transition: all 0.25s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            transform: translateY(-2px);
        }

        /* Info/success/warning boxes */
        div[data-testid="stAlert"] {
            background: rgba(0, 212, 255, 0.06);
            border: 1px solid rgba(0, 212, 255, 0.25);
            border-radius: 10px;
            color: #cbd5e1;
        }

        /* Dataframes */
        .dataframe {
            border-radius: 10px !important;
            border: 1px solid #1f2937 !important;
        }

        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #7c3aed, transparent);
            border-radius: 10px;
            margin: 1.5rem 0;
        }

        /* Code-style caption */
        .caption-text {
            font-family: 'JetBrains Mono', monospace;
            color: #64748b;
            font-size: 0.85rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.03);
            border-radius: 8px 8px 0 0;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(0, 212, 255, 0.1) !important;
            color: #00d4ff !important;
        }
        </style>
    """, unsafe_allow_html=True)


PALETTE = {
    "cyan": "#00d4ff",
    "purple": "#7c3aed",
    "green": "#00ffa3",
    "slate": "#0d1117",
    "text_muted": "#94a3b8",
    "text": "#e2e8f0",
}