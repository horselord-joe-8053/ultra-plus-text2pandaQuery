"""Custom assertion helpers for testing.

This module provides custom assertion functions that make tests more
readable and reduce code duplication across different profile tests.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Union


def assert_valid_query_response(response: Dict[str, Any]) -> None:
    """Validate that a query response has the correct structure.
    
    Args:
        response: Query response dictionary to validate
        
    Raises:
        AssertionError: If response structure is invalid
    """
    assert isinstance(response, dict), "Response should be a dictionary"
    
    required_keys = ["answer", "sources", "stats", "method", "execution_time"]
    for key in required_keys:
        assert key in response, f"Response missing required key: {key}"
    
    assert isinstance(response["answer"], str), "Answer should be a string"
    assert isinstance(response["sources"], list), "Sources should be a list"
    assert isinstance(response["stats"], dict), "Stats should be a dictionary"
    assert isinstance(response["method"], str), "Method should be a string"
    assert isinstance(response["execution_time"], (int, float)), "Execution time should be a number"


def assert_censoring_consistency(censor, original: str, censored: str) -> None:
    """Validate that censoring produces consistent results.
    
    Args:
        censor: Censoring service instance
        original: Original value that was censored
        censored: Censored value
        
    Raises:
        AssertionError: If censoring is not consistent
    """
    # Test that same input produces same output
    censored_again = censor.censor_text(original)
    assert censored == censored_again, "Censoring should be consistent"
    
    # Test that censored value can be desensorized
    desensorized = censor.desensorize_text(censored)
    assert desensorized == original, "Desensorizing should restore original"


def assert_dataframe_structure(df: pd.DataFrame, expected_columns: List[str]) -> None:
    """Validate that a DataFrame has the expected structure.
    
    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names
        
    Raises:
        AssertionError: If DataFrame structure is invalid
    """
    assert isinstance(df, pd.DataFrame), "Should be a pandas DataFrame"
    
    for col in expected_columns:
        assert col in df.columns, f"Missing expected column: {col}"
    
    assert len(df) > 0, "DataFrame should not be empty"


def assert_profile_configuration(profile, required_attributes: List[str]) -> None:
    """Validate that a profile has the required configuration attributes.
    
    Args:
        profile: Profile instance to validate
        required_attributes: List of required attribute names
        
    Raises:
        AssertionError: If profile configuration is invalid
    """
    assert profile is not None, "Profile should not be None"
    
    for attr in required_attributes:
        assert hasattr(profile, attr), f"Profile missing required attribute: {attr}"
        assert getattr(profile, attr) is not None, f"Profile attribute {attr} should not be None"


def assert_censoring_mappings(profile, expected_mappings: Dict[str, str]) -> None:
    """Validate that a profile has the correct censoring mappings.
    
    Args:
        profile: Profile instance to validate
        expected_mappings: Dictionary of expected mapping names and types
        
    Raises:
        AssertionError: If censoring mappings are invalid
    """
    mappings = profile.get_censoring_mappings()
    assert isinstance(mappings, dict), "Censoring mappings should be a dictionary"
    
    # Check that we have the expected mapping function names (not column names)
    expected_function_names = list(expected_mappings.values())
    for function_name in expected_function_names:
        assert function_name in mappings, f"Missing censoring mapping function: {function_name}"
        assert callable(mappings[function_name]), f"Censoring mapping {function_name} should be callable"


def assert_query_spec_validity(query_spec: Dict[str, Any]) -> None:
    """Validate that a query specification has valid structure.
    
    Args:
        query_spec: Query specification dictionary to validate
        
    Raises:
        AssertionError: If query specification is invalid
    """
    assert isinstance(query_spec, dict), "Query spec should be a dictionary"
    
    # Validate select clause
    if "select" in query_spec:
        assert isinstance(query_spec["select"], list), "Select should be a list"
        assert len(query_spec["select"]) > 0, "Select should not be empty"
    
    # Validate filters
    if "filters" in query_spec:
        assert isinstance(query_spec["filters"], list), "Filters should be a list"
        for filter_item in query_spec["filters"]:
            assert isinstance(filter_item, dict), "Filter item should be a dictionary"
            required_filter_keys = ["column", "op", "value"]
            for key in required_filter_keys:
                assert key in filter_item, f"Filter missing required key: {key}"
    
    # Validate sort
    if "sort" in query_spec:
        assert isinstance(query_spec["sort"], list), "Sort should be a list"
        for sort_item in query_spec["sort"]:
            assert isinstance(sort_item, dict), "Sort item should be a dictionary"
            assert "by" in sort_item, "Sort item missing 'by' key"
            assert "order" in sort_item, "Sort item missing 'order' key"
            assert sort_item["order"] in ["asc", "desc"], "Sort order should be 'asc' or 'desc'"
    
    # Validate limit
    if "limit" in query_spec:
        assert isinstance(query_spec["limit"], int), "Limit should be an integer"
        assert query_spec["limit"] > 0, "Limit should be positive"


def assert_stats_structure(stats: Dict[str, Any], expected_keys: List[str]) -> None:
    """Validate that statistics have the expected structure.
    
    Args:
        stats: Statistics dictionary to validate
        expected_keys: List of expected statistic keys
        
    Raises:
        AssertionError: If statistics structure is invalid
    """
    assert isinstance(stats, dict), "Stats should be a dictionary"
    
    for key in expected_keys:
        assert key in stats, f"Stats missing expected key: {key}"
    
    # Validate specific stat types
    if "total_records" in stats:
        assert isinstance(stats["total_records"], int), "total_records should be an integer"
        assert stats["total_records"] >= 0, "total_records should be non-negative"


def assert_censoring_hash_format(censored_value: str, expected_prefix: str, expected_length: int) -> None:
    """Validate that a censored value has the correct hash format.
    
    Args:
        censored_value: Censored value to validate
        expected_prefix: Expected prefix (e.g., "VIN_", "DEALER_")
        expected_length: Expected total length of censored value
        
    Raises:
        AssertionError: If censored value format is invalid
    """
    assert censored_value.startswith(expected_prefix), f"Censored value should start with {expected_prefix}"
    assert len(censored_value) == expected_length, f"Censored value should be {expected_length} characters long"
    
    # Validate hash part is alphanumeric
    hash_part = censored_value[len(expected_prefix):]
    assert hash_part.isalnum(), "Hash part should be alphanumeric"


def assert_date_range_validity(date_range: List[str]) -> None:
    """Validate that a date range is properly formatted.
    
    Args:
        date_range: List of two date strings [start_date, end_date]
        
    Raises:
        AssertionError: If date range format is invalid
    """
    assert isinstance(date_range, list), "Date range should be a list"
    assert len(date_range) == 2, "Date range should have exactly 2 elements"
    
    for date_str in date_range:
        assert isinstance(date_str, str), "Date should be a string"
        # Basic format validation (YYYY-MM-DD)
        assert len(date_str) == 10, "Date should be in YYYY-MM-DD format"
        assert date_str[4] == "-" and date_str[7] == "-", "Date should have proper separators"


def assert_empty_response_handling(response: Dict[str, Any]) -> None:
    """Validate that empty responses are handled correctly.
    
    Args:
        response: Response dictionary to validate
        
    Raises:
        AssertionError: If empty response handling is invalid
    """
    assert_valid_query_response(response)
    
    assert "No matching rows" in response["answer"] or "Error" in response["answer"], "Empty response should indicate no results or error"
    assert response["sources"] == [], "Empty response should have empty sources"


def assert_error_response_handling(response: Dict[str, Any]) -> None:
    """Validate that error responses are handled correctly.
    
    Args:
        response: Response dictionary to validate
        
    Raises:
        AssertionError: If error response handling is invalid
    """
    assert_valid_query_response(response)
    
    assert "error" in response["answer"].lower() or "failed" in response["answer"].lower(), "Error response should indicate failure"
