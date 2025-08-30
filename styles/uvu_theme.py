"""
UVU Color Palette and Theme for CS AI Grader
"""

import streamlit as st

# UVU Official Colors
UVU_DARK_GREEN = "#275D38"  # PANTONE 7483
UVU_BLACK = "#231F20"       # PANTONE Black C (RGB 35/31/32)
UVU_WHITE = "#FFFFFF"
UVU_LIGHT_GREEN = "#4A8B3B"  # Lighter shade for accents

def apply_uvu_theme():
    """Apply UVU color palette and styling to the app"""
    
    st.markdown("""
    <style>
    /* Import UVU fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
    
    /* Root variables for UVU colors */
    :root {
        --uvu-dark-green: #275D38;
        --uvu-black: #231F20;
        --uvu-white: #FFFFFF;
        --uvu-light-green: #4A8B3B;
        --uvu-accent: #E8F5E8;
    }
    
    /* Main app background */
    .stApp {
        background-color: var(--uvu-white);
        color: var(--uvu-black);
        font-family: 'Open Sans', sans-serif;
    }
    
    /* Header styling */
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1 {
        color: var(--uvu-dark-green) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--uvu-dark-green);
        padding-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: var(--uvu-dark-green) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--uvu-dark-green) !important;
    }
    
    .sidebar .sidebar-content {
        background-color: var(--uvu-dark-green) !important;
        color: var(--uvu-white) !important;
    }
    
    /* Sidebar text */
    .css-1d391kg .css-10trblm {
        color: var(--uvu-white) !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: var(--uvu-white) !important;
    }
    
    .css-1d391kg .css-1cpxqw2 {
        color: var(--uvu-white) !important;
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: var(--uvu-dark-green) !important;
        border: 2px solid var(--uvu-dark-green) !important;
        color: var(--uvu-white) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: var(--uvu-light-green) !important;
        border-color: var(--uvu-light-green) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(39, 93, 56, 0.3) !important;
    }
    
    /* Secondary buttons */
    .stButton > button {
        border: 2px solid var(--uvu-dark-green) !important;
        color: var(--uvu-dark-green) !important;
        background-color: var(--uvu-white) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--uvu-accent) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: var(--uvu-accent) !important;
        border-left: 4px solid var(--uvu-dark-green) !important;
        color: var(--uvu-black) !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #F0F8F0 !important;
        border-left: 4px solid var(--uvu-light-green) !important;
        color: var(--uvu-black) !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #FFF8E1 !important;
        border-left: 4px solid #FF8F00 !important;
    }
    
    /* Error messages */
    .stError {
        background-color: #FFEBEE !important;
        border-left: 4px solid #D32F2F !important;
    }
    
    /* Metrics */
    .css-1r6slb0 {
        background-color: var(--uvu-accent) !important;
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .css-1r6slb0 .css-1wivap2 {
        color: var(--uvu-dark-green) !important;
        font-weight: 700 !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
        color: var(--uvu-black) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--uvu-light-green) !important;
        box-shadow: 0 0 0 2px rgba(39, 93, 56, 0.2) !important;
    }
    
    /* Text areas */
    .stTextArea > div > div > textarea {
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
        color: var(--uvu-black) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--uvu-light-green) !important;
        box-shadow: 0 0 0 2px rgba(39, 93, 56, 0.2) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div > div {
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--uvu-accent) !important;
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
        color: var(--uvu-dark-green) !important;
        font-weight: 600 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--uvu-white) !important;
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 8px !important;
        color: var(--uvu-dark-green) !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--uvu-dark-green) !important;
        color: var(--uvu-white) !important;
    }
    
    /* Forms */
    .stForm {
        border: 2px solid var(--uvu-dark-green) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        background-color: var(--uvu-accent) !important;
    }
    
    /* Dividers */
    .stDivider > div {
        background-color: var(--uvu-dark-green) !important;
        height: 2px !important;
    }
    
    /* Custom UVU header */
    .uvu-header {
        background: linear-gradient(135deg, var(--uvu-dark-green) 0%, var(--uvu-light-green) 100%);
        color: var(--uvu-white);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(39, 93, 56, 0.3);
    }
    
    .uvu-header h1 {
        color: var(--uvu-white) !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .uvu-header .caption {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Chat styling */
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--uvu-dark-green);
    }
    
    .chat-user {
        background-color: var(--uvu-accent);
        border-left-color: var(--uvu-dark-green);
    }
    
    .chat-assistant {
        background-color: #F5F5F5;
        border-left-color: var(--uvu-light-green);
    }
    
    /* Footer */
    .uvu-footer {
        background-color: var(--uvu-dark-green);
        color: var(--uvu-white);
        padding: 1rem;
        text-align: center;
        border-radius: 8px;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def create_uvu_header(title: str, subtitle: str = ""):
    """Create UVU-branded header"""
    
    header_html = f"""
    <div class="uvu-header">
        <h1>🎓 {title}</h1>
        {f'<div class="caption">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)


def create_uvu_footer():
    """Create UVU-branded footer"""
    
    footer_html = """
    <div class="uvu-footer">
        <strong>Utah Valley University - Computer Science Department</strong><br>
        AI-Assisted Grading Platform | Powered by GPT-5-mini
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)
