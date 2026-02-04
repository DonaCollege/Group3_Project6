import yfinance as yf

def fetch_stock_data(symbol: str, period="1y", interval="1d"):
    """
    Fetch real stock data from Yahoo Finance using yfinance
    """

    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)

    data = []

    for date, row in hist.iterrows():
        data.append({
            "companyName": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        })

    return data