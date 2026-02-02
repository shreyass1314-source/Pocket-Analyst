import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Sniper Tool", page_icon="🎯", layout="centered")

# --- STYLING & HELPER FUNCTIONS ---
st.markdown("""<style>.big-score { font-size: 40px; font-weight: bold; text-align: center; }</style>""", unsafe_allow_html=True)

def analyze_stock(symbol, invest_amount):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")
        if df.empty: return None
        
        # Technicals
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        curr_price = df['Close'].iloc[-1]
        atr = df['ATR'].iloc[-1] if pd.notna(df['ATR'].iloc[-1]) else curr_price * 0.02
        rsi = df['RSI'].iloc[-1] if pd.notna(df['RSI'].iloc[-1]) else 50
        ema_200 = df['EMA_200'].iloc[-1] if pd.notna(df['EMA_200'].iloc[-1]) else curr_price
        
        # Scoring
        score = 50
        if curr_price > ema_200: score += 20
        if 40 < rsi < 65: score += 20
        
        # Risk Math
        stop_loss = curr_price - (2 * atr)
        quantity = int(invest_amount / curr_price)
        risk_amt = quantity * (curr_price - stop_loss)
        
        return {
            "price": curr_price, "score": score, "stop_loss": stop_loss,
            "quantity": quantity, "risk": risk_amt, "symbol": symbol
        }
    except:
        return None

# --- UI ---
st.header("🎯 Sniper Analysis")
col1, col2 = st.columns([2,1])
with col1:
    ticker = st.text_input("Ticker", value="TATASTEEL").upper()
with col2:
    capital = st.number_input("Capital", value=10000, step=1000)

symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"

if st.button("Analyze"):
    data = analyze_stock(symbol, capital)
    if data:
        color = "green" if data['score'] > 70 else "red"
        st.markdown(f"<div class='big-score' style='color:{color}'>{data['score']}/100</div>", unsafe_allow_html=True)
        st.write(f"**CMP:** ₹{round(data['price'], 2)}")
        
        st.info(f"**Plan:** Buy {data['quantity']} Qty | Stop Loss: ₹{int(data['stop_loss'])} | Max Risk: ₹{int(data['risk'])}")
        
        # ADD TO WATCHLIST BUTTON
        if st.button(f"Add {ticker} to Watchlist 💼"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.success(f"Added {ticker} to Watchlist!")
    else:
        st.error("Error fetching data.")
