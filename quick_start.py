#!/usr/bin/env python3
"""
Quick Start Script for StarLabs Twitter Bot v3.0
Installs dependencies and runs the bot without virtual environment
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    requirements = [
        "loguru==0.7.2",
        "aiohttp==3.11.16", 
        "curl_cffi==0.10.0",
        "rich==14.0.0",
        "requests>=2.27.1",
        "beautifulsoup4>=4.10.0",
        "tabulate==0.9.0",
        "tqdm==4.67.1",
        "Pillow>=9.0.0",
    ]
    
    try:
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_directories():
    """Setup required directories"""
    directories = [
        "data",
        "data/images", 
        "logs",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_default_files():
    """Create default data files"""
    # Create default accounts.txt
    accounts_file = Path("data/accounts.txt")
    if not accounts_file.exists():
        with open(accounts_file, 'w', encoding='utf-8') as f:
            f.write("# Add your Twitter accounts here\n")
            f.write("# Format: auth_token|proxy|username|status|created_at|last_used|notes\n")
        print("✅ Created data/accounts.txt")
    
    # Create default tweets.txt
    tweets_file = Path("data/tweets.txt")
    if not tweets_file.exists():
        with open(tweets_file, 'w', encoding='utf-8') as f:
            f.write("Hello Twitter! 🌟|tweet|0|2025-01-21 12:00:00\n")
            f.write("Having a great day! ☀️|tweet|0|2025-01-21 12:00:00\n")
            f.write("Building something amazing 🚀|tweet|0|2025-01-21 12:00:00\n")
        print("✅ Created data/tweets.txt")
    
    # Create default comments.txt
    comments_file = Path("data/comments.txt")
    if not comments_file.exists():
        with open(comments_file, 'w', encoding='utf-8') as f:
            f.write("Great post! 👍|comment|0|2025-01-21 12:00:00\n")
            f.write("Thanks for sharing! 🙏|comment|0|2025-01-21 12:00:00\n")
            f.write("Interesting perspective 🤔|comment|0|2025-01-21 12:00:00\n")
        print("✅ Created data/comments.txt")


def main():
    """Main quick start function"""
    print("🌟 StarLabs Twitter Bot v3.0 - Quick Start")
    print("=" * 50)
    
    print("🔧 Setting up bot...")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed!")
        return
    
    # Setup directories
    setup_directories()
    
    # Create default files
    create_default_files()
    
    print("\n✅ Quick setup completed successfully!")
    print("\n🚀 You can now run the bot with:")
    print("   python main.py")
    print("\n📝 Don't forget to:")
    print("   1. Add your Twitter accounts to data/accounts.txt")
    print("   2. Customize tweets in data/tweets.txt")
    print("   3. Add comments in data/comments.txt")
    print("   4. Add images to data/images/ folder")


if __name__ == "__main__":
    main()