"""
Enhanced Data management module for StarLabs Twitter Bot v3.0
Advanced content management with AI integration and analytics
"""

import os
import json
import base64
import random
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger
from dataclasses import dataclass, asdict
from enum import Enum
import re


class ContentType(Enum):
    TWEET = "tweet"
    COMMENT = "comment"
    HASHTAG = "hashtag"
    EMOJI = "emoji"


class ContentQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


@dataclass
class ContentItem:
    text: str
    content_type: ContentType
    created_at: datetime = None
    usage_count: int = 0
    success_rate: float = 0.0
    quality_score: ContentQuality = ContentQuality.AVERAGE
    tags: List[str] = None
    language: str = "en"
    sentiment: str = "neutral"  # positive, negative, neutral
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if not isinstance(self.content_type, ContentType):
            self.content_type = ContentType(self.content_type) if isinstance(self.content_type, str) else ContentType.TWEET
        if not isinstance(self.quality_score, ContentQuality):
            self.quality_score = ContentQuality(self.quality_score) if isinstance(self.quality_score, str) else ContentQuality.AVERAGE
    
    def get_hash(self) -> str:
        """Get unique hash for content"""
        return hashlib.md5(self.text.encode()).hexdigest()[:8]


@dataclass
class MediaItem:
    filename: str
    file_path: str
    base64_data: str
    file_size: int
    dimensions: Tuple[int, int] = (0, 0)
    format: str = ""
    created_at: datetime = None
    usage_count: int = 0
    tags: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []


class EnhancedDataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.content_items: Dict[ContentType, List[ContentItem]] = {
            ContentType.TWEET: [],
            ContentType.COMMENT: [],
            ContentType.HASHTAG: [],
            ContentType.EMOJI: []
        }
        self.media_items: List[MediaItem] = []
        self.templates: Dict[str, List[str]] = {}
        
        self.ensure_data_directory()
        self.init_default_data()
        self.load_all_data()
    
    def ensure_data_directory(self):
        """Ensure data directory and subdirectories exist"""
        directories = [
            self.data_dir,
            os.path.join(self.data_dir, "images"),
            os.path.join(self.data_dir, "content"),
            os.path.join(self.data_dir, "templates"),
            os.path.join(self.data_dir, "analytics")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def init_default_data(self):
        """Initialize default data files if they don't exist"""
        # Default tweet content
        default_tweets = [
            ContentItem("Hello Twitter! 🌟 #TwitterBot", ContentType.TWEET, tags=["greeting", "general"]),
            ContentItem("Having a great day! ☀️ #PositiveVibes", ContentType.TWEET, tags=["positive", "mood"]),
            ContentItem("Building something amazing 🚀 #Innovation", ContentType.TWEET, tags=["tech", "motivation"]),
            ContentItem("Learning new things every day 📚 #Growth", ContentType.TWEET, tags=["education", "personal"]),
            ContentItem("Grateful for this community 🙏 #Thankful", ContentType.TWEET, tags=["gratitude", "community"])
        ]
        
        # Default comment content
        default_comments = [
            ContentItem("Great post! 👍", ContentType.COMMENT, tags=["positive", "engagement"]),
            ContentItem("Thanks for sharing! 🙏", ContentType.COMMENT, tags=["gratitude", "appreciation"]),
            ContentItem("Interesting perspective 🤔", ContentType.COMMENT, tags=["thoughtful", "neutral"]),
            ContentItem("Love this! ❤️", ContentType.COMMENT, tags=["positive", "enthusiasm"]),
            ContentItem("Amazing work! 🔥", ContentType.COMMENT, tags=["praise", "positive"])
        ]
        
        # Default hashtags
        default_hashtags = [
            ContentItem("#TwitterBot", ContentType.HASHTAG, tags=["bot", "automation"]),
            ContentItem("#AI", ContentType.HASHTAG, tags=["technology", "artificial intelligence"]),
            ContentItem("#Innovation", ContentType.HASHTAG, tags=["tech", "progress"]),
            ContentItem("#Community", ContentType.HASHTAG, tags=["social", "networking"]),
            ContentItem("#Growth", ContentType.HASHTAG, tags=["personal", "development"])
        ]
        
        # Default emojis
        default_emojis = [
            ContentItem("🚀", ContentType.EMOJI, tags=["rocket", "launch", "success"]),
            ContentItem("💡", ContentType.EMOJI, tags=["idea", "innovation", "bright"]),
            ContentItem("🔥", ContentType.EMOJI, tags=["fire", "hot", "trending"]),
            ContentItem("⭐", ContentType.EMOJI, tags=["star", "favorite", "excellent"]),
            ContentItem("🎯", ContentType.EMOJI, tags=["target", "goal", "focus"])
        ]
        
        # Initialize content if not exists
        for content_type, default_items in [
            (ContentType.TWEET, default_tweets),
            (ContentType.COMMENT, default_comments),
            (ContentType.HASHTAG, default_hashtags),
            (ContentType.EMOJI, default_emojis)
        ]:
            if not self.content_items[content_type]:
                self.content_items[content_type] = default_items
                self.save_content_items(content_type)
    
    def _serialize_content_item(self, item: ContentItem) -> dict:
        """Serialize content item to dictionary"""
        data = asdict(item)
        data['created_at'] = item.created_at.isoformat()
        data['content_type'] = item.content_type.value
        data['quality_score'] = item.quality_score.value
        return data
    
    def _deserialize_content_item(self, data: dict) -> ContentItem:
        """Deserialize content item from dictionary"""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'content_type' in data:
            data['content_type'] = ContentType(data['content_type'])
        if 'quality_score' in data:
            data['quality_score'] = ContentQuality(data['quality_score'])
        return ContentItem(**data)
    
    def _serialize_media_item(self, item: MediaItem) -> dict:
        """Serialize media item to dictionary"""
        data = asdict(item)
        data['created_at'] = item.created_at.isoformat()
        return data
    
    def _deserialize_media_item(self, data: dict) -> MediaItem:
        """Deserialize media item from dictionary"""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return MediaItem(**data)
    
    def save_content_items(self, content_type: ContentType):
        """Save content items to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "content", f"{content_type.value}_content.json")
            serialized_items = [self._serialize_content_item(item) for item in self.content_items[content_type]]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized_items, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved {len(self.content_items[content_type])} {content_type.value} items")
        except Exception as e:
            logger.error(f"Error saving {content_type.value} content: {e}")
    
    def load_content_items(self, content_type: ContentType) -> List[ContentItem]:
        """Load content items from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "content", f"{content_type.value}_content.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    items = [self._deserialize_content_item(item_data) for item_data in data]
                    self.content_items[content_type] = items
                    logger.success(f"Loaded {len(items)} {content_type.value} items")
                    return items
            else:
                logger.warning(f"No {content_type.value} content file found")
                return []
        except Exception as e:
            logger.error(f"Error loading {content_type.value} content: {e}")
            return []
    
    def load_all_data(self):
        """Load all data from files"""
        for content_type in ContentType:
            self.load_content_items(content_type)
        self.load_media_items()
        self.load_templates()
    
    def save_media_items(self):
        """Save media items to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "media_items.json")
            serialized_items = [self._serialize_media_item(item) for item in self.media_items]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized_items, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved {len(self.media_items)} media items")
        except Exception as e:
            logger.error(f"Error saving media items: {e}")
    
    def load_media_items(self) -> List[MediaItem]:
        """Load media items from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "media_items.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.media_items = [self._deserialize_media_item(item_data) for item_data in data]
                    logger.success(f"Loaded {len(self.media_items)} media items")
            
            # Also scan images directory for new files
            self._scan_images_directory()
            return self.media_items
        except Exception as e:
            logger.error(f"Error loading media items: {e}")
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
                        file_format = filename.split('.')[-1].lower()
                        
                        # Try to get image dimensions
                        dimensions = self._get_image_dimensions(file_path)
                        
                        media_item = MediaItem(
                            filename=filename,
                            file_path=file_path,
                            base64_data=base64_data,
                            file_size=file_size,
                            dimensions=dimensions,
                            format=file_format
                        )
                        
                        self.media_items.append(media_item)
                        logger.info(f"Added new media item: {filename}")
                        
                except Exception as e:
                    logger.error(f"Error processing image {filename}: {e}")
        
        if len(self.media_items) > len(existing_files):
            self.save_media_items()
    
    def _get_image_dimensions(self, file_path: str) -> Tuple[int, int]:
        """Get image dimensions"""
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                return img.size
        except ImportError:
            logger.warning("PIL not available, cannot get image dimensions")
            return (0, 0)
        except Exception as e:
            logger.error(f"Error getting image dimensions: {e}")
            return (0, 0)
    
    def load_templates(self):
        """Load content templates"""
        try:
            templates_dir = os.path.join(self.data_dir, "templates")
            for filename in os.listdir(templates_dir):
                if filename.endswith('.json'):
                    template_name = filename[:-5]  # Remove .json extension
                    file_path = os.path.join(templates_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.templates[template_name] = json.load(f)
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def add_content_item(self, text: str, content_type: ContentType, **kwargs) -> bool:
        """Add a new content item"""
        try:
            # Check for duplicates
            existing_texts = {item.text for item in self.content_items[content_type]}
            if text in existing_texts:
                logger.warning(f"Content already exists: {text[:50]}...")
                return False
            
            new_item = ContentItem(text=text, content_type=content_type, **kwargs)
            self.content_items[content_type].append(new_item)
            self.save_content_items(content_type)
            logger.success(f"Added new {content_type.value}: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error adding content item: {e}")
            return False
    
    def get_content_items(self, content_type: ContentType, 
                         tags: List[str] = None, 
                         quality_filter: List[ContentQuality] = None,
                         limit: int = None) -> List[ContentItem]:
        """Get content items with filtering"""
        items = self.content_items[content_type]
        
        # Apply tag filter
        if tags:
            items = [item for item in items if any(tag in item.tags for tag in tags)]
        
        # Apply quality filter
        if quality_filter:
            items = [item for item in items if item.quality_score in quality_filter]
        
        # Apply limit
        if limit:
            items = items[:limit]
        
        return items
    
    def get_random_content(self, content_type: ContentType, **filters) -> Optional[ContentItem]:
        """Get random content item with filters"""
        items = self.get_content_items(content_type, **filters)
        if items:
            # Weighted selection based on quality and usage
            weights = []
            for item in items:
                weight = 1.0
                if item.quality_score == ContentQuality.EXCELLENT:
                    weight *= 2.0
                elif item.quality_score == ContentQuality.GOOD:
                    weight *= 1.5
                elif item.quality_score == ContentQuality.POOR:
                    weight *= 0.5
                
                # Reduce weight for frequently used items
                if item.usage_count > 10:
                    weight *= 0.8
                
                weights.append(weight)
            
            return random.choices(items, weights=weights)[0]
        return None
    
    def generate_enhanced_content(self, base_text: str, content_type: ContentType) -> str:
        """Generate enhanced content with emojis and hashtags"""
        enhanced_text = base_text
        
        # Add emojis if enabled
        if random.random() < 0.7:  # 70% chance to add emoji
            emoji_item = self.get_random_content(ContentType.EMOJI)
            if emoji_item:
                enhanced_text += f" {emoji_item.text}"
        
        # Add hashtags for tweets
        if content_type == ContentType.TWEET and random.random() < 0.8:  # 80% chance
            hashtag_item = self.get_random_content(ContentType.HASHTAG)
            if hashtag_item:
                enhanced_text += f" {hashtag_item.text}"
        
        return enhanced_text
    
    def update_content_usage(self, content_hash: str, success: bool):
        """Update content usage statistics"""
        for content_type in ContentType:
            for item in self.content_items[content_type]:
                if item.get_hash() == content_hash:
                    item.usage_count += 1
                    if success:
                        # Update success rate
                        total_successes = item.success_rate * (item.usage_count - 1) / 100
                        total_successes += 1
                        item.success_rate = (total_successes / item.usage_count) * 100
                    else:
                        # Update success rate for failure
                        total_successes = item.success_rate * (item.usage_count - 1) / 100
                        item.success_rate = (total_successes / item.usage_count) * 100
                    
                    self.save_content_items(content_type)
                    return
    
    def get_content_analytics(self) -> Dict:
        """Get comprehensive content analytics"""
        analytics = {
            "total_items": 0,
            "by_type": {},
            "by_quality": {},
            "top_performing": [],
            "least_used": [],
            "average_success_rate": 0
        }
        
        all_items = []
        for content_type in ContentType:
            items = self.content_items[content_type]
            all_items.extend(items)
            analytics["by_type"][content_type.value] = len(items)
        
        analytics["total_items"] = len(all_items)
        
        # Quality breakdown
        for quality in ContentQuality:
            count = len([item for item in all_items if item.quality_score == quality])
            analytics["by_quality"][quality.value] = count
        
        # Top performing content
        sorted_by_success = sorted(all_items, key=lambda x: x.success_rate, reverse=True)
        analytics["top_performing"] = [
            {"text": item.text[:50], "success_rate": item.success_rate, "usage_count": item.usage_count}
            for item in sorted_by_success[:5]
        ]
        
        # Least used content
        sorted_by_usage = sorted(all_items, key=lambda x: x.usage_count)
        analytics["least_used"] = [
            {"text": item.text[:50], "usage_count": item.usage_count}
            for item in sorted_by_usage[:5]
        ]
        
        # Average success rate
        if all_items:
            analytics["average_success_rate"] = sum(item.success_rate for item in all_items) / len(all_items)
        
        return analytics
    
    def export_content(self, filename: str, content_type: ContentType = None, format: str = "json") -> bool:
        """Export content to file"""
        try:
            if content_type:
                items = self.content_items[content_type]
            else:
                items = []
                for ct in ContentType:
                    items.extend(self.content_items[ct])
            
            if format.lower() == "json":
                serialized_items = [self._serialize_content_item(item) for item in items]
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(serialized_items, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "txt":
                with open(filename, 'w', encoding='utf-8') as f:
                    for item in items:
                        f.write(f"{item.text}\n")
            
            elif format.lower() == "csv":
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Text', 'Type', 'Usage Count', 'Success Rate', 'Quality', 'Tags'])
                    for item in items:
                        writer.writerow([
                            item.text,
                            item.content_type.value,
                            item.usage_count,
                            f"{item.success_rate:.2f}%",
                            item.quality_score.value,
                            ', '.join(item.tags)
                        ])
            
            logger.success(f"Exported {len(items)} items to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting content: {e}")
            return False
    
    def interactive_manage_content(self):
        """Enhanced interactive content management"""
        while True:
            analytics = self.get_content_analytics()
            
            print("\n📝 Enhanced Content Management")
            print("=" * 50)
            print(f"📊 Total content items: {analytics['total_items']}")
            print(f"📈 Average success rate: {analytics['average_success_rate']:.1f}%")
            
            print("\n[1] Manage tweets")
            print("[2] Manage comments")
            print("[3] Manage hashtags")
            print("[4] Manage emojis")
            print("[5] Content analytics")
            print("[6] Bulk operations")
            print("[7] Import/Export")
            print("[8] Content templates")
            print("[9] Media management")
            print("[10] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._manage_content_type(ContentType.TWEET)
            elif choice == "2":
                self._manage_content_type(ContentType.COMMENT)
            elif choice == "3":
                self._manage_content_type(ContentType.HASHTAG)
            elif choice == "4":
                self._manage_content_type(ContentType.EMOJI)
            elif choice == "5":
                self._show_content_analytics()
            elif choice == "6":
                self._bulk_content_operations()
            elif choice == "7":
                self._import_export_content()
            elif choice == "8":
                self._manage_templates()
            elif choice == "9":
                self._manage_media()
            elif choice == "10":
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
            print(f"[4] Edit {content_type.value}")
            print(f"[5] Delete {content_type.value}")
            print(f"[6] Quality management")
            print("[7] Back")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._add_content_interactive(content_type)
            elif choice == "2":
                self._view_content(content_type)
            elif choice == "3":
                self._search_content(content_type)
            elif choice == "4":
                self._edit_content(content_type)
            elif choice == "5":
                self._delete_content(content_type)
            elif choice == "6":
                self._manage_content_quality(content_type)
            elif choice == "7":
                break
    
    def _add_content_interactive(self, content_type: ContentType):
        """Interactive content addition"""
        print(f"\nAdd {content_type.value.title()} Content")
        print("Enter content (empty line to finish):")
        
        while True:
            text = input(f"{content_type.value.title()}: ").strip()
            if not text:
                break
            
            tags = input("Tags (comma separated, optional): ").strip()
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
            
            quality = input("Quality (excellent/good/average/poor) [average]: ").strip().lower()
            quality_map = {
                "excellent": ContentQuality.EXCELLENT,
                "good": ContentQuality.GOOD,
                "average": ContentQuality.AVERAGE,
                "poor": ContentQuality.POOR
            }
            quality_score = quality_map.get(quality, ContentQuality.AVERAGE)
            
            if self.add_content_item(text, content_type, tags=tag_list, quality_score=quality_score):
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
                quality_emoji = {"excellent": "⭐", "good": "👍", "average": "➖", "poor": "👎"}
                emoji = quality_emoji.get(item.quality_score.value, "➖")
                print(f"{i:2d}. {emoji} {item.text[:60]}{'...' if len(item.text) > 60 else ''}")
                print(f"    📊 Used: {item.usage_count} | Success: {item.success_rate:.1f}% | Tags: {', '.join(item.tags[:3])}")
            
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
    
    def _show_content_analytics(self):
        """Show detailed content analytics"""
        analytics = self.get_content_analytics()
        
        print("\n📊 Content Analytics Dashboard")
        print("=" * 50)
        print(f"Total Items: {analytics['total_items']}")
        print(f"Average Success Rate: {analytics['average_success_rate']:.2f}%")
        
        print("\n📈 Content by Type:")
        for content_type, count in analytics['by_type'].items():
            print(f"  {content_type.title()}: {count}")
        
        print("\n🏆 Quality Distribution:")
        for quality, count in analytics['by_quality'].items():
            print(f"  {quality.title()}: {count}")
        
        print("\n🔥 Top Performing Content:")
        for i, item in enumerate(analytics['top_performing'], 1):
            print(f"  {i}. {item['text']}... ({item['success_rate']:.1f}% success, {item['usage_count']} uses)")
        
        print("\n💤 Least Used Content:")
        for i, item in enumerate(analytics['least_used'], 1):
            print(f"  {i}. {item['text']}... ({item['usage_count']} uses)")
        
        input("\nPress Enter to continue...")
    
    def _manage_media(self):
        """Manage media files"""
        print("\n🖼️ Media Management")
        print(f"Total media items: {len(self.media_items)}")
        
        print("\n[1] View media items")
        print("[2] Add media description")
        print("[3] Media analytics")
        print("[4] Rescan images directory")
        
        choice = input("Your choice: ").strip()
        
        if choice == "1":
            self._view_media_items()
        elif choice == "2":
            self._add_media_description()
        elif choice == "3":
            self._show_media_analytics()
        elif choice == "4":
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
            print(f"    📏 {item.dimensions[0]}x{item.dimensions[1]} | 💾 {size_mb:.2f}MB | 🔄 Used: {item.usage_count}")
            if item.description:
                print(f"    📝 {item.description}")
    
    def _show_media_analytics(self):
        """Show media analytics"""
        if not self.media_items:
            print("📭 No media analytics available")
            return
        
        total_size = sum(item.file_size for item in self.media_items)
        total_usage = sum(item.usage_count for item in self.media_items)
        
        print("\n📊 Media Analytics")
        print("=" * 30)
        print(f"Total Files: {len(self.media_items)}")
        print(f"Total Size: {total_size / (1024 * 1024):.2f} MB")
        print(f"Total Usage: {total_usage}")
        print(f"Average Usage: {total_usage / len(self.media_items):.1f}")
        
        # Most used media
        sorted_media = sorted(self.media_items, key=lambda x: x.usage_count, reverse=True)
        print("\n🔥 Most Used Media:")
        for item in sorted_media[:5]:
            print(f"  {item.filename} - {item.usage_count} uses")
    
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


def get_data_manager() -> EnhancedDataManager:
    """Get data manager singleton"""
    global _data_manager
    if _data_manager is None:
        _data_manager = EnhancedDataManager()
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