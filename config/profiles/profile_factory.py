#!/usr/bin/env python3
"""
Profile factory for loading and managing data processing profiles.
"""

from typing import Dict, Type, Optional
import importlib
import os
from pathlib import Path
from .base_profile import DataProfile


class ProfileFactory:
    """Factory for creating and managing profiles with dynamic discovery."""

    # Cache for discovered profiles to avoid repeated filesystem scans
    _discovered_profiles: Optional[Dict[str, tuple[str, str]]] = None

    @classmethod
    def _discover_profiles(cls) -> Dict[str, tuple[str, str]]:
        """Dynamically discover available profiles by scanning the profiles directory."""
        if cls._discovered_profiles is not None:
            return cls._discovered_profiles
            
        cls._discovered_profiles = {}
        profiles_dir = Path(__file__).parent
        
        # Scan for profile directories (exclude special directories)
        for item in profiles_dir.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                not item.name.startswith('__') and
                not item.name.endswith('_backup') and
                item.name not in ['common_test_utils']):
                
                profile_name = item.name
                profile_config_path = item / 'profile_config.py'
                
                if profile_config_path.exists():
                    # Try to find the profile class by scanning the module
                    module_path = f'config.profiles.{profile_name}.profile_config'
                    try:
                        module = importlib.import_module(module_path)
                        # Look for a class that ends with 'Profile' and inherits from DataProfile
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                attr_name.endswith('Profile') and 
                                issubclass(attr, DataProfile) and 
                                attr != DataProfile):
                                cls._discovered_profiles[profile_name] = (module_path, attr_name)
                                break
                    except Exception:
                        # Skip profiles that can't be imported
                        continue
                        
        return cls._discovered_profiles

    @classmethod
    def get_available_profiles(cls) -> list[str]:
        """Return profile names that can be successfully imported."""
        available: list[str] = []
        profile_map = cls._discover_profiles()
        
        for name, (module_path, class_name) in profile_map.items():
            try:
                module = importlib.import_module(module_path)
                getattr(module, class_name)
                available.append(name)
            except Exception:
                # If a profile package is missing, skip it silently
                continue
        return available

    @classmethod
    def create_profile(cls, profile_name: str) -> DataProfile:
        """Create a profile instance by name using lazy import."""
        profile_map = cls._discover_profiles()
        
        if profile_name not in profile_map:
            raise ValueError(
                f"Unknown profile: {profile_name}. Available profiles: {cls.get_available_profiles()}"
            )

        module_path, class_name = profile_map[profile_name]
        try:
            module = importlib.import_module(module_path)
            profile_class: Type[DataProfile] = getattr(module, class_name)
        except Exception as e:
            raise ImportError(
                f"Failed to import profile '{profile_name}' from {module_path}.{class_name}: {e}"
            )
        return profile_class()

    @classmethod
    def register_profile(cls, name: str, module_path: str, class_name: str):
        """Register a new profile by module path and class name."""
        # Clear cache to force rediscovery on next access
        cls._discovered_profiles = None
        # Note: In dynamic discovery mode, profiles are auto-discovered
        # This method is kept for backward compatibility but profiles
        # should be discovered automatically from the filesystem

    @classmethod
    def get_default_profile(cls) -> DataProfile:
        """Get the default profile based on settings configuration."""
        available_profiles = cls.get_available_profiles()
        
        # If no profiles are available, raise an error
        if not available_profiles:
            raise RuntimeError("No profiles are available. Please ensure at least one profile is properly configured.")
        
        # Get the default profile name from settings
        from config.settings import PROFILE_NAME
        
        # Try to get the configured default profile first
        if PROFILE_NAME in available_profiles:
            return cls.create_profile(PROFILE_NAME)
        
        # Fallback to the first available profile if configured profile is not available
        return cls.create_profile(available_profiles[0])

    @classmethod
    def is_profile_available(cls, profile_name: str) -> bool:
        """Check if a specific profile is available."""
        return profile_name in cls.get_available_profiles()

    @classmethod
    def get_profile_info(cls) -> Dict[str, Dict[str, str]]:
        """Get information about all available profiles."""
        info = {}
        profile_map = cls._discover_profiles()
        
        for name, (module_path, class_name) in profile_map.items():
            if cls.is_profile_available(name):
                info[name] = {
                    'module_path': module_path,
                    'class_name': class_name,
                    'available': True
                }
            else:
                info[name] = {
                    'module_path': module_path,
                    'class_name': class_name,
                    'available': False
                }
        return info
