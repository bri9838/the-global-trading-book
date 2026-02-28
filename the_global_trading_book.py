import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- STEP 1: SMART IMPORT (Cloud vs Desktop) ---
# Ye block check karega ki MetaTrader5 install hai ya nahi
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- STEP 2: UI & BRANDING ---
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

# --- STEP 3: EXECUTION LOGIC ---
def place_tgtb_order(symbol, lot, side, order_type, price=None):
    if not MT5_AVAILABLE:
        st.error("❌ Direct Trading (MT5) sirf Windows Desktop par kaam karega.")
        return None
    
    if not mt5.initialize():
        st.error("❌ MT5 Terminal nahi mil raha. Ise open karein.")
        return None
        
    order_dict = {
        "Market": mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL,
        "Limit": mt5.ORDER_TYPE_BUY_LIMIT if side == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT,
        "Stop": mt5.ORDER_TYPE_BUY_STOP if side == "BUY" else mt5.ORDER_TYPE_SELL_STOP
    }
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        st.error(f"❌ Symbol {symbol} nahi mila.")
        return None
        
    p = price if order_type != "Market" else (tick.ask if side == "BUY" else tick.bid)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL if order_type == "Market" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol, "volume": lot, "type": order_dict[order_type], "price": p,
        "magic": 786, "comment": "TGTB Pro", "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC
    }
    return mt5.order_send(request)

# --- STEP 4: DATABASE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)

# --- STEP 5: MAIN APP ---
st.markdown("<h1>📔 THE GLOBAL TRADING BOOK</h1>", unsafe_allow_html=True)

# Sidebar Control
with st.sidebar:
    st.header("⚙️ Status")
    if MT5_AVAILABLE:
        st.success("Desktop Mode: MT5 Ready 🟢")
        if st.button("Connect MT5"):
            mt5.initialize()
    else:
        st.info("Cloud Mode: Journaling Active 📲")
    daily_limit = st.number_input("Daily Loss Limit ($)", value=500.0)

df = pd.read_csv(DATA_FILE)

# Tabs
tabs = st.tabs(["⚡ TRADE", "📈 STATS", "🧠 REVIEW", "🚨 EMERGENCY"])

with tabs[0]: # TRADE TAB
    col_chart, col_form = st.columns([2, 1])
    with col_chart:
        sym = st.text_input("Symbol", value="XAUUSD").upper()
        chart_html = f'<div style="height:450px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"symbol":"{sym}","interval":"15","theme":"dark","style":"1","container_id":"tv"}});</script></div>'
        components.html(chart_html, height=450)
    
    with col_form:
        st.subheader("New Entry")
        with st.form("trade_form", clear_on_submit=True):
            ot = st.selectbox("Order Type", ["Market", "Limit", "Stop"])
            sd = st.radio("Side", ["BUY", "SELL"], horizontal=True)
            lt = st.number_input("Lots", value=0.01, step=0.01)
            pr = st.number_input("Price", format="%.5f") if ot != "Market" else 0.0
            md = st.selectbox("Psychology", ["Disciplined", "FOMO", "Impulsive", "Revenge"])
            nt = st.text_input("Notes")
            
            if st.form_submit_button("PLACE & LOG"):
                exec_price = pr
                if MT5_AVAILABLE:
                    res = place_tgtb_order(sym, lt, sd, ot, pr)
                    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                        st.success("Trade Executed!")
                        exec_price = res.price
                
                # Log to CSV
                new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, sd, ot, exec_price, lt, 0, md, nt]
                pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.rerun()

with tabs[1]: # STATS TAB
    if not df.empty:
        st.metric("Total P&L", f"${df['PnL'].sum():,.2f}")
        st.line_chart(df['PnL'].cumsum())

with tabs[3]: # EMERGENCY TAB
    st.header("🛑 Kill Switch")
    if st.button("CLOSE ALL POSITIONS"):
        if MT5_AVAILABLE:
            st.warning("Closing all trades...")
        else:
            st.error("Desktop connectivity required for Kill Switch.")
