import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & UI FIX ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Pura screen space use karne ke liye */
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    
    /* Buttons aur spacing choti karne ke liye taaki chart ko jagah mile */
    .stButton > button { height: 32px; font-size: 10px; border-radius: 4px; }
    .stNumberInput, .stSelectbox { margin-top: -15px; }
    
    /* Chart container height fix */
    iframe { min-height: 650px !important; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
COLS_REAL = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS_REAL).to_csv(DATA_FILE, index=False)

# --- 3. NAVIGATION ---
nav = st.columns(6)
tabs = ["🌐 TERMINAL", "🧠 COACH", "🏆 ASSETS", "📖 HISTORY", "📊 STATS", "🧪 BACKTEST"]
pages = ["terminal", "ai", "rank", "history", "stats", "backtest"]

for i, tab in enumerate(tabs):
    if nav[i].button(tab): st.session_state.page = pages[i]

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (MAX CHART SIZE) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # Chart height 650px fix
    chart_html = f'''
        <div style="height:650px; width:100%; border-radius:8px; overflow:hidden; border: 1px solid #1e222d;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "locale": "en", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true}});
            </script>
        </div>
    '''
    components.html(chart_html, height=660)

    st.markdown("### ⚡ Execution")
    
    # Layout ko 2 rows mein kiya taaki chart compress na ho
    c1, c2, c3, c4 = st.columns(4)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    o_type = c2.selectbox("Type", ["Market", "Limit", "SL"])
    qty = c3.number_input("Qty", value=0.01, step=0.01)
    mood = c4.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    ent = r2c1.number_input("Entry", value=0.0)
    sl = r2c2.number_input("SL", value=0.0)
    tp = r2c3.number_input("TP", value=0.0)
    pnl = r2c4.number_input("PnL", value=0.0)
    
    risk = abs(ent - sl)
    reward = abs(tp - ent)
    rr = round(reward/risk, 2) if risk != 0 else 0
    st.markdown(f"<p style='color:#00ffca; font-size:12px;'>Planned RR: 1:{rr}</p>", unsafe_allow_html=True)

    if st.button("LOG TRADE", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, pnl, rr, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Order Placed!")
        st.rerun()

# (Baaki pages: AI Coach, History etc. ka logic same rahega)
