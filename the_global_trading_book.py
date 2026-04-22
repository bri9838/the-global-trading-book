import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & UI ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    .stButton > button { border-radius: 5px; background-color: #12151c !important; color: #848e9c !important; border: 1px solid #2b2f3a !important; font-size: 11px; }
    .stButton > button:hover { border-color: #00ffca !important; color: #00ffca !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
BT_FILE = "backtest_data.csv"

# Columns sync with RR
COLS_REAL = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood"]
COLS_BT = ["Strategy", "Result", "PnL", "RR", "Notes"]

if not os.path.exists(DATA_FILE): pd.DataFrame(columns=COLS_REAL).to_csv(DATA_FILE, index=False)
if not os.path.exists(BT_FILE): pd.DataFrame(columns=COLS_BT).to_csv(BT_FILE, index=False)

df = pd.read_csv(DATA_FILE)
bt_df = pd.read_csv(BT_FILE)

# --- 3. NAVIGATION (6 TABS) ---
nav = st.columns(6)
if nav[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav[1].button("🧠 COACH"): st.session_state.page = "ai"
if nav[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav[3].button("📖 HISTORY"): st.session_state.page = "history"
if nav[4].button("📊 STATS"): st.session_state.page = "stats"
if nav[5].button("🧪 BACKTEST"): st.session_state.page = "backtest"

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- HELPER: RR CALCULATOR ---
def calculate_rr(entry, sl, tp):
    try:
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        return round(reward / risk, 2) if risk != 0 else 0
    except: return 0

# --- 4. TERMINAL TAB ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    components.html(f'<div style="height:400px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "container_id": "tv"}});</script></div>', height=410)

    st.markdown("### ⚡ Execution & RR")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    o_type = r1c1.selectbox("Type", ["Market", "Limit", "SL"])
    qty = r1c2.number_input("Qty", value=0.01)
    mood = r1c3.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])
    side = r1c4.selectbox("Side", ["BUY", "SELL"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    ent = r2c1.number_input("Entry", value=0.0)
    sl = r2c2.number_input("SL", value=0.0)
    tp = r2c3.number_input("TP", value=0.0)
    pnl = r2c4.number_input("PnL", value=0.0)
    
    current_rr = calculate_rr(ent, sl, tp)
    st.info(f"Planned RR: 1 : {current_rr}")

    if st.button("LOG TRADE", use_container_width=True):
        new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, pnl, current_rr, mood]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Trade Logged Successfully!")
        st.rerun()

# --- 5. HISTORY TAB (With Download) ---
elif st.session_state.page == "history":
    st.header("📖 Trade Journal")
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True)
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download History CSV", data=csv, file_name="trading_history.csv", mime="text/csv")
    else: st.info("No trades found.")

# --- 6. BACKTEST TAB (With Download) ---
elif st.session_state.page == "backtest":
    st.header("🧪 Strategy Backtester")
    col1, col2 = st.columns([1, 2])
    with col1:
        st_name = st.text_input("Strategy")
        b_ent = st.number_input("B-Entry", value=0.0)
        b_sl = st.number_input("B-SL", value=0.0)
        b_tp = st.number_input("B-TP", value=0.0)
        b_rr = calculate_rr(b_ent, b_sl, b_tp)
        b_pnl = st.number_input("B-PnL", value=0.0)
        if st.button("Save Test"):
            pd.DataFrame([[st_name, "Done", b_pnl, b_rr, "N/A"]]).to_csv(BT_FILE, mode='a', header=False, index=False)
            st.rerun()
    with col2:
        st.dataframe(bt_df.iloc[::-1], use_container_width=True)
        # Download Button
        csv_bt = bt_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Backtest CSV", data=csv_bt, file_name="backtest_report.csv", mime="text/csv")

# --- 7. AI COACH, STATS, ASSETS (Remaining Logic) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Analysis")
    if not df.empty:
        st.metric("Total Equity PnL", f"${df['PnL'].sum():.2f}")
        st.line_chart(df['PnL'].cumsum())
