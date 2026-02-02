import streamlit as st
import yfinance as yf

st.set_page_config(page_title="My Watchlist", page_icon="💼")

st.header("💼 My Watchlist")

if 'watchlist' not in st.session_state or not st.session_state.watchlist:
    st.info("Your watchlist is empty. Go to the Sniper Tool to add stocks.")
else:
    if st.button("Clear Watchlist"):
        st.session_state.watchlist = []
        st.experimental_rerun()

    for ticker in st.session_state.watchlist:
        symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        
        st.markdown(f"**{ticker}**")
        st.write(f"Current Price: ₹{round(price, 2)}")
        st.markdown("---")
