import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- STEP 1: UI CONFIG & FULL SCREEN CSS ---
st.set_page_config(page_title="TGTB | Terminal", layout="wide", initial_sidebar_state="collapsed")

# CSS to remove margins and make chart look like an App
st.markdown("""
    <style>
    /* Main Container Padding Hatao */
    .block-container { padding: 0rem 0rem 0rem 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #000000; }
    
    /* Header/Footer Hide karein */
    header, footer { visibility: hidden; }

    /* Floating Side Panel Styling */
    .floating-panel {
        background-color: rgba(22, 26, 30, 0.9);
        border: 1px solid #2d3439;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 2: DATA & SIDEBAR ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Price", "Qty", "PnL", "Mood", "Notes"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

with st.sidebar:
    st.title("TGTB Menu")
    menu = st.radio("Go to", ["🌐 Terminal", "🧠 AI Report", "📔 Journal"])

# --- STEP 3: FULL SCREEN TERMINAL VIEW ---
if menu == "🌐 Terminal":
    # Symbol Input at Top (Small Bar)
    col_input, col_spacer = st.columns([1, 4])
    with col_input:
        sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()

    # Layout: Chart (Left) and Small Floating Control (Right)
    col_chart, col_ctrl = st.columns([4, 1])

    with col_chart:
        # TradingView Widget - Height increased to 800px for "App" feel
        chart_html = f'''
            <div style="height:85vh; width:100%;">
                <div id="tv_chart_container" style="height:100%;"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>
                new TradingView.widget({{
                  "autosize": true,
                  "symbol": "{sym}",
                  "interval": "15",
                  "timezone": "Etc/UTC",
                  "theme": "dark",
                  "style": "1",
                  "locale": "en",
                  "toolbar_bg": "#f1f3f6",
                  "enable_publishing": false,
                  "hide_side_toolbar": false,
                  "allow_symbol_change": true,
                  "container_id": "tv_chart_container"
                }});
                </script>
            </div>
        '''
        components.html(chart_html, height=800)

    with col_ctrl:
        st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
        st.subheader("Order")
        lots = st.number_input("Lots", value=0.01, step=0.01)
        pnl = st.number_input("PnL", value=0.0)
        mood = st.selectbox("Mood", ["Disciplined", "FOMO", "Revenge"])
        
        if st.button("BUY", type="primary"):
            new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "BUY", "Market", 0, lots, pnl, mood, ""]
            pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.toast("Trade Logged!")
        
        if st.button("SELL"):
            new_trade = [datetime.now().strftime("%Y-%m-%d %H:%M"), sym, "SELL", "Market", 0, lots, pnl, mood, ""]
            pd.DataFrame([new_trade]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.toast("Trade Logged!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 4: AI REPORT SECTION ---
elif menu == "🧠 AI Report":
    st.header("🧠 AI Analysis & Insights")
    if not df.empty:
        st.write("### Weekly Analysis")
        st.bar_chart(df.groupby('Mood')['PnL'].sum())
        
        # Simple AI Insight
        bad_mood = df[df['PnL'] < 0]['Mood'].mode()
        if not bad_mood.empty:
            st.error(f"AI Alert: Aapne sabse zyada loss '{bad_mood[0]}' mood mein kiya hai. Be careful!")
    else:
        st.info("Log some trades to see AI report.")
