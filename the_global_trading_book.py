import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components
import base64
import time

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
    
    /* Close Button - Red Theme */
    .close-btn > div > button {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4) !important;
    }

    /* Chart Height Lock (Strict 650px) */
    iframe { min-height: 650px !important; border: 2px solid #6a11cb; border-radius: 12px; }
    
    .pnl-box {
        background: rgba(22, 26, 30, 0.8);
        border-left: 5px solid #00ffca;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
COLS = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood", "Screenshot", "Status"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS).to_csv(DATA_FILE, index=False)

def load_data():
    try:
        temp_df = pd.read_csv(DATA_FILE)
        temp_df['PnL'] = pd.to_numeric(temp_df['PnL'], errors='coerce').fillna(0)
        return temp_df
    except: return pd.DataFrame(columns=COLS)

df = load_data()

# --- 3. NAVIGATION (LOCKED) ---
nav = st.columns(6)
pages = {"🌐 TERMINAL": "terminal", "🧠 AI COACH": "ai", "🏆 ASSETS": "rank", "📖 HISTORY": "history", "📊 STATS": "stats", "🧪 BACKTEST": "backtest"}
for i, (label, page_id) in enumerate(pages.items()):
    if nav[i].button(label): st.session_state.page = page_id

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (POSITION CLOSE ADDED, REST LOCKED) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # Locked Chart
    components.html(f'''<div style="height:650px; width:100%; border-radius:12px; overflow:hidden;"><div id="tv_chart" style="height:100%;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "locale": "en", "enable_publishing": false, "allow_symbol_change": true}});</script></div>''', height=660)

    # --- ACTIVE POSITION & CLOSE LOGIC ---
    st.markdown("### 🟢 Active Position")
    # Check for open trades (Status == 'OPEN')
    open_trades = df[df['Status'] == 'OPEN']
    
    if not open_trades.empty:
        last_open = open_trades.iloc[-1]
        idx = open_trades.index[-1]
        
        c_pnl, c_info, c_action = st.columns([2, 2, 1])
        with c_pnl:
            st.markdown(f'''<div class="pnl-box">
                <span style="color:#848e9c; font-size:12px;">M2M LIVE PNL</span><br>
                <span style="font-size:24px; color:#00ffca; font-weight:bold;">+ ${last_open['Qty'] * 15.20:.2f}</span>
            </div>''', unsafe_allow_html=True)
        
        c_info.write(f"**{last_open['Symbol']}** | {last_open['Side']} | Entry: {last_open['Entry']}")
        
        with c_action:
            st.markdown('<div class="close-btn">', unsafe_allow_html=True)
            if st.button("CLOSE TRADE", key=f"close_{idx}"):
                # Logic: Update status and add final PnL
                df.at[idx, 'Status'] = 'CLOSED'
                df.at[idx, 'PnL'] = last_open['Qty'] * 15.20 # Sample final PnL
                df.to_csv(DATA_FILE, index=False)
                st.toast("Position Closed Successfully!")
                time.sleep(1)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No active positions.")

    st.markdown("### ⚡ Execution Panel")
    c1, c2, c3, c4 = st.columns(4)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    o_type = c2.selectbox("Type", ["Market", "Limit"])
    qty = c3.number_input("Qty", value=0.01)
    mood = c4.selectbox("Mood", ["Disciplined", "FOMO"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    ent, sl, tp = r2c1.number_input("Entry", value=0.0), r2c2.number_input("SL", value=0.0), r2c3.number_input("TP", value=0.0)
    
    if st.button("EXECUTE & OPEN POSITION", use_container_width=True):
        new_trade = [datetime.now().strftime("%y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, 0, 0, mood, "", "OPEN"]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Trade Opened!")
        st.rerun()

# --- 5. AI COACH (LOCKED) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Intelligence Insights")
    closed_df = df[df['Status'] == 'CLOSED']
    if not closed_df.empty:
        st.metric("Total Realized PnL", f"${closed_df['PnL'].sum():.2f}")
        st.line_chart(closed_df['PnL'].cumsum())
    else:
        st.info("No closed trades to analyze.")
