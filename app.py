import streamlit as st
from database.postgres_client import initialize_tables
from components.intake_form import render_intake_form
from components.tracker import render_tracker
from components.traceability import render_traceability
from components.analytics import render_analytics

st.set_page_config(
    page_title="ReqAgent - AI Requirements Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, .stApp {
        background: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        color: #181818 !important;
    }

    #MainMenu, footer, header, .stDeployButton,
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

    .block-container {
        padding: 0 2.5rem 4rem !important;
        max-width: 1400px !important;
    }

    /* NAV */
    .sf-nav {
        background: #ffffff;
        border-bottom: 1px solid #e5e5e5;
        padding: 0 2.5rem;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0 -2.5rem 0;
    }
    .sf-nav-left { display: flex; align-items: center; gap: 10px; }
    .sf-nav-icon {
        width: 34px; height: 34px;
        background: #0176d3; border-radius: 8px;
        color: white; font-size: 0.75rem; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
    }
    .sf-nav-name { font-size: 1.05rem; font-weight: 700; color: #032d60; }
    .sf-nav-name span { color: #0176d3; }
    .sf-nav-tag {
        font-size: 0.7rem; color: #706e6b;
        background: #f3f2f2; padding: 2px 8px;
        border-radius: 4px; font-weight: 500;
    }
    .sf-nav-right { display: flex; gap: 0.5rem; }
    .sf-badge {
        display: inline-flex; align-items: center; gap: 5px;
        font-size: 0.72rem; color: #3e3e3c;
        background: #f3f2f2; border: 1px solid #e5e5e5;
        padding: 4px 10px; border-radius: 4px; font-weight: 500;
    }
    .sf-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .sf-dot-g { background: #2e844a; }
    .sf-dot-b { background: #0176d3; }
    .sf-dot-p { background: #9050e9; }

    /* HERO */
    .sf-hero {
        background: #f3f2f2;
        border-bottom: 1px solid #e5e5e5;
        padding: 3rem 2.5rem;
        margin: 0 -2.5rem 2rem;
    }
    .sf-eyebrow {
        font-size: 0.72rem; font-weight: 700;
        color: #0176d3; letter-spacing: 1.5px;
        text-transform: uppercase; margin-bottom: 0.75rem;
    }
    .sf-title {
        font-size: 2.1rem; font-weight: 700;
        color: #032d60; line-height: 1.2;
        letter-spacing: -0.8px; margin-bottom: 1rem; max-width: 560px;
    }
    .sf-title span { color: #0176d3; }
    .sf-desc {
        font-size: 0.95rem; color: #3e3e3c;
        line-height: 1.7; margin-bottom: 1.5rem; max-width: 560px;
    }
    .sf-checks { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.5rem; }
    .sf-check { display: flex; align-items: center; gap: 10px; font-size: 0.88rem; color: #3e3e3c; }
    .sf-check-icon {
        width: 20px; height: 20px;
        background: #eaf5fe; border: 1.5px solid #0176d3;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-size: 0.6rem;
        color: #0176d3; font-weight: 700; flex-shrink: 0;
    }
    .sf-stack { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .sf-pill {
        background: #ffffff; border: 1.5px solid #dddbda;
        color: #3e3e3c; font-size: 0.78rem; font-weight: 600;
        padding: 5px 12px; border-radius: 4px;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff !important;
        border-bottom: 2px solid #dddbda !important;
        border-radius: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        box-shadow: none !important;
        margin-bottom: 2rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff !important;
        color: #706e6b !important;
        border-radius: 0 !important;
        padding: 14px 28px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        margin-bottom: -2px !important;
        transition: all 0.15s !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0176d3 !important;
        border-bottom-color: #9fd6ff !important;
        background: #f8f9fb !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0176d3 !important;
        border-bottom: 3px solid #0176d3 !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* EXPANDER - Streamlit 1.58 */
    [data-testid="stExpander"] {
        border: 1px solid #dddbda !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        margin-bottom: 0.75rem !important;
        background: #ffffff !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] details {
        background: #ffffff !important;
    }
    [data-testid="stExpander"] details summary {
        background: #ffffff !important;
        padding: 1rem 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #032d60 !important;
        cursor: pointer !important;
    }
    [data-testid="stExpander"] details summary:hover {
        background: #eaf5fe !important;
        color: #0176d3 !important;
    }
    [data-testid="stExpander"] details[open] summary {
        border-bottom: 1px solid #dddbda !important;
        color: #0176d3 !important;
    }
    [data-testid="stExpanderDetails"] {
        background: #f8f9fb !important;
        padding: 1.2rem !important;
    }

    /* FORM */
    .stForm {
        background: #ffffff !important;
        border: 1px solid #dddbda !important;
        border-radius: 6px !important;
        padding: 2rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }

    /* INPUTS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 1px solid #dddbda !important;
        border-radius: 4px !important;
        color: #181818 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        transition: all 0.15s !important;
        padding: 0.55rem 0.85rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0176d3 !important;
        box-shadow: 0 0 0 3px rgba(1,118,211,0.12) !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder { color: #c9c7c5 !important; }
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #dddbda !important;
        border-radius: 4px !important;
        color: #181818 !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #3e3e3c !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    /* SUBMIT */
    .stFormSubmitButton > button {
        background: #0176d3 !important;
        color: #ffffff !important;
        border: 1px solid #0176d3 !important;
        border-radius: 4px !important;
        padding: 0.65rem 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.15s !important;
    }
    .stFormSubmitButton > button:hover {
        background: #014486 !important;
        border-color: #014486 !important;
    }

    /* BUTTONS */
    .stButton > button {
        background: #ffffff !important;
        color: #0176d3 !important;
        border: 1px solid #0176d3 !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: #eaf5fe !important;
        border-color: #014486 !important;
        color: #014486 !important;
    }
    .stDownloadButton > button {
        background: #ffffff !important;
        color: #0176d3 !important;
        border: 1px solid #0176d3 !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    /* METRICS */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border: 1px solid #dddbda !important;
        border-top: 3px solid #0176d3 !important;
        border-radius: 6px !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.15s !important;
    }
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 12px rgba(1,118,211,0.1) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="metric-container"] label {
        color: #706e6b !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #0176d3 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ALERTS */
    .stSuccess > div {
        background: #eef7ee !important;
        border: 1px solid #a8d5a2 !important;
        border-left: 4px solid #2e844a !important;
        border-radius: 4px !important;
        color: #1a4731 !important;
    }
    .stError > div {
        background: #fef1ee !important;
        border: 1px solid #f5a28a !important;
        border-left: 4px solid #ba0517 !important;
        border-radius: 4px !important;
        color: #640019 !important;
    }
    .stWarning > div {
        background: #fef5e5 !important;
        border: 1px solid #f5c07a !important;
        border-left: 4px solid #dd7a01 !important;
        border-radius: 4px !important;
        color: #5d3e00 !important;
    }
    .stInfo > div {
        background: #eaf5fe !important;
        border: 1px solid #9fd6ff !important;
        border-left: 4px solid #0176d3 !important;
        border-radius: 4px !important;
        color: #032d60 !important;
    }

    /* TYPOGRAPHY */
    h2 { color: #032d60 !important; font-size: 1.1rem !important; font-weight: 700 !important; }
    h3 { color: #0176d3 !important; font-size: 0.72rem !important; font-weight: 700 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
    p { color: #3e3e3c !important; font-size: 0.9rem !important; line-height: 1.6 !important; }
    hr { border-color: #e5e5e5 !important; margin: 1.2rem 0 !important; }
    .stDataFrame { border: 1px solid #dddbda !important; border-radius: 6px !important; overflow: hidden !important; }
    .stSpinner > div { border-top-color: #0176d3 !important; }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #f3f2f2; }
    ::-webkit-scrollbar-thumb { background: #c9c7c5; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #0176d3; }
</style>
""", unsafe_allow_html=True)

initialize_tables()

st.markdown("""
<div class="sf-nav">
    <div class="sf-nav-left">
        <div class="sf-nav-icon">RA</div>
        <div class="sf-nav-name">Req<span>Agent</span></div>
        <div class="sf-nav-tag">AI Platform</div>
    </div>
    <div class="sf-nav-right">
        <div class="sf-badge"><span class="sf-dot sf-dot-g"></span>LLaMA 3.3 70B · Active</div>
        <div class="sf-badge"><span class="sf-dot sf-dot-b"></span>MongoDB · Connected</div>
        <div class="sf-badge"><span class="sf-dot sf-dot-p"></span>Postgres · Connected</div>
    </div>
</div>
<div class="sf-hero">
    <div class="sf-eyebrow">AI Requirements Intelligence</div>
    <div class="sf-title">Ready to automate your<br><span>requirements intake?</span></div>
    <div class="sf-desc">ReqAgent autonomously processes stakeholder input, generates user stories, detects conflicts, and tracks lifecycle — so your team can focus on building.</div>
    <div class="sf-checks">
        <div class="sf-check"><div class="sf-check-icon">✓</div>AI-generated user stories with acceptance criteria</div>
        <div class="sf-check"><div class="sf-check-icon">✓</div>MoSCoW classification and role-weighted priority scoring</div>
        <div class="sf-check"><div class="sf-check-icon">✓</div>Conflict detection against all existing requirements</div>
        <div class="sf-check"><div class="sf-check-icon">✓</div>Full lifecycle tracking with audit trail</div>
    </div>
    <div class="sf-stack">
        <div class="sf-pill">🤖 LLaMA 3.3 70B</div>
        <div class="sf-pill">🍃 MongoDB Atlas</div>
        <div class="sf-pill">🐘 Neon Postgres</div>
        <div class="sf-pill">📊 Plotly</div>
        <div class="sf-pill">🐍 Python 3.12</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "  Submit Requirement",
    "  Requirements Tracker",
    "  Traceability Matrix",
    "  Analytics"
])

with tab1:
    render_intake_form()
with tab2:
    render_tracker()
with tab3:
    render_traceability()
with tab4:
    render_analytics()