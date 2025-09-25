"""Pytest fixtures for common test setup.

This module provides reusable pytest fixtures that eliminate code duplication
across different profile tests.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator, Tuple

from config.settings import Config
# Legacy LLMProvider import removed - use config.providers.registry.LLMFactory instead
# Removed fridge-specific import - now using generic profile-based data generation
from .mocks import FakeLLMProvider, FakeLLMProviderEmpty, FakeLLMProviderError
from .config_helpers import create_profile_specific_test_data


@pytest.fixture
def temp_csv_path(tmp_path) -> str:
    """Create a temporary CSV file path for testing.
    
    Args:
        tmp_path: pytest temporary directory fixture
        
    Returns:
        str: Path to temporary CSV file
    """
    csv_file = tmp_path / "test_data.csv"
    return str(csv_file)




# Fridge-specific test CSV fixture removed - now using generic profile-based data generation


@pytest.fixture
def test_config() -> Config:
    """Create a test configuration using the current active profile.
    
    Returns:
        Config: Test configuration object
    """
    from config.settings import PROFILE_NAME
    
    return Config(
        google_api_key="test-key",
        generation_model="gemini-1.5-flash",
        port=9999,
        profile_name=PROFILE_NAME,
    )


@pytest.fixture
def active_profile_config() -> Config:
    """Create a test configuration for the currently active profile.
    
    Returns:
        Config: Test configuration for the active profile
    """
    from config.settings import PROFILE_NAME
    
    return Config(
        google_api_key="test-key",
        generation_model="gemini-1.5-flash",
        port=9999,
        profile_name=PROFILE_NAME,
    )


@pytest.fixture
def mock_llm_provider() -> FakeLLMProvider:
    """Create a mock LLM provider that returns realistic responses.
    
    Returns:
        FakeLLMProvider: Mock LLM provider instance
    """
    return FakeLLMProvider("test-key")


@pytest.fixture
def mock_llm_provider_empty() -> FakeLLMProviderEmpty:
    """Create a mock LLM provider that returns empty responses.
    
    Returns:
        FakeLLMProviderEmpty: Mock LLM provider that returns empty results
    """
    return FakeLLMProviderEmpty("test-key")


@pytest.fixture
def mock_llm_provider_error() -> FakeLLMProviderError:
    """Create a mock LLM provider that raises errors.
    
    Returns:
        FakeLLMProviderError: Mock LLM provider that raises exceptions
    """
    return FakeLLMProviderError("test-key")


# Removed test_environment_setup fixture - no longer needed without customized_profile


@pytest.fixture
def active_profile_environment(tmp_path) -> Generator[Tuple[str, Config], None, None]:
    """Set up test environment for the currently active profile.
    
    Args:
        tmp_path: pytest temporary directory fixture
        
    Yields:
        Tuple[str, Config]: CSV path and configuration for the active profile
    """
    from config.settings import PROFILE_NAME
    
    # Use the profile-specific test data generator
    csv_path = create_profile_specific_test_data(PROFILE_NAME, tmp_path)
    config = Config(
        google_api_key="test-key",
        generation_model="gemini-1.5-flash",
        port=9999,
        profile_name=PROFILE_NAME,
    )
    yield csv_path, config
