"""
Simple configuration browser for StarLabs Twitter Bot
"""

def run():
    """Simple configuration interface"""
    print("\n⚙️ Configuration Browser")
    print("=" * 40)
    print("This is a simplified configuration interface.")
    print("For full configuration, use the main menu in main.py")
    
    try:
        from config import configure_bot
        configure_bot()
    except ImportError:
        print("❌ Full configuration not available")
        print("Please install all dependencies first")