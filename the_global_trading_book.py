import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & UI ---
st.set_page_config(page_title="TGTB Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    .stApp { background-color: #000000; }
    header, footer { visibility: hidden; }
    
    /* Buttons ko TradingView jaisa premium banane ke liye */
    .stButton > button {
        border-radius: 6px;
        height: 3em;
        font-weight: bold;
        background-color: #1e222d !important;
        color: white !important;
        border: 1px solid #363c4e !important;
    }
    
    /* Buy/Sell colors */
    div[data-testid="column"]:nth-of-type(1) .stButton > button:hover { border: 1px solid #26a69a !important; }
    div[data-testid="column"]:nth-of-type(2) .stButton > button:hover { border: 1px solid #ef5350 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. TOP NAVIGATION (Hamesha dikhega) ---
# Yahan humne buttons ko upar rakha hai taaki reports tak turant pahunche
nav_col = st.columns(4)
if nav_col[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav_col[1].button("🧠 AI REPORT"): st.session_state.page = "ai"
if nav_col[2].button("🏆 RANKING"): st.session_state.page = "rank"
if nav_col[3].button("📝 JOURNAL"): st.session_state.page = "journal"

if 'page' not in st.session_state:
    st.session_state.page = "terminal"

# --- 4. PAGES LOGIC ---

if st.session_state.page == "terminal":
    # Symbol Bar
    t_col1, t_col2, t_col3 = st.columns([2, 1, 1])
    with t_col1:
        sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    with t_col2:
        st.success("LIVE")
    
    # Chart & Order Section
    col_chart, col_order = st.columns([3.5, 1.5])
    
    with col_chart:
        chart_html = f'''
            <div style="height:700px; width:100%; border: 1px solid #2d3439;">
                <div id="tv_chart" style="height:100%;"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "hide_side_toolbar": false, "allow_symbol_change": true}});
                </script>
            </div>
        '''
        components.html(chart_html, height=700)

    with col_order:
        st.subheader("Quick Log")
        lots = st.number_input("Lots", value=0.01, step=0.01)
        pnl_val = st.number_input("PnL ($)", value=0.0)
        mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])
        
        b_col, s_col = st.columns(2)
        if b_col.button("🟢 BUY"):
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", "Market", 0, lots, pnl_val, mood, ""]
            pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.toast("Saved!")
        if s_col.button("🔴 SELL"):
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", "Market", 0, lots, pnl_val, mood, ""]
            pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.toast("Saved!")

elif st.session_state.page == "ai":
    st.header("🧠 AI Trade Analysis")
    if not df.empty:
        st.bar_chart(df.groupby('Mood')['PnL'].sum())
        st.write("### AI Coach Advice")
        if df['PnL'].sum() < 0: st.error("Dhyan dein: Aapki strategy mein emotional trading zyada ho rahi hai.")
        else: st.success("Keep it up! Aapka discipline score badh raha hai.")
    else: st.info("No data.")

elif st.session_state.page == "rank":
    st.header("🏆 Symbol Ranking")
    if not df.empty:
        st.table(df.groupby('Symbol')['PnL'].sum().sort_values(ascending=False))

elif st.session_state.page == "journal":
    st.header("📝 Full History")
    st.dataframe(df, use_container_width=True)
