# FSEC Database Operations Package

## Overview
This package provides utilities for interacting with PostgreSQL and SQLite databases, including data insertion, querying, schema inspection, and metadata extraction. It also includes unit tests and helper functions for logging, file handling, and data parsing.

---

## File Descriptions

### Core Modules
- **`postgres_operations.py`**  
  Contains the `PostgresDB` class for PostgreSQL operations:
  - Connect to a PostgreSQL database.
  - Insert data from pandas DataFrames.
  - Query records by date, fetch table schemas, and retrieve table metadata.
  - Error handling and logging.

- **`sqlite_operations.py`**  
  Contains the `SQLiteDB` class for SQLite operations:
  - Read/write data to SQLite tables.
  - Insert records via DataFrames or single entries.
  - Join module metadata and retrieve the latest measurement dates.

### Testing Modules
- **`test_postgres_operations.py`**  
  Unit tests for `PostgresDB` methods (e.g., DataFrame insertion, schema queries).

- **`test_sqlite_operations.py`**  
  Unit tests for `SQLiteDB` methods (e.g., record creation, metadata joining).

### Utilities
- **`utils.py`**  
  Helper functions for:
  - Logging configuration.
  - File selection GUI.
  - Metadata extraction from filenames.
  - Array deserialization and folder traversal.

---

## Installation
Dependencies:
```bash
pip install pandas sqlalchemy numpy tkinter
