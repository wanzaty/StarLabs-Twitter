"""
Account management module for StarLabs Twitter Bot
Replaces Excel file functionality with Python data structures
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger
import threading


@dataclass
class Account:
    auth_token: str
    proxy: str = ""
    username: str = ""
    status: str = "unknown"

    def __repr__(self):
        return f"Account(auth_token={self.auth_token[:10]}..., proxy={self.proxy}, username={self.username}, status={self.status})"


class AccountManager:
    def __init__(self, data_file: str = "data/accounts.json"):
        self.data_file = data_file
        self.accounts: List[Account] = []
        self._lock = threading.Lock()
        self._ensure_data_directory()
        self.load_accounts()

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load_accounts(self) -> List[Account]:
        """Load accounts from JSON file"""
        with self._lock:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.accounts = [Account(**account_data) for account_data in data]
                        logger.success(f"Loaded {len(self.accounts)} accounts from {self.data_file}")
                else:
                    self.accounts = []
                    logger.info(f"No accounts file found at {self.data_file}. Starting with empty list.")
                return self.accounts
            except Exception as e:
                logger.error(f"Error loading accounts: {e}")
                self.accounts = []
                return self.accounts

    def save_accounts(self):
        """Save accounts to JSON file"""
        with self._lock:
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump([asdict(account) for account in self.accounts], f, indent=2, ensure_ascii=False)
                logger.success(f"Saved {len(self.accounts)} accounts to {self.data_file}")
            except Exception as e:
                logger.error(f"Error saving accounts: {e}")

    def add_account(self, auth_token: str, proxy: str = "", username: str = "", status: str = "unknown") -> bool:
        """Add a new account"""
        try:
            # Check if account already exists
            for account in self.accounts:
                if account.auth_token == auth_token:
                    logger.warning(f"Account with token {auth_token[:10]}... already exists")
                    return False
            
            new_account = Account(
                auth_token=auth_token,
                proxy=proxy,
                username=username,
                status=status
            )
            self.accounts.append(new_account)
            self.save_accounts()
            logger.success(f"Added new account: {new_account}")
            return True
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False

    def update_account(self, auth_token: str, username: str = None, status: str = None) -> bool:
        """Update account information"""
        with self._lock:
            try:
                for account in self.accounts:
                    if account.auth_token == auth_token:
                        if username is not None:
                            account.username = username
                        if status is not None:
                            account.status = status
                        self.save_accounts()
                        logger.info(f"Updated account {auth_token[:10]}...")
                        return True
                
                logger.warning(f"Account with token {auth_token[:10]}... not found")
                return False
            except Exception as e:
                logger.error(f"Error updating account: {e}")
                return False

    def get_accounts(self, start_index: int = 1, end_index: int = 0) -> List[Account]:
        """Get accounts within specified range"""
        if not self.accounts:
            return []
        
        # If both are 0 or equal, return all accounts
        if (start_index == 1 and end_index == 0) or start_index == end_index:
            return self.accounts
        
        # Validate indices
        if start_index < 1:
            start_index = 1
        if end_index == 0 or end_index > len(self.accounts):
            end_index = len(self.accounts)
        
        return self.accounts[start_index - 1:end_index]

    def remove_account(self, auth_token: str) -> bool:
        """Remove an account"""
        with self._lock:
            try:
                for i, account in enumerate(self.accounts):
                    if account.auth_token == auth_token:
                        removed_account = self.accounts.pop(i)
                        self.save_accounts()
                        logger.success(f"Removed account: {removed_account}")
                        return True
                
                logger.warning(f"Account with token {auth_token[:10]}... not found")
                return False
            except Exception as e:
                logger.error(f"Error removing account: {e}")
                return False

    def get_account_count(self) -> int:
        """Get total number of accounts"""
        return len(self.accounts)

    def interactive_add_accounts(self):
        """Interactive account addition"""
        print("\n📝 Add Twitter Accounts")
        print("=" * 30)
        print("Enter account details (press Enter with empty auth_token to finish)")
        
        while True:
            print("\n" + "-" * 30)
            auth_token = input("Auth Token: ").strip()
            if not auth_token:
                break
            
            proxy = input("Proxy (user:pass@ip:port, optional): ").strip()
            username = input("Username (optional): ").strip()
            
            if self.add_account(auth_token, proxy, username):
                print("✅ Account added successfully!")
            else:
                print("❌ Failed to add account (might already exist)")
        
        print(f"\n📊 Total accounts: {self.get_account_count()}")

    def interactive_manage_accounts(self):
        """Interactive account management"""
        while True:
            print("\n📋 Account Management")
            print("=" * 30)
            print(f"Total accounts: {self.get_account_count()}")
            print("\n[1] Add accounts")
            print("[2] View accounts")
            print("[3] Remove account")
            print("[4] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self.interactive_add_accounts()
            elif choice == "2":
                self._view_accounts()
            elif choice == "3":
                self._remove_account_interactive()
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice")

    def _view_accounts(self):
        """View all accounts"""
        if not self.accounts:
            print("📭 No accounts found")
            return
        
        print(f"\n📋 Accounts ({len(self.accounts)} total):")
        print("-" * 80)
        for i, account in enumerate(self.accounts, 1):
            print(f"{i:2d}. Token: {account.auth_token[:10]}... | "
                  f"Username: {account.username or 'N/A'} | "
                  f"Status: {account.status} | "
                  f"Proxy: {'Yes' if account.proxy else 'No'}")

    def _remove_account_interactive(self):
        """Interactive account removal"""
        if not self.accounts:
            print("📭 No accounts to remove")
            return
        
        self._view_accounts()
        try:
            index = int(input("\nEnter account number to remove: ")) - 1
            if 0 <= index < len(self.accounts):
                account = self.accounts[index]
                confirm = input(f"Remove account {account.auth_token[:10]}...? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    self.remove_account(account.auth_token)
                else:
                    print("❌ Removal cancelled")
            else:
                print("❌ Invalid account number")
        except ValueError:
            print("❌ Please enter a valid number")


# Global account manager instance
_account_manager = None


def get_account_manager() -> AccountManager:
    """Get account manager singleton"""
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager


def read_accounts_from_storage(start_index: int = 1, end_index: int = 0) -> List[Account]:
    """Read accounts from storage (replaces Excel functionality)"""
    manager = get_account_manager()
    return manager.get_accounts(start_index, end_index)


async def update_account_in_storage(auth_token: str, username: str = None, status: str = None) -> bool:
    """Update account in storage (replaces Excel functionality)"""
    manager = get_account_manager()
    return manager.update_account(auth_token, username, status)