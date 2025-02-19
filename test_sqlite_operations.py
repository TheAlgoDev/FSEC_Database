# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 17:52:45 2025

@author: Doing
"""

import unittest
import pandas as pd
import sqlite3 as sq
from sqlite_operations import SQLiteDB

class TestSQLiteDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the SQLiteDB class with test database path
        cls.db = SQLiteDB(database_path="C:/Users/Doing/University of Central Florida/UCF_Photovoltaics_GRP - module_databases/FSEC_Database.db")  # Use in-memory database for testing
        
        # Create a test table
        cls.test_table_name = "test_table"
        cls.create_test_table()

    @classmethod
    def tearDownClass(cls):
        # Drop the test table
        cls.drop_test_table()

    @classmethod
    def create_test_table(cls):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {cls.test_table_name} (
            id INTEGER PRIMARY KEY,
            name TEXT,
            date TEXT
        );
        """
        with sq.connect(cls.db.database_path) as connection:
            connection.execute(create_table_query)

    @classmethod
    def drop_test_table(cls):
        drop_table_query = f"DROP TABLE IF EXISTS {cls.test_table_name};"
        with sq.connect(cls.db.database_path) as connection:
            connection.execute(drop_table_query)

    def test_create_sqlite_record(self):
        columns = ["name", "date"]
        values = ["Alice", "2025-02-18"]
        result = self.db.create_sqlite_record(self.test_table_name, columns, values)
        self.assertEqual(result, "Entry added to " + self.test_table_name)

    def test_read_records(self):
        result_df = self.db.read_records(self.test_table_name)
        self.assertIsInstance(result_df, pd.DataFrame)

    def test_blank_insert_to_database(self):
        data = {
            'name': ['Bob', 'Charlie'],
            'date': ['2025-02-19', '2025-02-20']
        }
        dataframe = pd.DataFrame(data)
        self.db.blank_insert_to_database(self.test_table_name, dataframe)

        query = f"SELECT * FROM {self.test_table_name};"
        with sq.connect(self.db.database_path) as connection:
            result_df = pd.read_sql_query(query, connection)
        self.assertEqual(len(result_df), 2)

    def test_create_sqlite_records_from_dataframe(self):
        data = {
            'name': ['Dave', 'Eve'],
            'date': ['2025-02-21', '2025-02-22']
        }
        dataframe = pd.DataFrame(data)
        result = self.db.create_sqlite_records_from_dataframe(self.test_table_name, dataframe)
        self.assertIn("updated with 2 entries", result)

    def test_join_module_metadata(self):
        # Create module-metadata table for the test
        create_module_metadata_query = """
        CREATE TABLE IF NOT EXISTS module_metadata_test (
            module_id INTEGER PRIMARY KEY,
            make TEXT,
            model TEXT,
            serial_number TEXT
        );
        """
        with sq.connect(self.db.database_path) as connection:
            connection.execute(create_module_metadata_query)
            connection.execute("INSERT INTO module_metadata_test (make, model, serial_number) VALUES ('Make1', 'Model1', 'SN1')")
        
        data = {
            'serial_number': ['SN1', 'SN2']
        }
        dataframe = pd.DataFrame(data)
        result_df = self.db.join_module_metadata(dataframe)
        self.assertIn('make', result_df.columns)
        self.assertIn('model', result_df.columns)

    def test_get_last_date_from_table(self):
        last_date = self.db.get_last_date_from_table(self.test_table_name)
        self.assertEqual(last_date, '2025-02-22')

if __name__ == "__main__":
    unittest.main()