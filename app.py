import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Stock Screening Tool")

st.write("⚠️ Use NSE format only (Example: RELIANCE.NS)")

stock_symbol = st.text_input("Enter Stock Symbol").upper().strip()

if stock_symbol:

    # Strict rule: Must end with .NS
    if not stock_symbol.endswith(".NS"):
        st.error("Invalid format. Use NSE format like RELIANCE.NS")
    else:
        stock = yf.Ticker(stock_symbol)

        try:
            info = stock.info
        except:
            st.error("Unable to fetch stock information.")
            st.stop()

        # Strict validation checks
        if (
            "regularMarketPrice" not in info
            or info["regularMarketPrice"] is None
            or "longName" not in info
        ):
            st.error("Invalid or unsupported stock symbol.")
        else:
            # Check recent trading activity (last 10 days)
            recent_data = stock.history(period="10d")

            if recent_data.empty:
                st.error("Stock not actively trading or invalid.")
            else:
                data = stock.history(period="max")

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

