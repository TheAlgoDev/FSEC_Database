# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 17:41:16 2025

@author: Doing

"""

import unittest
import pandas as pd
from sqlalchemy import create_engine, text
from postgres_operations import PostgresDB

class TestPostgresDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the PostgresDB class with test database credentials

        cls.db = PostgresDB(username="dpv", password="sun", database="fsecdatabase")

        
        # Create a test table
        cls.test_table_name = "test_table"
        cls.create_test_table()

    @classmethod
    def tearDownClass(cls):
        # Drop the test table
        cls.drop_test_table()
        cls.db.engine.dispose()

    @classmethod
    def create_test_table(cls):

        create_table_query = text(f"""
        CREATE TABLE IF NOT EXISTS {cls.test_table_name} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            date DATE
        );
        """)
        with cls.db.engine.connect() as connection:
            connection.execute(create_table_query)

    @classmethod
    def drop_test_table(cls):
        drop_table_query = text(f"DROP TABLE IF EXISTS {cls.test_table_name};")
        with cls.db.engine.connect() as connection:
            connection.execute(drop_table_query)

    def test_create_postgres_records_from_dataframe(self):
        data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'date': ['2025-02-18', '2025-02-19', '2025-02-20']
        }
        dataframe = pd.DataFrame(data)
        self.db.create_postgres_records_from_dataframe(self.test_table_name, dataframe)

        query = f"SELECT * FROM {self.test_table_name};"
        result_df = self.db.read_records_from_postgres(query)
        self.assertEqual(len(result_df), 3)
        self.assertIn('Alice', result_df['name'].values)

    def test_read_records_from_postgres(self):
        query = f"SELECT * FROM {self.test_table_name};"
        result_df = self.db.read_records_from_postgres(query)
        self.assertIsInstance(result_df, pd.DataFrame)

    def test_fetch_data_by_date(self):
        start_date = "2025-02-18"
        end_date = "2025-02-19"
        result_df = self.db.fetch_data_by_date(self.test_table_name, start_date, end_date)
        self.assertEqual(len(result_df), 2)
        self.assertIn('Alice', result_df['name'].values)

    def test_get_table_names_and_comments(self):
        result_df = self.db.get_table_names_and_comments()
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn(self.test_table_name, result_df['table_name'].values)

    def test_get_table_schema(self):
        result_df = self.db.get_table_schema(self.test_table_name)
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn('name', result_df['column_name'].values)

if __name__ == "__main__":
    unittest.main()