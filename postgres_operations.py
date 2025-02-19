# -*- coding: utf-8 -*-
"""
PostgreSQL operations module.

Author: Brent
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

def connect_to_postgres(username, password):
    """
    Establish a connection to the PostgreSQL database and execute a query.

    Parameters:
    username (str): PostgreSQL username.
    password (str): PostgreSQL password.
    """
    with psycopg2.connect(
        database="fsecdatabase", user=username, password=password, host="34.73.180.136", port=5432) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM 'fsecdatabase.module_metadata';")

def create_postgres_records_from_dataframe(username, password, table_name, dataframe):
    """
    Insert new rows into the PostgreSQL table for every row in the DataFrame.

    Parameters:
    username (str): PostgreSQL username.
    password (str): PostgreSQL password.
    table_name (str): Name of the SQL table.
    dataframe (pd.DataFrame): DataFrame containing data to insert.
    """
    engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
    try:
        dataframe.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            method='multi'
        )
    except Exception as e:
        logging.error("Error inserting dataframe records: %s", str(e))

def read_records_from_postgres(username, password, query):
    """
    Fetch data from PostgreSQL using SQLAlchemy and return a DataFrame.

    Parameters:
    username (str): PostgreSQL username.
    password (str): PostgreSQL password.
    query (str): SQL query to execute.

    Returns:
    pd.DataFrame: DataFrame containing the query results.
    """
    engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        logging.error("Error fetching data with SQLAlchemy: %s", str(e))
    finally:
        engine.dispose()

def fetch_data_by_date(username, password, start_date, end_date):
    """
    Fetch records from elmetadata where the date is between start_date and end_date.

    Parameters:
    username (str): PostgreSQL username.
    password (str): PostgreSQL password.
    start_date (str): Start date in YYYY-MM-DD format.
    end_date (str): End date in YYYY-MM-DD format.

    Returns:
    pd.DataFrame: DataFrame containing the query results.
    """
    engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
    try:
        query = f"""
        SELECT * FROM el_metadata 
        WHERE date BETWEEN '{start_date}' AND '{end_date}';
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        logging.error("Error fetching data: %s", str(e))
    finally:
        engine.dispose()

def get_table_names_and_comments(username, password):
    """
    Connect to PostgreSQL and return a list of dictionaries with table names and comments.

    Parameters:
    username (str): PostgreSQL username.
    password (str): PostgreSQL password.

    Returns:
    list: List of dictionaries containing table names and comments.
    """
    engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
    query = text("""
       SELECT
           c.relname AS table_name,
           obj_description(c.oid) AS table_comment
       FROM pg_class c
       LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
       WHERE c.relkind = 'r'
         AND n.nspname NOT IN ('pg_catalog', 'information_schema');
   """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query)
            rows = result.fetchall()
            tables = [{"table_name": row[0], "table_comment": row[1]} for row in rows]
            return tables
    except SQLAlchemyError as e:
        logging.error("Error querying database: %s", str(e))
    finally:
        engine.dispose()