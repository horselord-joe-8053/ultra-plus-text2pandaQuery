"""
Legacy query processing components.

This module contains deprecated query processing code that has been replaced
by newer, more efficient implementations. These components are maintained
for backward compatibility but should not be used in new code.

The entire legacy_query/ folder can be safely deleted at any time.
"""

# Legacy LLM providers
from .llm_providers import GoogleProvider
from .llm_providers.base_provider import LLMProvider

__all__ = [
    'GoogleProvider',  # Legacy - use config.providers.registry.LLMFactory instead
    'LLMProvider',     # Legacy - use config.providers.registry.LLMFactory instead
]
