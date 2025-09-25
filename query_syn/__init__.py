"""Query processing system for natural language to pandas queries."""

from .engine import QuerySynthesisEngine

# Legacy imports for backward compatibility
from .legacy_query import GoogleProvider

__all__ = [
    'QuerySynthesisEngine',
    'GoogleProvider',  # Legacy - use config.providers.registry.LLMFactory instead
]