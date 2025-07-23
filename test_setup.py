"""
Simple test script to validate the AI Chatbot setup.
Run this script to check if all dependencies are properly installed.
"""
import sys
import os
from pathlib import Path


def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")

    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

    try:
        import llama_index
        print("✅ LlamaIndex imported successfully")
    except ImportError as e:
        print(f"❌ LlamaIndex import failed: {e}")
        return False

    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB import failed: {e}")
        return False

    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False

    try:
        import psycopg2
        print("✅ Psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ Psycopg2 import failed: {e}")
        return False

    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False

    try:
        import docx
        print("✅ Python-docx imported successfully")
    except ImportError as e:
        print(f"❌ Python-docx import failed: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False

    return True


def test_environment():
    """Test environment setup."""
    print("\nTesting environment setup...")

    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")

        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Check for OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("✅ OPENAI_API_KEY found in environment")
        else:
            print("⚠️  OPENAI_API_KEY not found in .env file")
            print("   Please add your OpenAI API key to the .env file")
            return False
    else:
        print("⚠️  .env file not found")
        print("   Please copy .env.example to .env and add your API key")
        return False

    return True


def test_directories():
    """Test if required directories exist."""
    print("\nTesting directory structure...")

    required_dirs = ["uploads", "data", "config", "src"]

    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            return False

    return True


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from config.settings import settings
        print("✅ Settings imported successfully")

        # Test some key settings
        if hasattr(settings, 'OPENAI_API_KEY'):
            print("✅ OpenAI API key setting available")
        else:
            print("❌ OpenAI API key setting missing")
            return False

        if hasattr(settings, 'SUPPORTED_FILE_TYPES'):
            print(f"✅ Supported file types: {settings.SUPPORTED_FILE_TYPES}")
        else:
            print("❌ Supported file types setting missing")
            return False

    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False

    return True


def test_handlers():
    """Test handler classes can be imported."""
    print("\nTesting handler imports...")

    try:
        from src.document_handler import DocumentHandler
        print("✅ DocumentHandler imported successfully")
    except ImportError as e:
        print(f"❌ DocumentHandler import failed: {e}")
        return False

    try:
        from src.database_handler import DatabaseHandler
        print("✅ DatabaseHandler imported successfully")
    except ImportError as e:
        print(f"❌ DatabaseHandler import failed: {e}")
        return False

    try:
        from src.chat_engine import ChatEngine
        print("✅ ChatEngine imported successfully")
    except ImportError as e:
        print(f"❌ ChatEngine import failed: {e}")
        return False

    try:
        from src.utils import format_file_size, get_timestamp
        print("✅ Utility functions imported successfully")
    except ImportError as e:
        print(f"❌ Utility functions import failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🧪 AI Chatbot Setup Validation")
    print("=" * 40)

    tests = [
        ("Package Imports", test_imports),
        ("Environment Setup", test_environment),
        ("Directory Structure", test_directories),
        ("Configuration", test_configuration),
        ("Handler Classes", test_handlers),
    ]

    all_passed = True

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            all_passed = False

    print("\n" + "=" * 40)

    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the application, run:")
        print("streamlit run app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: cp .env.example .env")
        print("3. Add your OpenAI API key to .env file")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
