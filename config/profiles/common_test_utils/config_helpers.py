"""Configuration and profile utilities for testing.

This module provides utilities for creating test configurations,
setting up test environments, and managing profile-specific test data.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Any

from config.settings import Config
from config.profiles.profile_factory import ProfileFactory


def create_test_profile(profile_name: str, csv_path: str) -> Any:
    """Create a test profile with custom CSV path.
    
    Args:
        profile_name: Name of the profile to create
        csv_path: Path to CSV file for testing
        
    Returns:
        Profile instance configured for testing
        
    Raises:
        ValueError: If profile_name is not supported
    """
    # Create the base profile using the factory
    base_profile = ProfileFactory.create_profile(profile_name)
    
    # Create a test wrapper that overrides the CSV path
    class TestProfileWrapper:
        def __init__(self, base_profile, csv_path):
            self._base_profile = base_profile
            self._csv_path = csv_path
            # Copy all attributes from base profile
            for attr in dir(base_profile):
                if not attr.startswith('_') and not callable(getattr(base_profile, attr)):
                    setattr(self, attr, getattr(base_profile, attr))
        
        def get_csv_file_path(self):
            return self._csv_path
        
        def __getattr__(self, name):
            # Delegate any missing attributes to the base profile
            return getattr(self._base_profile, name)
    
    return TestProfileWrapper(base_profile, csv_path)


def setup_test_environment(profile_name: str, csv_path: str) -> Tuple[str, Config]:
    """Set up complete test environment with configuration and profile.
    
    Args:
        profile_name: Name of the profile to set up
        csv_path: Path to CSV file for testing
        
    Returns:
        Tuple of (csv_path, Config) for testing
    """
    config = Config(
        google_api_key="test-key",
        generation_model="gemini-1.5-flash",
        port=9999,
        profile_name=profile_name,
    )
    
    return csv_path, config


def get_profile_test_data_path(profile_name: str) -> str:
    """Get the path to real test data for a profile.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        str: Path to the profile's test data file
        
    Raises:
        ValueError: If profile_name is not available
        FileNotFoundError: If test data file does not exist
    """
    # Check if profile is available
    if not ProfileFactory.is_profile_available(profile_name):
        raise ValueError(f"Profile '{profile_name}' is not available. Available profiles: {ProfileFactory.get_available_profiles()}")
    
    # Create the profile instance to get its data file path
    profile = ProfileFactory.create_profile(profile_name)
    data_path = profile.get_csv_file_path()
    
    if not Path(data_path).exists():
        raise FileNotFoundError(f"Test data file not found: {data_path}")
    
    return str(data_path)


def create_test_config(profile_name: str, csv_path: Optional[str] = None) -> Config:
    """Create a test configuration for the specified profile.
    
    Args:
        profile_name: Name of the profile
        csv_path: Optional CSV path override
        
    Returns:
        Config: Test configuration object
    """
    return Config(
        google_api_key="test-key",
        generation_model="gemini-1.5-flash",
        port=9999,
        profile_name=profile_name,
    )


def get_profile_class(profile_name: str) -> type:
    """Get the profile class for the specified profile name.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        type: Profile class
        
    Raises:
        ValueError: If profile_name is not supported
    """
    # Get the profile info from the factory
    profile_info = ProfileFactory.get_profile_info()
    if profile_name not in profile_info:
        raise ValueError(f"Unsupported profile name: {profile_name}")
    
    # Import and return the profile class dynamically
    module_path = profile_info[profile_name]['module_path']
    class_name = profile_info[profile_name]['class_name']
    
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def validate_profile_configuration(profile: Any, profile_name: str) -> bool:
    """Validate that a profile has the correct configuration for its type.
    
    Args:
        profile: Profile instance to validate
        profile_name: Expected profile name
        
    Returns:
        bool: True if profile configuration is valid
        
    Raises:
        AssertionError: If profile configuration is invalid
    """
    # Get the expected profile class dynamically
    expected_class = get_profile_class(profile_name)
    
    # Validate the profile type (allow for test wrappers)
    assert hasattr(profile, 'get_csv_file_path'), f"Profile must have get_csv_file_path method"
    
    # For test wrappers, check if the base profile is of the correct type
    if hasattr(profile, '_base_profile'):
        base_profile = profile._base_profile
        assert isinstance(base_profile, expected_class), f"Base profile must be instance of {expected_class.__name__}"
    else:
        # For direct profile instances, check the type
        assert isinstance(profile, expected_class), f"Profile must be instance of {expected_class.__name__}"
    
    return True


# Test profiles are now created dynamically using the ProfileFactory and TestProfileWrapper


def mock_llm_provider_path(profile_name: str) -> str:
    """Get the correct monkeypatch path for LLM provider based on profile.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        str: Monkeypatch path for the LLM provider
    """
    return "query_syn.legacy_query.llm_providers.GoogleProvider"


def create_profile_specific_test_data(profile_name: str, tmp_path) -> str:
    """Create profile-specific test data.
    
    Args:
        profile_name: Name of the profile
        tmp_path: Temporary directory path
        
    Returns:
        str: Path to created test data file
    """
    # Check if profile is available
    if not ProfileFactory.is_profile_available(profile_name):
        raise ValueError(f"Profile '{profile_name}' is not available. Available profiles: {ProfileFactory.get_available_profiles()}")
    
    # Create the profile instance to get its data structure
    profile = ProfileFactory.create_profile(profile_name)
    
    # Use the profile's data generator if available
    if hasattr(profile, 'generate_test_data'):
        return profile.generate_test_data(tmp_path)
    
    # Fallback to generic data generation based on profile structure
    from .data_generators import create_generic_test_data
    return create_generic_test_data(profile, tmp_path)


def get_profile_expected_columns(profile_name: str) -> list:
    """Get the expected columns for a profile's test data.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        list: List of expected column names
    """
    # Check if profile is available
    if not ProfileFactory.is_profile_available(profile_name):
        raise ValueError(f"Profile '{profile_name}' is not available. Available profiles: {ProfileFactory.get_available_profiles()}")
    
    # Create the profile instance to get its column definitions
    profile = ProfileFactory.create_profile(profile_name)
    return profile.required_columns


def get_profile_sensitive_columns(profile_name: str) -> dict:
    """Get the sensitive columns mapping for a profile.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        dict: Mapping of sensitive columns to censoring function names
    """
    # Check if profile is available
    if not ProfileFactory.is_profile_available(profile_name):
        raise ValueError(f"Profile '{profile_name}' is not available. Available profiles: {ProfileFactory.get_available_profiles()}")
    
    # Create the profile instance to get its sensitive column definitions
    profile = ProfileFactory.create_profile(profile_name)
    return profile.sensitive_columns
