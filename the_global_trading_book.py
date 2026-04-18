import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & NEON THEME ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    
    /* Navigation Neon Buttons */
    .stButton > button {
        border-radius: 5px;
        background-color: #12151c !important;
        color: #848e9c !important;
        border: 1px solid #2b2f3a !important;
        font-weight: bold;
    }
    .stButton > button:hover { border-color: #00ffca !important; color: #00ffca !important; }

    /* Custom Cards */
    .metric-card {
        background: #161a1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2b2f3a;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Qty", "PnL", "Mood"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. NAVIGATION ---
nav = st.columns(4)
if nav[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav[1].button("🧠 AI COACH"): st.session_state.page = "ai"
if nav[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav[3].button("📖 HISTORY"): st.session_state.page = "journal"

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (INDIAN MARKET FIX) ---
if st.session_state.page == "terminal":
    # Ticker Tape for Market Mood
    ticker_html = '<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{"symbols":[{"proName":"FOREXCOM:SPX500","title":"S&P 500"},{"proName":"NSE:NIFTY","title":"Nifty 50"},{"proName":"NSE:BANKNIFTY","title":"Bank Nifty"}],"colorTheme":"dark","isTransparent":true,"locale":"in"}</script>'
    components.html(ticker_html, height=50)

    sym = st.text_input("Symbol", value="NSE:NIFTY", label_visibility="collapsed").upper()
    
    # Advanced Widget for Indian Data
    chart_html = f'''
        <div style="height:500px; border-radius:10px; overflow:hidden;">
            <div id="tradingview_tgtb"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{
              "autosize": true,
              "symbol": "{sym}",
              "interval": "15",
              "timezone": "Asia/Kolkata",
              "theme": "dark",
              "style": "1",
              "locale": "in",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "withdateranges": true,
              "hide_side_toolbar": false,
              "allow_symbol_change": true,
              "container_id": "tradingview_tgtb"
            }});
            </script>
        </div>
    '''
    components.html(chart_html, height=510)

    # Quick Execution Panel
    st.markdown("### ⚡ Quick Log")
    c1, c2, c3 = st.columns(3)
    with c1: qty = st.number_input("Qty", value=1)
    with c2: pnl = st.number_input("PnL (₹)", value=0.0)
    with c3: mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])

    btn1, btn2 = st.columns(2)
    if btn1.button("🟢 BUY MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", qty, pnl, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Trade Logged!")
        st.rerun()
    if btn2.button("🔴 SELL MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", qty, pnl, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.error("Trade Logged!")
        st.rerun()

# --- 5. ASSETS (GAINER/LOSER LIST) ---
elif st.session_state.page == "rank":
    st.header("🏆 Indian Market Pulse")
    hotlist_html = '<div style="height:600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>{"colorTheme":"dark","exchange":"NSE","showChart":true,"locale":"in","width":"100%","height":"600","isTransparent":true}</script></div>'
    components.html(hotlist_html, height=620)

# --- 6. AI COACH (EQUITY CURVE) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Growth Analysis")
    if not df.empty:
        df['Cumulative PnL'] = df['PnL'].cumsum()
        st.subheader("📈 Your Equity Curve (₹)")
        st.line_chart(df['Cumulative PnL'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card"><h4>Total Profit</h4><h2>₹{df["PnL"].sum()}</h2></div>', unsafe_allow_html=True)
        with col2:
            win_rate = (len(df[df['PnL'] > 0]) / len(df)) * 100
            st.markdown(f'<div class="metric-card"><h4>Win Rate</h4><h2>{win_rate:.1f}%</h2></div>', unsafe_allow_html=True)
    else:
        st.info("Pahle trades log karein!")

# --- 7. HISTORY ---
elif st.session_state.page == "journal":
    st.header("📖 Trade History")
    st.dataframe(df.iloc[::-1], use_container_width=True)
