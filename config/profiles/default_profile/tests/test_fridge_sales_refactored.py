"""Refactored tests for fridge sales profile using common test utilities.

This file demonstrates how to use the common test utilities for the default profile
to eliminate code duplication and improve test maintainability.
"""

import pytest
import pandas as pd

from config.profiles.default_profile.profile_config import DefaultProfileProfile
from config.settings import Config, load_profile

# Import common test utilities
from config.profiles.common_test_utils import (
    # Fixtures
    fridge_test_csv, default_profile_config, mock_llm_provider, default_profile_environment,
    
    # Data generators
    create_fridge_test_data, create_custom_test_data,
    
    # Assertions
    assert_profile_configuration, assert_dataframe_structure, assert_censoring_mappings,
    assert_censoring_hash_format,
    
    # Config helpers
    create_test_profile, setup_test_environment,
    get_profile_expected_columns, get_profile_sensitive_columns, validate_profile_configuration,
    
    # Real data utilities
    load_real_test_data, get_real_data_sample, validate_real_data_structure,
    get_real_data_info, get_real_data_column_stats
)


class TestDefaultProfileWithFixtures:
    """Test default profile using pytest fixtures for setup."""
    
    def test_profile_initialization_with_fixtures(self, fridge_test_csv, default_profile_config):
        """Test profile initialization using fixtures."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        
        # Validate profile configuration
        required_attributes = ['get_csv_file_path', 'required_columns', 'sensitive_columns']
        # Note: Test profile wrapper may not have all attributes, so test what's available
        assert hasattr(profile, 'get_csv_file_path')
        assert hasattr(profile, 'required_columns')
        assert hasattr(profile, 'sensitive_columns')
        
        # Test CSV file path
        csv_path = profile.get_csv_file_path()
        assert csv_path == fridge_test_csv
    
    def test_required_columns_with_fixtures(self, fridge_test_csv, default_profile_config):
        """Test required columns using fixtures."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        expected_columns = get_profile_expected_columns("default_profile")
        
        for col in expected_columns:
            assert col in profile.required_columns
    
    def test_column_type_inference_with_fixtures(self, fridge_test_csv, default_profile_config):
        """Test column type inference using fixtures."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        
        # Test that column types are inferred
        assert 'required' in profile._inferred_columns
        assert 'text' in profile._inferred_columns
        assert 'date' in profile._inferred_columns
        assert 'numeric' in profile._inferred_columns
        
        # Test specific column types
        assert 'BRAND' in profile.text_columns
        assert 'CAPACITY_LITERS' in profile.numeric_columns
        assert 'PRICE' in profile.numeric_columns
        assert 'SALES_DATE' in profile.date_columns
    
    def test_sensitive_columns_with_fixtures(self, fridge_test_csv, default_profile_config):
        """Test sensitive columns using fixtures."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        expected_sensitive = get_profile_sensitive_columns("default_profile")
        
        for col, expected_type in expected_sensitive.items():
            assert col in profile.sensitive_columns
            assert profile.sensitive_columns[col] == expected_type
    
    def test_data_cleaning_with_fixtures(self, fridge_test_csv, default_profile_config):
        """Test data cleaning using fixtures."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        
        # Load test data
        df = pd.read_csv(fridge_test_csv)
        cleaned_df = profile.clean_data(df)
        
        # Validate structure
        expected_columns = get_profile_expected_columns("default_profile")
        assert_dataframe_structure(cleaned_df, expected_columns)
        
        # Test that cleaning worked
        assert len(cleaned_df) > 0
        assert pd.notna(cleaned_df['PRICE'].iloc[0])
        assert pd.notna(cleaned_df['CAPACITY_LITERS'].iloc[0])


class TestDefaultProfileWithEnvironmentSetup:
    """Test default profile using environment setup fixture."""
    
    def test_complete_environment_setup(self, default_profile_environment):
        """Test using complete environment setup fixture."""
        csv_path, config = default_profile_environment
        
        # Validate configuration
        assert config.profile_name == "default_profile"
        
        # Create profile
        profile = create_test_profile("default_profile", csv_path)
        
        # Test profile configuration
        validate_profile_configuration(profile, "default_profile")
        
        # Test data loading
        df = pd.read_csv(csv_path)
        expected_columns = get_profile_expected_columns("default_profile")
        assert_dataframe_structure(df, expected_columns)


class TestDefaultProfileWithRealData:
    """Test default profile using real data utilities."""
    
    def test_real_data_loading(self):
        """Test loading and validating real data."""
        # Load sample of real data
        real_df = get_real_data_sample("default_profile", sample_size=10)
        
        # Validate structure
        validate_real_data_structure("default_profile")
        
        # Check expected columns
        expected_columns = get_profile_expected_columns("default_profile")
        assert_dataframe_structure(real_df, expected_columns)
    
    def test_real_data_info(self):
        """Test getting real data information."""
        info = get_real_data_info("default_profile")
        
        assert 'file_path' in info
        assert 'total_rows' in info
        assert 'columns' in info
        assert 'column_count' in info
        assert info['total_rows'] > 0
        assert info['column_count'] > 0
    
    def test_real_data_column_stats(self):
        """Test getting column statistics from real data."""
        # Test numeric column
        price_stats = get_real_data_column_stats("default_profile", "PRICE")
        assert price_stats['column_name'] == "PRICE"
        assert price_stats['data_type'] in ['float64', 'int64']
        assert 'min' in price_stats
        assert 'max' in price_stats
        assert 'mean' in price_stats
        
        # Test string column
        brand_stats = get_real_data_column_stats("default_profile", "BRAND")
        assert brand_stats['column_name'] == "BRAND"
        assert 'most_common' in brand_stats
        assert 'unique_count' in brand_stats
    
    def test_real_vs_synthetic_data_comparison(self, tmp_path):
        """Test comparison between real and synthetic data."""
        # Create synthetic data
        synthetic_csv = create_fridge_test_data(tmp_path)
        synthetic_df = pd.read_csv(synthetic_csv)
        
        # Load real data sample
        real_df = get_real_data_sample("default_profile", sample_size=len(synthetic_df))
        
        # Compare structures
        assert len(synthetic_df) == len(real_df)
        
        # Check common columns
        common_columns = set(synthetic_df.columns) & set(real_df.columns)
        assert len(common_columns) > 0, "Should have common columns"


class TestDefaultProfileCensoringWithUtilities:
    """Test default profile censoring using common utilities."""
    
    def test_censoring_mappings_with_utilities(self, fridge_test_csv, default_profile_config):
        """Test censoring mappings using utilities."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        
        # Validate censoring mappings
        expected_mappings = get_profile_sensitive_columns("default_profile")
        assert_censoring_mappings(profile, expected_mappings)
        
        # Test actual censoring
        mappings = profile.get_censoring_mappings()
        
        # Test customer ID censoring
        customer_id = "CUST12345"
        censored = mappings['customer_id'](customer_id)
        assert_censoring_hash_format(censored, "DEALER_", 13)
        assert censored != customer_id
        
        # Test address censoring
        address = "123 Main St, New York, NY 10001"
        censored_addr = mappings['address'](address)
        assert_censoring_hash_format(censored_addr, "ADDR_", 13)
        assert censored_addr != address
    
    def test_censoring_consistency_with_utilities(self, fridge_test_csv, default_profile_config):
        """Test censoring consistency using utilities."""
        from censor_utils.censoring import CensoringService
        from config.profiles.common_test_utils.assertions import assert_censoring_consistency
        
        profile = create_test_profile("default_profile", fridge_test_csv)
        mappings = profile.get_censoring_mappings()
        
        # Test customer ID consistency
        customer_id = "CUST99999"
        censored1 = mappings['customer_id'](customer_id)
        censored2 = mappings['customer_id'](customer_id)
        assert censored1 == censored2
        
        # Test address consistency
        address = "999 Test Ave, Test City, TC 99999"
        censored_addr1 = mappings['address'](address)
        censored_addr2 = mappings['address'](address)
        assert censored_addr1 == censored_addr2
    
    def test_censoring_edge_cases_with_utilities(self, fridge_test_csv, default_profile_config):
        """Test censoring edge cases using utilities."""
        profile = create_test_profile("default_profile", fridge_test_csv)
        mappings = profile.get_censoring_mappings()
        
        # Test edge cases
        edge_cases = [None, "", "   "]
        
        for value in edge_cases:
            censored_customer = mappings['customer_id'](value)
            censored_address = mappings['address'](value)
            
            # Empty values should result in empty strings
            assert censored_customer == ""
            assert censored_address == ""


class TestDefaultProfileIntegration:
    """Integration tests using multiple common utilities."""
    
    def test_full_integration_with_common_utils(self, tmp_path):
        """Test full integration using multiple common utilities."""
        # Setup using environment helper  
        csv_path, config = setup_test_environment("default_profile", create_fridge_test_data(tmp_path))
        
        # Create profile
        profile = create_test_profile("default_profile", csv_path)
        
        # Validate profile configuration
        validate_profile_configuration(profile, "default_profile")
        
        # Test data loading and validation
        df = pd.read_csv(csv_path)
        expected_columns = get_profile_expected_columns("default_profile")
        assert_dataframe_structure(df, expected_columns)
        
        # Test data cleaning
        cleaned_df = profile.clean_data(df)
        assert_dataframe_structure(cleaned_df, expected_columns)
        
        # Test censoring mappings
        expected_sensitive = get_profile_sensitive_columns("default_profile")
        assert_censoring_mappings(profile, expected_sensitive)
        
        # Test real data comparison
        real_df = get_real_data_sample("default_profile", sample_size=len(df))
        assert_dataframe_structure(real_df, expected_columns)
        
        # Test profile switching
        from config.settings import load_profile
        switched_profile = load_profile(config)
        assert type(switched_profile).__name__ == "DefaultProfileProfile"
    
    def test_profile_switching_integration(self, tmp_path):
        """Test profile switching using common utilities."""
        # Test default profile
        config = Config(
            google_api_key="test-key",
            generation_model="gemini-1.5-flash", 
            port=9999,
            profile_name="default_profile"
        )
        
        default_profile = load_profile(config)
        assert type(default_profile).__name__ == "DefaultProfileProfile"
        
        # Test that profile works correctly
        expected_columns = get_profile_expected_columns("default_profile")
        assert len(default_profile.required_columns) > 0
        assert default_profile.get_language() == "en-US"
        
        # Validate against expected columns
        for col in expected_columns:
            assert col in default_profile.required_columns


class TestDefaultProfileWithCustomData:
    """Test default profile with custom data generation."""
    
    def test_custom_fridge_data_schema(self, tmp_path):
        """Test with custom fridge data schema."""
        # Define custom fridge schema
        custom_schema = {
            'ID': 'string',
            'CUSTOMER_ID': 'string',
            'FRIDGE_MODEL': 'string',
            'BRAND': 'string',
            'PRICE': 'float',
            'SALES_DATE': 'date'
        }
        
        # Create custom test data
        custom_csv = create_custom_test_data(tmp_path, custom_schema, num_rows=5)
        custom_df = pd.read_csv(custom_csv)
        
        # Validate structure
        assert_dataframe_structure(custom_df, list(custom_schema.keys()))
        assert len(custom_df) == 5
        
        # Test with profile
        profile = create_test_profile("default_profile", custom_csv)
        cleaned_df = profile.clean_data(custom_df)
        assert_dataframe_structure(cleaned_df, list(custom_schema.keys()))
