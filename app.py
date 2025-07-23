"""
AI Chatbot Application using Streamlit, OpenAI, and LlamaIndex
Main application file with user interface and interaction handling.
"""
import streamlit as st
import os
import pandas as pd
from typing import Dict, Any
import time

# Import custom modules
from config.settings import settings
from src.document_handler import DocumentHandler
from src.database_handler import DatabaseHandler
from src.chat_engine import ChatEngine
from src.utils import format_file_size, get_timestamp


def initialize_app():
    """Initialize the Streamlit application."""
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .file-upload-area {
        border: 2px dashed #cccccc;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_handlers():
    """Initialize application handlers."""
    if "document_handler" not in st.session_state:
        st.session_state.document_handler = DocumentHandler()

    if "database_handler" not in st.session_state:
        st.session_state.database_handler = DatabaseHandler()

    if "chat_engine" not in st.session_state:
        st.session_state.chat_engine = ChatEngine(
            st.session_state.document_handler,
            st.session_state.database_handler
        )


def render_sidebar():
    """Render the application sidebar."""
    st.sidebar.title("🤖 AI Chatbot")
    st.sidebar.markdown("---")

    # File Upload Section
    render_file_upload_section()

    st.sidebar.markdown("---")

    # Database Connection Section
    render_database_section()

    st.sidebar.markdown("---")

    # Settings Section
    render_settings_section()


def render_file_upload_section():
    """Render the file upload section in sidebar."""
    st.sidebar.subheader("📁 Document Upload")

    # File upload widget
    uploaded_files = st.sidebar.file_uploader(
        "Upload documents",
        type=settings.SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help=f"Supported formats: {', '.join([t.upper() for t in settings.SUPPORTED_FILE_TYPES])}\nMax size: {settings.MAX_FILE_SIZE_MB}MB per file"
    )

    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            process_uploaded_file(uploaded_file)

    # Display uploaded files
    display_uploaded_files()

    # Clear all documents button
    if st.sidebar.button("🗑️ Clear All Documents", type="secondary"):
        if st.session_state.document_handler.clear_all_documents():
            st.sidebar.success("All documents cleared!")
            st.rerun()


def process_uploaded_file(uploaded_file):
    """Process a single uploaded file."""
    document_handler = st.session_state.document_handler

    # Check if file is already uploaded
    file_content = uploaded_file.read()
    uploaded_file.seek(0)  # Reset file pointer

    file_hash = document_handler.get_file_hash(file_content)
    uploaded_files = document_handler.get_uploaded_files()

    if file_hash in uploaded_files:
        st.sidebar.info(f"File '{uploaded_file.name}' already uploaded")
        return

    # Validate file
    validation_result = document_handler.validate_file(uploaded_file)

    if not validation_result["is_valid"]:
        st.sidebar.error(validation_result["error_message"])
        return

    # Show upload progress
    with st.sidebar:
        with st.spinner(f"Uploading {uploaded_file.name}..."):
            # Save file
            file_path = document_handler.save_uploaded_file(uploaded_file)

            if file_path:
                # Process document
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    success = document_handler.process_document(
                        file_path, file_hash)

                    if success:
                        st.success(
                            f"✅ {uploaded_file.name} uploaded and processed!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to process {uploaded_file.name}")


def display_uploaded_files():
    """Display list of uploaded files with delete options."""
    uploaded_files = st.session_state.document_handler.get_uploaded_files()

    if not uploaded_files:
        st.sidebar.info("No documents uploaded yet")
        return

    st.sidebar.subheader(f"📄 Uploaded Files ({len(uploaded_files)})")

    for file_hash, file_metadata in uploaded_files.items():
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([3, 1])

            with col1:
                st.write(f"**{file_metadata['original_name']}**")
                st.caption(f"Size: {format_file_size(file_metadata['size'])}")
                st.caption(f"Uploaded: {file_metadata['upload_time']}")

                # Processing status
                if file_metadata.get('processed', False):
                    st.caption("✅ Processed")
                else:
                    st.caption("⏳ Processing...")

            with col2:
                if st.button("🗑️", key=f"delete_{file_hash}", help="Delete file"):
                    if st.session_state.document_handler.delete_document(file_hash):
                        st.success("File deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete file")


def render_database_section():
    """Render the database connection section in sidebar."""
    st.sidebar.subheader("🗄️ Database Connection")

    database_handler = st.session_state.database_handler

    # Connection status
    if database_handler.get_connection_status():
        st.sidebar.success("✅ Connected to database")

        # Database info
        db_info = database_handler.get_database_info()
        if db_info:
            st.sidebar.info(f"Tables: {db_info.get('total_tables', 0)}")

        # Disconnect button
        if st.sidebar.button("Disconnect", type="secondary"):
            database_handler.disconnect_from_database()
            st.sidebar.success("Disconnected from database")
            st.rerun()

        # Table browser
        render_table_browser()

    else:
        render_database_connection_form()


def render_database_connection_form():
    """Render database connection form."""
    with st.sidebar.form("db_connection_form"):
        st.write("**Connection Details**")

        host = st.text_input("Host", value=settings.POSTGRES_HOST)
        port = st.text_input("Port", value=str(settings.POSTGRES_PORT))
        database = st.text_input(
            "Database", value=settings.POSTGRES_DATABASE or "")
        username = st.text_input(
            "Username", value=settings.POSTGRES_USERNAME or "")
        password = st.text_input("Password", type="password")

        # Test connection button
        col1, col2 = st.columns(2)

        with col1:
            test_clicked = st.form_submit_button("Test", type="secondary")

        with col2:
            connect_clicked = st.form_submit_button("Connect", type="primary")

        if test_clicked or connect_clicked:
            if not all([host, port, database, username, password]):
                st.error("Please fill in all connection details")
            else:
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

                if test_clicked:
                    success, message = st.session_state.database_handler.test_connection(
                        connection_string)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                elif connect_clicked:
                    with st.spinner("Connecting to database..."):
                        if st.session_state.database_handler.connect_to_database(connection_string):
                            st.success("Connected successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to connect to database")


def render_table_browser():
    """Render table browser for connected database."""
    database_handler = st.session_state.database_handler
    available_tables = database_handler.get_available_tables()

    if not available_tables:
        st.sidebar.info("No tables found in database")
        return

    st.sidebar.subheader(f"📊 Tables ({len(available_tables)})")

    # Table selection
    selected_table = st.sidebar.selectbox(
        "Select table to preview",
        options=[""] + available_tables,
        key="selected_table"
    )

    if selected_table:
        # Show table schema
        schema_info = database_handler.get_table_schema(selected_table)
        if schema_info:
            st.sidebar.write(f"**{selected_table}**")
            st.sidebar.caption(f"Schema: {schema_info['schema']}")

            # Show columns
            with st.sidebar.expander("Columns"):
                for col in schema_info['columns']:
                    st.write(f"• {col['name']} ({col['type']})")

        # Preview button
        if st.sidebar.button("Preview Data", key=f"preview_{selected_table}"):
            preview_data = database_handler.get_table_preview(selected_table)
            if preview_data is not None:
                st.session_state.preview_data = preview_data
                st.session_state.preview_table = selected_table


def render_settings_section():
    """Render settings section in sidebar."""
    st.sidebar.subheader("⚙️ Settings")

    # Temperature setting
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.get(
            'temperature', settings.DEFAULT_TEMPERATURE),
        step=0.1,
        help="Controls randomness in responses. Lower values are more focused and deterministic."
    )
    st.session_state.temperature = temperature

    # Model selection
    model = st.sidebar.selectbox(
        "Model",
        options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0 if st.session_state.get(
            'model', settings.DEFAULT_MODEL) == "gpt-3.5-turbo" else 1,
        help="Select the OpenAI model to use for responses"
    )
    st.session_state.model = model

    # Clear chat button
    if st.sidebar.button("🧹 Clear Chat History", type="secondary"):
        st.session_state.chat_engine.clear_conversation()
        st.sidebar.success("Chat history cleared!")
        st.rerun()


def render_main_content():
    """Render the main chat interface."""
    st.title("🤖 AI Chatbot")
    st.markdown(
        "Ask me anything about your documents, database, or general questions!")

    # Show preview data if available
    if hasattr(st.session_state, 'preview_data') and st.session_state.preview_data is not None:
        st.subheader(f"📊 Table Preview: {st.session_state.preview_table}")
        st.dataframe(st.session_state.preview_data, use_container_width=True)
        st.markdown("---")

        # Clear preview button
        if st.button("Clear Preview"):
            del st.session_state.preview_data
            del st.session_state.preview_table
            st.rerun()

    # Chat interface
    render_chat_interface()


def render_chat_interface():
    """Render the chat interface."""
    # Display chat history
    messages = st.session_state.chat_engine.get_conversation_history()

    # Chat container
    chat_container = st.container()

    with chat_container:
        for message in messages:
            render_chat_message(message)

    # Chat input
    render_chat_input()


def render_chat_message(message: Dict[str, Any]):
    """Render a single chat message."""
    role = message["role"]
    content = message["content"]
    metadata = message.get("metadata", {})

    if role == "user":
        with st.chat_message("user"):
            st.write(content)

    elif role == "assistant":
        with st.chat_message("assistant"):
            st.write(content)

            # Show additional information based on message type
            msg_type = metadata.get("type", "general")

            if msg_type == "document" and metadata.get("sources"):
                render_document_sources(metadata["sources"])

            elif msg_type == "database":
                render_database_results(metadata)


def render_document_sources(sources):
    """Render document sources for a response."""
    if not sources:
        return

    with st.expander("📚 Sources"):
        for i, source in enumerate(sources, 1):
            st.write(
                f"{i}. **{source['file_name']}** (Score: {source['score']:.2f})")


def render_database_results(metadata):
    """Render database query results."""
    sql_query = metadata.get("sql_query")
    data = metadata.get("data")

    if sql_query:
        with st.expander("🔍 SQL Query"):
            st.code(sql_query, language="sql")

    if data is not None and not data.empty:
        with st.expander("📊 Query Results"):
            st.dataframe(data, use_container_width=True)

            # Download button for results
            csv = data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"query_results_{get_timestamp().replace(':', '-')}.csv",
                mime="text/csv"
            )


def render_chat_input():
    """Render chat input area."""
    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Process the message
        with st.spinner("Thinking..."):
            result = st.session_state.chat_engine.process_message(user_input)

        # Rerun to show the new messages
        st.rerun()


def main():
    """Main application function."""
    # Check for OpenAI API key
    if not settings.OPENAI_API_KEY:
        st.error(
            "🔑 OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        st.info("Create a `.env` file in the project root with your OpenAI API key:\n```\nOPENAI_API_KEY=your_api_key_here\n```")
        st.stop()

    # Initialize application
    initialize_app()
    initialize_handlers()

    # Render UI
    render_sidebar()
    render_main_content()

    # Show instructions for new users
    if not st.session_state.chat_engine.get_conversation_history():
        with st.container():
            st.info("""
            👋 **Welcome to AI Chatbot!**
            
            **Getting Started:**
            - 📁 Upload documents (PDF, TXT, DOCX) in the sidebar to ask questions about them
            - 🗄️ Connect to a PostgreSQL database to query your data with natural language
            - 🎛️ Adjust temperature and model settings in the sidebar
            - 💬 Start chatting by typing a message below
            
            **Example Questions:**
            - "What is the main topic of the uploaded document?"
            - "Show me all customers from the database"
            - "How many orders were placed last month?"
            """)


if __name__ == "__main__":
    main()
