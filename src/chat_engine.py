"""
Chat engine for the AI Chatbot application.
Handles message routing, conversation management, and response generation.
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from llama_index.llms.openai import OpenAI
except ImportError as e:
    st.error(f"Required chat libraries not installed: {e}")

from config.settings import settings
from src.document_handler import DocumentHandler
from src.database_handler import DatabaseHandler


class ChatEngine:
    """Manages chat interactions and response routing."""

    def __init__(self, document_handler: DocumentHandler, database_handler: DatabaseHandler):
        """Initialize the chat engine."""
        self.document_handler = document_handler
        self.database_handler = database_handler
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize chat-related session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        if "temperature" not in st.session_state:
            st.session_state.temperature = settings.DEFAULT_TEMPERATURE

        if "model" not in st.session_state:
            st.session_state.model = settings.DEFAULT_MODEL

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        st.session_state.messages.append(message)

        # Maintain conversation history limit
        if len(st.session_state.messages) > settings.MAX_CONVERSATION_HISTORY * 2:
            # Remove oldest messages (keep pairs)
            st.session_state.messages = st.session_state.messages[-settings.MAX_CONVERSATION_HISTORY * 2:]

    def classify_query(self, user_message: str) -> str:
        """Classify the user query to determine routing."""
        user_message_lower = user_message.lower()

        # Database-related keywords
        db_keywords = [
            "database", "table", "sql", "query", "select", "from", "where",
            "join", "count", "sum", "average", "data", "records", "rows",
            "columns", "schema", "postgres", "postgresql"
        ]

        # Document-related keywords
        doc_keywords = [
            "document", "file", "pdf", "text", "uploaded", "content",
            "what does the document say", "in the file", "according to"
        ]

        # Check for database-related query
        if any(keyword in user_message_lower for keyword in db_keywords):
            if self.database_handler.get_connection_status():
                return "database"

        # Check for document-related query
        if any(keyword in user_message_lower for keyword in doc_keywords):
            if self.document_handler.get_uploaded_files():
                return "document"

        # Check if we have uploaded documents and the query might be about them
        if self.document_handler.get_uploaded_files() and len(user_message.split()) > 3:
            return "document"

        # Default to general chat
        return "general"

    def process_document_query(self, user_message: str) -> Dict[str, Any]:
        """Process query against uploaded documents."""
        try:
            query_engine = self.document_handler.get_query_engine()

            if query_engine is None:
                return {
                    "response": "No documents are currently uploaded. Please upload some documents first.",
                    "sources": [],
                    "type": "error"
                }

            # Query the documents
            response = query_engine.query(user_message)

            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                for source_node in response.source_nodes:
                    if hasattr(source_node, 'metadata'):
                        sources.append({
                            "file_name": source_node.metadata.get("file_name", "Unknown"),
                            "score": getattr(source_node, 'score', 0.0)
                        })

            return {
                "response": str(response),
                "sources": sources,
                "type": "document",
                "query": user_message
            }

        except Exception as e:
            return {
                "response": f"Error processing document query: {str(e)}",
                "sources": [],
                "type": "error"
            }

    def process_database_query(self, user_message: str) -> Dict[str, Any]:
        """Process query against connected database."""
        try:
            if not self.database_handler.get_connection_status():
                return {
                    "response": "No database connection. Please connect to a database first.",
                    "sql_query": None,
                    "data": None,
                    "type": "error"
                }

            # Convert natural language to SQL and execute
            result = self.database_handler.natural_language_to_sql(
                user_message)

            if result is None:
                return {
                    "response": "Failed to process the database query. Please try rephrasing your question.",
                    "sql_query": None,
                    "data": None,
                    "type": "error"
                }

            sql_query, data = result

            if data is None or data.empty:
                return {
                    "response": "The query executed successfully but returned no results.",
                    "sql_query": sql_query,
                    "data": None,
                    "type": "database"
                }

            # Generate natural language response
            response_text = self._generate_database_response(
                user_message, data, sql_query)

            return {
                "response": response_text,
                "sql_query": sql_query,
                "data": data,
                "type": "database",
                "query": user_message
            }

        except Exception as e:
            return {
                "response": f"Error processing database query: {str(e)}",
                "sql_query": None,
                "data": None,
                "type": "error"
            }

    def process_general_query(self, user_message: str) -> Dict[str, Any]:
        """Process general chat query using OpenAI."""
        try:
            # Create OpenAI client
            llm = OpenAI(
                model=st.session_state.model,
                temperature=st.session_state.temperature,
                api_key=settings.OPENAI_API_KEY
            )

            # Prepare conversation context
            messages = []

            # Add system message
            system_message = """You are a helpful AI assistant. You can help users with general questions, 
            but you specialize in helping them work with documents and databases. If users ask about 
            documents or databases, suggest they upload documents or connect to a database first."""

            messages.append({"role": "system", "content": system_message})

            # Add recent conversation history
            # Last 10 messages
            recent_messages = st.session_state.messages[-10:]
            for msg in recent_messages:
                if msg["role"] in ["user", "assistant"]:
                    messages.append(
                        {"role": msg["role"], "content": msg["content"]})

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = llm.complete(user_message)

            return {
                "response": str(response),
                "type": "general",
                "query": user_message
            }

        except Exception as e:
            return {
                "response": f"Error processing general query: {str(e)}",
                "type": "error"
            }

    def _generate_database_response(self, question: str, data, sql_query: str) -> str:
        """Generate natural language response for database query results."""
        try:
            if data is None or data.empty:
                return "The query executed successfully but returned no results."

            # Basic response generation
            num_rows = len(data)
            num_cols = len(data.columns)

            response_parts = []

            # Add basic info about results
            if num_rows == 1:
                response_parts.append(
                    f"I found 1 record with {num_cols} columns.")
            else:
                response_parts.append(
                    f"I found {num_rows} records with {num_cols} columns.")

            # Add sample of data if not too large
            if num_rows <= 10 and num_cols <= 5:
                response_parts.append("\nHere are the results:")
                # This will be displayed as a table in the UI
            elif num_rows > 10:
                response_parts.append(
                    f"\nShowing first 10 out of {num_rows} records:")

            return " ".join(response_parts)

        except Exception as e:
            return f"Generated results successfully. Query returned {len(data) if data is not None else 0} records."

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Main method to process user messages."""
        if not user_message.strip():
            return {
                "response": "Please enter a message.",
                "type": "error"
            }

        # Add user message to history
        self.add_message("user", user_message)

        # Classify and route the query
        query_type = self.classify_query(user_message)

        if query_type == "document":
            result = self.process_document_query(user_message)
        elif query_type == "database":
            result = self.process_database_query(user_message)
        else:
            result = self.process_general_query(user_message)

        # Add assistant response to history
        self.add_message("assistant", result["response"], result)

        return result

    def clear_conversation(self):
        """Clear the conversation history."""
        st.session_state.messages = []
        st.session_state.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history."""
        return st.session_state.messages

    def export_conversation(self) -> str:
        """Export conversation history as text."""
        if not st.session_state.messages:
            return "No conversation to export."

        export_text = f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += "=" * 50 + "\n\n"

        for message in st.session_state.messages:
            timestamp = message.get("timestamp", "")
            role = message["role"].title()
            content = message["content"]

            export_text += f"[{timestamp}] {role}:\n{content}\n\n"

        return export_text
