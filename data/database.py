import sqlite3
import os

class Database:
    def __init__(self, db_name="stocks.db"):
        # Absolute path relative to THIS file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)

    def connect(self):
        return sqlite3.connect(self.db_path)
    def create_table(self):
        CREATE_STOCK_TABLE = """
        CREATE TABLE IF NOT EXISTS stocks (
            stockId INTEGER PRIMARY KEY AUTOINCREMENT,
            companyName TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER
        );
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(CREATE_STOCK_TABLE)
        conn.commit()
        conn.close()

    def insert_stock(self, stock):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO stocks (companyName, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stock["companyName"],
            stock["date"],
            stock["open"],
            stock["high"],
            stock["low"],
            stock["close"],
            stock["volume"]
        ))

        conn.commit()
        conn.close()

    def get_all_stocks(self, limit=100):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM stocks
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_stocks_by_company(self, company, limit=100):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM stocks
            WHERE companyName = ?
            ORDER BY date DESC
            LIMIT ?
        """, (company, limit))

        rows = cursor.fetchall()
        conn.close()
        return rows
    
    
def delete_stock(self, stock_id: int):
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stocks WHERE stockId = ?", (stock_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0
##
# @file database.py
# @brief SQLite database access layer.
#
# @details
# Handles database connection, table creation, insertion,
# and retrieval of stock market data.
# Implements simple repository pattern.
##