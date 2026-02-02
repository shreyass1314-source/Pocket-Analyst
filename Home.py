import streamlit as st

st.set_page_config(
    page_title="Pocket Analyst Pro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("⚡ Pocket Analyst Pro")

st.markdown("""
### Welcome, Client.
This is your institutional-grade command center. Select a module from the sidebar to begin.

#### 🚀 Modules
* **🎯 Sniper Tool:** Deep analysis of a single stock with Risk Management.
* **📡 Market Scanner:** Find momentum opportunities across sectors.
* **💼 Watchlist:** Track your shortlisted candidates.

---
*v7.0 | Institutional Build | Powered by Python*
""")

# Initialize Session State for Watchlist if not exists
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
