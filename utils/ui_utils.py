import streamlit as st

def apply_apple_style_ui():
    """
    Apply Apple-like styling to Streamlit application
    """
    st.markdown("""
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }
    .stApp {
        max-width: 99%;
        margin: 0 auto;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    .stSidebar {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)