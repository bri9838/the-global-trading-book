import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PRO CONFIG & MOBILE OPTIMIZATION ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    .stApp { background-color: #06080a; }
    header, footer { visibility: hidden; }
    
    /* Navigation Buttons Styling */
    .stButton > button {
        border-radius: 8px;
        height: 2.8em;
        font-size: 12px !important;
        background-color: #12151c !important;
        color: #848e9c !important;
        border: 1px solid #2b2f3a !important;
        transition: 0.3s;
    }
    .stButton > button:hover { color: #f0b90b !important; border-color: #f0b90b !important; }

    /* Custom Card for Journal */
    .trade-card {
        background-color: #161a1e;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #26a69a;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. TOP SMART NAVIGATION ---
nav_col = st.columns(4)
if nav_col[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav_col[1].button("🧠 AI COACH"): st.session_state.page = "ai"
if nav_col[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav_col[3].button("📖 HISTORY"): st.session_state.page = "journal"

if 'page' not in st.session_state:
    st.session_state.page = "terminal"

# --- 4. LOGIC ENGINE ---

if st.session_state.page == "terminal":
    # Layout: Chart (Top) | Controls (Bottom for Mobile)
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # 80vh Chart for full mobile height
    chart_html = f'''
        <div style="height:550px; width:100%; border-radius: 8px; overflow: hidden; border: 1px solid #1e222d;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "hide_side_toolbar": false}});
            </script>
        </div>
    '''
    components.html(chart_html, height=560)

    # Order Panel - Horizontal on Desktop, Vertical on Mobile
    st.markdown("### ⚡ Quick Execution")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: lots = st.number_input("Lots", value=0.01, step=0.01)
    with c2: pnl_val = st.number_input("PnL ($)", value=0.0)
    with c3: mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])
    
    b_col, s_col = st.columns(2)
    if b_col.button("🟢 BUY MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%d %b, %H:%M"), sym, "BUY", "Market", 0, lots, pnl_val, mood, ""]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.balloons()
        st.success("Trade Secured!")
    if s_col.button("🔴 SELL MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%d %b, %H:%M"), sym, "SELL", "Market", 0, lots, pnl_val, mood, ""]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.snow()
        st.error("Trade Logged!")

elif st.session_state.page == "ai":
    st.header("🧠 AI Trading Coach")
    if not df.empty:
        total_pnl = df['PnL'].sum()
        fomo_count = len(df[df['Mood'] == 'FOMO'])
        
        # AI Logic
        st.subheader("Today's Insight")
        if fomo_count > 2:
            st.warning(f"AI Alert: Aapne {fomo_count} trades FOMO mein liye hain. Overtrading se bachein!")
        if total_pnl > 0:
            st.success(f"Discipline Payoff: Aapka total profit ${total_pnl:.2f} hai. Good job!")
        
        st.subheader("Psychology Breakdown")
        st.bar_chart(df.groupby('Mood')['PnL'].sum())
    else: st.info("Kam se kam 1 trade log karein AI analysis ke liye.")

elif st.session_state.page == "rank":
    st.header("🏆 Top Performing Symbols")
    if not df.empty:
        rank_df = df.groupby('Symbol')['PnL'].sum().sort_values(ascending=False)
        st.dataframe(rank_df, use_container_width=True)

elif st.session_state.page == "journal":
    st.header("📖 Trade History")
    if not df.empty:
        for i, row in df.iloc[::-1].iterrows(): # Latest first
            color = "#26a69a" if row['PnL'] >= 0 else "#ef5350"
            st.markdown(f"""
                <div class="trade-card" style="border-left-color: {color}">
                    <b>{row['Date']}</b> | {row['Symbol']} - {row['Side']}<br>
                    <span style="color:{color}">PnL: ${row['PnL']}</span> | Mood: {row['Mood']}
                </div>
            """, unsafe_allow_html=True)
