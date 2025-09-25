"""Common test utilities for profile testing.

This module provides shared utilities, fixtures, and helpers for testing
across different profiles in the config/profiles/ directory.

Key Components:
- fixtures: Pytest fixtures for common test setup
- data_generators: Test data generation utilities  
- mocks: Mock objects and providers
- assertions: Custom assertion helpers
- config_helpers: Configuration and profile utilities
- real_data_loader: Utilities for loading real test data
"""

from .fixtures import *
from .data_generators import *
from .mocks import *
from .assertions import *
from .config_helpers import *
from .real_data_loader import *

__all__ = [
    # Fixtures
    'temp_csv_path',
    'test_config',
    'mock_llm_provider',
    'mock_llm_provider_empty',
    'mock_llm_provider_error',
    
    # Data Generators
    'create_custom_test_data',
    
    # Mocks
    'FakeLLMProvider',
    'FakeLLMProviderEmpty', 
    'FakeLLMProviderError',
    
    # Assertions
    'assert_valid_query_response',
    'assert_censoring_consistency',
    'assert_dataframe_structure',
    'assert_profile_configuration',
    
    # Config Helpers
    'create_test_profile',
    'setup_test_environment',
    'get_profile_test_data_path',
    
    # Real Data Loader
    'load_real_test_data',
    'get_real_data_sample',
]
