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
    
    /* Navigation Neon Buttons */
    .stButton > button {
        border-radius: 5px;
        background-color: #12151c !important;
        color: #848e9c !important;
        border: 1px solid #2b2f3a !important;
        font-size: 11px;
        height: 35px;
    }
    .stButton > button:hover { border-color: #00ffca !important; color: #00ffca !important; }
    
    /* Input Compactness */
    .stNumberInput, .stSelectbox { margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
BT_FILE = "backtest_data.csv"
COLS_REAL = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood"]
COLS_BT = ["Strategy", "Result", "PnL", "RR", "Notes"]

if not os.path.exists(DATA_FILE): pd.DataFrame(columns=COLS_REAL).to_csv(DATA_FILE, index=False)
if not os.path.exists(BT_FILE): pd.DataFrame(columns=COLS_BT).to_csv(BT_FILE, index=False)

df = pd.read_csv(DATA_FILE)
bt_df = pd.read_csv(BT_FILE)

# --- HELPER: RR CALCULATOR ---
def calculate_rr(entry, sl, tp):
    try:
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        return round(reward / risk, 2) if risk != 0 else 0
    except: return 0

# --- 3. NAVIGATION (6 TABS) ---
nav = st.columns(6)
if nav[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav[1].button("🧠 COACH"): st.session_state.page = "ai"
if nav[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav[3].button("📖 HISTORY"): st.session_state.page = "history"
if nav[4].button("📊 STATS"): st.session_state.page = "stats"
if nav[5].button("🧪 BACKTEST"): st.session_state.page = "backtest"

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL PAGE ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # BIG CHART FIX: Height set to 600
    chart_html = f'''
        <div style="height:600px; border-radius:10px; overflow:hidden; border: 1px solid #1e222d;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "container_id": "tv_chart", "locale": "en"}});
            </script>
        </div>
    '''
    components.html(chart_html, height=610)

    st.markdown("### ⚡ Execution & RR")
    
    # Compact Grid for Mobile
    c1, c2, c3, c4 = st.columns(4)
    with c1: side = st.selectbox("Side", ["BUY", "SELL"])
    with c2: o_type = st.selectbox("Type", ["Market", "Limit", "SL"])
    with c3: qty = st.number_input("Qty", value=0.01)
    with c4: mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1: ent = st.number_input("Entry", value=0.0)
    with r2c2: sl = st.number_input("SL", value=0.0)
    with r2c3: tp = st.number_input("TP", value=0.0)
    with r2c4: pnl = st.number_input("PnL", value=0.0)
    
    current_rr = calculate_rr(ent, sl, tp)
    st.info(f"Planned Risk:Reward = 1 : {current_rr}")

    if st.button("LOG TRADE", use_container_width=True):
        new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, pnl, current_rr, mood]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success(f"Trade Logged! RR 1:{current_rr}")
        st.rerun()

# --- 5. HISTORY TAB ---
elif st.session_state.page == "history":
    st.header("📖 Trade History")
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="history.csv", mime="text/csv")
    else: st.info("No trades found.")

# --- 6. BACKTEST TAB ---
elif st.session_state.page == "backtest":
    st.header("🧪 Backtester")
    col1, col2 = st.columns([1, 2])
    with col1:
        st_name = st.text_input("Strategy")
        b_ent = st.number_input("Entry Price", value=0.0)
        b_sl = st.number_input("SL Price", value=0.0)
        b_tp = st.number_input("TP Price", value=0.0)
        b_rr = calculate_rr(b_ent, b_sl, b_tp)
        st.write(f"Test RR: 1:{b_rr}")
        b_pnl = st.number_input("Test PnL", value=0.0)
        if st.button("Save Backtest"):
            pd.DataFrame([[st_name, "Done", b_pnl, b_rr, "Note"]]).to_csv(BT_FILE, mode='a', header=False, index=False)
            st.rerun()
    with col2:
        st.dataframe(bt_df.iloc[::-1], use_container_width=True)

# --- 7. STATS & COACH ---
elif st.session_state.page == "stats":
    st.header("📊 Stats")
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        st.line_chart(df.set_index('Date')['PnL'].cumsum())
    else: st.info("No data.")

elif st.session_state.page == "ai":
    st.header("🧠 Coach")
    if not df.empty:
        st.metric("Total Profit", f"${df['PnL'].sum():.2f}")
        st.write(f"Win Rate: {(len(df[df['PnL']>0])/len(df)*100):.1f}%")

elif st.session_state.page == "rank":
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>{"colorTheme":"dark","exchange":"US","width":"100%","height":"600"}</script>', height=620)
