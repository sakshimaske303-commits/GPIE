import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ---- Keep header visible (needed for the sidebar
        open/close button) but hide only the Deploy button ---- */
[data-testid="stHeader"] {
    background-color: #04181B !important;
    height: 0rem !important;
    min-height: 0 !important;
    padding: 0 !important;
}
[data-testid="stAppDeployButton"] {
    display: none !important;
}
[data-testid="stDecoration"] {
    display: none !important;
}
#MainMenu {
    visibility: hidden !important;
}
.block-container {
    padding-top: 0.5rem !important;
}

        /* ---- Sidebar collapse/expand button — safety net
        covering every naming variant Streamlit has used
        across versions, since it's invisible-by-default on
        a dark theme and hard to see on mobile otherwise ---- */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="baseButton-header"],
        [data-testid="stHeader"] button,
        [data-testid*="ollapse" i],
        button[kind="header"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            background: #052226 !important;
            border: 1.5px solid #F88379 !important;
            border-radius: 8px !important;
            padding: 4px !important;
        }
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="baseButton-header"] svg,
        [data-testid="stHeader"] button svg,
        button[kind="header"] svg {
            fill: #F88379 !important;
            stroke: #F88379 !important;
            opacity: 1 !important;
        }

        /* Deep teal-black background with soft coral/blush glows */
        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(248, 131, 121, 0.07), transparent 40%),
                radial-gradient(circle at 85% 15%, rgba(242, 212, 215, 0.05), transparent 40%),
                radial-gradient(circle at 50% 90%, rgba(0, 135, 149, 0.10), transparent 45%),
                linear-gradient(135deg, #04181B 0%, #071E22 50%, #04181B 100%);
            color: #F5EDEE;
        }

        /* ============================================================
           SIDEBAR — colored this time, spacing kept tight (no gaps)
           ============================================================ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #052226 0%, #04181B 100%);
            border-right: 1px solid rgba(248, 131, 121, 0.2);
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #C9DADC !important;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] a {
            border-radius: 8px !important;
            padding: 8px 14px !important;
            transition: all 0.2s ease;
        }
        section[data-testid="stSidebar"] a:hover {
            background: rgba(248, 131, 121, 0.12) !important;
            border-left: 3px solid #F88379;
        }
        section[data-testid="stSidebar"] a[aria-current="page"],
        section[data-testid="stSidebar"] [aria-selected="true"] {
            background: rgba(0, 135, 149, 0.18) !important;
            border-left: 3px solid #008795;
            font-weight: 700 !important;
        }

        /* Headers - coral-to-teal-to-blush gradient */
        h1 {
            background: linear-gradient(90deg, #F88379, #F2D4D7, #008795);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            font-size: 2.8rem !important;
            letter-spacing: -0.5px;
        }

        h2 {
            color: #F88379 !important;
            font-weight: 700 !important;
            border-left: 4px solid #008795;
            padding-left: 12px;
        }

        h3 {
            color: #F2D4D7 !important;
            font-weight: 600 !important;
        }

        p, li, .stMarkdown {
            color: #D7E4E5;
        }

        strong, b {
            color: #F88379;
            font-weight: 700;
        }

        /* Metric cards - glassmorphism with coral top edge */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(0, 135, 149, 0.3);
            border-top: 2px solid rgba(248, 131, 121, 0.6);
            box-shadow: 0 4px 20px rgba(0, 135, 149, 0.10);
            backdrop-filter: blur(10px);
        }

        div[data-testid="stMetricValue"] {
            color: #F2D4D7 !important;
            font-weight: 700 !important;
            font-family: 'JetBrains Mono', monospace;
        }

        div[data-testid="stMetricLabel"] {
            color: #7FA8AC !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 1px;
        }

        /* Metric delta pills — coral instead of Streamlit's default green */
        div[data-testid="stMetricDelta"] {
            color: #F88379 !important;
        }
        div[data-testid="stMetricDelta"] svg {
            fill: #F88379 !important;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #F88379, #008795);
            color: #04181B;
            border-radius: 8px;
            border: none;
            font-weight: 700;
            padding: 0.5rem 1.5rem;
            transition: all 0.25s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 0 20px rgba(248, 131, 121, 0.5);
            transform: translateY(-2px);
        }

        /* Info/success/warning boxes */
        div[data-testid="stAlert"] {
            background: rgba(0, 135, 149, 0.08);
            border: 1px solid rgba(0, 135, 149, 0.3);
            border-left: 3px solid #F88379;
            border-radius: 10px;
            color: #D7E4E5;
        }

        /* Dataframes */
        .dataframe {
            border-radius: 10px !important;
            border: 1px solid rgba(0, 135, 149, 0.3) !important;
        }

        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, #F88379, #F2D4D7, #008795, transparent);
            border-radius: 10px;
            margin: 1.5rem 0;
        }

        /* Code-style caption */
        .caption-text {
            font-family: 'JetBrains Mono', monospace;
            color: #7FA8AC;
            font-size: 0.85rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.03);
            border-radius: 8px 8px 0 0;
            color: #7FA8AC;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(248, 131, 121, 0.12) !important;
            color: #F88379 !important;
        }

        /* Custom scrollbar — coral-to-teal */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #04181B;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #F88379, #008795);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #F88379, #F2D4D7);
        }
        </style>
    """, unsafe_allow_html=True)


PALETTE = {
    "chantilly": "#F2D4D7",
    "coral": "#F88379",
    "lagoon": "#008795",
    # legacy key names kept so any existing page code referencing these still works
    "cyan": "#008795",
    "purple": "#F88379",
    "green": "#F2D4D7",
    "gold": "#F88379",
    "slate": "#04181B",
    "text_muted": "#7FA8AC",
    "text": "#F5EDEE",
}