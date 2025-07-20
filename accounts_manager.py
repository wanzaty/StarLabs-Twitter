"""
Enhanced Account management module for StarLabs Twitter Bot v3.0
Advanced account management with analytics and health monitoring
"""

import json
import os
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import threading
import hashlib
import base64
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
    created_at: datetime = None
    last_used: datetime = None
    stats: AccountStats = None
    
    # Advanced features
    user_agent: str = ""
    fingerprint: str = ""
    warmup_completed: bool = False
    cooldown_until: Optional[datetime] = None
    notes: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.stats is None:
            self.stats = AccountStats()
        if self.tags is None:
            self.tags = []
        if not isinstance(self.status, AccountStatus):
            self.status = AccountStatus(self.status) if isinstance(self.status, str) else AccountStatus.UNKNOWN
    
    def __repr__(self):
        return f"Account(token={self.auth_token[:10]}..., username={self.username}, status={self.status.value})"
    
    def get_masked_token(self) -> str:
        """Get masked auth token for display"""
        if len(self.auth_token) > 20:
            return f"{self.auth_token[:8]}...{self.auth_token[-8:]}"
        return f"{self.auth_token[:6]}..."
    
    def is_healthy(self) -> bool:
        """Check if account is in good health"""
        return (
            self.status == AccountStatus.ACTIVE and
            self.stats.consecutive_failures < 3 and
            self.stats.success_rate > 50
        )
    
    def is_available(self) -> bool:
        """Check if account is available for use"""
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        return self.status in [AccountStatus.ACTIVE, AccountStatus.UNKNOWN]
    
    def set_cooldown(self, minutes: int):
        """Set account cooldown period"""
        self.cooldown_until = datetime.now() + timedelta(minutes=minutes)
        self.status = AccountStatus.COOLDOWN
    
    def generate_fingerprint(self):
        """Generate unique fingerprint for account"""
        data = f"{self.auth_token}{self.username}{self.proxy}"
        self.fingerprint = hashlib.md5(data.encode()).hexdigest()


class AdvancedAccountManager:
    def __init__(self, data_file: str = "data/accounts.json"):
        self.data_file = data_file
        self.accounts: List[Account] = []
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._ensure_data_directory()
        self.load_accounts()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _serialize_account(self, account: Account) -> dict:
        """Serialize account to dictionary"""
        data = asdict(account)
        # Convert datetime objects to ISO strings
        if data['created_at']:
            data['created_at'] = account.created_at.isoformat()
        if data['last_used']:
            data['last_used'] = account.last_used.isoformat()
        if data['cooldown_until']:
            data['cooldown_until'] = account.cooldown_until.isoformat()
        if data['stats']['last_action_time']:
            data['stats']['last_action_time'] = account.stats.last_action_time.isoformat()
        
        # Convert enum to string
        data['status'] = account.status.value
        
        return data
    
    def _deserialize_account(self, data: dict) -> Account:
        """Deserialize account from dictionary"""
        # Convert ISO strings back to datetime objects
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        if data.get('cooldown_until'):
            data['cooldown_until'] = datetime.fromisoformat(data['cooldown_until'])
        
        # Handle stats
        if 'stats' in data and data['stats'].get('last_action_time'):
            data['stats']['last_action_time'] = datetime.fromisoformat(data['stats']['last_action_time'])
        
        # Create AccountStats object
        if 'stats' in data:
            stats_data = data['stats']
            data['stats'] = AccountStats(**stats_data)
        
        # Convert status string to enum
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = AccountStatus(data['status'])
            except ValueError:
                data['status'] = AccountStatus.UNKNOWN
        
        return Account(**data)
    
    def load_accounts(self) -> List[Account]:
        """Load accounts from JSON file"""
        with self._lock:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.accounts = [self._deserialize_account(account_data) for account_data in data]
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
                serialized_accounts = [self._serialize_account(account) for account in self.accounts]
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(serialized_accounts, f, indent=2, ensure_ascii=False)
                logger.success(f"Saved {len(self.accounts)} accounts to {self.data_file}")
            except Exception as e:
                logger.error(f"Error saving accounts: {e}")
    
    def add_account(self, auth_token: str, proxy: str = "", username: str = "", 
                   status: AccountStatus = AccountStatus.UNKNOWN, **kwargs) -> bool:
        """Add a new account with advanced features"""
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
            new_account.generate_fingerprint()
            
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
                        
                        account.last_used = datetime.now()
                        self.save_accounts()
                        logger.info(f"Updated account {account.get_masked_token()}")
                        return True
                
                logger.warning(f"Account with token not found")
                return False
            except Exception as e:
                logger.error(f"Error updating account: {e}")
                return False
    
    def get_accounts(self, start_index: int = 1, end_index: int = 0, 
                    status_filter: List[AccountStatus] = None,
                    health_filter: List[AccountHealth] = None) -> List[Account]:
        """Get accounts with advanced filtering"""
        if not self.accounts:
            return []
        
        # Apply status filter
        filtered_accounts = self.accounts
        if status_filter:
            filtered_accounts = [acc for acc in filtered_accounts if acc.status in status_filter]
        
        # Apply health filter
        if health_filter:
            filtered_accounts = [acc for acc in filtered_accounts 
                               if acc.stats.get_health_score() in health_filter]
        
        # Apply range filter
        if (start_index == 1 and end_index == 0) or start_index == end_index:
            return filtered_accounts
        
        if start_index < 1:
            start_index = 1
        if end_index == 0 or end_index > len(filtered_accounts):
            end_index = len(filtered_accounts)
        
        return filtered_accounts[start_index - 1:end_index]
    
    def get_healthy_accounts(self) -> List[Account]:
        """Get only healthy accounts"""
        return [acc for acc in self.accounts if acc.is_healthy()]
    
    def get_available_accounts(self) -> List[Account]:
        """Get only available accounts"""
        return [acc for acc in self.accounts if acc.is_available()]
    
    def get_account_statistics(self) -> Dict:
        """Get comprehensive account statistics"""
        if not self.accounts:
            return {}
        
        stats = {
            "total_accounts": len(self.accounts),
            "status_breakdown": {},
            "health_breakdown": {},
            "average_success_rate": 0,
            "total_actions": 0,
            "accounts_with_proxy": 0,
            "accounts_warmed_up": 0
        }
        
        # Status breakdown
        for status in AccountStatus:
            stats["status_breakdown"][status.value] = len([acc for acc in self.accounts if acc.status == status])
        
        # Health breakdown
        for health in AccountHealth:
            count = len([acc for acc in self.accounts if acc.stats.get_health_score() == health])
            stats["health_breakdown"][health.value] = count
        
        # Calculate averages
        total_success_rate = sum(acc.stats.success_rate for acc in self.accounts)
        stats["average_success_rate"] = total_success_rate / len(self.accounts)
        
        stats["total_actions"] = sum(acc.stats.total_actions for acc in self.accounts)
        stats["accounts_with_proxy"] = len([acc for acc in self.accounts if acc.proxy])
        stats["accounts_warmed_up"] = len([acc for acc in self.accounts if acc.warmup_completed])
        
        return stats
    
    def export_accounts(self, filename: str, format: str = "json") -> bool:
        """Export accounts to different formats"""
        try:
            if format.lower() == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    serialized_accounts = [self._serialize_account(account) for account in self.accounts]
                    json.dump(serialized_accounts, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Auth Token', 'Username', 'Proxy', 'Status', 'Success Rate', 'Total Actions'])
                    for account in self.accounts:
                        writer.writerow([
                            account.get_masked_token(),
                            account.username,
                            account.proxy,
                            account.status.value,
                            f"{account.stats.success_rate:.2f}%",
                            account.stats.total_actions
                        ])
            
            logger.success(f"Exported {len(self.accounts)} accounts to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting accounts: {e}")
            return False
    
    def import_accounts(self, filename: str, format: str = "json") -> bool:
        """Import accounts from different formats"""
        try:
            if format.lower() == "json":
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    imported_accounts = [self._deserialize_account(account_data) for account_data in data]
                    
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
        """Enhanced interactive account management"""
        while True:
            stats = self.get_account_statistics()
            
            print("\n📋 Advanced Account Management")
            print("=" * 50)
            print(f"📊 Total accounts: {stats.get('total_accounts', 0)}")
            print(f"💚 Healthy accounts: {stats['health_breakdown'].get('excellent', 0) + stats['health_breakdown'].get('good', 0)}")
            print(f"📈 Average success rate: {stats.get('average_success_rate', 0):.1f}%")
            
            print("\n[1] Add accounts")
            print("[2] View accounts")
            print("[3] Account statistics")
            print("[4] Health check")
            print("[5] Export accounts")
            print("[6] Import accounts")
            print("[7] Bulk operations")
            print("[8] Account search")
            print("[9] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._interactive_add_accounts()
            elif choice == "2":
                self._view_accounts_advanced()
            elif choice == "3":
                self._show_detailed_statistics()
            elif choice == "4":
                self._health_check()
            elif choice == "5":
                self._export_accounts_interactive()
            elif choice == "6":
                self._import_accounts_interactive()
            elif choice == "7":
                self._bulk_operations()
            elif choice == "8":
                self._search_accounts()
            elif choice == "9":
                break
            else:
                print("❌ Invalid choice")
    
    def _interactive_add_accounts(self):
        """Enhanced interactive account addition"""
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
            tags = input("Tags (comma separated, optional): ").strip()
            
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
            
            if self.add_account(auth_token, proxy, username, notes=notes, tags=tag_list):
                print("✅ Account added successfully!")
            else:
                print("❌ Failed to add account (might already exist)")
        
        print(f"\n📊 Total accounts: {self.get_account_count()}")
    
    def _view_accounts_advanced(self):
        """Enhanced account viewing with filtering"""
        if not self.accounts:
            print("📭 No accounts found")
            return
        
        print("\n📋 Account Filters:")
        print("[1] All accounts")
        print("[2] Active accounts only")
        print("[3] Healthy accounts only")
        print("[4] Accounts with issues")
        
        filter_choice = input("Filter choice: ").strip()
        
        accounts_to_show = self.accounts
        if filter_choice == "2":
            accounts_to_show = [acc for acc in self.accounts if acc.status == AccountStatus.ACTIVE]
        elif filter_choice == "3":
            accounts_to_show = self.get_healthy_accounts()
        elif filter_choice == "4":
            accounts_to_show = [acc for acc in self.accounts if not acc.is_healthy()]
        
        print(f"\n📋 Accounts ({len(accounts_to_show)} shown):")
        print("-" * 120)
        print(f"{'#':<3} {'Token':<15} {'Username':<15} {'Status':<12} {'Health':<10} {'Success%':<8} {'Actions':<8} {'Proxy':<8}")
        print("-" * 120)
        
        for i, account in enumerate(accounts_to_show, 1):
            health = account.stats.get_health_score().value
            print(f"{i:<3} {account.get_masked_token():<15} {account.username or 'N/A':<15} "
                  f"{account.status.value:<12} {health:<10} {account.stats.success_rate:<8.1f} "
                  f"{account.stats.total_actions:<8} {'Yes' if account.proxy else 'No':<8}")
    
    def _show_detailed_statistics(self):
        """Show detailed account statistics"""
        stats = self.get_account_statistics()
        
        print("\n📊 Detailed Account Statistics")
        print("=" * 40)
        print(f"Total Accounts: {stats['total_accounts']}")
        print(f"Average Success Rate: {stats['average_success_rate']:.2f}%")
        print(f"Total Actions Performed: {stats['total_actions']}")
        print(f"Accounts with Proxy: {stats['accounts_with_proxy']}")
        print(f"Warmed Up Accounts: {stats['accounts_warmed_up']}")
        
        print("\n📈 Status Breakdown:")
        for status, count in stats['status_breakdown'].items():
            print(f"  {status.title()}: {count}")
        
        print("\n💚 Health Breakdown:")
        for health, count in stats['health_breakdown'].items():
            print(f"  {health.title()}: {count}")
    
    def _health_check(self):
        """Perform health check on all accounts"""
        print("\n🏥 Account Health Check")
        print("=" * 30)
        
        healthy = self.get_healthy_accounts()
        available = self.get_available_accounts()
        
        print(f"✅ Healthy accounts: {len(healthy)}/{len(self.accounts)}")
        print(f"🟢 Available accounts: {len(available)}/{len(self.accounts)}")
        
        # Show problematic accounts
        problematic = [acc for acc in self.accounts if not acc.is_healthy()]
        if problematic:
            print(f"\n⚠️ Accounts needing attention ({len(problematic)}):")
            for acc in problematic[:10]:  # Show first 10
                print(f"  {acc.get_masked_token()} - {acc.status.value} - {acc.stats.success_rate:.1f}% success")
    
    def _export_accounts_interactive(self):
        """Interactive account export"""
        print("\n💾 Export Accounts")
        print("[1] JSON format")
        print("[2] CSV format")
        
        format_choice = input("Format choice: ").strip()
        filename = input("Filename: ").strip()
        
        if not filename:
            print("❌ Filename required")
            return
        
        format_map = {"1": "json", "2": "csv"}
        export_format = format_map.get(format_choice, "json")
        
        if self.export_accounts(filename, export_format):
            print(f"✅ Accounts exported to {filename}")
        else:
            print("❌ Export failed")
    
    def _import_accounts_interactive(self):
        """Interactive account import"""
        print("\n📥 Import Accounts")
        print("[1] JSON format")
        print("[2] CSV format")
        
        format_choice = input("Format choice: ").strip()
        filename = input("Filename: ").strip()
        
        if not filename or not os.path.exists(filename):
            print("❌ File not found")
            return
        
        format_map = {"1": "json", "2": "csv"}
        import_format = format_map.get(format_choice, "json")
        
        if self.import_accounts(filename, import_format):
            print(f"✅ Accounts imported from {filename}")
        else:
            print("❌ Import failed")
    
    def _bulk_operations(self):
        """Bulk operations on accounts"""
        print("\n🔧 Bulk Operations")
        print("[1] Reset all account stats")
        print("[2] Mark all as active")
        print("[3] Clear cooldowns")
        print("[4] Remove failed accounts")
        
        choice = input("Operation choice: ").strip()
        
        if choice == "1":
            confirm = input("Reset all account statistics? (y/n): ").strip().lower()
            if confirm == 'y':
                for account in self.accounts:
                    account.stats = AccountStats()
                self.save_accounts()
                print("✅ All account statistics reset")
        
        elif choice == "2":
            confirm = input("Mark all accounts as active? (y/n): ").strip().lower()
            if confirm == 'y':
                for account in self.accounts:
                    account.status = AccountStatus.ACTIVE
                self.save_accounts()
                print("✅ All accounts marked as active")
        
        elif choice == "3":
            for account in self.accounts:
                account.cooldown_until = None
                if account.status == AccountStatus.COOLDOWN:
                    account.status = AccountStatus.ACTIVE
            self.save_accounts()
            print("✅ All cooldowns cleared")
        
        elif choice == "4":
            confirm = input("Remove accounts with critical health? (y/n): ").strip().lower()
            if confirm == 'y':
                before_count = len(self.accounts)
                self.accounts = [acc for acc in self.accounts 
                               if acc.stats.get_health_score() != AccountHealth.CRITICAL]
                removed = before_count - len(self.accounts)
                self.save_accounts()
                print(f"✅ Removed {removed} failed accounts")
    
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


def get_account_manager() -> AdvancedAccountManager:
    """Get account manager singleton"""
    global _account_manager
    if _account_manager is None:
        _account_manager = AdvancedAccountManager()
    return _account_manager


def read_accounts_from_storage(start_index: int = 1, end_index: int = 0) -> List[Account]:
    """Read accounts from storage (replaces Excel functionality)"""
    manager = get_account_manager()
    return manager.get_accounts(start_index, end_index)


async def update_account_in_storage(auth_token: str, username: str = None, status: str = None) -> bool:
    """Update account in storage (replaces Excel functionality)"""
    manager = get_account_manager()
    update_data = {}
    if username is not None:
        update_data['username'] = username
    if status is not None:
        update_data['status'] = status
    return await manager.update_account(auth_token, **update_data)