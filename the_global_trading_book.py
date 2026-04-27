import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components
import base64
import time
import requests # Live price ke liye zaruri hai

# --- 1. FIXED UI CONFIG (THEME & CHART LOCKED) ---
st.set_page_config(page_title="TGTB AI Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background: radial-gradient(circle at top right, #1d0e3a, #06080a 70%); color: #e0e3eb; }
    header, footer { visibility: hidden; }
    
    /* Neon Purple Buttons Lock */
    .stButton > button {
        border-radius: 8px;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.4);
        font-weight: bold;
    }
    
    /* Chart Height Lock */
    iframe { min-height: 650px !important; border: 2px solid #6a11cb; border-radius: 12px; }
    
    .pnl-box {
        background: rgba(22, 26, 30, 0.8);
        border-left: 5px solid #00ffca;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIVE PRICE ENGINE (NEW) ---
def get_live_price(symbol):
    try:
        # Binance API se live price uthane ke liye
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        data = requests.get(url).json()
        return float(data['price'])
    except:
        return None

# --- 3. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
COLS = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood", "Screenshot", "Status"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS).to_csv(DATA_FILE, index=False)

def load_data():
    try:
        temp_df = pd.read_csv(DATA_FILE)
        temp_df['PnL'] = pd.to_numeric(temp_df['PnL'], errors='coerce').fillna(0.0)
        temp_df['Entry'] = pd.to_numeric(temp_df['Entry'], errors='coerce').fillna(0.0)
        temp_df['Qty'] = pd.to_numeric(temp_df['Qty'], errors='coerce').fillna(0.0)
        return temp_df
    except: return pd.DataFrame(columns=COLS)

df = load_data()

# --- 4. NAVIGATION ---
nav = st.columns(6)
pages = {"🌐 TERMINAL": "terminal", "🧠 AI COACH": "ai", "🏆 ASSETS": "rank", "📖 HISTORY": "history", "📊 STATS": "stats", "🧪 BACKTEST": "backtest"}
for i, (label, page_id) in enumerate(pages.items()):
    if nav[i].button(label): st.session_state.page = page_id

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 5. TERMINAL (LIVE PNL UPDATED) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", key="sym_input", label_visibility="collapsed").upper()
    
    # Locked Chart
    chart_url = f"https://s.tradingview.com/widgetembed/?symbol={sym}&interval=15&theme=dark"
    st.components.v1.iframe(chart_url, height=650)

    st.markdown("### 🟢 Active Position")
    open_trades = df[df['Status'] == 'OPEN']
    
    if not open_trades.empty:
        last_open = open_trades.iloc[-1]
        idx = open_trades.index[-1]
        
        # LIVE PRICE CALCULATION
        curr_price = get_live_price(last_open['Symbol'])
        if curr_price:
            entry = float(last_open['Entry'])
            qty = float(last_open['Qty'])
            # PnL Calculation: (Current - Entry) for BUY, (Entry - Current) for SELL
            if last_open['Side'] == "BUY":
                live_pnl = (curr_price - entry) * qty
            else:
                live_pnl = (entry - curr_price) * qty
            
            pnl_color = "#00ffca" if live_pnl >= 0 else "#ff4b2b"
            
            c_pnl, c_info, c_action = st.columns([2, 2, 1])
            with c_pnl:
                st.markdown(f'''<div class="pnl-box" style="border-left-color: {pnl_color};">
                    <span style="color:#848e9c; font-size:12px;">LIVE M2M PNL ({last_open['Symbol']})</span><br>
                    <span style="font-size:24px; color:{pnl_color}; font-weight:bold;">{" + " if live_pnl >= 0 else ""}${live_pnl:.2f}</span>
                </div>''', unsafe_allow_html=True)
            
            c_info.write(f"**Price:** {curr_price} | **Entry:** {entry}")
            
            if c_action.button("CLOSE TRADE", key="close_pos"):
                df.loc[idx, 'Status'] = 'CLOSED'
                df.loc[idx, 'PnL'] = live_pnl
                df.to_csv(DATA_FILE, index=False)
                st.rerun()
            
            # Auto-refresh for live effect
            time.sleep(2)
            st.rerun()
    else:
        st.info("No active positions.")

    # Execution Section (Locked)
    st.markdown("### ⚡ Execution")
    c1, c2 = st.columns(2)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    qty_in = c2.number_input("Qty", value=0.01, step=0.01)
    ent_in = st.number_input("Entry Price", value=0.0)

    if st.button("EXECUTE & OPEN", use_container_width=True):
        new_trade = [datetime.now().strftime("%y-%m-%d %H:%M"), sym, side, "Market", qty_in, ent_in, 0, 0, 0, 0, "Disciplined", "", "OPEN"]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.rerun()

# --- OTHER PAGES (AI COACH & HISTORY) LOCKED ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Intelligence Insights")
    if not df.empty:
        st.metric("Total PnL", f"${df['PnL'].sum():.2f}")
        st.line_chart(df['PnL'].cumsum())

elif st.session_state.page == "history":
    st.header("📖 Master Log History")
    st.dataframe(df.iloc[::-1], use_container_width=True)
