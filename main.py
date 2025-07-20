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
from config import get_config, configure_bot

VERSION = "2.1.0"


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    show_logo()
    show_dev_info()
    
    # Initialize managers
    account_manager = get_account_manager()
    data_manager = get_data_manager()
    config = get_config()

    # You can pass a proxy string in format "user:pass@ip:port" if needed
    await check_version(VERSION, proxy="")

    configuration()
    
    # Show main menu
    while True:
        print("\n🌟 StarLabs Twitter Bot Main Menu")
        print("=" * 40)
        print("[1] ⭐️ Start farming")
        print("[2] 🔄 Mutual Subscription")
        print("[3] 📝 Manage accounts")
        print("[4] 📄 Manage texts & images")
        print("[5] ⚙️ Configure bot")
        print("[6] 👋 Exit")
        
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
            configure_bot()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


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
