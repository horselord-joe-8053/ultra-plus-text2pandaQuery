"""Mock objects and providers for testing.

This module provides reusable mock objects that eliminate duplication
of mock implementations across different profile tests.
"""

import json
from typing import List
from query_syn.legacy_query import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Mock LLM provider that returns realistic query specifications.
    
    This provider returns a realistic JSON query specification that can be
    used for testing query synthesis and execution workflows.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list) -> str:
        """Generate a realistic query specification for testing.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: JSON string containing a realistic query specification
        """
        return json.dumps({
            "select": ["DEALER_CODE", "SCORE", "CREATE_DATE"],
            "filters": [
                {"column": "SCORE", "op": "gte", "value": 7.0}
            ],
            "sort": [{"by": "SCORE", "order": "desc"}],
            "limit": 10
        })


class FakeLLMProviderEmpty(LLMProvider):
    """Mock LLM provider that returns empty results.
    
    This provider is useful for testing scenarios where the LLM
    returns no results or empty specifications.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list) -> str:
        """Generate an empty response for testing.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: Empty JSON object string
        """
        return "{}"


class FakeLLMProviderError(LLMProvider):
    """Mock LLM provider that raises exceptions.
    
    This provider is useful for testing error handling scenarios
    when the LLM service fails or returns errors.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list) -> str:
        """Raise an exception to simulate LLM service failure.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Raises:
            Exception: Simulates LLM API error
        """
        raise Exception("LLM API Error")


class FakeLLMProviderCustom(LLMProvider):
    """Mock LLM provider that returns custom responses.
    
    This provider allows tests to specify exactly what response
    should be returned, useful for testing specific scenarios.
    """
    
    def __init__(self, api_key: str, custom_response: str = None):
        self.api_key = api_key
        self.custom_response = custom_response or "{}"

    def generate_content(self, model: str, contents: list) -> str:
        """Generate a custom response for testing.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: Custom response string
        """
        return self.custom_response


class FakeLLMProviderSlow(LLMProvider):
    """Mock LLM provider that simulates slow responses.
    
    This provider is useful for testing timeout scenarios
    and performance-related functionality.
    """
    
    def __init__(self, api_key: str, delay_seconds: float = 1.0):
        self.api_key = api_key
        self.delay_seconds = delay_seconds

    def generate_content(self, model: str, contents: list) -> str:
        """Generate a response with artificial delay.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: Response after delay
        """
        import time
        time.sleep(self.delay_seconds)
        return json.dumps({
            "select": ["DELAYED_RESULT"],
            "filters": [],
            "sort": [],
            "limit": 1
        })


class FakeLLMProviderInvalidJSON(LLMProvider):
    """Mock LLM provider that returns invalid JSON.
    
    This provider is useful for testing JSON parsing error scenarios
    and error handling in query synthesis.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list) -> str:
        """Generate invalid JSON for testing.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: Invalid JSON string
        """
        return "This is not valid JSON {"


class FakeLLMProviderMalformedSpec(LLMProvider):
    """Mock LLM provider that returns malformed query specifications.
    
    This provider is useful for testing error handling when the LLM
    returns valid JSON but with malformed query specifications.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list) -> str:
        """Generate malformed query specification for testing.
        
        Args:
            model: Model name (ignored in mock)
            contents: Input contents (ignored in mock)
            
        Returns:
            str: JSON string with malformed query specification
        """
        return json.dumps({
            "invalid_field": "invalid_value",
            "select": "not_a_list",
            "filters": "also_not_a_list"
        })
