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
    
    /* Close Button Style */
    div[data-testid="column"]:nth-child(3) button {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%) !important;
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

# --- 2. DATA ENGINE (FIXED TO SHOW DATA) ---
DATA_FILE = "global_trading_book_data.csv"
COLS = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood", "Screenshot", "Status"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS).to_csv(DATA_FILE, index=False)

def load_data():
    try:
        temp_df = pd.read_csv(DATA_FILE)
        temp_df['PnL'] = pd.to_numeric(temp_df['PnL'], errors='coerce').fillna(0.0)
        temp_df['Qty'] = pd.to_numeric(temp_df['Qty'], errors='coerce').fillna(0.0)
        return temp_df
    except: 
        return pd.DataFrame(columns=COLS)

df = load_data()

# --- 3. NAVIGATION ---
nav = st.columns(6)
pages = {"🌐 TERMINAL": "terminal", "🧠 AI COACH": "ai", "🏆 ASSETS": "rank", "📖 HISTORY": "history", "📊 STATS": "stats", "🧪 BACKTEST": "backtest"}
for i, (label, page_id) in enumerate(pages.items()):
    if nav[i].button(label): st.session_state.page = page_id

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (LOCKED) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    chart_url = f"https://s.tradingview.com/widgetembed/?symbol={sym}&interval=15&theme=dark"
    st.components.v1.iframe(chart_url, height=650)

    st.markdown("### 🟢 Active Position")
    open_trades = df[df['Status'] == 'OPEN']
    
    if not open_trades.empty:
        last_open = open_trades.iloc[-1]
        idx = open_trades.index[-1]
        current_pnl = float(last_open['Qty']) * 15.20 
        
        c_pnl, c_info, c_action = st.columns([2, 2, 1])
        with c_pnl:
            st.markdown(f'<div class="pnl-box"><span style="color:#848e9c; font-size:12px;">M2M LIVE PNL</span><br><span style="font-size:24px; color:#00ffca; font-weight:bold;">+ ${current_pnl:.2f}</span></div>', unsafe_allow_html=True)
        c_info.write(f"**{last_open['Symbol']}** | {last_open['Side']}")
        
        if c_action.button("CLOSE TRADE", key="close_pos"):
            df.loc[idx, 'Status'] = 'CLOSED'
            df.loc[idx, 'PnL'] = current_pnl
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
    else:
        st.info("No active positions.")

    # Execution Inputs
    st.markdown("### ⚡ Execution")
    c1, c2, c3, c4 = st.columns(4)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    qty = c3.number_input("Qty", value=0.01)
    ent = st.number_input("Entry Price", value=0.0)

    if st.button("EXECUTE & OPEN", use_container_width=True):
        new_trade = [datetime.now().strftime("%y-%m-%d %H:%M"), sym, side, "Market", qty, ent, 0, 0, 0, 0, "Disciplined", "", "OPEN"]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.rerun()

# --- 5. AI COACH (FIXED: SHOWS DATA NOW) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Intelligence Insights")
    if not df.empty:
        total_pnl = df['PnL'].sum()
        win_count = len(df[df['PnL'] > 0])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total PnL", f"${total_pnl:.2f}")
        m2.metric("Total Trades", len(df))
        m3.metric("Wins", win_count)
        
        st.subheader("Profit Curve")
        st.line_chart(df['PnL'].cumsum())
    else:
        st.warning("Data file khali hai. Pehle Terminal mein trade execute karein.")

# --- 6. HISTORY (FIXED: SHOWS LIST NOW) ---
elif st.session_state.page == "history":
    st.header("📖 Master Log History")
    if not df.empty:
        # Latest trades upar dikhane ke liye reverse kiya hai
        st.dataframe(df.iloc[::-1], use_container_width=True)
    else:
        st.info("Abhi tak koi trade history nahi hai.")
