import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import time

# --- 1. UI CONFIG (LAYOUT LOCK) ---
# Is section mein humne height aur padding ko fix rakha hai jaisa Screenshot_20260427_110945_2.jpg mein tha
st.set_page_config(page_title="TGTB Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; } /* Mobile optimization lock */
    .stApp { background: radial-gradient(circle at top right, #1d0e3a, #06080a 70%); color: #e0e3eb; }
    
    /* CHART SIZE LOCK: Isse aapka chart chota nahi hoga */
    iframe { min-height: 650px !important; border: 1px solid #6a11cb; border-radius: 8px; }
    
    /* Nav Buttons Style */
    .stButton > button {
        background: #111418; color: white; border: 1px solid #2d3139; border-radius: 5px;
    }
    
    /* Progress Bar Style for AI Report (Screenshot 3/6) */
    .p-bar-bg { width: 100%; background: #2d3139; border-radius: 10px; margin-bottom: 10px; }
    .p-bar-fill { height: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if 'df' not in st.session_state:
    try: st.session_state.df = pd.read_csv(DATA_FILE)
    except: st.session_state.df = pd.DataFrame(columns=["Date", "Symbol", "Side", "Qty", "Entry", "PnL", "Status", "Discipline", "Risk"])

# --- 3. TOP NAVIGATION (Locked Style) ---
nav = st.columns(5)
pages = ["🌐 TERMINAL", "🧠 AI REPORT", "📊 ANALYTICS", "📖 JOURNAL", "🧪 BACKTEST"]
if 'page' not in st.session_state: st.session_state.page = "🌐 TERMINAL"

for i, p_name in enumerate(pages):
    if nav[i].button(p_name, use_container_width=True):
        st.session_state.page = p_name

# --- 4. TERMINAL PAGE (LAYOUT LOCKED) ---
if st.session_state.page == "🌐 TERMINAL":
    # Symbol Input & Chart size locked to previous version
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    chart_url = f"https://s.tradingview.com/widgetembed/?symbol={sym}&interval=1&theme=dark"
    st.components.v1.iframe(chart_url, height=650) # Strict Height Lock

    # Execution Section (Reference: Screenshot_20260427_110945_2.jpg)
    st.markdown("### ⚡ Execution")
    c1, c2, c3 = st.columns(3)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    qty = c2.number_input("Qty", value=0.01, step=0.01)
    entry = c3.number_input("Entry Price", value=0.0)

    if st.button("EXECUTE & OPEN", use_container_width=True):
        new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Symbol": sym, "Side": side, 
                   "Qty": qty, "Entry": entry, "PnL": 0, "Status": "OPEN", "Discipline": 80, "Risk": 70}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.df.to_csv(DATA_FILE, index=False)
        st.success("Trade Logged in Global Trading Book!")

# --- 5. AI REPORT (Reference: Screenshot_20260430_150044.jpg) ---
elif st.session_state.page == "🧠 AI REPORT":
    st.subheader("TradinJournal AI: Behavioral Analysis")
    # Score metrics simulation
    scores = {"Discipline": 21, "Risk Management": 11, "Consistency": 43, "Entry Quality": 67}
    
    for label, val in scores.items():
        st.write(f"{label}: {val}%")
        color = "#ff4b2b" if val < 30 else "#00ffca"
        st.markdown(f"""<div class="p-bar-bg"><div class="p-bar-fill" style="width: {val}%; background: {color};"></div></div>""", unsafe_allow_html=True)
    st.info("AI Tip: Stop-Loss discipline is low. Improve your Risk Management score.")

# --- 6. ANALYTICS & JOURNAL (Reference: Screenshot_20260430_145444.jpg) ---
elif st.session_state.page == "📊 ANALYTICS":
    st.subheader("Performance Analytics")
    if not st.session_state.df.empty:
        fig = px.bar(st.session_state.df, x="Date", y="PnL", color="PnL", title="PnL Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available to analyze.")

elif st.session_state.page == "📖 JOURNAL":
    st.subheader("Trade Journal")
    st.dataframe(st.session_state.df, use_container_width=True)
