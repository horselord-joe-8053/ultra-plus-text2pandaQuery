from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
import pandas as pd
from config.providers.registry import ProviderConfig


# =============================================================================
# SHARED CONFIGURATION CONSTANTS
# =============================================================================

class ProfileConfig:
    """Shared configuration constants for all data profiles."""
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER = "google"
    DEFAULT_LLM_MODEL = "gemini-1.5-flash"
    
    # Query Configuration
    DEFAULT_QUERY_LIMIT = 100
    MAX_QUERY_LIMIT = 500
    DEFAULT_SAMPLE_ROWS = 3
    
    # Response Configuration
    DEFAULT_MAX_DISPLAY_ROWS = 50
    DEFAULT_MAX_DISPLAY_CHARS = 6000
    DEFAULT_SOURCES_LIMIT = 20
    
    # Supported Operations
    SUPPORTED_FILTER_OPS = ["eq", "neq", "gt", "gte", "lt", "lte", "in", "contains", "date_range"]
    SUPPORTED_AGGREGATIONS = ["mean", "min", "max", "count", "sum"]
    SUPPORTED_SORT_ORDERS = ["asc", "desc"]


class DataProfile(ABC):
    """Abstract base class for data profiles that define schema, processing, and LLM configuration."""
    
    # Schema Definition
    @property
    @abstractmethod
    def required_columns(self) -> List[str]:
        """List of required columns for this data profile."""
        pass
    
    @property
    @abstractmethod
    def text_columns(self) -> List[str]:
        """List of text columns that need special handling."""
        pass
    
    @property
    @abstractmethod
    def date_columns(self) -> List[str]:
        """List of date columns that need datetime parsing."""
        pass
    
    @property
    @abstractmethod
    def numeric_columns(self) -> List[str]:
        """List of numeric columns that need numeric conversion."""
        pass
    
    @property
    @abstractmethod
    def sensitive_columns(self) -> Dict[str, str]:
        """Mapping of column names to censoring types (e.g., 'VIN' -> 'vin')."""
        pass
    
    # Data Processing
    @abstractmethod
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the DataFrame according to this profile's requirements."""
        pass
    
    @abstractmethod
    def get_censoring_mappings(self) -> Dict[str, Callable]:
        """Return mapping of censoring type names to censoring functions."""
        pass
    
    # LLM Configuration
    @abstractmethod
    def get_llm_provider(self) -> str:
        """Return the LLM provider name (e.g., 'google', 'openai')."""
        pass
    
    @abstractmethod
    def get_llm_model(self) -> str:
        """Return the LLM model name."""
        pass
    
    @abstractmethod
    def get_llm_system_prompt(self) -> str:
        """Return the system prompt for LLM query synthesis."""
        pass
    
    @abstractmethod
    def get_schema_hints(self, sample_data: str) -> str:
        """Return schema-specific hints for LLM query synthesis."""
        pass
    
    @abstractmethod
    def get_example_queries(self) -> List[str]:
        """Return example queries for this data profile."""
        pass
    
    # Output Formatting
    @abstractmethod
    def create_sources_from_df(self, df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
        """Create source dictionaries from DataFrame rows."""
        pass
    
    @abstractmethod
    def get_stats_columns(self) -> Dict[str, str]:
        """Return mapping of stat names to column names for statistics generation."""
        pass
    
    # Localization
    @abstractmethod
    def get_language(self) -> str:
        """Return the language code for this profile (e.g., 'pt-BR', 'en-US')."""
        pass
    
    @abstractmethod
    def get_domain_terminology(self) -> Dict[str, str]:
        """Return domain-specific terminology mapping."""
        pass
    
    # Utility Methods
    def validate_columns(self, df: pd.DataFrame) -> List[str]:
        """Validate that DataFrame has all required columns. Returns list of missing columns."""
        missing = set(self.required_columns) - set(df.columns)
        return list(missing)
    
    def get_column_type(self, column: str) -> str:
        """Get the type of a column based on profile definition."""
        if column in self.text_columns:
            return "text"
        elif column in self.date_columns:
            return "date"
        elif column in self.numeric_columns:
            return "numeric"
        else:
            return "unknown"
    
    def get_default_query_limit(self) -> int:
        """Get the default query limit for this profile."""
        return ProfileConfig.DEFAULT_QUERY_LIMIT
    
    def get_max_query_limit(self) -> int:
        """Get the maximum query limit for this profile."""
        return ProfileConfig.MAX_QUERY_LIMIT
    
    def get_supported_filter_ops(self) -> List[str]:
        """Get the list of supported filter operations."""
        return ProfileConfig.SUPPORTED_FILTER_OPS.copy()
    
    def get_supported_aggregations(self) -> List[str]:
        """Get the list of supported aggregation functions."""
        return ProfileConfig.SUPPORTED_AGGREGATIONS.copy()
    
    def get_supported_sort_orders(self) -> List[str]:
        """Get the list of supported sort orders."""
        return ProfileConfig.SUPPORTED_SORT_ORDERS.copy()
    
    def get_provider_config(self) -> ProviderConfig:
        """Get the provider configuration for this profile."""
        # This should be implemented by each profile
        # Default implementation tries to import from provider_config.py
        try:
            # Get the profile's module path dynamically
            profile_module = self.__class__.__module__
            profile_package = profile_module.split('.')[:-1]  # Remove 'profile_config'
            provider_module_path = '.'.join(profile_package) + '.provider_config'
            
            # Import the provider config function
            import importlib
            provider_module = importlib.import_module(provider_module_path)
            return provider_module.get_provider_config()
        except Exception as e:
            # Fallback to a default Google configuration
            from config.providers.registry import ProviderConfig
            return ProviderConfig(
                provider="google",
                generation_model="gemini-1.5-flash",
                credentials={"api_key": "PLACEHOLDER"},
                extras={"temperature": 0.2, "max_tokens": 2048}
            )
