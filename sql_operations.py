# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:04:11 2025

@author: Brent
"""
import numpy as np
import pandas as pd
import logging
import sqlite3 as sq
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

MODULES = 'E:/University of Central Florida/UCF_Photovoltaics_GRP - Documents/General/FSEC_PVMCF/module_databases/module-metadata.txt'

main_dir = "E:/University of Central Florida/UCF_Photovoltaics_GRP - Documents/General/FSEC_PVMCF/module_databases"

#main_dir = "C:/Data/"

DATABASE = "C:/Users/Doing/University of Central Florida/UCF_Photovoltaics_GRP - module_databases/FSEC_Database.db"
DATASETS = f"{main_dir}module_databases/"
#database = "C:/Users/Doing/University of Central Florida/UCF_Photovoltaics_GRP - module_databases/FSEC_Database.db"

database = main_dir + "FSEC_Database.db"

database_log = DATASETS + "FSEC_Database_log.log"


def join_module_metadata(dataframe):
    """
    This function can be used to join the Make and Model from module metadata
    reducing the room for human error and keeping everything consistant.

    The only input is a dataframe that has serial numbers as a column

    If the serial numbers match, the make and model will replace exisiting.
    """
    
    query = """
        SELECT "module-id","make","model","serial-number"
        FROM "module-metadata";
            """

# Establish a connection to the SQLite database
    with sq.connect(DATABASE) as conn:
    # Load the query result into a Pandas DataFrame
        modules = pd.read_sql_query(query, conn)
    
    #modules = pd.read_csv(MODULES, sep='\t', usecols=[
         #                 "module-id", "make", "model", "serial-number"])
    dataframe = dataframe.merge(
        modules, how='left', left_on="serial_number", right_on="serial-number")
    try:
        dataframe = dataframe.drop(columns={'make_y', 'model_y'})
        dataframe = dataframe.rename(
            columns={'make_x': 'make', 'model_x': 'model'})
    except:
        print("There were no existing columns named make and model")
    return dataframe

def get_last_date_from_table(table_name='sinton-iv-metadata'):
    """
    Gets the last date of a measurement for a table in the database. Used to 
    determine which folders need to be added for processing.

    Parameters
    ----------
    table_name : String
        Name of the table in the sqlite database to search in

    Returns
    -------
    Integer value of last date in YYYYMMDD format

    """

    with sq.connect(database) as connection:
        cursor = connection.cursor()
    sql = f"SELECT MAX(date) from '{table_name}'"

    try:
        # Execute and commit the SQL
        cursor.execute(sql)
        last_date = pd.read_sql_query(sql, connection)
        connection.close()
    except Exception:
        print("Problem with finding last date.")

    return last_date.loc[0][0]


def deserialize_array(blob, dtype=np.float64):  # Adjust dtype as needed
    """
    Used to deserialize the arrays that are encoded during the storage of 
    IV array data to database. Used to recover voc array, isc array, corrected
    results and interpolated data. 

    Parameters
    ----------
    blob : TYPE
        This blob is the result of serialization that occurs during parsing.
    dtype : TYPE, optional
        DESCRIPTION. The default is np.float64.

    Returns
    -------
    None.

    """
    return np.frombuffer(blob, dtype=dtype)


def create_sqlite_record(table_name, columns, values):
    """
    Inserts a single new entry to the database

    Parameters
    ----------
    table_name : String
        Name of SQL table to insert data to
        Single quotes surround table name in double quotes '"table-name"'
    columns : List
        List of column names for respective table name.
    values : List
        List of values to enter on column names

    """
    with sq.connect(database) as connection:
        cursor = connection.cursor()

    # Generate SQL for inserting data
    columns = ', '.join(columns)
    values = ', '.join(values)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    try:
        # Execute and commit the SQL
        cursor.execute(sql)
        connection.commit()
    except Exception as e:

        print("Problem with SQL command: " + sql)
        return e

    connection.close()
    return "Entry added to " + table_name


def create_sqlite_records_from_dataframe(table_name, dataframe):
    """
    Inserts a new row to the database for every row in dataframe

    Parameters
    ----------
    table_name : String
        Name of SQL table to insert data to
        Single quotes surround table name in double quotes '"table-name"'.
    dataframe : Pandas Dataframe
        Output from metadata parsing modules, used as raw data to construct
        SQL statements.

    """
    with sq.connect(database) as connection:
        cursor = connection.cursor()

    # Generate SQL for inserting data
    for value, row in dataframe.iterrows():
        space = ' ', ''
        columns = ', '.join(
            [f'"{col.replace(space[0],space[1])}"' for col in row.index])
        placeholders = ', '.join([f'"{value}"' for value in row.values])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            # Execute and commit the SQL
            cursor.execute(sql)
            connection.commit()
        except Exception:
            # print(str(row[0]) + " Was not added to " + table_name)
            pass

    connection.close()
    return table_name + " Updated With " + str(len(dataframe)) + " Entries."


# Function to read data from a table
def read_records(database, table_name, select='*', conditions=None):
    """
    Returns the contents of a table as a dataframe.

    Parameters
    ----------
    database: String of path to sqlite database
    table_name : String
        Name of SQL table to insert data to
        Single quotes surround table name in double quotes '"table-name"'.
    select : String, optional
        Choose which columns to select, default is all
    conditions : String, optional
        WHERE, GROUP BY, ect..

    Returns
    -------
    records : Pandas Datafrane
        Results of SQL query in dataframe.

    """
    with sq.connect(database) as connection:
        cursor = connection.cursor()

    # Build SQL query, optional conditions for complex queries
    sql = f"SELECT {select} FROM {table_name}"
    if conditions:
        sql += f" {conditions}"

    # Execute the query and fetch all records
    cursor.execute(sql)
    records = pd.read_sql_query(sql, connection)
    connection.close()
    return records


def create_logger():
    """
    Sets up and configures a logger to keep track of errors and system events.

    Returns
    -------
    logger : Logger Object
        Records events during runtime in log file FSEC_Database_log.log.

    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(database_log)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(file_handler)
    logger.info("Main update database program started.")

    return logger


def blank_insert_to_database(table_name, dataframe):
    """
    This function can be used as a fallback in automated systems to ensure
    data is saved to a table even if something unexpected changes
    with the data. 
    
    There is no schema or failsafes with this method. Best of luck, truely.

    Should only be called during exception handling or one of inserts to the
    database
    """
    with sq.connect(database) as connection:

        dataframe.to_sql(
            f'{table_name}', connection, if_exists='append', index=False,
            dtype={col_name: 'TEXT' for col_name in dataframe})
        
def connect_to_postgres():
    connection = psycopg2.connect(
        database="fsecdatabase", user="brenthom", password="Solar2025", host="34.73.180.136", port=5432)
    cursor = connection.cursor()
    cursor.execute("SELECT * from 'fsecdatabase.module_metadata';")


def create_postgres_records_from_dataframeold(table_name, dataframe):
    
    with psycopg2.connect(
            database="fsecdatabase", user="brenthom", password="Solar2025", host="34.73.180.136", port=5432) as connection:
        cursor = connection.cursor()

    # Generate SQL for inserting data
    for value, row in dataframe.iterrows():
        space = ' ', ''
        columns = ', '.join(
            [f'"{col.replace(space[0],space[1])}"' for col in row.index])
        placeholders = ', '.join([f'"{value}"' for value in row.values])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            # Execute and commit the SQL
            cursor.execute(sql)
            connection.commit()
        except Exception as e:
            print(e)
            print(str(row[0]) + " Was not added to " + table_name)
            pass

    connection.close()
    return table_name + " Updated With " + str(len(dataframe)) + " Entries."


def create_postgres_records_from_dataframe(table_name, dataframe):
    """
    Inserts new rows into the table for every row in the dataframe.
    
    Parameters:
        table_name (str): Name of the SQL table.
        dataframe (pd.DataFrame): DataFrame containing data to insert.
    """
    engine = create_engine("postgresql://brenthom:Solar2025@34.73.180.136:5432/fsecdatabase")
    
    # It is best to use pandas' built-in to_sql with SQLAlchemy engine.
    try:
        dataframe.to_sql(
            name=table_name,   # Replace with your actual table name
            con=engine,
            if_exists='append',       # or 'replace' or 'fail'
            index=False,
            method='multi'            # Optional: allows multi-row insert for efficiency
            )
        #return f"{table_name} updated with {len(dataframe)} entries."
    except Exception as e:
        logging.error("Error inserting dataframe records: %s", e)
        #return e

def read_records_from_postgres(username, password, query):
    """Fetches data using SQLAlchemy and returns a pandas DataFrame."""
    try:
        engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print("Error fetching data with SQLAlchemy:", e)
    finally:
        engine.dispose()
        


def fetch_data_by_date(username, password, start_date, end_date):
    """Fetch records from elmetadata where date_column is between start_date and end_date."""
    try:
        # Establish connection
        engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
        
        # Define SQL query with date filter (Assuming the date column is named 'date_column')
        query = f"""
        SELECT * FROM el_metadata 
        WHERE date BETWEEN '{start_date}' AND '{end_date}';
        """
        
        # Fetch data into DataFrame
        df = pd.read_sql(query, engine)
        
        return df
    except Exception as e:
        print("Error fetching data:", e)
    finally:
        engine.dispose()
        return None
    
    
def get_table_names_and_comments(username, password):
    """
    Connects to a PostgreSQL database and returns a list of dictionaries,
    each containing the table name and its associated comment.
    """
    # Create the SQLAlchemy engine for PostgreSQL.
    engine = create_engine(f"postgresql://{username}:{password}@34.73.180.136:5432/fsecdatabase")
    
    # SQL query to get table names and comments.
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
            
            # Convert each row to a dictionary.
            tables = [
                {"table_name": row[0], "table_comment": row[1]}
                for row in rows
            ]
            return tables
    except SQLAlchemyError as e:
        print("Error querying database:", e)
    finally:
        engine.dispose()