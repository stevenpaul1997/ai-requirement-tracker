import streamlit as st
from database.postgres_client import initialize_tables
from components.intake_form import render_intake_form
from components.tracker import render_tracker
from components.traceability import render_traceability
from components.analytics import render_analytics

# Page config
st.set_page_config(
    page_title="AI Requirement Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }

        /* Header */
        .main-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid #gold;
            text-align: center;
        }

        .main-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
        }

        .main-header p {
            color: #a0aec0;
            font-size: 1rem;
            margin-top: 0.5rem;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #1a1a2e;
            padding: 0.5rem;
            border-radius: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #16213e;
            color: #a0aec0;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #0f3460;
            color: #ffffff;
        }

        /* Cards */
        .metric-card {
            background-color: #1a1a2e;
            border: 1px solid #2d3748;
            border-radius: 10px;
            padding: 1rem;
        }

        /* Buttons */
        .stButton > button {
            background-color: #0f3460;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            background-color: #1a4a8a;
            transform: translateY(-1px);
        }

        /* Form inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background-color: #1a1a2e;
            color: #ffffff;
            border: 1px solid #2d3748;
            border-radius: 8px;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1a1a2e;
            border-radius: 8px;
        }

        /* Divider */
        hr {
            border-color: #2d3748;
        }

        /* Success/Error/Warning */
        .stSuccess {
            background-color: #1a3a2a;
            border-left: 4px solid #00cc44;
        }

        .stError {
            background-color: #3a1a1a;
            border-left: 4px solid #ff4b4b;
        }

        .stWarning {
            background-color: #3a2a1a;
            border-left: 4px solid #ffd700;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize database tables
initialize_tables()

# Header
st.markdown("""
    <div class="main-header">
        <h1>📋 AI Requirement Tracker</h1>
        <p>Enterprise-grade requirements intake with AI-powered analysis | MongoDB + Neon Postgres</p>
    </div>
""", unsafe_allow_html=True)

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Submit Requirement",
    "📊 Requirements Tracker",
    "🔗 Traceability Matrix",
    "📈 Analytics"
])

with tab1:
    render_intake_form()

with tab2:
    render_tracker()

with tab3:
    render_traceability()

with tab4:
    render_analytics()