import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & NEON DARK THEME ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    
    /* Neon Navigation */
    .stButton > button {
        border-radius: 5px;
        background-color: #12151c !important;
        color: #848e9c !important;
        border: 1px solid #2b2f3a !important;
    }
    .stButton > button:hover { border-color: #00ffca !important; color: #00ffca !important; }

    /* Stats Cards */
    .metric-card {
        background: #161a1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2b2f3a;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Qty", "PnL", "Mood"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# --- 3. NAVIGATION ---
nav = st.columns(4)
if nav[0].button("🌐 TERMINAL"): st.session_state.page = "terminal"
if nav[1].button("🧠 AI COACH"): st.session_state.page = "ai"
if nav[2].button("🏆 ASSETS"): st.session_state.page = "rank"
if nav[3].button("📅 CALENDAR"): st.session_state.page = "news"

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL ---
if st.session_state.page == "terminal":
    ticker_html = '<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{"symbols":[{"proName":"BITSTAMP:BTCUSD","title":"BTC/USD"},{"proName":"FX_IDC:EURUSD","title":"EUR/USD"},{"proName":"FX:GBPUSD","title":"GBP/USD"}],"colorTheme":"dark","isTransparent":true,"locale":"en"}</script>'
    components.html(ticker_html, height=50)

    col_chart, col_exec = st.columns([3, 1])

    with col_chart:
        sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
        chart_html = f'''
            <div style="height:550px; border-radius:10px; overflow:hidden;">
                <div id="tradingview_tgtb"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{
                  "autosize": true, "symbol": "{sym}", "interval": "15",
                  "timezone": "Etc/UTC", "theme": "dark", "style": "1",
                  "locale": "en", "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                  "hide_side_toolbar": false, "container_id": "tradingview_tgtb"
                }});
                </script>
            </div>
        '''
        components.html(chart_html, height=560)

    with col_exec:
        st.markdown("### ⚡ Quick Log")
        qty = st.number_input("Qty", value=0.01, step=0.01)
        pnl = st.number_input("PnL ($)", value=0.0)
        mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])
        
        if st.button("🟢 BUY MARKET", use_container_width=True):
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", qty, pnl, mood]
            pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()
            
        if st.button("🔴 SELL MARKET", use_container_width=True):
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", qty, pnl, mood]
            pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()

# --- 5. ECONOMIC CALENDAR (FOREX FACTORY STYLE) ---
elif st.session_state.page == "news":
    st.header("📅 Economic Calendar & News")
    # Ye widget high-impact events ko Red/Orange indicators ke sath dikhata hai
    calendar_html = '''
    <div style="height:600px;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
        {
          "colorTheme": "dark",
          "isTransparent": true,
          "width": "100%",
          "height": "600",
          "locale": "en",
          "importanceFilter": "-1,0,1",
          "currencyFilter": "USD,EUR,GBP,JPY,AUD,CAD"
        }
        </script>
    </div>
    '''
    components.html(calendar_html, height=620)

# --- 6. AI COACH ---
elif st.session_state.page == "ai":
    st.header("🧠 AI Performance Coach")
    if not df.empty:
        df['Cumulative PnL'] = df['PnL'].cumsum()
        st.line_chart(df['Cumulative PnL'])
        st.metric("Total Profit", f"${df['PnL'].sum():.2f}")
    else:
        st.info("Trades log karein!")

# --- 7. ASSETS ---
elif st.session_state.page == "rank":
    st.header("🏆 Global Hotlist")
    hot_html = '<div style="height:600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>{"colorTheme":"dark","exchange":"US","showChart":true,"locale":"en","width":"100%","height":"600","isTransparent":true}</script></div>'
    components.html(hot_html, height=620)
