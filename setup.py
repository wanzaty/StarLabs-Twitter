"""
Setup and installation script for StarLabs Twitter Bot v3.0
Replaces batch files with Python functionality
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_pip_executable():
    """Get the correct pip executable path"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")


def get_python_executable():
    """Get the correct Python executable path"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")


def install_requirements():
    """Install required packages with enhanced dependencies"""
    pip_exe = get_pip_executable()
    
    if not pip_exe.exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    requirements = [
        # Core dependencies
        "aiogram==3.19.0",           # Telegram bot integration
        "aiohttp==3.11.16",          # Async HTTP client
        "curl_cffi==0.10.0",         # HTTP client with TLS fingerprinting
        "loguru==0.7.2",             # Advanced logging
        "pydantic==2.10.3",          # Data validation
        "rich==14.0.0",              # Rich text and beautiful formatting
        
        # Data processing
        "pandas==2.2.3",             # Data analysis and manipulation
        "openpyxl==3.1.5",           # Excel file support
        "beautifulsoup4>=4.10.0",    # HTML parsing
        
        # Networking and requests
        "requests>=2.27.1",          # HTTP library
        "httpx>=0.23.0",             # Modern async HTTP client
        "urllib3==2.3.0",            # HTTP client
        
        # Utilities
        "tabulate==0.9.0",           # Pretty-print tabular data
        "tqdm==4.67.1",              # Progress bars
        "python-dateutil>=2.8.0",   # Date utilities
        
        # Image processing (optional)
        "Pillow>=9.0.0",             # Image processing
        
        # Cryptography and security
        "cryptography>=3.4.0",       # Cryptographic recipes
        
        # Development and testing
        "pytest>=7.0.0",             # Testing framework
        "pytest-asyncio>=0.21.0",    # Async testing support
        
        # Performance monitoring
        "psutil>=5.9.0",             # System and process utilities
        "memory-profiler>=0.60.0",   # Memory usage monitoring
    ]
    
    try:
        print("📦 Installing enhanced requirements...")
        
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True, capture_output=True)
        
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([str(pip_exe), "install", package], check=True, capture_output=True)
        
        print("✅ All enhanced requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def setup_data_directories():
    """Setup enhanced data directories"""
    directories = [
        "data",
        "data/content",
        "data/images",
        "data/templates",
        "data/analytics",
        "logs",
        "backups",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_default_config():
    """Create default configuration files"""
    try:
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# StarLabs Twitter Bot v3.0 Environment Variables\n")
                f.write("# Add your sensitive configuration here\n")
                f.write("TELEGRAM_BOT_TOKEN=\n")
                f.write("ENCRYPTION_KEY=\n")
            print("✅ Created .env file")
        
        # Create .gitignore if it doesn't exist
        gitignore_file = Path(".gitignore")
        if not gitignore_file.exists():
            with open(gitignore_file, 'w') as f:
                f.write("# StarLabs Twitter Bot v3.0 .gitignore\n")
                f.write("__pycache__/\n")
                f.write("*.pyc\n")
                f.write("*.pyo\n")
                f.write("*.pyd\n")
                f.write(".Python\n")
                f.write("venv/\n")
                f.write("env/\n")
                f.write(".env\n")
                f.write("data/\n")
                f.write("logs/\n")
                f.write("backups/\n")
                f.write("exports/\n")
                f.write("*.log\n")
                f.write(".DS_Store\n")
                f.write("Thumbs.db\n")
            print("✅ Created .gitignore file")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not create config files: {e}")


def check_system_requirements():
    """Check system requirements and dependencies"""
    print("🔍 Checking system requirements...")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.total < 2 * 1024 * 1024 * 1024:  # 2GB
            print("⚠️ Warning: Less than 2GB RAM available. Performance may be affected.")
        else:
            print(f"✅ Memory: {memory.total // (1024**3)}GB available")
    except ImportError:
        print("ℹ️ Cannot check memory (psutil not installed)")
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        if free < 1 * 1024 * 1024 * 1024:  # 1GB
            print("⚠️ Warning: Less than 1GB disk space available.")
        else:
            print(f"✅ Disk space: {free // (1024**3)}GB available")
    except Exception:
        print("ℹ️ Cannot check disk space")


def run_bot():
    """Run the bot"""
    python_exe = get_python_executable()
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return False
    
    try:
        print("🚀 Starting StarLabs Twitter Bot v3.0...")
        subprocess.run([str(python_exe), "main.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start bot: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
        return True


def run_tests():
    """Run test suite"""
    python_exe = get_python_executable()
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return False
    
    try:
        print("🧪 Running test suite...")
        subprocess.run([str(python_exe), "-m", "pytest", "tests/", "-v"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False
    except FileNotFoundError:
        print("ℹ️ No tests directory found")
        return True


def full_setup():
    """Complete setup process"""
    print("🌟 StarLabs Twitter Bot v3.0 Setup")
    print("=" * 50)
    
    if not check_python_version():
        return False
    
    check_system_requirements()
    
    if not create_virtual_environment():
        return False
    
    if not install_requirements():
        return False
    
    setup_data_directories()
    create_default_config()
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Configure your settings: python setup.py configure")
    print("2. Add your accounts: python main.py")
    print("3. Start farming: python setup.py start")
    return True


def configure_interactive():
    """Interactive configuration setup"""
    print("⚙️ Interactive Configuration")
    print("=" * 40)
    
    try:
        # Import and run configuration
        from config import configure_bot
        configure_bot()
    except ImportError:
        print("❌ Configuration module not found. Please run setup first.")


def show_status():
    """Show system status"""
    print("📊 StarLabs Twitter Bot v3.0 Status")
    print("=" * 40)
    
    # Check virtual environment
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment: Ready")
    else:
        print("❌ Virtual environment: Not found")
    
    # Check data directories
    data_dirs = ["data", "logs", "backups"]
    for directory in data_dirs:
        if Path(directory).exists():
            print(f"✅ Directory {directory}: Exists")
        else:
            print(f"❌ Directory {directory}: Missing")
    
    # Check configuration
    if Path("data/config.json").exists():
        print("✅ Configuration: Found")
    else:
        print("⚠️ Configuration: Using defaults")
    
    # Check accounts
    if Path("data/accounts.json").exists():
        try:
            import json
            with open("data/accounts.json", 'r') as f:
                accounts = json.load(f)
                print(f"✅ Accounts: {len(accounts)} loaded")
        except Exception:
            print("⚠️ Accounts: File exists but cannot read")
    else:
        print("⚠️ Accounts: No accounts file found")


def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            full_setup()
        elif command == "start":
            run_bot()
        elif command == "test":
            run_tests()
        elif command == "configure":
            configure_interactive()
        elif command == "status":
            show_status()
        elif command == "venv":
            create_virtual_environment()
        elif command == "requirements":
            install_requirements()
        elif command == "clean":
            print("🧹 Cleaning up...")
            import shutil
            if Path("venv").exists():
                shutil.rmtree("venv")
                print("✅ Virtual environment removed")
            if Path("__pycache__").exists():
                shutil.rmtree("__pycache__")
                print("✅ Cache cleared")
        else:
            print("❌ Unknown command")
            print("Available commands: install, start, test, configure, status, venv, requirements, clean")
    else:
        print("🌟 StarLabs Twitter Bot v3.0 Setup")
        print("=" * 50)
        print("[1] Full setup (install everything)")
        print("[2] Start bot")
        print("[3] Run tests")
        print("[4] Configure bot")
        print("[5] Show status")
        print("[6] Create virtual environment only")
        print("[7] Install requirements only")
        print("[8] Clean installation")
        print("[9] Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            full_setup()
        elif choice == "2":
            run_bot()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            configure_interactive()
        elif choice == "5":
            show_status()
        elif choice == "6":
            create_virtual_environment()
        elif choice == "7":
            install_requirements()
        elif choice == "8":
            print("🧹 This will remove the virtual environment and cache")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                import shutil
                if Path("venv").exists():
                    shutil.rmtree("venv")
                    print("✅ Virtual environment removed")
                if Path("__pycache__").exists():
                    shutil.rmtree("__pycache__")
                    print("✅ Cache cleared")
        elif choice == "9":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()