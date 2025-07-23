"""
Docker Database Management Script for AI Chatbot
Provides easy commands to manage the PostgreSQL database using Docker.
"""
import subprocess
import time
import os


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True,
                                check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_docker():
    """Check if Docker is installed and running."""
    print("🐳 Checking Docker installation...")
    try:
        subprocess.run(["docker", "--version"],
                       check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"],
                       check=True, capture_output=True)
        print("✅ Docker and Docker Compose are available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose not found!")
        print("Please install Docker Desktop from https://www.docker.com/products/docker-desktop")
        return False


def start_database():
    """Start the PostgreSQL database using Docker Compose."""
    if not check_docker():
        return False

    print("🚀 Starting PostgreSQL database with Docker...")

    # Start the database
    if not run_command("docker-compose up -d postgres", "Starting PostgreSQL container"):
        return False

    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "pg_isready",
                    "-U", "chatbot_user", "-d", "ai_chatbot"],
                check=True, capture_output=True
            )
            print("✅ Database is ready!")
            break
        except subprocess.CalledProcessError:
            if attempt < max_attempts - 1:
                print(
                    f"⏳ Attempt {attempt + 1}/{max_attempts} - Database not ready yet, waiting...")
                time.sleep(2)
            else:
                print("❌ Database failed to start within expected time")
                return False

    print("\n📊 Database Information:")
    print("Host: localhost")
    print("Port: 5432")
    print("Database: ai_chatbot")
    print("Username: chatbot_user")
    print("Password: chatbot_password")

    return True


def start_with_pgadmin():
    """Start PostgreSQL database with pgAdmin interface."""
    if not check_docker():
        return False

    print("🚀 Starting PostgreSQL database with pgAdmin...")

    if not run_command("docker-compose up -d", "Starting PostgreSQL and pgAdmin containers"):
        return False

    print("\n📊 Services Information:")
    print("PostgreSQL:")
    print("  Host: localhost")
    print("  Port: 5432")
    print("  Database: ai_chatbot")
    print("  Username: chatbot_user")
    print("  Password: chatbot_password")
    print("\npgAdmin:")
    print("  URL: http://localhost:8181")
    print("  Email: admin@chatbot.local")
    print("  Password: admin")

    return True


def stop_database():
    """Stop the PostgreSQL database containers."""
    return run_command("docker-compose down", "Stopping database containers")


def restart_database():
    """Restart the PostgreSQL database containers."""
    print("🔄 Restarting database...")
    stop_database()
    time.sleep(2)
    return start_database()


def show_status():
    """Show the status of database containers."""
    print("📊 Container Status:")
    run_command("docker-compose ps", "Checking container status")


def show_logs():
    """Show logs from the PostgreSQL container."""
    print("📋 PostgreSQL Logs:")
    run_command("docker-compose logs postgres", "Fetching PostgreSQL logs")


def reset_database():
    """Reset the database by recreating containers and volumes."""
    print("⚠️  This will delete all data in the database!")
    confirm = input(
        "Are you sure you want to reset the database? (yes/no): ").lower().strip()

    if confirm == 'yes':
        print("🗑️  Resetting database...")
        run_command("docker-compose down -v",
                    "Stopping containers and removing volumes")
        time.sleep(2)
        return start_database()
    else:
        print("❌ Database reset cancelled")
        return False


def setup_env_file():
    """Set up the environment file for Docker configuration."""
    if os.path.exists('.env'):
        overwrite = input(
            "📄 .env file already exists. Overwrite with Docker configuration? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("❌ Environment setup cancelled")
            return False

    try:
        # Copy Docker environment template
        with open('.env.docker', 'r') as source:
            content = source.read()

        with open('.env', 'w') as target:
            target.write(content)

        print("✅ Environment file configured for Docker!")
        print("📝 Please edit .env and add your OpenAI API key")
        return True
    except FileNotFoundError:
        print("❌ .env.docker template not found!")
        return False


def main():
    """Main menu for database management."""
    while True:
        print("\n🤖 AI Chatbot - Docker Database Manager")
        print("=" * 45)
        print("1. 🚀 Start PostgreSQL database")
        print("2. 🖥️  Start with pgAdmin interface")
        print("3. 🛑 Stop database")
        print("4. 🔄 Restart database")
        print("5. 📊 Show container status")
        print("6. 📋 Show database logs")
        print("7. 🗑️  Reset database (delete all data)")
        print("8. 📄 Setup .env file for Docker")
        print("9. ❌ Exit")

        choice = input("\nSelect an option (1-9): ").strip()

        if choice == '1':
            start_database()
        elif choice == '2':
            start_with_pgadmin()
        elif choice == '3':
            stop_database()
        elif choice == '4':
            restart_database()
        elif choice == '5':
            show_status()
        elif choice == '6':
            show_logs()
        elif choice == '7':
            reset_database()
        elif choice == '8':
            setup_env_file()
        elif choice == '9':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-9.")


if __name__ == "__main__":
    main()
