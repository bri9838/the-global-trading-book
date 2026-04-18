import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- STEP 1: UI & BRANDING ---
st.set_page_config(
    page_title="TGTB | Professional Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0c0e12; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #161a1e !important; border-right: 1px solid #2d3439; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; color: #00ffcc !important; font-weight: 700; }
    .stButton > button { width: 100%; border-radius: 4px; font-weight: bold; text-transform: uppercase; border: none; }
    
    /* Progress Bar Color Customization */
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4facfe, #00f2fe) !important; }
    
    /* Table Styling */
    .styled-table { border-collapse: collapse; width: 100%; background-color: #1e222d; border-radius: 8px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 2: DATA MANAGEMENT ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- STEP 3: SIDEBAR (Navigation & Leaderboard) ---
with st.sidebar:
    st.title("TGTB Terminal")
    menu = st.radio("MAIN MENU", ["🌐 Web Terminal", "🏆 Leaderboard", "📊 Analytics", "📔 Journal"])
    
    st.divider()
    st.subheader("🚀 Progress Tracker")
    target = 1000.0  # Monthly Profit Target
    current_pnl = df['PnL'].sum() if not df.empty else 0.0
    progress_per = min(max(current_pnl / target, 0.0), 1.0)
    st.write(f"Monthly Target: ${current_pnl:,.2f} / ${target:,.2f}")
    st.progress(progress_per)
    
    st.divider()
    st.subheader("Account Summary")
    st.metric("Total P&L", f"${current_pnl:,.2f}")

# --- STEP 4: APP INTERFACES ---

if menu == "🌐 Web Terminal":
    t_col1, t_col2, t_col3, t_col4 = st.columns([2, 1, 1, 4])
    with t_col1: sym = st.text_input("Symbol", value="BTCUSDT").upper()
    with t_col2: st.caption("Interval"); st.code("15m")
    with t_col3: st.caption("Status"); st.success("LIVE")

    st.divider()
    col_chart, col_exec = st.columns([3, 1])

    with col_chart:
        chart_html = f'''
            <div style="height:600px; border: 1px solid #2d3439; border-radius: 4px; overflow: hidden;">
                <div id="tv_chart" style="height:100%;"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart"}});
                </script>
            </div>
        '''
        components.html(chart_html, height=600)

    with col_exec:
        st.subheader("Order Panel")
        lots = st.number_input("Lots", value=0.01, step=0.01)
        pnl_entry = st.number_input("Profit/Loss Amount", value=0.0)
        mood = st.selectbox("Psychology", ["Disciplined", "FOMO", "Revenge"])
        
        b_col, s_col = st.columns(2)
        if b_col.button("BUY"):
            new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", "Market", 0, lots, pnl_entry, mood, ""]
            pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()
        if s_col.button("SELL"):
            new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", "Market", 0, lots, pnl_entry, mood, ""]
            pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()

elif menu == "🏆 Leaderboard":
    st.header("🏆 Strategy Leaderboard")
    if not df.empty:
        # Strategy ke basis par ranking
        leaderboard_df = df.groupby('Symbol')['PnL'].sum().sort_values(ascending=False).reset_index()
        leaderboard_df.index += 1 
        st.table(leaderboard_df)
    else:
        st.info("Leaderboard data available after first trade.")

elif menu == "📊 Analytics":
    st.header("Performance Analytics")
    if not df.empty:
        st.line_chart(df['PnL'].cumsum())
        st.subheader("Psychology Impact")
        st.bar_chart(df.groupby('Mood')['PnL'].sum())

elif menu == "📔 Journal":
    st.header("Trading Journal")
    st.dataframe(df, use_container_width=True)
