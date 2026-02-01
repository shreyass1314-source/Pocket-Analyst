import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import numpy as np

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Pocket Analyst V6", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for "Midnight Blue" Theme (Better Visibility)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FAFAFA; }
    .header { color: #00FFAA; font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .sub-header { color: #a1a1aa; font-size: 14px; text-align: center; margin-bottom: 25px; }
    
    /* Cards */
    .metric-card { background-color: #1e2530; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .success-box { background-color: #052e16; border: 1px solid #22c55e; padding: 10px; border-radius: 8px; color: #bbf7d0; }
    .warning-box { background-color: #450a0a; border: 1px solid #ef4444; padding: 10px; border-radius: 8px; color: #fecaca; }
    
    /* Text */
    .big-score { font-size: 45px; font-weight: 800; text-align: center; }
    .cmp-text { font-size: 22px; font-weight: 600; text-align: center; color: #e4e4e7; }
    .news-link { color: #38bdf8; text-decoration: none; font-size: 15px; font-weight: 500; }
    .news-link:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LISTS (For the Scanner) ---
SECTORS = {
    "NIFTY 50 (Top Picks)": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATASTEEL.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS"],
    "Auto Sector": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "HEROMOTOCO.NS", "EICHERMOT.NS"],
    "Banking & Finance": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "BAJFINANCE.NS"],
    "IT Sector": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "Metals": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "COALINDIA.NS"]
}

# --- 3. HELPER FUNCTIONS ---
def get_stock_data(symbol, period="2y"):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        if df.empty: return None, None
        return df, stock
    except:
        return None, None

def calculate_technical_score(df):
    # Indicators
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    curr_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    ema_200 = df['EMA_200'].iloc[-1]
    
    # Handle NaN (New stocks)
    if pd.isna(ema_200): ema_200 = curr_price
    if pd.isna(rsi): rsi = 50

    # Logic
    score = 50
    reasons = []
    
    if curr_price > ema_200:
        score += 25
        reasons.append("✅ Bullish Trend (>200 EMA)")
    else:
        score -= 10
        reasons.append("⚠️ Bearish Trend (<200 EMA)")

    if 45 < rsi < 65:
        score += 25
        reasons.append("✅ RSI Momentum (Strong)")
    elif rsi > 70:
        score -= 10
        reasons.append("⚠️ Overbought (Risk)")
    elif rsi < 30:
        reasons.append("⚠️ Oversold (Weak)")

    return score, reasons, curr_price, ema_200, rsi

# --- 4. APP LAYOUT ---
st.markdown("<div class='header'>⚡ Pocket Analyst V6</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Scan. Analyze. Execute.</div>", unsafe_allow_html=True)

# TABS for Switcher
tab1, tab2 = st.tabs(["🔍 Analyze Stock", "📡 Find Opportunities"])

# ==========================================
# TAB 1: ANALYZE STOCK (Single Ticker)
# ==========================================
with tab1:
    col1, col2 = st.columns([2,1])
    with col1:
        ticker = st.text_input("Ticker Symbol", value="TATASTEEL").upper()
    with col2:
        invest_amount = st.number_input("Invest (₹)", value=10000, step=1000)

    symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"

    if st.button("Run Deep Analysis 🚀", use_container_width=True):
        with st.spinner(f"Analyzing {symbol}..."):
            df, stock = get_stock_data(symbol)
            
            if df is None:
                st.error("❌ Could not fetch data. Check symbol.")
            else:
                score, reasons, price, ema, rsi = calculate_technical_score(df)
                
                # Risk Math
                atr = ta.atr(df['High'], df['Low'], df['Close'], length=14).iloc[-1]
                if pd.isna(atr): atr = price * 0.02
                stop_loss = price - (2 * atr)
                quantity = int(invest_amount / price)
                risk_amt = quantity * (price - stop_loss)

                # --- DISPLAY ---
                # Score Circle
                color = "#00FFAA" if score > 70 else "#F43F5E" if score < 40 else "#FACC15"
                st.markdown(f"""
                <div class='metric-card' style='text-align:center;'>
                    <div style='color:#888; font-size:12px;'>CONFIDENCE SCORE</div>
                    <div class='big-score' style='color:{color};'>{score}/100</div>
                    <div class='cmp-text'>₹{round(price, 2)}</div>
                </div>
                """, unsafe_allow_html=True)

                # Trade Plan
                st.subheader("📋 Execution Plan")
                c1, c2 = st.columns(2)
                c1.metric("Buy Quantity", f"{quantity} Qty")
                c2.metric("Stop Loss", f"₹{int(stop_loss)}")
                st.info(f"🛡️ Max Risk on Trade: ₹{int(risk_amt)}")

                # Logic Reasons
                with st.expander("See Analysis Logic", expanded=True):
                    for r in reasons:
                        st.write(r)

                # --- NEWS SECTION (FIXED) ---
                st.subheader("📰 Market Intel")
                news_found = False
                try:
                    news = stock.news
                    if news:
                        for n in news[:3]:
                            st.markdown(f"• <a href='{n['link']}' class='news-link' target='_blank'>{n['title']}</a>", unsafe_allow_html=True)
                            news_found = True
                except:
                    pass
                
                if not news_found:
                    # Fallback to Google News Search
                    search_url = f"https://www.google.com/search?q={ticker}+stock+news&tbm=nws"
                    st.markdown(f"⚠️ API News unavailable. <a href='{search_url}' class='news-link' target='_blank'>Click here to search Google News for {ticker}</a>", unsafe_allow_html=True)

# ==========================================
# TAB 2: FIND OPPORTUNITIES (Scanner)
# ==========================================
with tab2:
    st.write("Select a sector to scan for High Momentum setups.")
    selected_sector = st.selectbox("Select Sector", list(SECTORS.keys()))
    
    if st.button("Scan Sector 📡", use_container_width=True):
        stock_list = SECTORS[selected_sector]
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, stock_sym in enumerate(stock_list):
            status_text.text(f"Scanning {stock_sym}...")
            df, _ = get_stock_data(stock_sym, period="1y")
            
            if df is not None:
                score, reasons, price, ema, rsi = calculate_technical_score(df)
                
                # FILTER: Only show stocks with Score > 60 (Good setups)
                if score >= 60:
                    results.append({
                        "Symbol": stock_sym.replace(".NS", ""),
                        "Price": f"₹{int(price)}",
                        "Score": score,
                        "Signal": "Strong Buy" if score > 75 else "Buy"
                    })
            
            progress_bar.progress((i + 1) / len(stock_list))
            
        status_text.empty()
        progress_bar.empty()
        
        if results:
            st.success(f"Found {len(results)} potential trades in {selected_sector}!")
            # Convert to DataFrame for nice display
            df_results = pd.DataFrame(results)
            st.dataframe(df_results.style.applymap(lambda x: 'color: green' if x == 'Strong Buy' else '', subset=['Signal']), use_container_width=True, hide_index=True)
            st.caption("Tip: Go to the 'Analyze Stock' tab to calculate position size for these matches.")
        else:
            st.warning("No high-probability setups found in this sector right now. Market might be weak.")
