import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Personal Stock Screening Tool")

st.write("⚠️ Use NSE format only (Example: RELIANCE.NS)")

stock_symbol = st.text_input("Enter Stock Symbol").upper().strip()

if stock_symbol:

    if not stock_symbol.endswith(".NS"):
        st.error("Invalid format. Use NSE format like RELIANCE.NS")
    else:
        stock = yf.Ticker(stock_symbol)

        # Fetch only price data (more reliable)
        data = stock.history(period="max")

        if data.empty:
            st.error("Unable to fetch stock data. Try again later.")
        else:
            # Recent activity check
            recent_data = stock.history(period="10d")

            if recent_data.empty:
                st.error("Stock not actively trading or invalid.")
            else:
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

                # Fallback name (symbol itself)
                company_name = stock_symbol.replace(".NS", "")

                st.subheader("Company Information")
                st.write(f"Stock Symbol: {stock_symbol}")
                st.write(f"Display Name: {company_name}")

                st.subheader("Stock Data")
                st.write(f"Current Price: ₹{current_price:.2f}")
                st.write(f"All Time High: ₹{ath:.2f}")
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
