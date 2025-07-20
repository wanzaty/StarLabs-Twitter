"""
Data management module for StarLabs Twitter Bot
Handles tweet texts, comments, and images in Python format
"""

import os
import json
import base64
from typing import List, Dict
from loguru import logger


class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        self.init_default_data()

    def ensure_data_directory(self):
        """Ensure data directory and subdirectories exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "images"), exist_ok=True)

    def init_default_data(self):
        """Initialize default data files if they don't exist"""
        # Default tweet texts
        tweet_file = os.path.join(self.data_dir, "tweet_texts.json")
        if not os.path.exists(tweet_file):
            default_tweets = [
                "Hello Twitter! 🌟",
                "Having a great day! ☀️",
                "Building something amazing 🚀",
                "Learning new things every day 📚",
                "Grateful for this community 🙏"
            ]
            self.save_tweet_texts(default_tweets)

        # Default comment texts
        comment_file = os.path.join(self.data_dir, "comment_texts.json")
        if not os.path.exists(comment_file):
            default_comments = [
                "Great post! 👍",
                "Thanks for sharing! 🙏",
                "Interesting perspective 🤔",
                "Love this! ❤️",
                "Amazing work! 🔥"
            ]
            self.save_comment_texts(default_comments)

    def save_tweet_texts(self, texts: List[str]):
        """Save tweet texts to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "tweet_texts.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(texts, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved {len(texts)} tweet texts")
        except Exception as e:
            logger.error(f"Error saving tweet texts: {e}")

    def load_tweet_texts(self) -> List[str]:
        """Load tweet texts from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "tweet_texts.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    texts = json.load(f)
                logger.success(f"Loaded {len(texts)} tweet texts")
                return texts
            else:
                logger.warning("No tweet texts file found")
                return []
        except Exception as e:
            logger.error(f"Error loading tweet texts: {e}")
            return []

    def save_comment_texts(self, texts: List[str]):
        """Save comment texts to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "comment_texts.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(texts, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved {len(texts)} comment texts")
        except Exception as e:
            logger.error(f"Error saving comment texts: {e}")

    def load_comment_texts(self) -> List[str]:
        """Load comment texts from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "comment_texts.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    texts = json.load(f)
                logger.success(f"Loaded {len(texts)} comment texts")
                return texts
            else:
                logger.warning("No comment texts file found")
                return []
        except Exception as e:
            logger.error(f"Error loading comment texts: {e}")
            return []

    def load_images_as_base64(self) -> List[str]:
        """Load images from directory and encode as base64"""
        encoded_images = []
        images_dir = os.path.join(self.data_dir, "images")
        
        try:
            if not os.path.exists(images_dir):
                logger.warning(f"Images directory not found: {images_dir}")
                return encoded_images

            files = os.listdir(images_dir)
            if not files:
                logger.warning(f"No files found in {images_dir}")
                return encoded_images

            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(images_dir, filename)
                    try:
                        with open(image_path, "rb") as image_file:
                            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                            encoded_images.append(encoded_image)
                    except Exception as e:
                        logger.error(f"Error loading image {filename}: {e}")

            logger.success(f"Loaded {len(encoded_images)} images")
        except Exception as e:
            logger.error(f"Error loading images: {e}")

        return encoded_images

    def add_tweet_text(self, text: str):
        """Add a new tweet text"""
        texts = self.load_tweet_texts()
        if text not in texts:
            texts.append(text)
            self.save_tweet_texts(texts)
            return True
        return False

    def add_comment_text(self, text: str):
        """Add a new comment text"""
        texts = self.load_comment_texts()
        if text not in texts:
            texts.append(text)
            self.save_comment_texts(texts)
            return True
        return False

    def interactive_manage_texts(self):
        """Interactive text management"""
        while True:
            print("\n📝 Text Management")
            print("=" * 30)
            print("[1] Manage tweet texts")
            print("[2] Manage comment texts")
            print("[3] View current texts")
            print("[4] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._manage_tweet_texts()
            elif choice == "2":
                self._manage_comment_texts()
            elif choice == "3":
                self._view_all_texts()
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice")

    def _manage_tweet_texts(self):
        """Manage tweet texts"""
        while True:
            print("\n🐦 Tweet Texts Management")
            print("-" * 30)
            texts = self.load_tweet_texts()
            print(f"Current tweet texts: {len(texts)}")
            
            print("\n[1] Add tweet text")
            print("[2] View all tweet texts")
            print("[3] Replace all tweet texts")
            print("[4] Back")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                text = input("Enter new tweet text: ").strip()
                if text:
                    if self.add_tweet_text(text):
                        print("✅ Tweet text added!")
                    else:
                        print("⚠️ Tweet text already exists")
            elif choice == "2":
                self._view_texts(texts, "Tweet")
            elif choice == "3":
                self._replace_all_tweet_texts()
            elif choice == "4":
                break

    def _manage_comment_texts(self):
        """Manage comment texts"""
        while True:
            print("\n💬 Comment Texts Management")
            print("-" * 30)
            texts = self.load_comment_texts()
            print(f"Current comment texts: {len(texts)}")
            
            print("\n[1] Add comment text")
            print("[2] View all comment texts")
            print("[3] Replace all comment texts")
            print("[4] Back")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                text = input("Enter new comment text: ").strip()
                if text:
                    if self.add_comment_text(text):
                        print("✅ Comment text added!")
                    else:
                        print("⚠️ Comment text already exists")
            elif choice == "2":
                self._view_texts(texts, "Comment")
            elif choice == "3":
                self._replace_all_comment_texts()
            elif choice == "4":
                break

    def _view_texts(self, texts: List[str], text_type: str):
        """View texts"""
        if not texts:
            print(f"📭 No {text_type.lower()} texts found")
            return
        
        print(f"\n📋 {text_type} Texts ({len(texts)} total):")
        print("-" * 50)
        for i, text in enumerate(texts, 1):
            print(f"{i:2d}. {text}")

    def _view_all_texts(self):
        """View all texts"""
        tweet_texts = self.load_tweet_texts()
        comment_texts = self.load_comment_texts()
        images = self.load_images_as_base64()
        
        print("\n📊 Current Data Summary")
        print("=" * 30)
        print(f"Tweet texts: {len(tweet_texts)}")
        print(f"Comment texts: {len(comment_texts)}")
        print(f"Images: {len(images)}")
        
        if tweet_texts:
            print(f"\nFirst few tweet texts:")
            for i, text in enumerate(tweet_texts[:3], 1):
                print(f"  {i}. {text}")
        
        if comment_texts:
            print(f"\nFirst few comment texts:")
            for i, text in enumerate(comment_texts[:3], 1):
                print(f"  {i}. {text}")

    def _replace_all_tweet_texts(self):
        """Replace all tweet texts"""
        print("\nEnter new tweet texts (one per line, empty line to finish):")
        texts = []
        while True:
            text = input(f"Tweet {len(texts) + 1}: ").strip()
            if not text:
                break
            texts.append(text)
        
        if texts:
            self.save_tweet_texts(texts)
            print(f"✅ Replaced with {len(texts)} tweet texts!")
        else:
            print("❌ No texts entered")

    def _replace_all_comment_texts(self):
        """Replace all comment texts"""
        print("\nEnter new comment texts (one per line, empty line to finish):")
        texts = []
        while True:
            text = input(f"Comment {len(texts) + 1}: ").strip()
            if not text:
                break
            texts.append(text)
        
        if texts:
            self.save_comment_texts(texts)
            print(f"✅ Replaced with {len(texts)} comment texts!")
        else:
            print("❌ No texts entered")


# Global data manager instance
_data_manager = None


def get_data_manager() -> DataManager:
    """Get data manager singleton"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def read_txt_file(file_name: str, file_type: str = "tweet") -> List[str]:
    """Read text file (replaces old txt file functionality)"""
    manager = get_data_manager()
    if file_type == "tweet":
        return manager.load_tweet_texts()
    elif file_type == "comment":
        return manager.load_comment_texts()
    else:
        logger.error(f"Unknown file type: {file_type}")
        return []


async def read_pictures(images_dir: str = None) -> List[str]:
    """Read pictures (replaces old picture reading functionality)"""
    manager = get_data_manager()
    return manager.load_images_as_base64()