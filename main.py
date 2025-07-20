from loguru import logger
import urllib3
import sys
import asyncio
import platform
import logging

from process import start
from src.utils.output import show_logo, show_dev_info
from src.utils.check_github_version import check_version
from accounts_manager import get_account_manager
from data_manager import get_data_manager
from analytics_manager import get_analytics_manager
from config import get_config, configure_bot

VERSION = "3.0.0"


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    show_logo()
    show_dev_info()
    
    # Initialize all managers
    try:
        account_manager = get_account_manager()
        data_manager = get_data_manager()
        analytics_manager = get_analytics_manager()
        config = get_config()
    except Exception as e:
        logger.error(f"Error initializing managers: {e}")
        return

    # You can pass a proxy string in format "user:pass@ip:port" if needed
    await check_version(VERSION, proxy="")

    configuration()
    
    # Show main menu
    while True:
        print("\n🌟 StarLabs Twitter Bot v3.0 Main Menu")
        print("=" * 50)
        print("[1] ⭐️ Start farming")
        print("[2] 🔄 Mutual Subscription")
        print("[3] 📝 Manage accounts")
        print("[4] 📄 Manage texts & images")
        print("[5] 📊 Analytics & Reports")
        print("[6] ⚙️ Configure bot")
        print("[7] 🔧 Advanced Tools")
        print("[8] 👋 Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            await start()
        elif choice == "2":
            # Set flag for mutual subscription and start
            import process
            await process.run_mutual_subscription()
        elif choice == "3":
            account_manager.interactive_manage_accounts()
        elif choice == "4":
            data_manager.interactive_manage_texts()
        elif choice == "5":
            analytics_manager.interactive_analytics_dashboard()
        elif choice == "6":
            configure_bot()
        elif choice == "7":
            _advanced_tools_menu()
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


def _advanced_tools_menu():
    """Advanced tools menu"""
    while True:
        print("\n🔧 Advanced Tools")
        print("=" * 30)
        print("[1] 🧹 Cleanup & Maintenance")
        print("[2] 🔄 Data Migration")
        print("[3] 🛠️ System Diagnostics")
        print("[4] 📦 Backup & Restore")
        print("[5] 🔍 Debug Tools")
        print("[6] Back to main menu")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            _cleanup_maintenance()
        elif choice == "2":
            _data_migration()
        elif choice == "3":
            _system_diagnostics()
        elif choice == "4":
            _backup_restore()
        elif choice == "5":
            _debug_tools()
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")


def _cleanup_maintenance():
    """Cleanup and maintenance tools"""
    print("\n🧹 Cleanup & Maintenance")
    print("[1] Clear old logs")
    print("[2] Optimize data files")
    print("[3] Remove unused media")
    print("[4] Reset analytics data")
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        import glob
        log_files = glob.glob("logs/*.log*")
        if log_files:
            for log_file in log_files[:-5]:  # Keep last 5 log files
                try:
                    os.remove(log_file)
                    print(f"Removed {log_file}")
                except Exception as e:
                    print(f"Error removing {log_file}: {e}")
            print("✅ Old logs cleaned up")
        else:
            print("No old logs found")
    
    elif choice == "2":
        print("🔄 Optimizing data files...")
        # Reload and save all managers to optimize storage
        get_account_manager().save_accounts()
        get_data_manager().save_content_items(ContentType.TWEET)
        get_analytics_manager().save_analytics_data()
        print("✅ Data files optimized")
    
    elif choice == "3":
        data_manager = get_data_manager()
        unused_media = []
        for media_item in data_manager.media_items:
            if media_item.usage_count == 0:
                unused_media.append(media_item)
        
        if unused_media:
            print(f"Found {len(unused_media)} unused media files")
            confirm = input("Remove unused media? (y/n): ").strip().lower()
            if confirm == 'y':
                for media_item in unused_media:
                    try:
                        if os.path.exists(media_item.file_path):
                            os.remove(media_item.file_path)
                        data_manager.media_items.remove(media_item)
                    except Exception as e:
                        print(f"Error removing {media_item.filename}: {e}")
                data_manager.save_media_items()
                print("✅ Unused media removed")
        else:
            print("No unused media found")
    
    elif choice == "4":
        confirm = input("⚠️ Reset all analytics data? (y/n): ").strip().lower()
        if confirm == 'y':
            analytics_manager = get_analytics_manager()
            analytics_manager.metrics.clear()
            analytics_manager.task_executions.clear()
            analytics_manager.account_performances.clear()
            analytics_manager.save_analytics_data()
            print("✅ Analytics data reset")


def _data_migration():
    """Data migration tools"""
    print("\n🔄 Data Migration")
    print("[1] Import from old format")
    print("[2] Export to new format")
    print("[3] Migrate accounts from Excel")
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        print("📥 Import from old format")
        # Implementation for importing old data formats
        print("Feature coming soon...")
    
    elif choice == "2":
        print("📤 Export to new format")
        # Implementation for exporting to new formats
        print("Feature coming soon...")
    
    elif choice == "3":
        excel_file = input("Excel file path: ").strip()
        if excel_file and os.path.exists(excel_file):
            try:
                import pandas as pd
                df = pd.read_excel(excel_file)
                account_manager = get_account_manager()
                
                imported = 0
                for _, row in df.iterrows():
                    auth_token = row.get('auth_token', '')
                    proxy = row.get('proxy', '')
                    username = row.get('username', '')
                    
                    if auth_token and account_manager.add_account(auth_token, proxy, username):
                        imported += 1
                
                print(f"✅ Imported {imported} accounts from Excel")
            except Exception as e:
                print(f"❌ Error importing from Excel: {e}")
        else:
            print("❌ File not found")


def _system_diagnostics():
    """System diagnostics"""
    print("\n🛠️ System Diagnostics")
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check dependencies
    try:
        import curl_cffi
        print(f"✅ curl_cffi: {curl_cffi.__version__}")
    except ImportError:
        print("❌ curl_cffi: Not installed")
    
    try:
        import aiohttp
        print(f"✅ aiohttp: {aiohttp.__version__}")
    except ImportError:
        print("❌ aiohttp: Not installed")
    
    # Check data directories
    directories = ["data", "data/images", "data/content", "logs"]
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory {directory}: Exists")
        else:
            print(f"❌ Directory {directory}: Missing")
    
    # Check data files
    account_manager = get_account_manager()
    data_manager = get_data_manager()
    analytics_manager = get_analytics_manager()
    
    print(f"\n📊 Data Status:")
    print(f"Accounts: {len(account_manager.accounts)}")
    print(f"Tweet texts: {len(data_manager.content_items[ContentType.TWEET])}")
    print(f"Comment texts: {len(data_manager.content_items[ContentType.COMMENT])}")
    print(f"Media items: {len(data_manager.media_items)}")
    print(f"Analytics metrics: {len(analytics_manager.metrics)}")
    
    input("\nPress Enter to continue...")


def _backup_restore():
    """Backup and restore tools"""
    print("\n📦 Backup & Restore")
    print("[1] Create full backup")
    print("[2] Restore from backup")
    print("[3] Schedule automatic backups")
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        import shutil
        from datetime import datetime
        
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = f"backups/{backup_name}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copytree("data", f"{backup_dir}/data")
            shutil.copytree("logs", f"{backup_dir}/logs", ignore_errors=True)
            
            print(f"✅ Backup created: {backup_dir}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    elif choice == "2":
        backup_dir = input("Backup directory: ").strip()
        if backup_dir and os.path.exists(backup_dir):
            confirm = input("⚠️ This will overwrite current data. Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    import shutil
                    if os.path.exists(f"{backup_dir}/data"):
                        shutil.rmtree("data")
                        shutil.copytree(f"{backup_dir}/data", "data")
                    print("✅ Data restored from backup")
                except Exception as e:
                    print(f"❌ Restore failed: {e}")
        else:
            print("❌ Backup directory not found")
    
    elif choice == "3":
        print("📅 Automatic backup scheduling")
        print("Feature coming soon...")


def _debug_tools():
    """Debug tools"""
    print("\n🔍 Debug Tools")
    print("[1] Test account connection")
    print("[2] Validate proxy")
    print("[3] Check API endpoints")
    print("[4] Generate test data")
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        print("🔗 Test account connection")
        # Implementation for testing account connections
        print("Feature coming soon...")
    
    elif choice == "2":
        proxy = input("Proxy (user:pass@ip:port): ").strip()
        if proxy:
            print(f"🔍 Testing proxy: {proxy}")
            # Implementation for proxy validation
            print("Feature coming soon...")
    
    elif choice == "3":
        print("🌐 Checking API endpoints")
        # Implementation for API endpoint checks
        print("Feature coming soon...")
    
    elif choice == "4":
        print("🧪 Generating test data")
        # Generate some test data for development
        data_manager = get_data_manager()
        analytics_manager = get_analytics_manager()
        
        # Add some test metrics
        import random
        for i in range(100):
            analytics_manager.record_metric(
                MetricType.SUCCESS_RATE,
                random.uniform(70, 100),
                f"test_account_{i % 10}",
                "test_task"
            )
        
        print("✅ Test data generated")


async def old_main():
    """Original main function for backward compatibility"""
    show_logo()
    show_dev_info()

    # You can pass a proxy string in format "user:pass@ip:port" if needed
    await check_version(VERSION, proxy="")

    configuration()
    await start()


log_format = (
    "<light-blue>[</light-blue><yellow>{time:HH:mm:ss}</yellow><light-blue>]</light-blue> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file}:{line}</cyan> | "
    "<level>{message}</level>"
)


def configuration():
    urllib3.disable_warnings()
    logger.remove()

    # Disable primp and web3 logging
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("web3").setLevel(logging.WARNING)

    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 month",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} - {message}",
        level="INFO",
    )

if __name__ == "__main__":
    asyncio.run(main())
