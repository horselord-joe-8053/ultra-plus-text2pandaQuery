from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from config.profiles.base_profile import DataProfile

from config.logging_config import get_logger

logger = get_logger(__name__)

# =============================================================================
# CONFIGURATION - Change this to switch profiles
# =============================================================================
PROFILE_NAME = "default_profile"  # Options: "default_profile", "customized_profile"

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
BASE_DIR = Path(__file__).parent.parent.resolve()

# API Configuration
GENERATION_MODEL = "gemini-1.5-flash"
PORT = 7788

@dataclass
class Config:
    google_api_key: str
    generation_model: str
    port: int
    profile_name: str


def load_config() -> Config:
    """Load configuration with all settings embedded."""
    # Note: API keys are now loaded dynamically through provider configurations
    # This maintains backward compatibility while removing hardcoded dependencies
    return Config(
        google_api_key="PLACEHOLDER",  # Will be loaded dynamically via provider config
        generation_model=GENERATION_MODEL,
        port=PORT,
        profile_name=PROFILE_NAME,
    )


def load_profile(config: Config) -> 'DataProfile':
    """Load the appropriate data profile based on configuration."""
    from .profiles.profile_factory import ProfileFactory
    
    try:
        return ProfileFactory.create_profile(config.profile_name)
    except (ValueError, ImportError) as e:
        logger.warning(f"Failed to load profile '{config.profile_name}': {e}")
        logger.info("Falling back to default profile")
        return ProfileFactory.get_default_profile()


