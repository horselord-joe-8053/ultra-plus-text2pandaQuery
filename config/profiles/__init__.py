"""Profile system for data schema and LLM configuration management."""

from .base_profile import DataProfile
from .profile_factory import ProfileFactory

# Note: Individual profiles are loaded dynamically via ProfileFactory
# This ensures complete independence between profiles

__all__ = ['DataProfile', 'ProfileFactory']
