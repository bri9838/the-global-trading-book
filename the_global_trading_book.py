import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- STEP 1: SMART IMPORT ---
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- STEP 2: UI & BRANDING ---
st.set_page_config(page_title="The Global Trading Book", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00ffd0 !important; font-weight: 800; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #4facfe, #00f2fe) !important; color: black !important; font-weight: bold; border-radius: 10px; }
    .stButton > button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; background: linear-gradient(45deg, #00dbde, #fc00ff) !important; color: white !important; border: none; }
    h1 { text-align: center; color: white; text-shadow: 0 0 20px rgba(79, 172, 254, 0.6); }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 3: DATABASE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# --- STEP 4: MAIN APP ---
st.markdown("<h1>📔 THE GLOBAL TRADING BOOK</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Risk Status")
    if not df.empty:
        pnl_sum = df['PnL'].sum()
        st.metric("Total P&L", f"${pnl_sum:,.2f}")
    if MT5_AVAILABLE:
        st.success("MT5 Ready 🟢")

tabs = st.tabs(["⚡ TRADE", "📈 STATS", "🧠 AI REVIEW", "🚨 EMERGENCY"])

with tabs[0]: # TRADE TAB
    col_chart, col_form = st.columns([3, 1])
    with col_chart:
        sym = st.text_input("Symbol", value="XAUUSD").upper()
        # FORCE FULL HEIGHT CHART
        chart_html = f'<div style="height:700px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"symbol":"{sym}","interval":"15","theme":"dark","style":"1","container_id":"tv","hide_side_toolbar":false,"allow_symbol_change":true}});</script></div>'
        components.html(chart_html, height=720) # Height increased here
    
    with col_form:
        st.subheader("Quick Entry")
        if 't_lots' not in st.session_state: st.session_state['t_lots'] = 0.01
        
        qc = st.columns(3)
        if qc[0].button("0.01"): st.session_state['t_lots'] = 0.01
        if qc[1].button("0.10"): st.session_state['t_lots'] = 0.10
        if qc[2].button("1.00"): st.session_state['t_lots'] = 1.00

        with st.form("trade_form", clear_on_submit=True):
            sd = st.radio("Side", ["BUY", "SELL"], horizontal=True)
            lt = st.number_input("Lots", value=st.session_state['t_lots'], step=0.01)
            md = st.selectbox("Psychology", ["Disciplined", "FOMO", "Impulsive", "Revenge"])
            pnl_val = st.number_input("PnL (if closing)", value=0.0)
            
            if st.form_submit_button("LOG TRADE"):
                new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, sd, "Market", 0.0, lt, pnl_val, md, ""]
                pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.rerun()

with tabs[2]: # AI REVIEW
    st.header("🧠 AI Insights")
    if not df.empty:
        # FIXED: map() for numeric PnL color coding
        st.dataframe(df.style.map(lambda x: 'background-color: #1b4d3e' if isinstance(x, (int, float)) and x > 0 else ('background-color: #4d1b1b' if isinstance(x, (int, float)) and x < 0 else ''), subset=['PnL']), use_container_width=True)
    else:
        st.info("No trades to analyze yet.")
