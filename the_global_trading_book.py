import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components
import yfinance as yf

# --- ERROR FIX: MT5 Cloud Compatibility Check ---
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- 1. BRANDING & MOBILE-READY UI ---
st.set_page_config(page_title="The Global Trading Book", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #050505, #000000); color: white; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #00ffcc !important; text-shadow: 0 0 10px #00ffcc; }
    .stTabs [aria-selected="true"] { background-color: #4facfe !important; box-shadow: 0 0 10px #4facfe; border-radius: 5px; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background: linear-gradient(45deg, #4facfe, #00f2fe); color: black; }
    h1 { text-align: center; letter-spacing: 2px; text-shadow: 2px 2px 8px #4facfe; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXECUTION ENGINE (With Safety Check) ---
def place_tgtb_order(symbol, lot, side, order_type, price=None):
    if not MT5_AVAILABLE:
        st.error("❌ Direct Trading feature is only available on Windows Desktop with MT5 installed.")
        return None
    
    if not mt5.initialize(): 
        st.error("❌ MT5 Initialization Failed. Please open your MT5 Terminal.")
        return None
        
    order_dict = {
        "Market": mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL,
        "Limit": mt5.ORDER_TYPE_BUY_LIMIT if side == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT,
        "Stop": mt5.ORDER_TYPE_BUY_STOP if side == "BUY" else mt5.ORDER_TYPE_SELL_STOP
    }
    
    # Get Price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        st.error(f"❌ Symbol {symbol} not found in MT5.")
        return None
        
    p = price if order_type != "Market" else (tick.ask if side == "BUY" else tick.bid)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL if order_type == "Market" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol, "volume": lot, "type": order_dict[order_type], "price": p,
        "magic": 786, "comment": "TGTB Pro", "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC
    }
    return mt5.order_send(request)

# --- 3. DATABASE SETUP ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)

# --- 4. MAIN TERMINAL ---
st.markdown("<h1>📔 THE GLOBAL TRADING BOOK</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Station Control")
    if MT5_AVAILABLE:
        if st.button("🔗 Connect Broker (MT5)"):
            if mt5.initialize(): st.success("Broker Connected! 🟢")
            else: st.error("MT5 Terminal not running.")
    else:
        st.info("ℹ️ Running in Cloud Mode (Journaling Only)")
    daily_limit = st.number_input("Daily Loss Limit ($)", value=500.0)

df = pd.read_csv(DATA_FILE)

# --- 5. TABS ---
tabs = st.tabs(["⚡ TRADE", "📈 STATS", "🧠 REVIEW", "🚨 EMERGENCY"])

with tabs[0]: # TRADE & CHART
    col_chart, col_form = st.columns([2, 1])
    with col_chart:
        sym = st.text_input("Symbol (e.g., XAUUSD)", value="XAUUSD").upper()
        chart_html = f'<div style="height:450px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"symbol":"{sym}","interval":"15","theme":"dark","style":"1","container_id":"tv"}});</script></div>'
        components.html(chart_html, height=450)
    
    with col_form:
        st.subheader("Order Entry")
        with st.form("trade_form", clear_on_submit=True):
            ot = st.selectbox("Order Type", ["Market", "Limit", "Stop"])
            sd = st.radio("Side", ["BUY", "SELL"], horizontal=True)
            lt = st.number_input("Lots", value=0.01, step=0.01, format="%.2f")
            pr = st.number_input("Price (Limit/Stop)", format="%.5f") if ot != "Market" else 0.0
            md = st.selectbox("Psychology", ["Disciplined", "FOMO", "Impulsive", "Revenge"])
            nt = st.text_input("Notes")
            
            if st.form_submit_button("PLACE & LOG TRADE"):
                # If MT5 is available, try direct trade
                if MT5_AVAILABLE:
                    res = place_tgtb_order(sym, lt, sd, ot, pr)
                    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                        st.success("Trade Executed & Logged!")
                        exec_price = res.price
                    else:
                        st.warning("Execution Failed, Logging manually...")
                        exec_price = pr
                else:
                    st.info("Cloud Mode: Trade Logged Locally.")
                    exec_price = pr
                
                # Always log to CSV
                new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, sd, ot, exec_price, lt, 0, md, nt]
                pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)

with tabs[1]: # STATS
    if not df.empty:
        st.metric("Total P&L", f"${df['PnL'].sum():,.2f}")
        st.line_chart(df['PnL'].cumsum())
        

with tabs[2]: # REVIEW
    st.subheader("🧠 Weekly Psychology Audit")
    if not df.empty:
        mood_data = df.groupby('Mood')['PnL'].sum()
        st.bar_chart(mood_data)
