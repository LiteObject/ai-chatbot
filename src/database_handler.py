"""
Database handling functionality for the AI Chatbot.
Handles PostgreSQL connections and SQL query processing using LlamaIndex.
"""
from typing import List, Optional, Dict, Any, Tuple
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase
from src.utils import validate_connection_string


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

            if self.engine is None:
                st.error("No database connection available")
                return

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

        except SQLAlchemyError as e:
            st.error(f"SQL execution error: {str(e)}")
            return None
        except ValueError as e:
            st.error(
                f"Value error while previewing table {table_name}: {str(e)}")
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

            # Use text() to wrap the query for SQLAlchemy 2.x compatibility
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = list(result.keys())

                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=columns)
                return df

        except SQLAlchemyError as e:
            st.error(f"SQL execution error: {str(e)}")
            return None

    def natural_language_to_sql(self, question: str) -> Tuple[str | None, pd.DataFrame | None] | None:
        """Convert natural language question to SQL and execute."""
        try:
            if not self.sql_database:
                st.error("No database connection")
                return None

            # Enhance the question with context about the database structure
            enhanced_question = self._enhance_question_with_context(question)

            # Create query engine
            query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql_database,
                tables=self.available_tables,
                synthesize_response=True
            )

            # Execute natural language query with enhanced context
            response = query_engine.query(enhanced_question)

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

        except SQLAlchemyError as e:
            st.error(f"Failed to process natural language query: {str(e)}")
            return None

    def _enhance_question_with_context(self, question: str) -> str:
        """Enhance the question with database context to improve SQL generation."""
        # Build context about the database
        context_info = []

        try:
            if self.engine:
                with self.engine.connect() as conn:
                    # Get available categories
                    if 'products' in [t.lower() for t in self.available_tables]:
                        categories_result = conn.execute(
                            text("SELECT DISTINCT category FROM products"))
                        categories = [row[0]
                                      for row in categories_result.fetchall()]
                        context_info.append(
                            f"The products table has these categories: {', '.join(categories)}.")

                        # Check for specific product name matches
                        search_terms = ['lamp', 'light', 'desk', 'chair', 'computer',
                                        'phone', 'coffee', 'mug', 'table', 'monitor', 'keyboard']
                        for term in search_terms:
                            if term.lower() in question.lower():
                                sample_result = conn.execute(
                                    text(
                                        f"SELECT name FROM products WHERE name ILIKE '%{term}%' LIMIT 5")
                                )
                                sample_names = [row[0]
                                                for row in sample_result.fetchall()]
                                if sample_names:
                                    context_info.append(
                                        f"Products with '{term}' in name: {', '.join(sample_names)}.")

        except Exception:
            # If context building fails, continue without context
            pass

        # Create enhanced question with context and explicit instructions
        context_str = " ".join(context_info)

        enhanced_question = f"""{question}

Context: {context_str}

Important: When searching for product types or items, search the 'name' column using ILIKE for partial matches, not the 'category' column. For example:
- To find items with 'desk': SELECT * FROM products WHERE name ILIKE '%desk%'
- To find items with 'lamp': SELECT * FROM products WHERE name ILIKE '%lamp%'
- Categories are broad groups like 'Furniture', 'Electronics', 'Office Supplies'
- Product names contain specific items like 'Desk Lamp', 'Standing Desk', 'Coffee Mug'"""

        return enhanced_question

    def get_database_info(self) -> Dict[str, Any]:
        """Get general database information."""
        if not self.connection_status or self.engine is None:
            return {}

        try:
            with self.engine.connect() as conn:
                # Get database version
                version_result = conn.execute(text("SELECT version()"))
                version_row = version_result.fetchone()
                version = version_row[0] if version_row else "Unknown"

                # Get database size
                size_result = conn.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database()))")
                )
                size_row = size_result.fetchone()
                size = size_row[0] if size_row else "Unknown"

                return {
                    'version': version,
                    'size': size,
                    'total_tables': len(self.available_tables),
                    'connection_status': self.connection_status
                }

        except SQLAlchemyError as e:
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

        except SQLAlchemyError as e:
            st.error(f"Failed to validate table access: {str(e)}")
            return {table: False for table in table_names}

    def get_connection_status(self) -> bool:
        """Get current connection status."""
        return self.connection_status

    def refresh_table_list(self):
        """Refresh the list of available tables."""
        if self.connection_status:
            self._load_table_information()
