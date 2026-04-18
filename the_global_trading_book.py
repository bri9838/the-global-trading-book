import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & FULL SCREEN APP LOOK ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Chart ko border-to-border karne ke liye */
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #000000; }
    header, footer { visibility: hidden; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #111418 !important; width: 250px !important; }
    
    /* Order Panel Styling */
    .order-box {
        background-color: #161a1e;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2d3439;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. SIDEBAR NAVIGATION (Yahan se saari Report dikhengi) ---
with st.sidebar:
    st.markdown("### 📔 TGTB MENU")
    menu = st.radio("Reports & Tools", ["🌐 Live Terminal", "🧠 AI Analysis", "🏆 Leaderboard", "📝 Trade Journal"])
    
    st.divider()
    # Monthly Progress
    target = 1000.0
    current_pnl = df['PnL'].sum() if not df.empty else 0.0
    st.write(f"Monthly Target: ${current_pnl:.1f} / ${target}")
    st.progress(min(max(current_pnl/target, 0.0), 1.0))

# --- 4. NAVIGATION LOGIC ---

if menu == "🌐 Live Terminal":
    # Symbol Input & Top Info
    t_col1, t_col2 = st.columns([1, 4])
    with t_col1:
        sym = st.text_input("Sym", value="BTCUSDT", label_visibility="collapsed").upper()

    col_chart, col_order = st.columns([4, 1.2])

    with col_chart:
        # TradingView Chart - 800px High
        chart_html = f'''
            <div style="height:800px; width:100%;">
                <div id="tv_chart" style="height:100%;"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart", "hide_side_toolbar": false}});
                </script>
            </div>
        '''
        components.html(chart_html, height=800)

    with col_order:
        st.markdown('<div class="order-box">', unsafe_allow_html=True)
        st.subheader("Order")
        lots = st.number_input("Lots", value=0.01, step=0.01)
        pnl_amt = st.number_input("PnL", value=0.0)
        mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge", "Impulsive"])
        
        b_btn = st.button("BUY", type="primary", use_container_width=True)
        s_btn = st.button("SELL", use_container_width=True)
        
        if b_btn or s_btn:
            side = "BUY" if b_btn else "SELL"
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, side, "Market", 0, lots, pnl_amt, mood, ""]
            pd.DataFrame([new_data]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Trade Logged!")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🧠 AI Analysis":
    st.title("🧠 AI Report")
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Profit by Psychology")
            st.bar_chart(df.groupby('Mood')['PnL'].sum())
        with col2:
            st.subheader("AI Insight")
            avg_pnl = df['PnL'].mean()
            if avg_pnl > 0: st.success(f"Discipline Score High! Average profit ${avg_pnl:.2f}")
            else: st.warning("AI Hint: Check your FOMO trades in the Leaderboard.")
    else: st.info("No data found.")

elif menu == "🏆 Leaderboard":
    st.title("🏆 Best Trading Symbols")
    if not df.empty:
        leaderboard = df.groupby('Symbol')['PnL'].sum().sort_values(ascending=False)
        st.table(leaderboard)

elif menu == "📝 Trade Journal":
    st.title("📝 Journal History")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
