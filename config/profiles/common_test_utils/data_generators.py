"""Test data generation utilities.

This module provides utilities for creating test data that matches the
structure and characteristics of real profile data.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any




# Fridge-specific test data function removed - now using generic profile-based data generation


def create_custom_test_data(tmp_path: Path, data_schema: Dict[str, Any], num_rows: int = 5) -> str:
    """Create custom test data with specified schema.
    
    Args:
        tmp_path: Temporary directory path
        data_schema: Dictionary defining column names and data types
        num_rows: Number of rows to generate
        
    Returns:
        str: Path to created CSV file
    """
    data = []
    for i in range(num_rows):
        row = {}
        for column, data_type in data_schema.items():
            if data_type == 'string':
                row[column] = f"Test_{column}_{i+1}"
            elif data_type == 'int':
                row[column] = i + 1
            elif data_type == 'float':
                row[column] = float(i + 1) + 0.5
            elif data_type == 'date':
                row[column] = f"2024-01-{15 + i}"
            else:
                row[column] = f"Test_{column}_{i+1}"
        data.append(row)
    
    df = pd.DataFrame(data)
    csv_path = tmp_path / "custom_test.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def create_generic_test_data(profile, tmp_path) -> str:
    """Create generic test data based on profile structure.
    
    Args:
        profile: Profile instance to get structure from
        tmp_path: Temporary directory path (string or Path object)
        
    Returns:
        str: Path to created CSV file
    """
    from pathlib import Path
    
    # Convert string to Path if needed
    if isinstance(tmp_path, str):
        tmp_path = Path(tmp_path)
    
    data = []
    required_columns = profile.required_columns
    
    # Generate 5 rows of test data
    for i in range(5):
        row = {}
        for col in required_columns:
            if col in profile.numeric_columns:
                # Generate numeric data
                row[col] = (i + 1) * 10.5
            elif col in profile.date_columns:
                # Generate date data
                row[col] = f"2024-01-{15 + i}"
            elif col in profile.text_columns:
                # Generate text data
                row[col] = f"Test_{col}_{i+1}"
            else:
                # Generate categorical/text data
                row[col] = f"TEST_{col}_{i+1}"
        data.append(row)
    
    df = pd.DataFrame(data)
    csv_path = tmp_path / f"{profile.profile_name}_test.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def create_edge_case_test_data(tmp_path: Path) -> str:
    """Create test data with various edge cases for comprehensive testing.
    
    Args:
        tmp_path: Temporary directory path
        
    Returns:
        str: Path to created CSV file with edge cases
    """
    data = [
        # Normal data
        {'ID': 'N001', 'VALUE': 100, 'TEXT': 'normal', 'DATE': '2024-01-01'},
        # Empty/null values
        {'ID': 'E001', 'VALUE': None, 'TEXT': '', 'DATE': None},
        # Special characters
        {'ID': 'S001', 'VALUE': 200, 'TEXT': 'special chars: !@#$%^&*()', 'DATE': '2024-01-02'},
        # Very long text
        {'ID': 'L001', 'VALUE': 300, 'TEXT': 'very long text ' * 100, 'DATE': '2024-01-03'},
        # Numeric edge cases
        {'ID': 'N002', 'VALUE': 0, 'TEXT': 'zero', 'DATE': '2024-01-04'},
        {'ID': 'N003', 'VALUE': -100, 'TEXT': 'negative', 'DATE': '2024-01-05'},
    ]
    
    df = pd.DataFrame(data)
    csv_path = tmp_path / "edge_case_test.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)
