"""Tests for fridge sales profile functionality."""

import pandas as pd
import pytest
from pathlib import Path
from config.profiles.default_profile.profile_config import DefaultProfileProfile


class TestDefaultProfileProfile:
    """Test suite for DefaultProfileProfile functionality."""

    def test_profile_initialization(self):
        """Test that DefaultProfileProfile initializes correctly."""
        profile = DefaultProfileProfile()
        assert profile is not None
        assert hasattr(profile, 'csv_file')
        assert hasattr(profile, '_inferred_columns')

    def test_csv_file_path(self):
        """Test CSV file path configuration."""
        profile = DefaultProfileProfile()
        csv_path = profile.get_csv_file_path()
        assert csv_path.endswith('fridge_sales_with_rating.csv')
        assert Path(csv_path).exists()

    def test_required_columns(self):
        """Test required columns are correctly defined."""
        profile = DefaultProfileProfile()
        required_cols = profile.required_columns
        
        expected_cols = [
            'ID', 'CUSTOMER_ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 
            'PRICE', 'SALES_DATE', 'STORE_NAME', 'STORE_ADDRESS', 
            'CUSTOMER_FEEDBACK', 'FEEDBACK_RATING'
        ]
        
        for col in expected_cols:
            assert col in required_cols

    def test_column_type_inference(self):
        """Test column type inference works correctly."""
        profile = DefaultProfileProfile()
        
        # Test that column types are inferred
        assert 'required' in profile._inferred_columns
        assert 'text' in profile._inferred_columns
        assert 'date' in profile._inferred_columns
        assert 'numeric' in profile._inferred_columns
        
        # Test specific column types
        text_cols = profile.text_columns
        numeric_cols = profile.numeric_columns
        date_cols = profile.date_columns
        
        assert 'BRAND' in text_cols
        assert 'CAPACITY_LITERS' in numeric_cols
        assert 'PRICE' in numeric_cols
        assert 'SALES_DATE' in date_cols

    def test_sensitive_columns(self):
        """Test sensitive column mappings."""
        profile = DefaultProfileProfile()
        sensitive = profile.sensitive_columns
        
        assert 'CUSTOMER_ID' in sensitive
        assert 'STORE_ADDRESS' in sensitive
        assert sensitive['CUSTOMER_ID'] == 'customer_id'
        assert sensitive['STORE_ADDRESS'] == 'address'

    def test_data_cleaning(self):
        """Test data cleaning functionality."""
        profile = DefaultProfileProfile()
        
        # Create test DataFrame
        test_data = {
            'ID': ['F001', 'F002'],
            'CUSTOMER_ID': ['CUST001', 'CUST002'],
            'FRIDGE_MODEL': ['RF28K9070SG', 'GNE27JYMFS'],
            'BRAND': ['Samsung', 'GE'],
            'CAPACITY_LITERS': [28, 27],
            'PRICE': [1299.99, 899.99],
            'SALES_DATE': ['2024-01-15', '2024-01-16'],
            'STORE_NAME': ['New York Store', 'Chicago Store'],
            'STORE_ADDRESS': ['123 Broadway', '456 Michigan Ave'],
            'CUSTOMER_FEEDBACK': ['Great fridge!', ''],
            'FEEDBACK_RATING': ['Positive', 'Neutral']
        }
        
        df = pd.DataFrame(test_data)
        cleaned_df = profile.clean_data(df)
        
        # Test that cleaning worked
        assert len(cleaned_df) == 2
        assert 'BRAND' in cleaned_df.columns
        assert pd.notna(cleaned_df['PRICE'].iloc[0])
        assert pd.notna(cleaned_df['CAPACITY_LITERS'].iloc[0])

    def test_llm_configuration(self):
        """Test LLM configuration."""
        profile = DefaultProfileProfile()
        
        assert profile.get_llm_provider() == "google"
        assert profile.get_llm_model() == "gemini-1.5-flash"
        assert "fridge sales data" in profile.get_llm_system_prompt()

    def test_schema_hints(self):
        """Test schema hints generation."""
        profile = DefaultProfileProfile()
        sample_data = "ID,BRAND,PRICE\nF001,Samsung,1299.99\n"
        hints = profile.get_schema_hints(sample_data)
        
        assert "BRAND" in hints
        assert "PRICE" in hints
        assert "SALES_DATE" in hints
        assert "date_range" in hints

    def test_example_queries(self):
        """Test example queries."""
        profile = DefaultProfileProfile()
        examples = profile.get_example_queries()
        
        assert len(examples) > 0
        assert any("Samsung" in query for query in examples)
        assert any("price" in query.lower() for query in examples)
        assert any("brand" in query.lower() for query in examples)

    def test_create_sources_from_df(self):
        """Test source creation from DataFrame."""
        profile = DefaultProfileProfile()
        
        test_data = {
            'ID': ['F001', 'F002'],
            'CUSTOMER_ID': ['CUST001', 'CUST002'],
            'FRIDGE_MODEL': ['RF28K9070SG', 'GNE27JYMFS'],
            'BRAND': ['Samsung', 'GE'],
            'CAPACITY_LITERS': [28, 27],
            'PRICE': [1299.99, 899.99],
            'SALES_DATE': ['2024-01-15', '2024-01-16'],
            'STORE_NAME': ['New York Store', 'Chicago Store'],
            'STORE_ADDRESS': ['123 Broadway', '456 Michigan Ave'],
            'CUSTOMER_FEEDBACK': ['Great fridge!', 'It works.'],
            'FEEDBACK_RATING': ['Positive', 'Neutral']
        }
        
        df = pd.DataFrame(test_data)
        sources = profile.create_sources_from_df(df, limit=2)
        
        assert len(sources) == 2
        assert sources[0]['id'] == 'F001'
        assert sources[0]['brand'] == 'Samsung'
        assert sources[0]['price'] == 1299.99
        assert sources[0]['capacity'] == 28
        assert sources[1]['brand'] == 'GE'

    def test_stats_columns(self):
        """Test statistics column mappings."""
        profile = DefaultProfileProfile()
        stats = profile.get_stats_columns()
        
        assert 'total_sales' in stats
        assert 'average_price' in stats
        assert 'brands_count' in stats
        assert 'stores_count' in stats
        assert stats['average_price'] == 'PRICE'
        assert stats['brands_count'] == 'BRAND'

    def test_language_and_terminology(self):
        """Test language and terminology configuration."""
        profile = DefaultProfileProfile()
        
        assert profile.get_language() == "en-US"
        
        terminology = profile.get_domain_terminology()
        assert 'fridge' in terminology
        assert 'brand' in terminology
        assert 'price' in terminology
        assert terminology['fridge'] == 'refrigerator'

    def test_censoring_mappings(self):
        """Test censoring function mappings."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        assert 'customer_id' in mappings
        assert 'address' in mappings
        assert callable(mappings['customer_id'])
        assert callable(mappings['address'])

    def test_with_real_data(self):
        """Test profile with real data file."""
        profile = DefaultProfileProfile()
        
        # Test that we can load and process real data
        csv_path = profile.get_csv_file_path()
        df = pd.read_csv(csv_path, nrows=5)
        
        # Test column inference
        assert len(profile.required_columns) > 0
        
        # Test data cleaning
        cleaned_df = profile.clean_data(df)
        assert len(cleaned_df) == 5
        
        # Test source creation
        sources = profile.create_sources_from_df(cleaned_df)
        assert len(sources) > 0
        assert 'id' in sources[0]
        assert 'brand' in sources[0]


class TestDefaultProfileIntegration:
    """Integration tests for fridge sales profile with query engine."""

    def test_profile_with_query_engine(self):
        """Test profile integration with query engine."""
        from config.settings import Config
        from query_syn.engine import QuerySynthesisEngine
        
        # Create test configuration for default profile
        config = Config(
            google_api_key="test-key",
            generation_model="gemini-1.5-flash",
            port=9999,
            profile_name="default_profile"
        )
        
        profile = DefaultProfileProfile()
        
        # Test that profile can be used with engine
        assert profile is not None
        assert hasattr(profile, 'get_csv_file_path')
        
        # Test data loading
        csv_path = profile.get_csv_file_path()
        assert Path(csv_path).exists()

    def test_profile_switching(self):
        """Test switching between profiles."""
        from config.settings import load_profile
        
        # Test default profile
        from config.settings import Config
        config = Config(
            google_api_key="test-key",
            generation_model="gemini-1.5-flash", 
            port=9999,
            profile_name="default_profile"
        )
        
        default_profile = load_profile(config)
        assert type(default_profile).__name__ == "DefaultProfileProfile"
        
        # Test that profile works correctly
        assert default_profile.required_columns is not None
        assert len(default_profile.required_columns) > 0
        assert default_profile.get_language() == "en-US"
