# Import from the new config module
from config import get_config, Config, update_config, configure_bot

# Re-export for compatibility
__all__ = ['get_config', 'Config', 'update_config', 'configure_bot']
