"""
Setup and installation script for StarLabs Twitter Bot
Replaces batch files with Python functionality
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
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
    """Install required packages"""
    pip_exe = get_pip_executable()
    
    if not pip_exe.exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    requirements = [
        "aiogram==3.19.0",
        "aiohttp==3.11.16",
        "curl_cffi==0.10.0",
        "eth_account==0.13.5",
        "Flask==3.1.0",
        "loguru==0.7.2",
        "openpyxl==3.1.5",
        "pandas==2.2.3",
        "pydantic==2.10.3",
        "PyYAML==6.0.2",
        "rich==14.0.0",
        "tabulate==0.9.0",
        "tqdm==4.67.1",
        "urllib3==2.3.0",
        "beautifulsoup4>=4.10.0",
        "requests>=2.27.1",
        "httpx>=0.23.0"
    ]
    
    try:
        print("📦 Installing requirements...")
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([str(pip_exe), "install", package], check=True, capture_output=True)
        
        print("✅ All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def setup_data_directories():
    """Setup data directories"""
    directories = [
        "data",
        "data/images",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def run_bot():
    """Run the bot"""
    python_exe = get_python_executable()
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return False
    
    try:
        print("🚀 Starting StarLabs Twitter Bot...")
        subprocess.run([str(python_exe), "main.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start bot: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
        return True


def full_setup():
    """Complete setup process"""
    print("🌟 StarLabs Twitter Bot Setup")
    print("=" * 40)
    
    if not check_python_version():
        return False
    
    if not create_virtual_environment():
        return False
    
    if not install_requirements():
        return False
    
    setup_data_directories()
    
    print("\n✅ Setup completed successfully!")
    print("\nTo start the bot, run: python setup.py start")
    return True


def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            full_setup()
        elif command == "start":
            run_bot()
        elif command == "venv":
            create_virtual_environment()
        elif command == "requirements":
            install_requirements()
        else:
            print("❌ Unknown command")
            print("Available commands: install, start, venv, requirements")
    else:
        print("🌟 StarLabs Twitter Bot Setup")
        print("=" * 40)
        print("[1] Full setup (install everything)")
        print("[2] Start bot")
        print("[3] Create virtual environment only")
        print("[4] Install requirements only")
        print("[5] Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            full_setup()
        elif choice == "2":
            run_bot()
        elif choice == "3":
            create_virtual_environment()
        elif choice == "4":
            install_requirements()
        elif choice == "5":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()