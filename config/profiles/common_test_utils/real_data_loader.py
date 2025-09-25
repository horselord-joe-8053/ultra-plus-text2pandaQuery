"""Utilities for loading real test data files.

This module provides utilities for loading and working with actual test data
files from the profile directories, enabling tests with real data scenarios.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from .config_helpers import get_profile_test_data_path


def load_real_test_data(profile_name: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    """Load real test data for a profile.
    
    Args:
        profile_name: Name of the profile
        sample_size: Optional number of rows to sample (None for all data)
        
    Returns:
        pd.DataFrame: Loaded test data
        
    Raises:
        FileNotFoundError: If test data file does not exist
        ValueError: If profile_name is not supported
    """
    data_path = get_profile_test_data_path(profile_name)
    
    if sample_size is not None:
        df = pd.read_csv(data_path, nrows=sample_size)
    else:
        df = pd.read_csv(data_path)
    
    return df


def get_real_data_sample(profile_name: str, sample_size: int = 10) -> pd.DataFrame:
    """Get a sample of real test data for testing.
    
    Args:
        profile_name: Name of the profile
        sample_size: Number of rows to sample (default: 10)
        
    Returns:
        pd.DataFrame: Sample of real test data
    """
    return load_real_test_data(profile_name, sample_size)


def get_real_data_info(profile_name: str) -> Dict[str, Any]:
    """Get information about the real test data file.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        dict: Information about the test data file
    """
    data_path = get_profile_test_data_path(profile_name)
    df = load_real_test_data(profile_name, sample_size=1000)  # Load first 1000 rows for info
    
    return {
        'file_path': data_path,
        'total_rows': len(df),
        'columns': list(df.columns),
        'column_count': len(df.columns),
        'data_types': df.dtypes.to_dict(),
        'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
    }


def create_real_data_test_csv(profile_name: str, tmp_path, sample_size: int = 50) -> str:
    """Create a test CSV file with real data for testing.
    
    Args:
        profile_name: Name of the profile
        tmp_path: Temporary directory path (string or Path object)
        sample_size: Number of rows to include in test file
        
    Returns:
        str: Path to created test CSV file
    """
    from pathlib import Path
    
    df = get_real_data_sample(profile_name, sample_size)
    
    # Convert string to Path if needed
    if isinstance(tmp_path, str):
        tmp_path = Path(tmp_path)
    
    # Create a generic test file name based on profile name
    test_file = tmp_path / f"real_{profile_name}_test.csv"
    
    df.to_csv(test_file, index=False)
    return str(test_file)


def validate_real_data_structure(profile_name: str) -> bool:
    """Validate that real data has the expected structure.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        bool: True if data structure is valid
        
    Raises:
        AssertionError: If data structure is invalid
    """
    from .config_helpers import get_profile_expected_columns
    
    df = load_real_test_data(profile_name, sample_size=10)
    expected_columns = get_profile_expected_columns(profile_name)
    
    # Check that all expected columns exist
    for col in expected_columns:
        assert col in df.columns, f"Missing expected column: {col}"
    
    # Check that DataFrame is not empty
    assert len(df) > 0, "Real data should not be empty"
    
    return True


def get_real_data_column_stats(profile_name: str, column_name: str) -> Dict[str, Any]:
    """Get statistics for a specific column in real data.
    
    Args:
        profile_name: Name of the profile
        column_name: Name of the column to analyze
        
    Returns:
        dict: Column statistics
    """
    df = load_real_test_data(profile_name, sample_size=1000)
    
    if column_name not in df.columns:
        raise ValueError(f"Column {column_name} not found in {profile_name} data")
    
    column_data = df[column_name]
    
    stats = {
        'column_name': column_name,
        'data_type': str(column_data.dtype),
        'total_count': len(column_data),
        'non_null_count': column_data.count(),
        'null_count': column_data.isnull().sum(),
        'unique_count': column_data.nunique()
    }
    
    # Add type-specific statistics
    if pd.api.types.is_numeric_dtype(column_data):
        stats.update({
            'min': float(column_data.min()) if not column_data.empty else None,
            'max': float(column_data.max()) if not column_data.empty else None,
            'mean': float(column_data.mean()) if not column_data.empty else None,
            'std': float(column_data.std()) if not column_data.empty else None
        })
    elif pd.api.types.is_datetime64_any_dtype(column_data):
        stats.update({
            'min_date': str(column_data.min()) if not column_data.empty else None,
            'max_date': str(column_data.max()) if not column_data.empty else None
        })
    else:
        # String/categorical data
        stats.update({
            'most_common': column_data.value_counts().head(3).to_dict() if not column_data.empty else {},
            'min_length': column_data.astype(str).str.len().min() if not column_data.empty else None,
            'max_length': column_data.astype(str).str.len().max() if not column_data.empty else None
        })
    
    return stats


def compare_real_vs_synthetic_data(profile_name: str, synthetic_df: pd.DataFrame) -> Dict[str, Any]:
    """Compare real data with synthetic test data.
    
    Args:
        profile_name: Name of the profile
        synthetic_df: Synthetic DataFrame to compare
        
    Returns:
        dict: Comparison results
    """
    real_df = get_real_data_sample(profile_name, sample_size=len(synthetic_df))
    
    comparison = {
        'profile_name': profile_name,
        'real_data_shape': real_df.shape,
        'synthetic_data_shape': synthetic_df.shape,
        'columns_match': list(real_df.columns) == list(synthetic_df.columns),
        'common_columns': list(set(real_df.columns) & set(synthetic_df.columns)),
        'missing_in_synthetic': list(set(real_df.columns) - set(synthetic_df.columns)),
        'extra_in_synthetic': list(set(synthetic_df.columns) - set(real_df.columns))
    }
    
    # Compare data types for common columns
    type_comparison = {}
    for col in comparison['common_columns']:
        real_dtype = str(real_df[col].dtype)
        synthetic_dtype = str(synthetic_df[col].dtype)
        type_comparison[col] = {
            'real': real_dtype,
            'synthetic': synthetic_dtype,
            'match': real_dtype == synthetic_dtype
        }
    
    comparison['type_comparison'] = type_comparison
    
    return comparison
