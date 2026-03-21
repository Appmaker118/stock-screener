import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.title("Personal Stock Screening Tool")

st.write("⚠️ Use NSE format only (Example: RELIANCE.NS)")


# ✅ Cached + Retry function for INFO
@st.cache_data(ttl=300)  # cache for 5 minutes
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
@st.cache_data(ttl=300)
def fetch_history(symbol, period):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)


stock_symbol = st.text_input("Enter Stock Symbol").upper().strip()

if stock_symbol:

    # Strict rule: Must end with .NS
    if not stock_symbol.endswith(".NS"):
        st.error("Invalid format. Use NSE format like RELIANCE.NS")
    else:

        # ✅ Fetch info (cached + retry)
        info = fetch_info_with_retry(stock_symbol)

        if not info:
            st.error("Unable to fetch stock information (API issue). Please try again.")
            st.stop()

        # ✅ Validation
        if not info.get("regularMarketPrice") or not info.get("longName"):
            st.error("Invalid or unsupported stock symbol.")
        else:
            # Check recent trading activity
            recent_data = fetch_history(stock_symbol, "10d")

            if recent_data.empty:
                st.error("Stock not actively trading or invalid.")
            else:
                data = fetch_history(stock_symbol, "max")

                company_name = info.get("longName", "N/A")
                exchange = info.get("exchange", "N/A")
                currency = info.get("currency", "INR")

                current_price = data["Close"].iloc[-1]
                ath = data["Close"].max()

                distance_from_ath = ((ath - current_price) / ath) * 100

                six_month_data = data.last("6M")
                one_year_data = data.last("1Y")

                six_month_return = (
                    (current_price - six_month_data["Close"].iloc[0])
                    / six_month_data["Close"].iloc[0]
                ) * 100

                one_year_return = (
                    (current_price - one_year_data["Close"].iloc[0])
                    / one_year_data["Close"].iloc[0]
                ) * 100

                st.subheader("Company Information")
                st.write(f"Company Name: {company_name}")
                st.write(f"Exchange: {exchange}")
                st.write(f"Currency: {currency}")

                st.subheader("Stock Data")
                st.write(f"Current Price: {current_price:.2f} {currency}")
                st.write(f"All Time High: {ath:.2f} {currency}")
                st.write(f"Distance from ATH: {distance_from_ath:.2f}%")
                st.write(f"6 Month Return: {six_month_return:.2f}%")
                st.write(f"1 Year Return: {one_year_return:.2f}%")

                st.subheader("Condition Check")

                if current_price < ath:
                    st.success("✔ Not at All Time High")
                else:
                    st.error("✘ At All Time High")

                if distance_from_ath > 5:
                    st.success("✔ Not near ATH (more than 5% away)")
                else:
                    st.error("✘ Near ATH")

                if six_month_return > 0:
                    st.success("✔ 6 Month Trend Positive")
                else:
                    st.error("✘ 6 Month Trend Negative")

                if one_year_return > 0:
                    st.success("✔ 1 Year Trend Positive")
                else:
                    st.error("✘ 1 Year Trend Negative")

                st.subheader("Price Chart")
                st.line_chart(data["Close"])
