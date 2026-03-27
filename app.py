import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.title("Stock Screening Tool")

st.write("⚠️ Use NSE format only (Example: RELIANCE.NS)")


# ✅ Cached + Retry function
@st.cache_data(ttl=3600)
def fetch_info_with_retry(symbol, retries=3, delay=2):
    stock = yf.Ticker(symbol)

    for attempt in range(retries):
        try:
            info = stock.info
            if info and "longName" in info:
                return info
        except:
            pass

        if attempt < retries - 1:
            time.sleep(delay)

    return None


# ✅ Cached price data
@st.cache_data(ttl=3600)
def fetch_history(symbol, period):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)


stock_symbol = st.text_input("Enter Stock Symbol").upper().strip()

if stock_symbol:

    if not stock_symbol.endswith(".NS"):
        st.error("Invalid format. Use NSE format like RELIANCE.NS")
    else:

        info = fetch_info_with_retry(stock_symbol)

        if not info:
            st.error("Unable to fetch stock information (API issue). Please try again.")
            st.stop()

        if not info.get("regularMarketPrice") or not info.get("longName"):
            st.error("Invalid or unsupported stock symbol.")
        else:
            recent_data = fetch_history(stock_symbol, "10d")

            if recent_data.empty:
                st.error("Stock not actively trading or invalid.")
            else:
                # ✅ CHANGED: 5 YEAR DATA ONLY
                data = fetch_history(stock_symbol, "5y")

                company_name = info.get("longName", "N/A")
                exchange = info.get("exchange", "N/A")
                currency = info.get("currency", "INR")

                current_price = data["Close"].iloc[-1]

                # ✅ 5Y HIGH & LOW
                high_5y = data["Close"].max()
                low_5y = data["Close"].min()

                distance_from_high = ((high_5y - current_price) / high_5y) * 100
                distance_from_low = ((current_price - low_5y) / low_5y) * 100

                st.subheader("Company Information")
                st.write(f"Company Name: {company_name}")
                st.write(f"Exchange: {exchange}")
                st.write(f"Currency: {currency}")

                st.subheader("Stock Data")
                st.write(f"Current Price: {current_price:.2f} {currency}")
                st.write(f"5 Year High: {high_5y:.2f} {currency}")
                st.write(f"5 Year Low: {low_5y:.2f} {currency}")
                st.write(f"Distance from High: {distance_from_high:.2f}%")
                st.write(f"Distance from Low: {distance_from_low:.2f}%")

                st.subheader("Condition Check")

                # ❌ At High
                if current_price < high_5y:
                    st.success("✔ Not at 5Y High")
                else:
                    st.error("✘ At 5Y High")

                # ✅ Far from High (>10%)
                if distance_from_high > 10:
                    st.success("✔ Far from High (>10% away)")
                else:
                    st.error("✘ Too close to High")

                # ✅ Near Low (<20%)
                if distance_from_low < 20:
                    st.success("✔ Near 5Y Low (fallen stock)")
                else:
                    st.error("✘ Not near Low")

                st.subheader("Price Chart (5 Years)")
                st.line_chart(data["Close"])
