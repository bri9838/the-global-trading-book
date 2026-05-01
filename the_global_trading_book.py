import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SETTINGS & THEME LOCK ---
st.set_page_config(page_title="TGTB Master Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    .stApp { background: #06080a; color: #e0e3eb; }
    header, footer { visibility: hidden; }
    
    /* CHART & DRAWING BAR LOCK */
    .chart-wrapper {
        height: 650px !important;
        border: 2px solid #6a11cb;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    /* BUTTON & METRIC STYLING */
    .stButton > button {
        border-radius: 8px; font-weight: bold;
        border: 1px solid #6a11cb !important;
        background: rgba(106, 17, 203, 0.1);
    }
    [data-testid="stMetricValue"] { color: #00ffca !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
DATA_FILE = "global_trading_book_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Symbol", "Side", "Type", "Qty", "Entry", "Exit", "PnL", "Status"]).to_csv(DATA_FILE, index=False)

def get_data(): 
    return pd.read_csv(DATA_FILE)

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "🌐 TERMINAL"
nav = st.columns(5)
pages = ["🌐 TERMINAL", "🧠 AI REPORT", "📊 ANALYTICS", "📖 JOURNAL", "🧪 BACKTEST"]

for i, p in enumerate(pages):
    if nav[i].button(p, use_container_width=True):
        st.session_state.page = p

# --- 4. PAGE: TERMINAL (CHART + DRAWING TOOLS + ORDER TYPE) ---
if st.session_state.page == "🌐 TERMINAL":
    col_chart, col_order = st.columns([3.5, 1])
    
    with col_chart:
        sym = st.text_input("Symbol", value="BTCUSDT", label_visibility="collapsed").upper()
        # Advanced TradingView Widget with Side Toolbar Locked
        chart_html = f"""
        <div style="height:650px;">
          <div id="tv_chart" style="height:650px;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "BINANCE:{sym}", "interval": "1",
            "theme": "dark", "style": "1", "hide_side_toolbar": false,
            "allow_symbol_change": true, "container_id": "tv_chart"
          }});
          </script>
        </div>"""
        components.html(chart_html, height=650)

    with col_order:
        st.markdown("### ⚡ Execution")
        o_side = st.selectbox("Side", ["BUY", "SELL"])
        o_type = st.selectbox("Order Type", ["Market", "Limit", "SL", "TP"]) # Order Type Locked
        o_qty = st.number_input("Qty", value=0.01, step=0.01)
        o_ent = st.number_input("Entry", value=0.0)
        
        if st.button("EXECUTE TRADE", use_container_width=True):
            new_t = [datetime.now().strftime("%y-%m-%d"), sym, o_side, o_type, o_qty, o_ent, 0, 0, "OPEN"]
            pd.DataFrame([new_t]).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.toast("Trade Logged in Terminal!")

# --- 5. PAGE: BACKTEST (MANUAL ENTRY & ANALYTICS LOCKED) ---
elif st.session_state.page == "🧪 BACKTEST":
    st.subheader("Strategy Backtest Engine")
    
    # Form for Manual Entry (Fix for Screenshot_20260501_092354.jpg)
    with st.expander("➕ Add Manual Backtest Record", expanded=True):
        with st.form("bt_form"):
            bc1, bc2, bc3 = st.columns(3)
            b_sym = bc1.text_input("Symbol", "BTCUSDT")
            b_side = bc2.selectbox("Side", ["BUY", "SELL"])
            b_qty = bc3.number_input("Qty", 1.0)
            
            bc4, bc5 = st.columns(2)
            b_en = bc4.number_input("Entry Price")
            b_ex = bc5.number_input("Exit Price")
            
            if st.form_submit_button("Save & Lock to Backtest"):
                pnl = (b_ex - b_en) * b_qty if b_side == "BUY" else (b_en - b_ex) * b_qty
                new_bt = [datetime.now().strftime("%y-%m-%d"), b_sym, b_side, "Backtest", b_qty, b_en, b_ex, pnl, "CLOSED"]
                pd.DataFrame([new_bt]).to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success("Data added to Backtest Log!")
                st.rerun()

    # Backtest Metrics & Visuals
    df = get_data()
    if not df.empty:
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Profit", f"₹{df['PnL'].sum():,.2f}")
        m2.metric("Win Rate", f"{(len(df[df['PnL']>0])/len(df)*100):.1f}%" if len(df)>0 else "0%")
        m3.metric("Total Trades", len(df))
        
        st.markdown("#### 📈 Equity Growth")
        st.line_chart(df['PnL'].cumsum(), color="#6a11cb")
    else:
        st.info("No data found. Manual entries added here will show up in the report.")

# --- 6. PAGE: JOURNAL ---
elif st.session_state.page == "📖 JOURNAL":
    st.subheader("Master Trade Journal")
    st.dataframe(get_data().iloc[::-1], use_container_width=True)
