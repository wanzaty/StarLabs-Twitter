from .client import create_twitter_client, get_headers

# Safe imports with fallbacks
try:
    from .reader import read_txt_file, read_accounts_from_excel, read_pictures
except ImportError:
    # Fallback for missing functions
    def read_txt_file(file_name: str, file_type: str = "tweet") -> list:
        """Fallback function for reading text files"""
        import os
        file_path = f"data/{file_type}s.txt"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    return [line.split('|')[0].strip() for line in lines if line.strip() and not line.startswith('#')]
            except Exception:
                pass
        return []
    
    def read_accounts_from_excel(file_path: str, start_index: int = 1, end_index: int = 0) -> list:
        """Fallback function for reading accounts"""
        try:
            from accounts_manager import read_accounts_from_storage
            return read_accounts_from_storage(start_index, end_index)
        except ImportError:
            return []
    
    async def read_pictures(images_dir: str = None) -> list:
        """Fallback function for reading pictures"""
        import os
        import base64
        
        if images_dir is None:
            images_dir = "data/images"
        
        images = []
        if os.path.exists(images_dir):
            try:
                for filename in os.listdir(images_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        file_path = os.path.join(images_dir, filename)
                        try:
                            with open(file_path, "rb") as f:
                                file_data = f.read()
                                base64_data = base64.b64encode(file_data).decode('utf-8')
                                images.append(base64_data)
                        except Exception:
                            continue
            except Exception:
                pass
        return []

from .output import show_dev_info, show_logo, show_menu
from .config import get_config
from .proxy_parser import Proxy
from .constants import Account, MAIN_MENU_OPTIONS

# Safe imports for optional modules
try:
    from .config_browser import run
except ImportError:
    def run():
        print("Config browser not available")

try:
    from .logs import update_account_in_excel
except ImportError:
    def update_account_in_excel(*args, **kwargs):
        pass

try:
    from .check_github_version import check_version
except ImportError:
    async def check_version(*args, **kwargs):
        return True

__all__ = [
    "Account",
    "create_twitter_client",
    "get_headers",
    "read_txt_file",
    "show_dev_info",
    "show_logo",
    "Proxy",
    "run",
    "get_config",
    "read_accounts_from_excel",
    "read_pictures",
    "update_account_in_excel",
    "show_menu",
    "MAIN_MENU_OPTIONS",
    "check_version",
]