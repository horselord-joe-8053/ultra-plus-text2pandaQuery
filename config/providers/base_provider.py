#!/usr/bin/env python3
"""
Base provider interfaces and abstract classes.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from LLM providers."""
    content: str
    provider: str
    model: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, provider_name: str, model: str, credentials: Dict[str, str]):
        self.provider_name = provider_name
        self.model = model
        self.credentials = credentials
    
    @abstractmethod
    def generate_content(self, contents: List[str]) -> LLMResponse:
        """Generate content using the provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "available": self.is_available()
        }


class BaseEmbeddingsProvider(ABC):
    """Abstract base class for embeddings providers."""
    
    def __init__(self, provider_name: str, model: str, credentials: Dict[str, str]):
        self.provider_name = provider_name
        self.model = model
        self.credentials = credentials
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available or configured."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""
    pass


class ProviderQuotaExceededError(ProviderError):
    """Raised when provider quota is exceeded."""
    pass
