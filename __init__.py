# -*- coding: utf-8 -*-
"""
Database operations package.
"""

from .sqlite_operations import (
    join_module_metadata,
    get_last_date_from_table,
    create_sqlite_record,
    create_sqlite_records_from_dataframe,
    read_records,
    blank_insert_to_database,
)

from .postgres_operations import (
    connect_to_postgres,
    create_postgres_records_from_dataframe,
    read_records_from_postgres,
    fetch_data_by_date,
    get_table_names_and_comments,
)

from .utils import (
    deserialize_array,
    create_logger,
)