"""
Launch script for AI Chatbot application.
This script provides an easy way to start the Streamlit application with Docker containers.
"""
import subprocess
import sys
import os
import time


def check_docker():
    """Check if Docker is installed and running."""
    print("🐳 Checking Docker installation...")
    try:
        # Check if Docker is installed
        subprocess.run(["docker", "--version"], check=True,
                       capture_output=True, text=True)

        # Check if Docker is running
        subprocess.run(["docker", "info"], check=True,
                       capture_output=True, text=True)

        print("✅ Docker is installed and running!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not installed or not running!")
        print("Please install Docker and make sure it's running.")
        return False


def check_containers_running():
    """Check if required containers are already running."""
    try:
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}"],
                                capture_output=True, text=True, check=True)
        running_containers = result.stdout

        postgres_running = "ai-chatbot-postgres" in running_containers
        chromadb_running = "ai-chatbot-chromadb" in running_containers

        return postgres_running, chromadb_running
    except subprocess.CalledProcessError:
        return False, False


def start_docker_containers():
    """Start Docker containers using docker-compose."""
    print("🐳 Starting Docker containers...")

    if not os.path.exists("docker-compose.yml"):
        print("❌ docker-compose.yml not found!")
        return False

    try:
        # Start containers in detached mode
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Docker containers started successfully!")

        # Wait for containers to be ready
        print("⏳ Waiting for containers to be ready...")
        time.sleep(5)

        # Check PostgreSQL health
        max_retries = 30
        for i in range(max_retries):
            try:
                result = subprocess.run([
                    "docker", "exec", "ai-chatbot-postgres",
                    "pg_isready", "-U", "chatbot_user", "-d", "ai_chatbot"
                ], capture_output=True, text=True, timeout=10, check=False)

                if result.returncode == 0:
                    print("✅ PostgreSQL is ready!")
                    break

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

            if i < max_retries - 1:
                print(f"⏳ Waiting for PostgreSQL... ({i+1}/{max_retries})")
                time.sleep(2)
        else:
            print("⚠️ PostgreSQL might not be fully ready, but continuing...")

        # Check ChromaDB health
        for i in range(10):
            try:
                result = subprocess.run([
                    "docker", "exec", "ai-chatbot-chromadb",
                    "curl", "-f", "http://localhost:8000/api/v1/heartbeat"
                ], capture_output=True, text=True, timeout=10, check=False)

                if result.returncode == 0:
                    print("✅ ChromaDB is ready!")
                    break

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

            if i < 9:
                print(f"⏳ Waiting for ChromaDB... ({i+1}/10)")
                time.sleep(2)
        else:
            print("✅ ChromaDB containers started (health check skipped)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker containers: {e}")
        return False
    except FileNotFoundError:
        print("❌ docker-compose command not found!")
        print("Please install Docker Compose.")
        return False


def stop_docker_containers():
    """Stop Docker containers."""
    print("🛑 Stopping Docker containers...")
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ Docker containers stopped successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop Docker containers: {e}")
        return False


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
        subprocess.run([sys.executable, "-m", "streamlit",
                       "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit failed to launch: {e}")
    except OSError as e:
        print(f"❌ OS error launching application: {e}")


def main():
    """Main launcher function."""
    print("🤖 AI Chatbot Launcher")
    print("=" * 30)

    # Check environment
    if not check_environment():
        return

    # Check Docker
    use_docker = input(
        "Start Docker containers (PostgreSQL & ChromaDB)? (y/n): ").lower().strip()

    if use_docker in ['y', 'yes']:
        if not check_docker():
            print("⚠️ Continuing without Docker containers...")
        else:
            # Check if containers are already running
            postgres_running, chromadb_running = check_containers_running()

            if postgres_running and chromadb_running:
                print("✅ Docker containers are already running!")
            elif postgres_running or chromadb_running:
                print("⚠️ Some containers are running. Starting missing containers...")
                if not start_docker_containers():
                    print("⚠️ Continuing anyway...")
            else:
                if not start_docker_containers():
                    print("⚠️ Continuing without Docker containers...")

    # Ask user if they want to install dependencies
    install_deps = input(
        "Install/update dependencies? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            return

    try:
        # Launch the application
        launch_app()
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")

        # Ask if user wants to stop containers
        if use_docker in ['y', 'yes']:
            stop_containers = input(
                "Stop Docker containers? (y/n): ").lower().strip()
            if stop_containers in ['y', 'yes']:
                stop_docker_containers()


if __name__ == "__main__":
    main()
