from data.yfinance import fetch_stock_data
from data.database import Database

db = Database()
db.create_table()

symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

for symbol in symbols:
    stocks = fetch_stock_data(symbol, period="2y")
    for stock in stocks:
        db.insert_stock(stock)