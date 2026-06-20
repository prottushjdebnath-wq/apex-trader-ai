import sqlite3


class PerformanceTracker:

    def __init__(
        self,
        db_path="database/apex_trader.db"
    ):

        self.conn = sqlite3.connect(
            db_path
        )

        self.create_table()

    def create_table(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades(
                id INTEGER PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                entry REAL,
                exit REAL,
                pnl REAL
            )
            """
        )

        self.conn.commit()

    def add_trade(
        self,
        symbol,
        side,
        entry,
        exit_price,
        pnl
    ):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO trades(
                symbol,
                side,
                entry,
                exit,
                pnl
            )
            VALUES(?,?,?,?,?)
            """,
            (
                symbol,
                side,
                entry,
                exit_price,
                pnl
            )
        )

        self.conn.commit()

    def stats(self):

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT COUNT(*), SUM(pnl) FROM trades"
        )

        return cursor.fetchone()