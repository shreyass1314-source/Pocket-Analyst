import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="Market Scanner", page_icon="📡")

SECTORS = {
    "Auto": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS"],
    "Banks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "Metals": ["TATASTEEL.NS", "HINDALCO.NS", "VEDL.NS"]
}

st.header("📡 Market Scanner")
sector = st.selectbox("Select Sector", list(SECTORS.keys()))

if st.button("Scan Sector"):
    progress = st.progress(0)
    for i, ticker in enumerate(SECTORS[sector]):
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if not df.empty:
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            price = df['Close'].iloc[-1]
            
            if rsi < 30:
                st.success(f"🟢 **{ticker}** is OVERSOLD (RSI {int(rsi)}) - Potential Buy!")
            elif rsi > 70:
                st.error(f"🔴 **{ticker}** is OVERBOUGHT (RSI {int(rsi)}) - Be Careful.")
            else:
                st.write(f"⚪ {ticker}: Neutral (RSI {int(rsi)})")
        progress.progress((i + 1) / len(SECTORS[sector]))
