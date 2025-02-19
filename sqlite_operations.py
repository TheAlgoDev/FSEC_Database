# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:32:12 2025

SQLite operations module.

Author: Brent
"""

import pandas as pd
import sqlite3 as sq
import os
import logging

# Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "C:/Users/Doing/University of Central Florida/UCF_Photovoltaics_GRP - module_databases/FSEC_Database.db")

def read_records(database, table_name, select='*', conditions=None):
    """
    Return the contents of a table as a DataFrame.

    Parameters:
    database (str): Path to SQLite database.
    table_name (str): Name of the SQL table.
    select (str): Columns to select.
    conditions (str): SQL conditions.

    Returns:
    pd.DataFrame: DataFrame containing the query results.
    """
    with sq.connect(database) as connection:
        cursor = connection.cursor()
        sql = f"SELECT {select} FROM {table_name}"
        if conditions:
            sql += f" {conditions}"
        cursor.execute(sql)
        records = pd.read_sql_query(sql, connection)
    return records

def blank_insert_to_database(table_name, dataframe):
    """
    Fallback function to save data to a table even if data format changes.

    Parameters:
    table_name (str): Name of the SQL table.
    dataframe (pd.DataFrame): DataFrame containing data to insert.
    """
    with sq.connect(DATABASE_PATH) as connection:
        dataframe.to_sql(table_name, connection, if_exists='append', index=False, dtype={col: 'TEXT' for col in dataframe})


def create_sqlite_record(table_name, columns, values):
    """
    Insert a single new entry to the database.

    Parameters:
    table_name (str): Name of the SQL table.
    columns (list): List of column names.
    values (list): List of values to insert.

    Returns:
    str: Success message or error.
    """
    with sq.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        try:
            cursor.execute(sql)
            connection.commit()
            return "Entry added to " + table_name
        except Exception as e:
            logging.error("Problem with SQL command: %s", sql)
            return str(e)

def create_sqlite_records_from_dataframe(table_name, dataframe):
    """
    Insert new rows to the database for every row in the DataFrame.

    Parameters:
    table_name (str): Name of the SQL table.
    dataframe (pd.DataFrame): DataFrame containing data to insert.

    Returns:
    str: Success message.
    """
    with sq.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        for _, row in dataframe.iterrows():
            columns = ', '.join([f'"{col}"' for col in row.index])
            values = ', '.join([f'"{val}"' for val in row.values])
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            try:
                cursor.execute(sql)
                connection.commit()
            except Exception as e:
                logging.error("Error inserting row: %s", str(e))
                pass
    return f"{table_name} updated with {len(dataframe)} entries."

def join_module_metadata(dataframe):
    """
    Join the Make and Model from module metadata, reducing human error and maintaining consistency.

    Parameters:
    dataframe (pd.DataFrame): DataFrame with serial numbers as a column.

    Returns:
    pd.DataFrame: Updated DataFrame with joined metadata.
    """
    query = """
        SELECT "module-id","make","model","serial-number"
        FROM "module-metadata";
    """

    with sq.connect(DATABASE_PATH) as conn:
        modules = pd.read_sql_query(query, conn)

    dataframe = dataframe.merge(modules, how='left', left_on="serial_number", right_on="serial-number")
    dataframe.drop(columns=['make_y', 'model_y'], inplace=True, errors='ignore')
    dataframe.rename(columns={'make_x': 'make', 'model_x': 'model'}, inplace=True)
    return dataframe

def get_last_date_from_table(table_name='sinton-iv-metadata'):
    """
    Get the last date of a measurement for a table in the database.

    Parameters:
    table_name (str): Name of the table in the SQLite database.

    Returns:
    int: Last date in YYYYMMDD format.
    """
    with sq.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        sql = f"SELECT MAX(date) from '{table_name}'"
        cursor.execute(sql)
        last_date = pd.read_sql_query(sql, connection)
    return last_date.loc[0][0]


