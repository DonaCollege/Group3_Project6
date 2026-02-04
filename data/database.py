import sqlite3

class Database:
    def __init__(self, db_name = "data.db"):
        self.db_name = db_name

        def connect(self):
            return sqlite3.connect(self.db_name)
        
        def create_table(self):

            CREATE_STOCK_TABLE = """CREATE TABLE IF NOT EXISTS stocks (
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
            
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(CREATE_STOCK_TABLE)
            connection.commit()
            connection.close()
            