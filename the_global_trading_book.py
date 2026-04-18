import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PRO CONFIG & UI ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    .stApp { background-color: #06080a; }
    header, footer { visibility: hidden; }
    
    /* Navigation Buttons */
    .stButton > button {
        border-radius: 8px;
        height: 2.8em;
        font-size: 12px !important;
        background-color: #12151c !important;
        color: #848e9c !important;
        border: 1px solid #2b2f3a !important;
    }
    .stButton > button:hover { color: #f0b90b !important; border-color: #f0b90b !important; }

    /* Trade Cards */
    .trade-card {
        background-color: #161a1e;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #26a69a;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. TOP SMART NAVIGATION ---
nav_col = st.columns(4)
if nav_col[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav_col[1].button("🧠 AI COACH"): st.session_state.page = "ai"
if nav_col[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav_col[3].button("📖 HISTORY"): st.session_state.page = "journal"

if 'page' not in st.session_state:
    st.session_state.page = "terminal"

# --- 4. LOGIC ENGINE ---

if st.session_state.page == "terminal":
    # --- MARKET PULSE (GAINERS/LOSERS TAPE) ---
    ticker_html = '''
    <div style="height:60px; background-color:#06080a; border-bottom:1px solid #1e222d;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {
        "symbols": [
            {"proName": "NSE:NIFTY", "title": "Nifty 50"},
            {"proName": "NSE:BANKNIFTY", "title": "Bank Nifty"},
            {"s": "NSE:RELIANCE", "d": "Reliance"},
            {"s": "NSE:HDFCBANK", "d": "HDFC Bank"},
            {"s": "NSE:TCS", "d": "TCS"},
            {"s": "NSE:ICICIBANK", "d": "ICICI Bank"}
        ],
        "showSymbolLogo": true,
        "colorTheme": "dark",
        "isTransparent": true,
        "displayMode": "adaptive",
        "locale": "in"
        }
        </script>
    </div>
    '''
    components.html(ticker_html, height=60)

    # Symbol Input & Chart
    sym = st.text_input("Symbol", value="NSE:NIFTY", label_visibility="collapsed").upper()
    
    chart_html = f'''
        <div style="height:500px; width:100%; border-radius: 8px; overflow: hidden; border: 1px solid #1e222d;">
            <div id="tv_chart" style="height:100%;"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
            new TradingView.widget({{
              "autosize": true,
              "symbol": "{sym}",
              "interval": "15",
              "timezone": "Asia/Kolkata",
              "theme": "dark",
              "style": "1",
              "locale": "in",
              "hide_side_toolbar": false,
              "allow_symbol_change": true,
              "container_id": "tv_chart"
            }});
            </script>
        </div>
    '''
    components.html(chart_html, height=510)

    st.markdown("### ⚡ Quick Execution")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: lots = st.number_input("Qty", value=1, step=1)
    with c2: pnl_val = st.number_input("PnL (₹)", value=0.0)
    with c3: mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge", "Impulsive"])
    
    b_col, s_col = st.columns(2)
    if b_col.button("🟢 BUY MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%d %b, %H:%M"), sym, "BUY", "Market", 0, lots, pnl_val, mood, ""]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.balloons()
        st.rerun()
    if s_col.button("🔴 SELL MARKET", use_container_width=True):
        new_row = [datetime.now().strftime("%d %b, %H:%M"), sym, "SELL", "Market", 0, lots, pnl_val, mood, ""]
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.snow()
        st.rerun()

elif st.session_state.page == "ai":
    st.header("🧠 AI Trading Insights")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        wins = len(df[df['PnL'] > 0])
        total_trades = len(df)
        win_rate = (wins / total_trades) * 100
        
        c1.metric("Win Rate", f"{win_rate:.1f}%")
        c2.metric("Total PnL", f"₹{df['PnL'].sum():.2f}")
        c3.metric("Trades", total_trades)

        st.subheader("📈 Performance Growth")
        df['Cumulative PnL'] = df['PnL'].cumsum()
        st.line_chart(df['Cumulative PnL'])
        
        st.subheader("🤖 Coach Advice")
        if win_rate < 45: st.error("AI Alert: Win rate thoda kam hai.")
        else: st.success("Great! Aapka discipline score behtar ho raha hai.")
    else: st.info("AI analysis ke liye trades log karein.")

elif st.session_state.page == "rank":
    st.header("🏆 Asset Performance")
    # Yahan hum NSE Top Gainers ka widget add kar rahe hain
    gainer_loser_html = '''
    <div style="height:600px;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>
        {
          "colorTheme": "dark",
          "dateRange": "12M",
          "exchange": "NSE",
          "showChart": true,
          "locale": "in",
          "width": "100%",
          "height": "600",
          "largeChartUrl": "",
          "isTransparent": true,
          "showSymbolLogo": true,
          "showFloatingTooltip": false,
          "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
          "plotLineColorFalling": "rgba(41, 98, 255, 1)",
          "gridLineColor": "rgba(240, 243, 250, 0)",
          "scaleFontColor": "rgba(106, 109, 120, 1)",
          "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
          "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
          "symbolActiveColor": "rgba(41, 98, 255, 0.12)"
        }
        </script>
    </div>
    '''
    components.html(gainer_loser_html, height=620)

elif st.session_state.page == "journal":
    st.header("📖 Trade Journal")
    if not df.empty:
        for i, row in df.iloc[::-1].iterrows():
            color = "#26a69a" if row['PnL'] >= 0 else "#ef5350"
            st.markdown(f'<div class="trade-card" style="border-left-color: {color}"><b>{row["Date"]}</b> | {row["Symbol"]}<br><span style="color:{color}">PnL: ₹{row["PnL"]}</span> | Mood: {row["Mood"]}</div>', unsafe_allow_html=True)
