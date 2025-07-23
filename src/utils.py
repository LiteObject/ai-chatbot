"""
Utility functions for the AI Chatbot application.
"""
import os
import hashlib
from datetime import datetime
from typing import List, Optional


def get_file_hash(file_content: bytes) -> str:
    """Generate MD5 hash for file content."""
    return hashlib.md5(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"


def is_valid_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Check if file type is supported."""
    file_extension = filename.split('.')[-1].lower()
    return file_extension in allowed_types


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename


def get_timestamp() -> str:
    """Get current timestamp in readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_directory_exists(directory_path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(directory_path, exist_ok=True)


def clean_old_files(directory: str, max_age_hours: int = 24) -> None:
    """Remove files older than specified hours."""
    if not os.path.exists(directory):
        return

    current_time = datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            age_hours = (current_time - file_time).total_seconds() / 3600
            if age_hours > max_age_hours:
                os.remove(file_path)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_connection_string(connection_string: Optional[str]) -> bool:
    """Validate database connection string format."""
    if not connection_string:
        return False
    return connection_string.startswith(('postgresql://', 'postgres://'))


def format_sql_query(query: str) -> str:
    """Format SQL query for display."""
    # Basic SQL formatting
    keywords = ['SELECT', 'FROM', 'WHERE',
                'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING']
    formatted_query = query
    for keyword in keywords:
        formatted_query = formatted_query.replace(keyword, f'\n{keyword}')
    return formatted_query.strip()
