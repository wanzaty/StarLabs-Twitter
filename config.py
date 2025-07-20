"""
Enhanced Configuration module for StarLabs Twitter Bot v3.0
All settings with advanced features and validation
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import asyncio
import json
import os
from pathlib import Path
from enum import Enum


class TaskType(Enum):
    LIKE = "like"
    RETWEET = "retweet"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    TWEET = "tweet"
    TWEET_IMAGE = "tweet_image"
    COMMENT = "comment"
    COMMENT_IMAGE = "comment_image"
    QUOTE = "quote"
    QUOTE_IMAGE = "quote_image"
    CHECK_VALID = "check_valid"


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class AdvancedSettingsConfig:
    THREADS: int = 3
    ATTEMPTS: int = 5
    ACCOUNTS_RANGE: Tuple[int, int] = (0, 0)
    EXACT_ACCOUNTS_TO_USE: List[int] = field(default_factory=list)
    PAUSE_BETWEEN_ATTEMPTS: Tuple[int, int] = (3, 10)
    RANDOM_PAUSE_BETWEEN_ACCOUNTS: Tuple[int, int] = (5, 15)
    RANDOM_PAUSE_BETWEEN_ACTIONS: Tuple[int, int] = (2, 8)
    RANDOM_INITIALIZATION_PAUSE: Tuple[int, int] = (1, 5)
    
    # Advanced features
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    RETRY_BACKOFF_FACTOR: float = 2.0
    MAX_RETRY_DELAY: int = 60
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Account management
    SHUFFLE_ACCOUNTS: bool = True
    ACCOUNT_ROTATION_ENABLED: bool = True
    FAILED_ACCOUNT_COOLDOWN: int = 300  # 5 minutes
    
    # Telegram settings
    TELEGRAM_USERS_IDS: List[int] = field(default_factory=list)
    TELEGRAM_BOT_TOKEN: str = ""
    SEND_TELEGRAM_LOGS: bool = False
    SEND_ONLY_SUMMARY: bool = False
    TELEGRAM_REPORT_INTERVAL: int = 100  # Send report every N accounts
    
    # Monitoring and analytics
    ENABLE_ANALYTICS: bool = True
    SAVE_DETAILED_LOGS: bool = True
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Performance optimization
    USE_CONNECTION_POOLING: bool = True
    KEEP_ALIVE_CONNECTIONS: bool = True
    DNS_CACHE_ENABLED: bool = True


@dataclass
class SmartFlowConfig:
    TASKS_DATA: 'DataForTasks' = None
    SKIP_FAILED_TASKS: bool = True
    TASKS: List[str] = field(default_factory=list)
    
    # Smart retry logic
    SMART_RETRY_ENABLED: bool = True
    TASK_SPECIFIC_RETRIES: Dict[str, int] = field(default_factory=lambda: {
        "like": 3,
        "retweet": 3,
        "follow": 5,
        "unfollow": 3,
        "tweet": 5,
        "comment": 4
    })
    
    # Task scheduling
    TASK_PRIORITY: Dict[str, int] = field(default_factory=lambda: {
        "check_valid": 1,
        "follow": 2,
        "like": 3,
        "retweet": 4,
        "comment": 5,
        "tweet": 6,
        "unfollow": 7
    })
    
    # Batch processing
    BATCH_SIZE: int = 50
    BATCH_PROCESSING_ENABLED: bool = True
    
    # Error handling
    CONTINUE_ON_CRITICAL_ERROR: bool = False
    MAX_CONSECUTIVE_FAILURES: int = 5


@dataclass
class EnhancedTweetsConfig:
    RANDOM_TEXT_FOR_TWEETS: bool = True
    RANDOM_PICTURE_FOR_TWEETS: bool = True
    
    # Content generation
    USE_AI_GENERATED_CONTENT: bool = False
    CONTENT_TEMPLATES: List[str] = field(default_factory=list)
    HASHTAG_POOLS: List[str] = field(default_factory=list)
    
    # Media settings
    IMAGE_QUALITY: int = 85  # 1-100
    RESIZE_IMAGES: bool = True
    MAX_IMAGE_SIZE: Tuple[int, int] = (1920, 1080)
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: ["jpg", "jpeg", "png", "gif"])
    
    # Tweet scheduling
    SCHEDULE_TWEETS: bool = False
    TWEET_INTERVALS: Tuple[int, int] = (300, 1800)  # 5-30 minutes
    
    # Content variation
    USE_EMOJI_VARIATION: bool = True
    TEXT_VARIATION_ENABLED: bool = True
    MINIMUM_TEXT_LENGTH: int = 10
    MAXIMUM_TEXT_LENGTH: int = 280


@dataclass
class EnhancedCommentsConfig:
    RANDOM_TEXT_FOR_COMMENTS: bool = True
    RANDOM_PICTURE_FOR_COMMENTS: bool = True
    
    # Smart commenting
    CONTEXT_AWARE_COMMENTS: bool = False
    COMMENT_RELEVANCE_CHECK: bool = False
    
    # Comment patterns
    COMMENT_TEMPLATES: List[str] = field(default_factory=list)
    REACTION_EMOJIS: List[str] = field(default_factory=lambda: ["👍", "❤️", "🔥", "💯", "🙌"])
    
    # Engagement settings
    REPLY_TO_REPLIES: bool = False
    MAX_COMMENT_THREAD_DEPTH: int = 2


@dataclass
class SecurityConfig:
    SSL_VERIFICATION: bool = True
    USE_PROXY_ROTATION: bool = True
    PROXY_HEALTH_CHECK: bool = True
    PROXY_TIMEOUT: int = 10
    
    # Anti-detection
    USER_AGENT_ROTATION: bool = True
    RANDOM_HEADERS: bool = True
    FINGERPRINT_RANDOMIZATION: bool = True
    
    # Account protection
    ACCOUNT_WARMUP_ENABLED: bool = True
    WARMUP_ACTIONS_COUNT: int = 5
    SUSPICIOUS_ACTIVITY_DETECTION: bool = True
    
    # Data protection
    ENCRYPT_SENSITIVE_DATA: bool = False
    SECURE_TOKEN_STORAGE: bool = True


@dataclass
class AnalyticsConfig:
    TRACK_PERFORMANCE: bool = True
    SAVE_STATISTICS: bool = True
    GENERATE_REPORTS: bool = True
    
    # Metrics
    TRACK_SUCCESS_RATES: bool = True
    TRACK_RESPONSE_TIMES: bool = True
    TRACK_ERROR_PATTERNS: bool = True
    
    # Reporting
    DAILY_REPORTS: bool = True
    WEEKLY_SUMMARIES: bool = True
    EXPORT_TO_CSV: bool = True
    EXPORT_TO_JSON: bool = True


@dataclass
class Config:
    SETTINGS: AdvancedSettingsConfig = field(default_factory=AdvancedSettingsConfig)
    FLOW: SmartFlowConfig = field(default_factory=SmartFlowConfig)
    TWEETS: EnhancedTweetsConfig = field(default_factory=EnhancedTweetsConfig)
    COMMENTS: EnhancedCommentsConfig = field(default_factory=EnhancedCommentsConfig)
    SECURITY: SecurityConfig = field(default_factory=SecurityConfig)
    ANALYTICS: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    
    # System
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    config_file: str = "data/config.json"
    
    def __post_init__(self):
        self.ensure_config_directory()
        self.load_from_file()
    
    def ensure_config_directory(self):
        """Ensure config directory exists"""
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
    
    def save_to_file(self):
        """Save configuration to JSON file"""
        try:
            config_dict = {
                "settings": self._dataclass_to_dict(self.SETTINGS),
                "flow": self._dataclass_to_dict(self.FLOW),
                "tweets": self._dataclass_to_dict(self.TWEETS),
                "comments": self._dataclass_to_dict(self.COMMENTS),
                "security": self._dataclass_to_dict(self.SECURITY),
                "analytics": self._dataclass_to_dict(self.ANALYTICS)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_from_file(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                
                # Update dataclasses with loaded values
                self._update_dataclass(self.SETTINGS, config_dict.get("settings", {}))
                self._update_dataclass(self.FLOW, config_dict.get("flow", {}))
                self._update_dataclass(self.TWEETS, config_dict.get("tweets", {}))
                self._update_dataclass(self.COMMENTS, config_dict.get("comments", {}))
                self._update_dataclass(self.SECURITY, config_dict.get("security", {}))
                self._update_dataclass(self.ANALYTICS, config_dict.get("analytics", {}))
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def _dataclass_to_dict(self, obj) -> dict:
        """Convert dataclass to dictionary"""
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, (list, dict, str, int, float, bool)) or value is None:
                result[key] = value
        return result
    
    def _update_dataclass(self, obj, data: dict):
        """Update dataclass with dictionary data"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)


# Configuration instance
_config_instance = None


def get_config() -> Config:
    """Get configuration singleton"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def update_config(**kwargs):
    """Update configuration values"""
    config = get_config()
    
    # Update sections
    for section_name, section_data in kwargs.items():
        if hasattr(config, section_name.upper()):
            section = getattr(config, section_name.upper())
            for key, value in section_data.items():
                if hasattr(section, key.upper()):
                    setattr(section, key.upper(), value)
    
    # Save changes
    config.save_to_file()


def configure_bot():
    """Enhanced interactive configuration setup"""
    print("\n🔧 StarLabs Twitter Bot v3.0 Configuration")
    print("=" * 60)
    
    config = get_config()
    
    while True:
        print("\n📋 Configuration Menu:")
        print("[1] Basic Settings")
        print("[2] Advanced Settings")
        print("[3] Security Settings")
        print("[4] Tweet & Comment Settings")
        print("[5] Analytics Settings")
        print("[6] Telegram Settings")
        print("[7] Export/Import Config")
        print("[8] Reset to Defaults")
        print("[9] Save & Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            _configure_basic_settings(config)
        elif choice == "2":
            _configure_advanced_settings(config)
        elif choice == "3":
            _configure_security_settings(config)
        elif choice == "4":
            _configure_content_settings(config)
        elif choice == "5":
            _configure_analytics_settings(config)
        elif choice == "6":
            _configure_telegram_settings(config)
        elif choice == "7":
            _export_import_config(config)
        elif choice == "8":
            _reset_to_defaults(config)
        elif choice == "9":
            config.save_to_file()
            print("✅ Configuration saved successfully!")
            break
        else:
            print("❌ Invalid choice")


def _configure_basic_settings(config: Config):
    """Configure basic settings"""
    print("\n📊 Basic Settings:")
    
    threads = input(f"Number of threads [{config.SETTINGS.THREADS}]: ").strip()
    if threads.isdigit():
        config.SETTINGS.THREADS = int(threads)
    
    attempts = input(f"Retry attempts [{config.SETTINGS.ATTEMPTS}]: ").strip()
    if attempts.isdigit():
        config.SETTINGS.ATTEMPTS = int(attempts)
    
    shuffle = input(f"Shuffle accounts? (y/n) [{config.SETTINGS.SHUFFLE_ACCOUNTS}]: ").strip().lower()
    if shuffle in ['y', 'yes']:
        config.SETTINGS.SHUFFLE_ACCOUNTS = True
    elif shuffle in ['n', 'no']:
        config.SETTINGS.SHUFFLE_ACCOUNTS = False


def _configure_advanced_settings(config: Config):
    """Configure advanced settings"""
    print("\n⚙️ Advanced Settings:")
    
    rate_limit = input(f"Rate limit per minute [{config.SETTINGS.RATE_LIMIT_PER_MINUTE}]: ").strip()
    if rate_limit.isdigit():
        config.SETTINGS.RATE_LIMIT_PER_MINUTE = int(rate_limit)
    
    timeout = input(f"Request timeout [{config.SETTINGS.REQUEST_TIMEOUT}]: ").strip()
    if timeout.isdigit():
        config.SETTINGS.REQUEST_TIMEOUT = int(timeout)
    
    analytics = input(f"Enable analytics? (y/n) [{config.SETTINGS.ENABLE_ANALYTICS}]: ").strip().lower()
    if analytics in ['y', 'yes']:
        config.SETTINGS.ENABLE_ANALYTICS = True
    elif analytics in ['n', 'no']:
        config.SETTINGS.ENABLE_ANALYTICS = False


def _configure_security_settings(config: Config):
    """Configure security settings"""
    print("\n🔒 Security Settings:")
    
    ssl = input(f"SSL verification? (y/n) [{config.SECURITY.SSL_VERIFICATION}]: ").strip().lower()
    if ssl in ['y', 'yes']:
        config.SECURITY.SSL_VERIFICATION = True
    elif ssl in ['n', 'no']:
        config.SECURITY.SSL_VERIFICATION = False
    
    proxy_rotation = input(f"Use proxy rotation? (y/n) [{config.SECURITY.USE_PROXY_ROTATION}]: ").strip().lower()
    if proxy_rotation in ['y', 'yes']:
        config.SECURITY.USE_PROXY_ROTATION = True
    elif proxy_rotation in ['n', 'no']:
        config.SECURITY.USE_PROXY_ROTATION = False


def _configure_content_settings(config: Config):
    """Configure content settings"""
    print("\n📝 Content Settings:")
    
    random_tweets = input(f"Random tweet texts? (y/n) [{config.TWEETS.RANDOM_TEXT_FOR_TWEETS}]: ").strip().lower()
    if random_tweets in ['y', 'yes']:
        config.TWEETS.RANDOM_TEXT_FOR_TWEETS = True
    elif random_tweets in ['n', 'no']:
        config.TWEETS.RANDOM_TEXT_FOR_TWEETS = False
    
    emoji_variation = input(f"Use emoji variation? (y/n) [{config.TWEETS.USE_EMOJI_VARIATION}]: ").strip().lower()
    if emoji_variation in ['y', 'yes']:
        config.TWEETS.USE_EMOJI_VARIATION = True
    elif emoji_variation in ['n', 'no']:
        config.TWEETS.USE_EMOJI_VARIATION = False


def _configure_analytics_settings(config: Config):
    """Configure analytics settings"""
    print("\n📈 Analytics Settings:")
    
    track_performance = input(f"Track performance? (y/n) [{config.ANALYTICS.TRACK_PERFORMANCE}]: ").strip().lower()
    if track_performance in ['y', 'yes']:
        config.ANALYTICS.TRACK_PERFORMANCE = True
    elif track_performance in ['n', 'no']:
        config.ANALYTICS.TRACK_PERFORMANCE = False
    
    daily_reports = input(f"Generate daily reports? (y/n) [{config.ANALYTICS.DAILY_REPORTS}]: ").strip().lower()
    if daily_reports in ['y', 'yes']:
        config.ANALYTICS.DAILY_REPORTS = True
    elif daily_reports in ['n', 'no']:
        config.ANALYTICS.DAILY_REPORTS = False


def _configure_telegram_settings(config: Config):
    """Configure Telegram settings"""
    print("\n📱 Telegram Settings:")
    
    telegram_logs = input(f"Send Telegram logs? (y/n) [{config.SETTINGS.SEND_TELEGRAM_LOGS}]: ").strip().lower()
    if telegram_logs in ['y', 'yes']:
        config.SETTINGS.SEND_TELEGRAM_LOGS = True
        
        bot_token = input(f"Bot token [{config.SETTINGS.TELEGRAM_BOT_TOKEN[:10]}...]: ").strip()
        if bot_token:
            config.SETTINGS.TELEGRAM_BOT_TOKEN = bot_token
        
        user_ids = input("User IDs (comma separated): ").strip()
        if user_ids:
            config.SETTINGS.TELEGRAM_USERS_IDS = [int(uid.strip()) for uid in user_ids.split(',')]
    elif telegram_logs in ['n', 'no']:
        config.SETTINGS.SEND_TELEGRAM_LOGS = False


def _export_import_config(config: Config):
    """Export/Import configuration"""
    print("\n💾 Export/Import Configuration:")
    print("[1] Export current config")
    print("[2] Import config from file")
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        filename = input("Export filename [config_backup.json]: ").strip() or "config_backup.json"
        try:
            config.config_file = filename
            config.save_to_file()
            print(f"✅ Configuration exported to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    elif choice == "2":
        filename = input("Import filename: ").strip()
        if filename and os.path.exists(filename):
            try:
                config.config_file = filename
                config.load_from_file()
                print(f"✅ Configuration imported from {filename}")
            except Exception as e:
                print(f"❌ Import failed: {e}")
        else:
            print("❌ File not found")


def _reset_to_defaults(config: Config):
    """Reset configuration to defaults"""
    confirm = input("⚠️ Reset all settings to defaults? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        global _config_instance
        _config_instance = Config()
        print("✅ Configuration reset to defaults")