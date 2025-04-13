import sqlite3
import pandas as pd

DB_PATH = "data.sqlite"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_table():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            value REAL,
            category TEXT
        );
        """)

def insert_data(name, value, category):
    with get_connection() as conn:
        conn.execute("INSERT INTO data (name, value, category) VALUES (?, ?, ?)",
                     (name, value, category))
        conn.commit()

def query_data(filter_category=None):
    with get_connection() as conn:
        if filter_category:
            return pd.read_sql_query("SELECT * FROM data WHERE category = ?", conn, params=(filter_category,))
        return pd.read_sql_query("SELECT * FROM data", conn)