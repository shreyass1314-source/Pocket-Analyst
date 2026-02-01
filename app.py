import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import numpy as np

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Pocket Analyst V5", layout="mobile", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .header { color: #00FFAA; font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .warning-box { background-color: #3d0c0c; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; color: #ffcccc; margin-bottom: 10px; }
    .success-box { background-color: #0c3d21; border: 1px solid #00ffaa; padding: 15px; border-radius: 8px; color: #ccffdd; margin-bottom: 10px; }
    .metric-value { font-size: 20px; color: #fff; font-weight: 600; }
    .news-link { color: #58a6ff; text-decoration: none; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. USER INPUTS ---
st.markdown("<div class='header'>⚡ Pocket Analyst V5</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    ticker = st.text_input("Ticker Symbol", value="TATASTEEL").upper()
with col2:
    # MANUAL INVESTMENT INPUT
    invest_amount = st.number_input("Invest (₹)", value=10000, step=1000)

symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"

# --- 3. THE LOGIC ENGINE ---
def run_analysis_v5(symbol, invest_amount):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="6mo")
        info = stock.info
        
        if df.empty: return {"error": "Invalid Ticker or No Data Found"}

        # A. EVENTS RADAR (Earnings Check)
        earnings_warning = None
        try:
            cal = stock.calendar
            if cal is not None and not cal.empty:
                next_event = cal.iloc[0, 0]
                if isinstance(next_event, (datetime, pd.Timestamp)):
                    days_to = (next_event.date() - datetime.now().date()).days
                    if 0 <= days_to <= 7:
                        earnings_warning = f"⚠️ WARNING: Earnings in {days_to} days!"
        except:
            pass

        # B. LIQUIDITY CHECK
        avg_vol = info.get('averageVolume', 0)
        if avg_vol < 100000:
            return {"error": f"❌ LIQUIDITY TRAP! Volume is too low ({avg_vol}). Cannot exit easily."}

        # C. NEWS SCANNER
        news_list = stock.news
        headlines = []
        danger_flag = False
        danger_words = ["fraud", "scam", "sebi", "plunge", "crash", "investigation", "lawsuit"]
        
        if news_list:
            for item in news_list[:3]:
                title = item.get('title', '')
                link = item.get('link', '#')
                headlines.append({"title": title, "link": link})
                if any(w in title.lower() for w in danger_words):
                    danger_flag = True

        # D. TECHNICALS & MATH
        curr_price = df['Close'].iloc[-1]
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        atr = df['ATR'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        ema_200 = df['EMA_200'].iloc[-1]
        
        # E. CALCULATIONS
        stop_loss = curr_price - (2 * atr)
        quantity = int(invest_amount / curr_price) # Calculate shares based on user money
        total_risk = quantity * (curr_price - stop_loss) # How much money you lose if SL hits

        # F. SCORING
        score = 50
        reasons = []
        
        if curr_price > ema_200: 
            score += 20
            reasons.append("Trend: Bullish (Above 200 EMA)")
        else:
            reasons.append("Trend: Bearish (Below 200 EMA)")
            
        if 40 < rsi < 65: 
            score += 20
            reasons.append("Momentum: Healthy")
            
        if danger_flag: 
            score -= 40
            reasons.append("News: Negative Sentiment")
            
        if earnings_warning:
            score -= 20

        return {
            "price": curr_price,
            "score": min(max(score, 0), 100),
            "stop_loss": stop_loss,
            "quantity": quantity,
            "earnings_warning": earnings_warning,
            "headlines": headlines,
            "reasons": reasons,
            "total_risk": total_risk
        }

    except Exception as e:
        return {"error": str(e)}

# --- 4. EXECUTION ---
if st.button("Analyze Trade 🔍", use_container_width=True):
    with st.spinner("Connecting to Market Data..."):
        data = run_analysis_v5(symbol, invest_amount)
        
        if "error" in data:
            st.error(data["error"])
        else:
            # SCORE DISPLAY
            color = "#00ffaa" if data['score'] > 70 else "#ff4b4b" if data['score'] < 40 else "#cca300"
            st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 12px; color: #888;'>CONFIDENCE</div>
                <div style='font-size: 50px; font-weight: bold; color: {color};'>{data['score']}/100</div>
                <div style='font-size: 24px; color: white;'>CMP: ₹{round(data['price'], 2)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if data['earnings_warning']:
                st.warning(data['earnings_warning'])

            st.divider()
            
            # THE TRADE PLAN
            st.subheader("📋 Your Trade Plan")
            c1, c2 = st.columns(2)
            c1.metric("Buy Quantity", f"{data['quantity']} Shares")
            c2.metric("Stop Loss", f"₹{int(data['stop_loss'])}")
            
            # Risk Context
            st.info(f"💰 If Stop Loss hits, you lose: ₹{int(data['total_risk'])}")
            
            st.divider()
            
            # NEWS & LOGIC
            st.caption("Recent News Headlines:")
            for h in data['headlines']:
                st.markdown(f"• <a href='{h['link']}' class='news-link' target='_blank'>{h['title']}</a>", unsafe_allow_html=True)
