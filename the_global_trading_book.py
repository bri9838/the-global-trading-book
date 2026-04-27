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
    
    /* Chart Height Lock (Strict 650px) */
    iframe { min-height: 650px !important; border: 2px solid #6a11cb; border-radius: 12px; }
    
    /* SUCCESS BLINK ANIMATION */
    @keyframes blinker {  
        50% { opacity: 0; }
    }
    .success-msg {
        color: #00ffca;
        font-weight: bold;
        font-size: 20px;
        text-align: center;
        padding: 10px;
        border: 2px solid #00ffca;
        border-radius: 10px;
        animation: blinker 0.6s linear 3; /* 3 baar blink karega */
        background: rgba(0, 255, 202, 0.1);
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
COLS = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood", "Screenshot"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS).to_csv(DATA_FILE, index=False)

def load_data():
    try:
        temp_df = pd.read_csv(DATA_FILE)
        temp_df['PnL'] = pd.to_numeric(temp_df['PnL'], errors='coerce').fillna(0)
        temp_df['RR'] = pd.to_numeric(temp_df['RR'], errors='coerce').fillna(0)
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

# --- 4. TERMINAL PAGE (LOCKED) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # Locked Chart
    chart_html = f'''
        <div style="height:650px; width:100%; border-radius:12px; overflow:hidden;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "locale": "en", "enable_publishing": false, "allow_symbol_change": true}});
            </script>
        </div>
    '''
    components.html(chart_html, height=660)

    st.markdown("### ⚡ AI Execution Panel")
    
    # Inputs Layout
    c1, c2, c3, c4 = st.columns(4)
    side = c1.selectbox("Side", ["BUY", "SELL"])
    o_type = c2.selectbox("Type", ["Market", "Limit", "SL"])
    qty = c3.number_input("Qty", value=0.01, step=0.01)
    mood = c4.selectbox("Mood", ["Disciplined", "FOMO", "Revenge", "Impulsive"])

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    ent = r2c1.number_input("Entry", value=0.0)
    sl = r2c2.number_input("SL", value=0.0)
    tp = r2c3.number_input("TP", value=0.0)
    pnl = r2c4.number_input("PnL", value=0.0)
    
    # Screenshot Uploader
    img_file = st.file_uploader("Upload Chart Screenshot (Optional)", type=['png', 'jpg', 'jpeg'])
    img_base64 = ""
    if img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    risk = abs(ent - sl)
    reward = abs(tp - ent)
    rr = round(reward/risk, 2) if risk != 0 else 0
    st.markdown(f"<p style='color:#00ffca; font-weight:bold;'>🚀 Predicted RR: 1 : {rr}</p>", unsafe_allow_html=True)

    # SUCCESS MESSAGE LOGIC
    if "success_placed" in st.session_state and st.session_state.success_placed:
        st.markdown('<div class="success-msg">🚀 TRADE SUCCESSFULLY PLACED!</div>', unsafe_allow_html=True)
        # 3 seconds baad message hatane ke liye
        time.sleep(2)
        st.session_state.success_placed = False
        st.rerun()

    if st.button("EXECUTE & LOG TRADE", use_container_width=True):
        new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, o_type, qty, ent, sl, tp, pnl, rr, mood, img_base64]
        pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        
        # Blink message activate karna
        st.session_state.success_placed = True
        st.rerun()

# --- 5. AI COACH & HISTORY (SAME LOCKED LOGIC) ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Intelligence Insights")
    if not df.empty:
        total_pnl = df['PnL'].sum()
        m1, m2 = st.columns(2)
        m1.metric("Account Growth", f"${total_pnl:.2f}")
        m2.metric("Win Probability", f"{(len(df[df['PnL']>0])/len(df)*100):.1f}%")
        st.line_chart(df['PnL'].cumsum())

elif st.session_state.page == "history":
    st.header("📖 Master Log History")
    st.dataframe(df.iloc[::-1], use_container_width=True)
