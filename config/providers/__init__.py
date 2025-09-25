"""Provider-agnostic factories and configurations for LLM providers."""

from .registry import (
    ProviderConfig,
    LLMFactory,
    EmbeddingsFactory,
    LLMWrapper,
    GoogleLLMWrapper,
    OpenAILLMWrapper,
    AnthropicLLMWrapper,
    GoogleEmbeddingsWrapper
)

# LangChain providers (conditional import)
try:
    from .langchain_provider import (
        LangChainProviderConfig,
        LangChainLLMWrapper,
        LangChainFactory
    )
except ImportError:
    LangChainProviderConfig = None
    LangChainLLMWrapper = None
    LangChainFactory = None

from .base_provider import (
    BaseLLMProvider,
    BaseEmbeddingsProvider,
    LLMResponse,
    ProviderError,
    ProviderNotAvailableError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderQuotaExceededError
)

__all__ = [
    # Registry classes
    'ProviderConfig',
    'LLMFactory',
    'EmbeddingsFactory',
    'LLMWrapper',
    'GoogleLLMWrapper',
    'OpenAILLMWrapper',
    'AnthropicLLMWrapper',
    'GoogleEmbeddingsWrapper',
    
    # LangChain classes (conditional)
    'LangChainProviderConfig',
    'LangChainLLMWrapper',
    'LangChainFactory',
    
    # Base classes
    'BaseLLMProvider',
    'BaseEmbeddingsProvider',
    'LLMResponse',
    
    # Exceptions
    'ProviderError',
    'ProviderNotAvailableError',
    'ProviderAuthenticationError',
    'ProviderRateLimitError',
    'ProviderQuotaExceededError'
]
