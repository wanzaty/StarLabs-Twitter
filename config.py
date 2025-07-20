"""
Configuration module for StarLabs Twitter Bot
All settings are defined here in Python instead of YAML
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import asyncio


@dataclass
class SettingsConfig:
    THREADS: int = 1
    ATTEMPTS: int = 5
    ACCOUNTS_RANGE: Tuple[int, int] = (0, 0)
    EXACT_ACCOUNTS_TO_USE: List[int] = field(default_factory=list)
    PAUSE_BETWEEN_ATTEMPTS: Tuple[int, int] = (3, 10)
    RANDOM_PAUSE_BETWEEN_ACCOUNTS: Tuple[int, int] = (3, 10)
    RANDOM_PAUSE_BETWEEN_ACTIONS: Tuple[int, int] = (3, 10)
    RANDOM_INITIALIZATION_PAUSE: Tuple[int, int] = (3, 10)
    TELEGRAM_USERS_IDS: List[int] = field(default_factory=list)
    TELEGRAM_BOT_TOKEN: str = ""
    SEND_TELEGRAM_LOGS: bool = False
    SEND_ONLY_SUMMARY: bool = False
    SHUFFLE_ACCOUNTS: bool = True


@dataclass
class FlowConfig:
    TASKS_DATA: 'DataForTasks' = None
    SKIP_FAILED_TASKS: bool = False
    TASKS: List[str] = field(default_factory=list)


@dataclass
class TweetsConfig:
    RANDOM_TEXT_FOR_TWEETS: bool = False
    RANDOM_PICTURE_FOR_TWEETS: bool = True


@dataclass
class CommentsConfig:
    RANDOM_TEXT_FOR_COMMENTS: bool = False
    RANDOM_PICTURE_FOR_COMMENTS: bool = True


@dataclass
class OthersConfig:
    SSL_VERIFICATION: bool = False


@dataclass
class Config:
    SETTINGS: SettingsConfig = field(default_factory=SettingsConfig)
    FLOW: FlowConfig = field(default_factory=FlowConfig)
    TWEETS: TweetsConfig = field(default_factory=TweetsConfig)
    COMMENTS: CommentsConfig = field(default_factory=CommentsConfig)
    OTHERS: OthersConfig = field(default_factory=OthersConfig)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


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
    
    # Update SETTINGS
    if 'settings' in kwargs:
        for key, value in kwargs['settings'].items():
            if hasattr(config.SETTINGS, key.upper()):
                setattr(config.SETTINGS, key.upper(), value)
    
    # Update FLOW
    if 'flow' in kwargs:
        for key, value in kwargs['flow'].items():
            if hasattr(config.FLOW, key.upper()):
                setattr(config.FLOW, key.upper(), value)
    
    # Update TWEETS
    if 'tweets' in kwargs:
        for key, value in kwargs['tweets'].items():
            if hasattr(config.TWEETS, key.upper()):
                setattr(config.TWEETS, key.upper(), value)
    
    # Update COMMENTS
    if 'comments' in kwargs:
        for key, value in kwargs['comments'].items():
            if hasattr(config.COMMENTS, key.upper()):
                setattr(config.COMMENTS, key.upper(), value)
    
    # Update OTHERS
    if 'others' in kwargs:
        for key, value in kwargs['others'].items():
            if hasattr(config.OTHERS, key.upper()):
                setattr(config.OTHERS, key.upper(), value)


def configure_bot():
    """Interactive configuration setup"""
    print("\n🔧 Bot Configuration Setup")
    print("=" * 50)
    
    config = get_config()
    
    # Basic settings
    print("\n📊 Basic Settings:")
    threads = input(f"Number of threads [{config.SETTINGS.THREADS}]: ").strip()
    if threads:
        config.SETTINGS.THREADS = int(threads)
    
    attempts = input(f"Number of retry attempts [{config.SETTINGS.ATTEMPTS}]: ").strip()
    if attempts:
        config.SETTINGS.ATTEMPTS = int(attempts)
    
    # Telegram settings
    print("\n📱 Telegram Settings (optional):")
    telegram_logs = input(f"Send Telegram logs? (y/n) [{config.SETTINGS.SEND_TELEGRAM_LOGS}]: ").strip().lower()
    if telegram_logs in ['y', 'yes']:
        config.SETTINGS.SEND_TELEGRAM_LOGS = True
        bot_token = input("Telegram Bot Token: ").strip()
        if bot_token:
            config.SETTINGS.TELEGRAM_BOT_TOKEN = bot_token
        
        user_ids = input("Telegram User IDs (comma separated): ").strip()
        if user_ids:
            config.SETTINGS.TELEGRAM_USERS_IDS = [int(uid.strip()) for uid in user_ids.split(',')]
    
    # Tweet settings
    print("\n🐦 Tweet Settings:")
    random_text = input(f"Use random text for tweets? (y/n) [{config.TWEETS.RANDOM_TEXT_FOR_TWEETS}]: ").strip().lower()
    if random_text in ['y', 'yes']:
        config.TWEETS.RANDOM_TEXT_FOR_TWEETS = True
    
    random_images = input(f"Use random images for tweets? (y/n) [{config.TWEETS.RANDOM_PICTURE_FOR_TWEETS}]: ").strip().lower()
    if random_images in ['n', 'no']:
        config.TWEETS.RANDOM_PICTURE_FOR_TWEETS = False
    
    print("\n✅ Configuration updated successfully!")
    return config