import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. FUTURE AI UI CONFIG ---
st.set_page_config(page_title="TGTB AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Custom Styling for Purple-Blue Futuristic Theme
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    
    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1d0e3a, #06080a 60%);
        color: #e0e3eb;
    }
    
    header, footer { visibility: hidden; }
    
    /* Futuristic Neon Buttons */
    .stButton > button {
        border-radius: 8px;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.4);
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 117, 252, 0.6);
    }
    
    /* Metrics and Cards Styling */
    div[data-testid="stMetricValue"] { color: #00ffca !important; font-family: 'Courier New', monospace; }
    .stNumberInput, .stSelectbox { background-color: #161a1e !important; color: white !important; }
    
    /* Fixing Chart Container Height */
    iframe { min-height: 650px !important; border: 2px solid #6a11cb; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
COLS = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS).to_csv(DATA_FILE, index=False)

try:
    df = pd.read_csv(DATA_FILE)
    df['PnL'] = pd.to_numeric(df['PnL'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=COLS)

# --- 3. NAVIGATION ---
nav = st.columns(6)
tabs = ["🌐 TERMINAL", "🧠 AI COACH", "🏆 ASSETS", "📖 HISTORY", "📊 STATS", "🧪 BACKTEST"]
pages = ["terminal", "ai", "rank", "history", "stats", "backtest"]

for i, tab in enumerate(tabs):
    if nav[i].button(tab): st.session_state.page = pages[i]

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (MAX CHART & THEME) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    chart_html = f'''
        <div style="height:650px; width:100%; border-radius:15px; overflow:hidden;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "locale": "en", "enable_publishing": false, "allow_symbol_change": true}});
            </script>
        </div>
    '''
    components.html(chart_html, height=660)

    st.markdown("### ⚡ AI Execution Panel")
    c1, c2, c3, c4 = st.columns(4)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    o_type = c2.selectbox("Type", ["Market", "Limit", "SL"])
    qty = c3.number_input("Qty", value=0.01, step=0.01)
    mood = c4.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    ent = r2c1.number_input("Entry", value=0.0)
    sl = r2c2.number_input("SL", value=0.0)
    tp = r2c3.number_input("TP", value=0.0)
    pnl = r2c4.number_input("PnL", value=0.0)
    
    # RR Calculator
    risk = abs(ent - sl)
    reward = abs(tp - ent)
    rr = round(reward/risk, 2) if risk != 0 else 0
    st.markdown(f"<p style='color:#00ffca; font-size:14px; font-weight:bold;'>🚀 Predicted RR: 1 : {rr}</p>", unsafe_allow_html=True)

    if st.button("EXECUTE & LOG TRADE", use_container_width=True):
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, pnl, rr, mood]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success(f"Trade successfully recorded in AI database!")
        st.rerun()

# --- 5. AI COACH (VISUAL REPORT) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Intelligence Report")
    if not df.empty:
        total_pnl = df['PnL'].sum()
        win_rate = (len(df[df['PnL'] > 0]) / len(df)) * 100
        
        m1, m2 = st.columns(2)
        m1.metric("Cumulative PnL", f"${total_pnl:.2f}")
        m2.metric("Intelligence Accuracy", f"{win_rate:.1f}%")
        
        st.subheader("Performance Curve")
        st.line_chart(df['PnL'].cumsum())
        
        st.subheader("Mood Impact Analysis")
        st.bar_chart(df.groupby('Mood')['PnL'].sum())
    else:
        st.info("AI needs data. Please log trades in the Terminal.")

# --- 6. HISTORY ---
elif st.session_state.page == "history":
    st.header("📖 Master Log History")
    st.dataframe(df.iloc[::-1], use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export AI Data (CSV)", data=csv, file_name="TGTB_Data.csv", mime="text/csv")
