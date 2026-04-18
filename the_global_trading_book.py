import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    .stButton > button { border-radius: 5px; background-color: #12151c !important; color: #848e9c !important; border: 1px solid #2b2f3a !important; font-size: 12px; }
    .stButton > button:hover { border-color: #00ffca !important; color: #00ffca !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (FIXED & UPDATED) ---
DATA_FILE = "global_trading_book_data.csv"
# Naye columns ke sath file initialize karna
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Qty", "PnL", "Mood"]).to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# TypeError Fix: PnL ko hamesha number mein rakhna
if not df.empty:
    df['PnL'] = pd.to_numeric(df['PnL'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0)

# --- 3. NAVIGATION ---
nav = st.columns(4)
if nav[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav[1].button("🧠 AI COACH"): st.session_state.page = "ai"
if nav[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav[3].button("📅 CALENDAR"): st.session_state.page = "news"

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL PAGE ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # Chart Widget
    chart_html = f'''
        <div style="height:500px; border-radius:10px; overflow:hidden; border: 1px solid #1e222d;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "container_id": "tv_chart", "locale": "en"}});
            </script>
        </div>
    '''
    components.html(chart_html, height=510)

    st.markdown("### ⚡ Quick Execution")
    c1, c2, c3, c4 = st.columns(4)
    with c1: order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop Loss", "Take Profit"])
    with c2: qty = st.number_input("Qty", value=0.01, step=0.01)
    with c3: pnl_input = st.number_input("PnL ($)", value=0.0)
    with c4: mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge", "Impulsive"])
    
    btn_buy, btn_sell = st.columns(2)
    
    if btn_buy.button("🟢 BUY MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", order_type, qty, pnl_input, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.toast(f"Logged: {order_type} BUY")
        st.rerun()

    if btn_sell.button("🔴 SELL MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", order_type, qty, pnl_input, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.toast(f"Logged: {order_type} SELL")
        st.rerun()

# --- 5. AI COACH (Updated Analysis) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Trading Insights")
    if not df.empty:
        col_m1, col_m2 = st.columns(2)
        win_rate = (len(df[df['PnL'] > 0]) / len(df)) * 100
        col_m1.metric("Win Rate", f"{win_rate:.1f}%")
        col_m2.metric("Total PnL", f"${df['PnL'].sum():.2f}")
        
        st.subheader("📊 Performance by Order Type")
        type_analysis = df.groupby('Type')['PnL'].sum()
        st.bar_chart(type_analysis)
    else:
        st.info("Kam se kam 1 trade log karein AI analysis ke liye.")

# --- 6. REMAINING TABS ---
elif st.session_state.page == "news":
    st.header("📅 Economic Calendar")
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>{"colorTheme":"dark","width":"100%","height":"600"}</script>', height=620)

elif st.session_state.page == "rank":
    st.header("🏆 Top Assets")
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>{"colorTheme":"dark","exchange":"US","width":"100%","height":"600"}</script>', height=620)
