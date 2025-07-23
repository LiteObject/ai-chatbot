"""
Configuration settings for the AI Chatbot application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings and configuration."""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Database Configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

    # File Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "100"))
    UPLOAD_DIR = "uploads"
    DATA_DIR = "data"

    # Default Model Settings
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    MAX_CONVERSATION_HISTORY = 20

    # Supported File Types
    SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx"]

    @property
    def postgres_connection_string(self):
        """Generate PostgreSQL connection string."""
        if not all([self.POSTGRES_HOST, self.POSTGRES_DATABASE,
                   self.POSTGRES_USERNAME, self.POSTGRES_PASSWORD]):
            return None
        return (f"postgresql://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")


settings = Settings()
