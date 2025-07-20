"""
Simple Data management module for StarLabs Twitter Bot v3.0
Text-based content management with analytics
"""

import os
import base64
import random
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger
from enum import Enum


class ContentType(Enum):
    TWEET = "tweet"
    COMMENT = "comment"




class ContentItem:
    def __init__(self, text: str, content_type: ContentType, usage_count: int = 0):
        self.text = text
        self.content_type = content_type
        self.usage_count = usage_count
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    


class MediaItem:
    def __init__(self, filename: str, file_path: str, base64_data: str, file_size: int):
        self.filename = filename
        self.file_path = file_path
        self.base64_data = base64_data
        self.file_size = file_size
        self.usage_count = 0
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    


class SimpleDataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.content_items: Dict[ContentType, List[ContentItem]] = {
            ContentType.TWEET: [],
            ContentType.COMMENT: [],
        }
        self.media_items: List[MediaItem] = []
        
        self.ensure_data_directory()
        self.init_default_data()
        self.load_all_data()
    
    def ensure_data_directory(self):
        """Ensure data directory and subdirectories exist"""
        directories = [
            self.data_dir,
            os.path.join(self.data_dir, "images"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def init_default_data(self):
        """Initialize default data files if they don't exist"""
        # Default tweet content
        default_tweets = [
            ContentItem("Hello Twitter! 🌟 #TwitterBot", ContentType.TWEET),
            ContentItem("Having a great day! ☀️ #PositiveVibes", ContentType.TWEET),
            ContentItem("Building something amazing 🚀 #Innovation", ContentType.TWEET),
            ContentItem("Learning new things every day 📚 #Growth", ContentType.TWEET),
            ContentItem("Grateful for this community 🙏 #Thankful", ContentType.TWEET)
        ]
        
        # Default comment content
        default_comments = [
            ContentItem("Great post! 👍", ContentType.COMMENT),
            ContentItem("Thanks for sharing! 🙏", ContentType.COMMENT),
            ContentItem("Interesting perspective 🤔", ContentType.COMMENT),
            ContentItem("Love this! ❤️", ContentType.COMMENT),
            ContentItem("Amazing work! 🔥", ContentType.COMMENT)
        ]
        
        # Initialize content if not exists
        for content_type, default_items in [
            (ContentType.TWEET, default_tweets),
            (ContentType.COMMENT, default_comments),
        ]:
            if not self.content_items[content_type]:
                self.content_items[content_type] = default_items
                self.save_content_items(content_type)
    
    def _content_item_to_line(self, item: ContentItem) -> str:
        """Convert content item to text line"""
        return f"{item.text}|{item.content_type.value}|{item.usage_count}|{item.created_at}"
    
    def _line_to_content_item(self, line: str) -> ContentItem:
        """Convert text line to content item"""
        parts = line.strip().split('|')
        if len(parts) >= 2:
            text = parts[0]
            content_type = ContentType(parts[1])
            usage_count = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
            item = ContentItem(text, content_type, usage_count)
            if len(parts) > 3:
                item.created_at = parts[3]
            return item
        return None
    
    def save_content_items(self, content_type: ContentType):
        """Save content items to TXT file"""
        try:
            file_path = os.path.join(self.data_dir, f"{content_type.value}s.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in self.content_items[content_type]:
                    f.write(self._content_item_to_line(item) + '\n')
            logger.success(f"Saved {len(self.content_items[content_type])} {content_type.value} items")
        except Exception as e:
            logger.error(f"Error saving {content_type.value} content: {e}")
    
    def load_content_items(self, content_type: ContentType) -> List[ContentItem]:
        """Load content items from TXT file"""
        try:
            file_path = os.path.join(self.data_dir, f"{content_type.value}s.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    items = []
                    for line in lines:
                        if line.strip():
                            item = self._line_to_content_item(line)
                            if item:
                                items.append(item)
                    self.content_items[content_type] = items
                    logger.success(f"Loaded {len(items)} {content_type.value} items")
                    return items
            else:
                logger.warning(f"No {content_type.value} content file found")
                return []
        except Exception as e:
            logger.error(f"Error loading {content_type.value} content: {e}")
            return []
    
    def save_media_items(self):
        """Save media items to file"""
        # For text-based system, we don't need to save media items
        # They are automatically scanned from the images directory
        pass
    
    def load_all_data(self):
        """Load all data from files"""
        for content_type in ContentType:
            self.load_content_items(content_type)
        self.load_media_items()
    
    def load_media_items(self) -> List[MediaItem]:
        """Load media items from images directory"""
        try:
            # For simplicity, just scan the images directory
            self.media_items = []
            self._scan_images_directory()
            logger.success(f"Loaded {len(self.media_items)} media items")
            return self.media_items
        except Exception as e:
            logger.error(f"Error loading media items: {e}")
            self.media_items = []
            return []
    def _scan_images_directory(self):
        """Scan images directory for new files"""
        images_dir = os.path.join(self.data_dir, "images")
        if not os.path.exists(images_dir):
            return
        
        existing_files = {item.filename for item in self.media_items}
        
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) and filename not in existing_files:
                try:
                    file_path = os.path.join(images_dir, filename)
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                        base64_data = base64.b64encode(file_data).decode('utf-8')
                        
                        # Get file info
                        file_size = len(file_data)
                        
                        media_item = MediaItem(
                            filename=filename,
                            file_path=file_path,
                            base64_data=base64_data,
                            file_size=file_size
                        )
                        
                        self.media_items.append(media_item)
                        logger.info(f"Added new media item: {filename}")
                        
                except Exception as e:
                    logger.error(f"Error processing image {filename}: {e}")
    
    def add_content_item(self, text: str, content_type: ContentType, **kwargs) -> bool:
        """Add a new content item"""
        try:
            # Check for duplicates
            existing_texts = {item.text for item in self.content_items[content_type]}
            if text in existing_texts:
                logger.warning(f"Content already exists: {text[:50]}...")
                return False
            
            new_item = ContentItem(text, content_type)
            self.content_items[content_type].append(new_item)
            self.save_content_items(content_type)
            logger.success(f"Added new {content_type.value}: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error adding content item: {e}")
            return False
    
    def get_content_items(self, content_type: ContentType, 
                         limit: int = None) -> List[ContentItem]:
        """Get content items with filtering"""
        items = self.content_items[content_type]
        
        # Apply limit
        if limit:
            items = items[:limit]
        
        return items
    
    def get_random_content(self, content_type: ContentType, **filters) -> Optional[ContentItem]:
        """Get random content item with filters"""
        items = self.get_content_items(content_type, **filters)
        if items:
            return random.choice(items)
        return None
    
    def update_content_usage(self, text: str, content_type: ContentType):
        """Update content usage statistics"""
        for item in self.content_items[content_type]:
            if item.text == text:
                item.usage_count += 1
                self.save_content_items(content_type)
                return
    
    def export_content(self, filename: str, content_type: ContentType = None, format: str = "txt") -> bool:
        """Export content to file"""
        try:
            if content_type:
                items = self.content_items[content_type]
            else:
                items = []
                for ct in ContentType:
                    items.extend(self.content_items[ct])
            
            if format.lower() == "txt":
                with open(filename, 'w', encoding='utf-8') as f:
                    for item in items:
                        f.write(self._content_item_to_line(item) + '\n')
            
            elif format.lower() == "csv":
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Text', 'Type', 'Usage Count', 'Created At'])
                    for item in items:
                        writer.writerow([
                            item.text,
                            item.content_type.value,
                            item.usage_count,
                            item.created_at
                        ])
            
            logger.success(f"Exported {len(items)} items to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting content: {e}")
            return False
    
    def interactive_manage_texts(self):
        """Interactive text management"""
        while True:
            print("\n📝 Text Management")
            print("=" * 50)
            tweet_count = len(self.content_items[ContentType.TWEET])
            comment_count = len(self.content_items[ContentType.COMMENT])
            print(f"📊 Tweets: {tweet_count} | Comments: {comment_count}")
            
            print("\n[1] Manage tweets")
            print("[2] Manage comments")
            print("[3] Import/Export")
            print("[4] Media management")
            print("[5] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._manage_content_type(ContentType.TWEET)
            elif choice == "2":
                self._manage_content_type(ContentType.COMMENT)
            elif choice == "3":
                self._import_export_content()
            elif choice == "4":
                self._manage_media()
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice")
    
    def _manage_content_type(self, content_type: ContentType):
        """Manage specific content type"""
        while True:
            items = self.content_items[content_type]
            print(f"\n📝 {content_type.value.title()} Management")
            print(f"Current items: {len(items)}")
            
            print(f"\n[1] Add {content_type.value}")
            print(f"[2] View all {content_type.value}s")
            print(f"[3] Search {content_type.value}s")
            print(f"[4] Delete {content_type.value}")
            print("[5] Back")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._add_content_interactive(content_type)
            elif choice == "2":
                self._view_content(content_type)
            elif choice == "3":
                self._search_content(content_type)
            elif choice == "4":
                self._delete_content(content_type)
            elif choice == "5":
                break
    
    def _add_content_interactive(self, content_type: ContentType):
        """Interactive content addition"""
        print(f"\nAdd {content_type.value.title()} Content")
        print("Enter content (empty line to finish):")
        
        while True:
            text = input(f"{content_type.value.title()}: ").strip()
            if not text:
                break
            
            if self.add_content_item(text, content_type):
                print("✅ Content added successfully!")
            else:
                print("❌ Failed to add content (might already exist)")
    
    def _view_content(self, content_type: ContentType):
        """View content with pagination"""
        items = self.content_items[content_type]
        if not items:
            print(f"📭 No {content_type.value} content found")
            return
        
        page_size = 10
        total_pages = (len(items) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(items))
            page_items = items[start_idx:end_idx]
            
            print(f"\n📋 {content_type.value.title()} Content (Page {current_page}/{total_pages})")
            print("-" * 80)
            
            for i, item in enumerate(page_items, start_idx + 1):
                print(f"{i:2d}. {item.text[:60]}{'...' if len(item.text) > 60 else ''}")
                print(f"    📊 Used: {item.usage_count} times | Created: {item.created_at}")
            
            if total_pages > 1:
                print(f"\n[n]ext page | [p]revious page | [q]uit")
                nav = input("Navigation: ").strip().lower()
                if nav == 'n' and current_page < total_pages:
                    current_page += 1
                elif nav == 'p' and current_page > 1:
                    current_page -= 1
                elif nav == 'q':
                    break
            else:
                input("\nPress Enter to continue...")
                break
    
    def _search_content(self, content_type: ContentType):
        """Search content"""
        search_term = input("Search term: ").strip().lower()
        if not search_term:
            return
        
        results = [item for item in self.content_items[content_type] 
                  if search_term in item.text.lower()]
        
        if results:
            print(f"\n🎯 Found {len(results)} matching items:")
            for i, item in enumerate(results, 1):
                print(f"{i}. {item.text[:60]}{'...' if len(item.text) > 60 else ''}")
        else:
            print("❌ No matching content found")
    
    def _delete_content(self, content_type: ContentType):
        """Delete content"""
        if not self.content_items[content_type]:
            print("📭 No content to delete")
            return
        
        print(f"\n🗑️ Delete {content_type.value.title()} Content")
        for i, item in enumerate(self.content_items[content_type], 1):
            print(f"{i}. {item.text[:60]}{'...' if len(item.text) > 60 else ''}")
        
        try:
            index = int(input("\nEnter number to delete (0 to cancel): ")) - 1
            if index >= 0 and index < len(self.content_items[content_type]):
                deleted_item = self.content_items[content_type].pop(index)
                self.save_content_items(content_type)
                print(f"✅ Deleted: {deleted_item.text[:50]}...")
            elif index != -1:
                print("❌ Invalid number")
        except ValueError:
            print("❌ Invalid input")
    
    def _import_export_content(self):
        """Import/Export content"""
        print("\n💾 Import/Export Content")
        print("[1] Export tweets")
        print("[2] Export comments")
        print("[3] Import tweets")
        print("[4] Import comments")
        
        choice = input("Your choice: ").strip()
        
        if choice in ["1", "2"]:
            content_type = ContentType.TWEET if choice == "1" else ContentType.COMMENT
            filename = input("Export filename: ").strip()
            if filename:
                if self.export_content(filename, content_type):
                    print(f"✅ Content exported to {filename}")
                else:
                    print("❌ Export failed")
        
        elif choice in ["3", "4"]:
            content_type = ContentType.TWEET if choice == "3" else ContentType.COMMENT
            filename = input("Import filename: ").strip()
            if filename and os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        imported = 0
                        for line in lines:
                            text = line.strip()
                            if text and self.add_content_item(text, content_type):
                                imported += 1
                    print(f"✅ Imported {imported} items")
                except Exception as e:
                    print(f"❌ Import failed: {e}")
            else:
                print("❌ File not found")
    
    def _manage_media(self):
        """Manage media files"""
        print("\n🖼️ Media Management")
        print(f"Total media items: {len(self.media_items)}")
        
        print("\n[1] View media items")
        print("[2] Rescan images directory")
        
        choice = input("Your choice: ").strip()
        
        if choice == "1":
            self._view_media_items()
        elif choice == "2":
            self._scan_images_directory()
            print("✅ Images directory rescanned")
    
    def _view_media_items(self):
        """View media items"""
        if not self.media_items:
            print("📭 No media items found")
            return
        
        print(f"\n🖼️ Media Items ({len(self.media_items)} total):")
        print("-" * 80)
        
        for i, item in enumerate(self.media_items, 1):
            size_mb = item.file_size / (1024 * 1024)
            print(f"{i:2d}. {item.filename}")
            print(f"    💾 {size_mb:.2f}MB | 🔄 Used: {item.usage_count} times")
    
    # Legacy compatibility methods
    def load_tweet_texts(self) -> List[str]:
        """Legacy method for backward compatibility"""
        items = self.get_content_items(ContentType.TWEET)
        return [item.text for item in items]
    
    def load_comment_texts(self) -> List[str]:
        """Legacy method for backward compatibility"""
        items = self.get_content_items(ContentType.COMMENT)
        return [item.text for item in items]
    
    def load_images_as_base64(self) -> List[str]:
        """Legacy method for backward compatibility"""
        return [item.base64_data for item in self.media_items]


# Global data manager instance
_data_manager = None


def get_data_manager() -> SimpleDataManager:
    """Get data manager singleton"""
    global _data_manager
    if _data_manager is None:
        _data_manager = SimpleDataManager()
    return _data_manager


def read_txt_file(file_name: str, file_type: str = "tweet") -> List[str]:
    """Read text file"""
    manager = get_data_manager()
    if file_type == "tweet":
        return manager.load_tweet_texts()
    elif file_type == "comment":
        return manager.load_comment_texts()
    else:
        logger.error(f"Unknown file type: {file_type}")
        return []


async def read_pictures(images_dir: str = None) -> List[str]:
    """Read pictures"""
    manager = get_data_manager()
    return manager.load_images_as_base64()