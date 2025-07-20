# Import from the new modules
from accounts_manager import read_accounts_from_storage, Account
from data_manager import read_txt_file, read_pictures

# For backward compatibility
def read_accounts_from_excel(file_path: str, start_index: int = 1, end_index: int = 0):
    """Backward compatibility function"""
    return read_accounts_from_storage(start_index, end_index)

def split_list(lst, chunk_size=90):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
