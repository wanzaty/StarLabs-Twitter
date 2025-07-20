"""
Simple Account management module for StarLabs Twitter Bot v3.0
Text-based account management with analytics and health monitoring
"""

import os
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import threading
from enum import Enum


class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    WRONG_TOKEN = "wrong_token"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"
    WARMING_UP = "warming_up"
    COOLDOWN = "cooldown"


class AccountHealth(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class AccountStats:
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    last_action_time: Optional[datetime] = None
    success_rate: float = 0.0
    average_response_time: float = 0.0
    consecutive_failures: int = 0
    daily_actions: int = 0
    weekly_actions: int = 0
    
    def update_success_rate(self):
        if self.total_actions > 0:
            self.success_rate = (self.successful_actions / self.total_actions) * 100
    
    def get_health_score(self) -> AccountHealth:
        if self.success_rate >= 90:
            return AccountHealth.EXCELLENT
        elif self.success_rate >= 75:
            return AccountHealth.GOOD
        elif self.success_rate >= 50:
            return AccountHealth.FAIR
        elif self.success_rate >= 25:
            return AccountHealth.POOR
        else:
            return AccountHealth.CRITICAL


@dataclass
class Account:
    auth_token: str
    proxy: str = ""
    username: str = ""
    status: AccountStatus = AccountStatus.UNKNOWN
    created_at: str = ""
    last_used: str = ""
    
    notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not isinstance(self.status, AccountStatus):
            self.status = AccountStatus(self.status) if isinstance(self.status, str) else AccountStatus.UNKNOWN
    
    def __repr__(self):
        return f"Account(token={self.auth_token[:10]}..., username={self.username}, status={self.status.value})"
    
    def get_masked_token(self) -> str:
        """Get masked auth token for display"""
        if len(self.auth_token) > 20:
            return f"{self.auth_token[:8]}...{self.auth_token[-8:]}"
        return f"{self.auth_token[:6]}..."


class SimpleAccountManager:
    def __init__(self, data_file: str = "data/accounts.txt"):
        self.data_file = data_file
        self.accounts: List[Account] = []
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._ensure_data_directory()
        self.load_accounts()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _account_to_line(self, account: Account) -> str:
        """Convert account to text line"""
        return f"{account.auth_token}|{account.proxy}|{account.username}|{account.status.value}|{account.created_at}|{account.last_used}|{account.notes}"
    
    def _line_to_account(self, line: str) -> Account:
        """Convert text line to account"""
        parts = line.strip().split('|')
        if len(parts) >= 4:
            auth_token = parts[0]
            proxy = parts[1] if len(parts) > 1 else ""
            username = parts[2] if len(parts) > 2 else ""
            status_str = parts[3] if len(parts) > 3 else "unknown"
            created_at = parts[4] if len(parts) > 4 else ""
            last_used = parts[5] if len(parts) > 5 else ""
            notes = parts[6] if len(parts) > 6 else ""
            
            try:
                status = AccountStatus(status_str)
            except ValueError:
                status = AccountStatus.UNKNOWN
            
            return Account(
                auth_token=auth_token,
                proxy=proxy,
                username=username,
                status=status,
                created_at=created_at,
                last_used=last_used,
                notes=notes
            )
        return None
    
    def load_accounts(self) -> List[Account]:
        """Load accounts from TXT file"""
        with self._lock:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        self.accounts = []
                        for line in lines:
                            if line.strip():
                                account = self._line_to_account(line)
                                if account:
                                    self.accounts.append(account)
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
        """Save accounts to TXT file"""
        with self._lock:
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    for account in self.accounts:
                        f.write(self._account_to_line(account) + '\n')
                logger.success(f"Saved {len(self.accounts)} accounts to {self.data_file}")
            except Exception as e:
                logger.error(f"Error saving accounts: {e}")
    
    def add_account(self, auth_token: str, proxy: str = "", username: str = "", 
                   status: AccountStatus = AccountStatus.UNKNOWN, **kwargs) -> bool:
        """Add a new account"""
        try:
            # Check if account already exists
            for account in self.accounts:
                if account.auth_token == auth_token:
                    logger.warning(f"Account with token {account.get_masked_token()} already exists")
                    return False
            
            new_account = Account(
                auth_token=auth_token,
                proxy=proxy,
                username=username,
                status=status,
                **kwargs
            )
            
            self.accounts.append(new_account)
            self.save_accounts()
            logger.success(f"Added new account: {new_account}")
            return True
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False
    
    async def update_account(self, auth_token: str, **kwargs) -> bool:
        """Update account information asynchronously"""
        async with self._async_lock:
            try:
                for account in self.accounts:
                    if account.auth_token == auth_token:
                        for key, value in kwargs.items():
                            if hasattr(account, key):
                                if key == 'status' and isinstance(value, str):
                                    setattr(account, key, AccountStatus(value))
                                else:
                                    setattr(account, key, value)
                        
                        account.last_used = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.save_accounts()
                        logger.info(f"Updated account {account.get_masked_token()}")
                        return True
                
                logger.warning(f"Account with token not found")
                return False
            except Exception as e:
                logger.error(f"Error updating account: {e}")
                return False
    
    def get_accounts(self, start_index: int = 1, end_index: int = 0, 
                    status_filter: List[AccountStatus] = None) -> List[Account]:
        """Get accounts with filtering"""
        if not self.accounts:
            return []
        
        # Apply status filter
        filtered_accounts = self.accounts
        if status_filter:
            filtered_accounts = [acc for acc in filtered_accounts if acc.status in status_filter]
        
        # Apply range filter
        if (start_index == 1 and end_index == 0) or start_index == end_index:
            return filtered_accounts
        
        if start_index < 1:
            start_index = 1
        if end_index == 0 or end_index > len(filtered_accounts):
            end_index = len(filtered_accounts)
        
        return filtered_accounts[start_index - 1:end_index]
    
    def get_account_statistics(self) -> Dict:
        """Get comprehensive account statistics"""
        if not self.accounts:
            return {}
        
        stats = {
            "total_accounts": len(self.accounts),
            "status_breakdown": {},
            "accounts_with_proxy": 0,
        }
        
        # Status breakdown
        for status in AccountStatus:
            stats["status_breakdown"][status.value] = len([acc for acc in self.accounts if acc.status == status])
        
        stats["accounts_with_proxy"] = len([acc for acc in self.accounts if acc.proxy])
        
        return stats
    
    def export_accounts(self, filename: str, format: str = "txt") -> bool:
        """Export accounts to different formats"""
        try:
            if format.lower() == "txt":
                with open(filename, 'w', encoding='utf-8') as f:
                    for account in self.accounts:
                        f.write(self._account_to_line(account) + '\n')
            
            elif format.lower() == "csv":
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Auth Token', 'Username', 'Proxy', 'Status', 'Created At', 'Notes'])
                    for account in self.accounts:
                        writer.writerow([
                            account.get_masked_token(),
                            account.username,
                            account.proxy,
                            account.status.value,
                            account.created_at,
                            account.notes
                        ])
            
            logger.success(f"Exported {len(self.accounts)} accounts to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting accounts: {e}")
            return False
    
    def import_accounts(self, filename: str, format: str = "txt") -> bool:
        """Import accounts from different formats"""
        try:
            if format.lower() == "txt":
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    imported_accounts = []
                    for line in lines:
                        if line.strip():
                            account = self._line_to_account(line)
                            if account:
                                imported_accounts.append(account)
                    
                    # Merge with existing accounts
                    existing_tokens = {acc.auth_token for acc in self.accounts}
                    new_accounts = [acc for acc in imported_accounts if acc.auth_token not in existing_tokens]
                    
                    self.accounts.extend(new_accounts)
                    self.save_accounts()
                    logger.success(f"Imported {len(new_accounts)} new accounts")
                    return True
            
            elif format.lower() == "csv":
                import csv
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    new_accounts = 0
                    for row in reader:
                        if self.add_account(
                            auth_token=row.get('auth_token', ''),
                            username=row.get('username', ''),
                            proxy=row.get('proxy', '')
                        ):
                            new_accounts += 1
                    logger.success(f"Imported {new_accounts} new accounts from CSV")
                    return True
            
        except Exception as e:
            logger.error(f"Error importing accounts: {e}")
            return False
    
    def interactive_manage_accounts(self):
        """Interactive account management"""
        while True:
            stats = self.get_account_statistics()
            
            print("\n📋 Account Management")
            print("=" * 50)
            print(f"📊 Total accounts: {stats.get('total_accounts', 0)}")
            print(f"📡 Accounts with proxy: {stats.get('accounts_with_proxy', 0)}")
            
            print("\n[1] Add accounts")
            print("[2] View accounts")
            print("[3] Account statistics")
            print("[4] Export accounts")
            print("[5] Import accounts")
            print("[6] Account search")
            print("[7] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._interactive_add_accounts()
            elif choice == "2":
                self._view_accounts()
            elif choice == "3":
                self._show_statistics()
            elif choice == "4":
                self._export_accounts_interactive()
            elif choice == "5":
                self._import_accounts_interactive()
            elif choice == "6":
                self._search_accounts()
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice")
    
    def _interactive_add_accounts(self):
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
            notes = input("Notes (optional): ").strip()
            
            if self.add_account(auth_token, proxy, username, notes=notes):
                print("✅ Account added successfully!")
            else:
                print("❌ Failed to add account (might already exist)")
        
        print(f"\n📊 Total accounts: {self.get_account_count()}")
    
    def _view_accounts(self):
        """Account viewing with filtering"""
        if not self.accounts:
            print("📭 No accounts found")
            return
        
        print("\n📋 Account Filters:")
        print("[1] All accounts")
        print("[2] Active accounts only")
        print("[3] Accounts with proxy")
        
        filter_choice = input("Filter choice: ").strip()
        
        accounts_to_show = self.accounts
        if filter_choice == "2":
            accounts_to_show = [acc for acc in self.accounts if acc.status == AccountStatus.ACTIVE]
        elif filter_choice == "3":
            accounts_to_show = [acc for acc in self.accounts if acc.proxy]
        
        print(f"\n📋 Accounts ({len(accounts_to_show)} shown):")
        print("-" * 100)
        print(f"{'#':<3} {'Token':<15} {'Username':<15} {'Status':<12} {'Created':<20} {'Proxy':<8}")
        print("-" * 100)
        
        for i, account in enumerate(accounts_to_show, 1):
            print(f"{i:<3} {account.get_masked_token():<15} {account.username or 'N/A':<15} "
                  f"{account.status.value:<12} {account.created_at:<20} {'Yes' if account.proxy else 'No':<8}")
    
    def _show_statistics(self):
        """Show account statistics"""
        stats = self.get_account_statistics()
        
        print("\n📊 Account Statistics")
        print("=" * 40)
        print(f"Total Accounts: {stats['total_accounts']}")
        print(f"Accounts with Proxy: {stats['accounts_with_proxy']}")
        
        print("\n📈 Status Breakdown:")
        for status, count in stats['status_breakdown'].items():
            print(f"  {status.title()}: {count}")
    
    def _export_accounts_interactive(self):
        """Interactive account export"""
        print("\n💾 Export Accounts")
        print("[1] TXT format")
        print("[2] CSV format")
        
        format_choice = input("Format choice: ").strip()
        filename = input("Filename: ").strip()
        
        if not filename:
            print("❌ Filename required")
            return
        
        format_map = {"1": "txt", "2": "csv"}
        export_format = format_map.get(format_choice, "txt")
        
        if self.export_accounts(filename, export_format):
            print(f"✅ Accounts exported to {filename}")
        else:
            print("❌ Export failed")
    
    def _import_accounts_interactive(self):
        """Interactive account import"""
        print("\n📥 Import Accounts")
        print("[1] TXT format")
        print("[2] CSV format")
        
        format_choice = input("Format choice: ").strip()
        filename = input("Filename: ").strip()
        
        if not filename or not os.path.exists(filename):
            print("❌ File not found")
            return
        
        format_map = {"1": "txt", "2": "csv"}
        import_format = format_map.get(format_choice, "txt")
        
        if self.import_accounts(filename, import_format):
            print(f"✅ Accounts imported from {filename}")
        else:
            print("❌ Import failed")
    
    def _search_accounts(self):
        """Search accounts by various criteria"""
        print("\n🔍 Search Accounts")
        search_term = input("Search by username, token, or status: ").strip().lower()
        
        if not search_term:
            return
        
        results = []
        for account in self.accounts:
            if (search_term in account.username.lower() or
                search_term in account.get_masked_token().lower() or
                search_term in account.status.value.lower()):
                results.append(account)
        
        if results:
            print(f"\n🎯 Found {len(results)} matching accounts:")
            for i, account in enumerate(results, 1):
                print(f"{i}. {account.get_masked_token()} - {account.username} - {account.status.value}")
        else:
            print("❌ No matching accounts found")
    
    def get_account_count(self) -> int:
        """Get total number of accounts"""
        return len(self.accounts)


# Global account manager instance
_account_manager = None


def get_account_manager() -> SimpleAccountManager:
    """Get account manager singleton"""
    global _account_manager
    if _account_manager is None:
        _account_manager = SimpleAccountManager()
    return _account_manager


def read_accounts_from_storage(start_index: int = 1, end_index: int = 0) -> List[Account]:
    """Read accounts from storage"""
    manager = get_account_manager()
    return manager.get_accounts(start_index, end_index)


async def update_account_in_storage(auth_token: str, username: str = None, status: str = None) -> bool:
    """Update account in storage"""
    manager = get_account_manager()
    update_data = {}
    if username is not None:
        update_data['username'] = username
    if status is not None:
        update_data['status'] = status
    return await manager.update_account(auth_token, **update_data)