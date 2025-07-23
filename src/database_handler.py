"""
Database handling functionality for the AI Chatbot.
Handles PostgreSQL connections and SQL query processing using LlamaIndex.
"""
import streamlit as st
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd

try:
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.exc import SQLAlchemyError
    from llama_index.core.query_engine import NLSQLTableQueryEngine
    from llama_index.core import SQLDatabase
    import psycopg2
except ImportError as e:
    st.error(f"Required database libraries not installed: {e}")

from config.settings import settings
from src.utils import validate_connection_string, format_sql_query


class DatabaseHandler:
    """Handles database connections and query processing."""

    def __init__(self):
        """Initialize the database handler."""
        self.engine = None
        self.sql_database = None
        self.connection_status = False
        self.available_tables = []
        self.table_schemas = {}

    def test_connection(self, connection_string: str) -> Tuple[bool, str]:
        """Test database connection."""
        try:
            if not validate_connection_string(connection_string):
                return False, "Invalid connection string format"

            # Test basic connection
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return True, "Connection successful"

        except SQLAlchemyError as e:
            return False, f"Database connection error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def connect_to_database(self, connection_string: str) -> bool:
        """Connect to PostgreSQL database."""
        try:
            if not validate_connection_string(connection_string):
                st.error("Invalid connection string format")
                return False

            # Create SQLAlchemy engine
            self.engine = create_engine(connection_string)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # Create LlamaIndex SQL database
            self.sql_database = SQLDatabase(self.engine)

            # Load table information
            self._load_table_information()

            self.connection_status = True
            st.session_state.db_connected = True
            st.session_state.db_connection_string = connection_string

            return True

        except SQLAlchemyError as e:
            st.error(f"Database connection error: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Failed to connect to database: {str(e)}")
            return False

    def disconnect_from_database(self):
        """Disconnect from database."""
        try:
            if self.engine:
                self.engine.dispose()

            self.engine = None
            self.sql_database = None
            self.connection_status = False
            self.available_tables = []
            self.table_schemas = {}

            st.session_state.db_connected = False
            if "db_connection_string" in st.session_state:
                del st.session_state.db_connection_string

        except Exception as e:
            st.error(f"Error disconnecting from database: {str(e)}")

    def _load_table_information(self):
        """Load table and schema information."""
        try:
            inspector = inspect(self.engine)

            # Get all schemas
            schemas = inspector.get_schema_names()

            self.available_tables = []
            self.table_schemas = {}

            for schema in schemas:
                # Skip system schemas
                if schema in ['information_schema', 'pg_catalog', 'pg_toast']:
                    continue

                tables = inspector.get_table_names(schema=schema)

                for table in tables:
                    full_table_name = f"{schema}.{table}" if schema != 'public' else table
                    self.available_tables.append(full_table_name)

                    # Get column information
                    columns = inspector.get_columns(table, schema=schema)
                    self.table_schemas[full_table_name] = {
                        'schema': schema,
                        'table': table,
                        'columns': columns
                    }

            self.available_tables.sort()

        except Exception as e:
            st.error(f"Failed to load table information: {str(e)}")

    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        return self.available_tables

    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema information for a specific table."""
        return self.table_schemas.get(table_name)

    def get_table_preview(self, table_name: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """Get a preview of table data."""
        try:
            if not self.engine:
                return None

            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = pd.read_sql(query, self.engine)
            return df

        except Exception as e:
            st.error(f"Failed to preview table {table_name}: {str(e)}")
            return None

    def execute_sql_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results."""
        try:
            if not self.engine:
                st.error("No database connection")
                return None

            # Basic SQL injection protection
            query = query.strip()
            if not query.upper().startswith('SELECT'):
                st.error("Only SELECT queries are allowed")
                return None

            df = pd.read_sql(query, self.engine)
            return df

        except SQLAlchemyError as e:
            st.error(f"SQL execution error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Failed to execute query: {str(e)}")
            return None

    def natural_language_to_sql(self, question: str) -> Optional[Tuple[str, pd.DataFrame]]:
        """Convert natural language question to SQL and execute."""
        try:
            if not self.sql_database:
                st.error("No database connection")
                return None

            # Create query engine
            query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql_database,
                tables=self.available_tables
            )

            # Execute natural language query
            response = query_engine.query(question)

            # Extract SQL query from response metadata
            sql_query = getattr(response, 'metadata', {}).get(
                'sql_query', 'Query not available')

            # Execute the SQL query to get DataFrame
            if sql_query and sql_query != 'Query not available':
                df = self.execute_sql_query(sql_query)
                return sql_query, df
            else:
                # If we can't extract the SQL, return the response as text
                return None, pd.DataFrame({'Response': [str(response)]})

        except Exception as e:
            st.error(f"Failed to process natural language query: {str(e)}")
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """Get general database information."""
        if not self.connection_status:
            return {}

        try:
            with self.engine.connect() as conn:
                # Get database version
                version_result = conn.execute(text("SELECT version()"))
                version = version_result.fetchone()[0]

                # Get database size
                size_result = conn.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database()))")
                )
                size = size_result.fetchone()[0]

                return {
                    'version': version,
                    'size': size,
                    'total_tables': len(self.available_tables),
                    'connection_status': self.connection_status
                }

        except Exception as e:
            st.error(f"Failed to get database info: {str(e)}")
            return {}

    def validate_table_access(self, table_names: List[str]) -> Dict[str, bool]:
        """Validate access to specified tables."""
        access_status = {}

        if not self.engine:
            return {table: False for table in table_names}

        try:
            with self.engine.connect() as conn:
                for table in table_names:
                    try:
                        conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                        access_status[table] = True
                    except:
                        access_status[table] = False

            return access_status

        except Exception as e:
            st.error(f"Failed to validate table access: {str(e)}")
            return {table: False for table in table_names}

    def get_connection_status(self) -> bool:
        """Get current connection status."""
        return self.connection_status

    def refresh_table_list(self):
        """Refresh the list of available tables."""
        if self.connection_status:
            self._load_table_information()
