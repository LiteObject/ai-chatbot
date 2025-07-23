"""
Launch script for AI Chatbot application.
This script provides an easy way to start the Streamlit application.
"""
import subprocess
import sys
import os
from pathlib import Path


def check_environment():
    """Check if the environment is properly set up."""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print(
            "Please create a .env file based on .env.example and add your OpenAI API key.")
        return False

    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False

    return True


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False


def launch_app():
    """Launch the Streamlit application."""
    print("🚀 Launching AI Chatbot...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"❌ Error launching application: {e}")


def main():
    """Main launcher function."""
    print("🤖 AI Chatbot Launcher")
    print("=" * 30)

    # Check environment
    if not check_environment():
        return

    # Ask user if they want to install dependencies
    install_deps = input(
        "Install/update dependencies? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            return

    # Launch the application
    launch_app()


if __name__ == "__main__":
    main()
