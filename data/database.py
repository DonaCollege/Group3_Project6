import sqlite3

class Database:
    def __init__(self, db_name="data/data.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

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
            volume INTEGER,
            UNIQUE(companyName, date)
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
            INSERT OR REPLACE INTO stocks (companyName, date, open, high, low, close, volume)
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
    
    # This will delete th ewhole table

    def delete_all_stocks(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM stocks")

        conn.commit()
        conn.close()

    # this will delete rows for a single company 

    def delete_stocks_by_company(self, company):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM stocks WHERE companyName = ?", (company,))

        conn.commit()
        conn.close()

    # This will delete the stocks by date 

    def delete_stocks_by_date(self, date):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM stocks WHERE date = ?", (date,))

        conn.commit()
        conn.close()