
#Test
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import matplotlib.pyplot as plt

def get_stock_data(ticker, start=None, end=None, period="1y"):
    """Download stock data for the specified ticker and period or date range"""
    print(f"Downloading data for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        if start and end:
            data = stock.history(start=start, end=end)
        else:
            data = stock.history(period=period)
        print(f"Downloaded {len(data)} days of data")
        return data
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()

def run_golden_cross_strategy(ticker="MSFT", start=None, end=None, period="1y"):
    """Run the Golden Cross trading strategy on the specified stock"""
    # Get stock data
    data = get_stock_data(ticker, start=start, end=end, period=period)
    if data.empty:
        return pd.DataFrame()
    # Calculate 50-day and 200-day moving averages
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    # We need at least 200 days of data for the strategy
    if len(data) < 200:
        return pd.DataFrame()
    # Find Golden Cross signals (MA50 crosses above MA200)
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    # Skip the first 200 days as we don't have moving averages for them
    strategy_data = data.iloc[200:].copy()
    signals = strategy_data[strategy_data['GoldenCross'] == True]
    if len(signals) == 0:
        return pd.DataFrame()
    # Implement the trading strategy
    trades = []
    for buy_date in signals.index:
        buy_price = strategy_data.loc[buy_date, 'Close']
        target_price = buy_price * 1.15  # 15% profit target
        max_hold_date = buy_date + pd.Timedelta(days=60)  # Max 60 days holding period
        # Find potential sell dates
        future_data = strategy_data.loc[buy_date:max_hold_date]
        # Check if target price was reached
        target_reached = future_data[future_data['Close'] >= target_price]
        if not target_reached.empty:
            # Sell at first date when target is reached
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            reason = "Target reached"
        elif len(future_data) > 1:
            # Sell at the end of holding period or last available date
            sell_date = future_data.index[-1]
            sell_price = future_data.loc[sell_date, 'Close']
            reason = "Max holding period"
        else:
            # Not enough future data
            continue
        # Calculate profit and holding period
        profit_pct = (sell_price / buy_price - 1) * 100
        holding_days = (sell_date - buy_date).days
        trades.append({
            'BuyDate': buy_date.strftime('%Y-%m-%d'),
            'BuyPrice': round(float(buy_price), 2),
            'SellDate': sell_date.strftime('%Y-%m-%d'),
            'SellPrice': round(float(sell_price), 2),
            'HoldingDays': holding_days,
            'ProfitPct': round(profit_pct, 2),
            'Reason': reason
        })
    # Convert to DataFrame and analyze results
    results = pd.DataFrame(trades)
    return results


def main():
    st.title("Trading Simulator")
   

    tickers_input = st.text_input("Enter stock tickers (comma separated, e.g., MSFT,AAPL,GOOG)", value="MSFT")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=datetime.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End date", value=datetime.today())
    period = None  # Not used if date range is selected

    if st.button("Create the chart and table"):
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        for ticker in tickers:
            with st.spinner(f"Downloading and analyzing data for {ticker}..."):
                # Download data for charting
                data = get_stock_data(ticker, start=start_date, end=end_date)
                st.subheader(f"Stock Prices and Moving Averages for {ticker}")
                if data.empty or len(data) < 20:
                    st.warning(f"Not enough data to plot for {ticker}.")
                else:
                    data['MA20'] = data['Close'].rolling(window=20).mean()
                    data['MA50'] = data['Close'].rolling(window=50).mean()
                    chart_data = data[['Open', 'Close', 'MA20', 'MA50']].dropna().copy()
                    # Plot with matplotlib for custom y-axis label
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(chart_data.index, chart_data['Close'], label='Close Price')
                    ax.plot(chart_data.index, chart_data['Open'], label='Open Price', linestyle='--', alpha=0.5)
                    ax.plot(chart_data.index, chart_data['MA20'], label='20-day MA')
                    ax.plot(chart_data.index, chart_data['MA50'], label='50-day MA')
                    ax.set_ylabel('Stock Price')
                    ax.set_xlabel('Date')
                    ax.legend()
                    plt.xticks(rotation=30)
                    plt.tight_layout()
                    st.pyplot(fig)
                    # Show table with Open and Close prices and MAs, matching chart period
                    st.dataframe(chart_data.reset_index())

if __name__ == "__main__":
    main()

