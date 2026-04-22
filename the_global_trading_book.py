import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG ---
st.set_page_config(page_title="TGTB Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA ENGINE (FIXED) ---
DATA_FILE = "global_trading_book_data.csv"
COLS_REAL = ["Date", "Symbol", "Side", "Type", "Qty", "Entry", "SL", "TP", "PnL", "RR", "Mood"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS_REAL).to_csv(DATA_FILE, index=False)

# File read karte waqt error handling
try:
    df = pd.read_csv(DATA_FILE)
except:
    df = pd.DataFrame(columns=COLS_REAL)

# --- 3. NAVIGATION ---
nav = st.columns(6)
tabs = ["🌐 TERMINAL", "🧠 COACH", "🏆 ASSETS", "📖 HISTORY", "📊 STATS", "🧪 BACKTEST"]
pages = ["terminal", "ai", "rank", "history", "stats", "backtest"]

for i, tab in enumerate(tabs):
    if nav[i].button(tab): st.session_state.page = pages[i]

if 'page' not in st.session_state: st.session_state.page = "terminal"

# --- 4. TERMINAL (FIXED LOGIC) ---
if st.session_state.page == "terminal":
    sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
    
    # Large Chart (As per your requirement)
    components.html(f'''<div style="height:600px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "15", "theme": "dark", "container_id": "tv"}});</script></div>''', height=610)
    
    st.markdown("### ⚡ Execution & RR")
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
    
    # RR Calculator logic
    risk = abs(ent - sl)
    reward = abs(tp - ent)
    rr = round(reward/risk, 2) if risk != 0 else 0
    st.info(f"Planned RR: 1:{rr}")

    # --- ORDER PLACING FIX ---
    if st.button("LOG TRADE", use_container_width=True):
        try:
            # Naya data taiyar karna
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Symbol": sym,
                "Side": side,
                "Type": o_type,
                "Qty": qty,
                "Entry": ent,
                "SL": sl,
                "TP": tp,
                "PnL": pnl,
                "RR": rr,
                "Mood": mood
            }
            
            # DataFrame mein convert karke CSV mein append karna
            new_df = pd.DataFrame([new_entry])
            new_df.to_csv(DATA_FILE, mode='a', header=False, index=False)
            
            st.toast(f"✅ Order Placed: {sym} {side}")
            st.success("Trade Successfully Saved in History!")
            # 1 second wait karke refresh taaki user ko message dikhe
            st.rerun()
            
        except Exception as e:
            st.error(f"Error saving trade: {e}")

# --- 5. HISTORY (To check if saved) ---
elif st.session_state.page == "history":
    st.header("📖 Trade History")
    fresh_df = pd.read_csv(DATA_FILE)
    if not fresh_df.empty:
        st.dataframe(fresh_df.iloc[::-1], use_container_width=True)
    else:
        st.info("No trades found. Terminal mein 'Log Trade' click karein.")
