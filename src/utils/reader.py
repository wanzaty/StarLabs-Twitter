# Import from the new modules
from accounts_manager import read_accounts_from_storage, Account
try:
    from data_manager import read_txt_file, read_pictures
except ImportError:
    # Fallback implementations
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
        return images

# For backward compatibility
def read_accounts_from_excel(file_path: str, start_index: int = 1, end_index: int = 0):
    """Backward compatibility function"""
    return read_accounts_from_storage(start_index, end_index)

def split_list(lst, chunk_size=90):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]