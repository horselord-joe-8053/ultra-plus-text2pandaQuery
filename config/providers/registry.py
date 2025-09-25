#!/usr/bin/env python3
"""
Provider-agnostic factories for LLM instances.

Profiles provide a ProviderConfig; factories create the appropriate
objects without the rest of the code importing provider-specific classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Supported provider SDK imports (lazy used behind factories)
try:  # Google Generative AI
    from google import genai
except ImportError:
    genai = None

try:  # OpenAI
    import openai
except ImportError:
    openai = None

try:  # Anthropic
    import anthropic
except ImportError:
    anthropic = None

# LangChain imports (lazy loading)
try:
    from .langchain_provider import LangChainProviderConfig, LangChainLLMWrapper, LangChainFactory
except ImportError:
    LangChainProviderConfig = None
    LangChainLLMWrapper = None
    LangChainFactory = None


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    provider: str = "google"  # e.g., google | openai | anthropic | cohere | azure_openai | langchain
    generation_model: str = ""
    embedding_model: str = ""  # For future use
    credentials: Dict[str, str] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)
    
    # LangChain integration
    use_langchain: bool = False
    langchain_provider: str = "openai"  # Which LangChain provider to use


class LLMFactory:
    """Factory for creating LLM instances from provider configurations."""
    
    @staticmethod
    def create(config: ProviderConfig):
        """Create an LLM instance based on the provider configuration."""
        provider = (config.provider or "google").lower()
        
        if provider == "google":
            if genai is None:
                raise ImportError("google-genai is not available. Install with: pip install google-genai")
            
            api_key = config.credentials.get("api_key", "")
            if not api_key:
                raise ValueError("Google provider requires 'api_key' in ProviderConfig.credentials")
            
            # Create Google client
            client = genai.Client(api_key=api_key)
            
            # Return a wrapper that implements our interface
            return GoogleLLMWrapper(client, config)
            
        elif provider == "openai":
            if openai is None:
                raise ImportError("openai is not available. Install with: pip install openai")
            
            api_key = config.credentials.get("api_key", "")
            if not api_key:
                raise ValueError("OpenAI provider requires 'api_key' in ProviderConfig.credentials")
            
            return OpenAILLMWrapper(config)
            
        elif provider == "anthropic":
            if anthropic is None:
                raise ImportError("anthropic is not available. Install with: pip install anthropic")
            
            api_key = config.credentials.get("api_key", "")
            if not api_key:
                raise ValueError("Anthropic provider requires 'api_key' in ProviderConfig.credentials")
            
            return AnthropicLLMWrapper(config)
            
        elif provider == "langchain" or config.use_langchain:
            if LangChainFactory is None:
                raise ImportError("LangChain providers are not available. Install with: pip install langchain langchain-openai")
            
            # Create LangChain config from base config
            langchain_config = LangChainFactory.create_from_base_config(
                config, 
                langchain_provider=config.langchain_provider
            )
            
            return LangChainFactory.create(langchain_config)
            
        else:
            raise ValueError(f"Unknown provider: {provider}")


class LLMWrapper:
    """Base wrapper for LLM providers to ensure consistent interface."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider = config.provider
        self.model = config.generation_model
    
    def generate_content(self, contents: list[str]) -> str:
        """Generate content using the configured provider and model."""
        raise NotImplementedError("Subclasses must implement generate_content")


class GoogleLLMWrapper(LLMWrapper):
    """Wrapper for Google Generative AI provider."""
    
    def __init__(self, client, config: ProviderConfig):
        super().__init__(config)
        self.client = client
    
    def generate_content(self, contents: list[str]) -> str:
        """Generate content using Google GenAI."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            return str(getattr(response, 'text', '') or '')
        except Exception as e:
            raise RuntimeError(f"Google GenAI generation failed: {e}")


class OpenAILLMWrapper(LLMWrapper):
    """Wrapper for OpenAI provider."""
    
    def generate_content(self, contents: list[str]) -> str:
        """Generate content using OpenAI."""
        try:
            # Combine contents into a single prompt
            prompt = "\n".join(contents)
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.extras.get("temperature", 0.2),
                max_tokens=self.config.extras.get("max_tokens", 2048),
                api_key=self.config.credentials.get("api_key")
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")


class AnthropicLLMWrapper(LLMWrapper):
    """Wrapper for Anthropic provider."""
    
    def generate_content(self, contents: list[str]) -> str:
        """Generate content using Anthropic Claude."""
        try:
            # Combine contents into a single prompt
            prompt = "\n".join(contents)
            
            client = anthropic.Anthropic(
                api_key=self.config.credentials.get("api_key")
            )
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.config.extras.get("max_tokens", 2048),
                temperature=self.config.extras.get("temperature", 0.2),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text if response.content else ""
        except Exception as e:
            raise RuntimeError(f"Anthropic generation failed: {e}")


# Embeddings factory for future use
class EmbeddingsFactory:
    """Factory for creating embedding instances from provider configurations."""
    
    @staticmethod
    def create(config: ProviderConfig):
        """Create an embeddings instance based on the provider configuration."""
        provider = (config.provider or "google").lower()
        
        if provider == "google":
            if genai is None:
                raise ImportError("google-genai is not available")
            
            api_key = config.credentials.get("api_key", "")
            if not api_key:
                raise ValueError("Google embeddings require 'api_key' in ProviderConfig.credentials")
            
            # For now, return a placeholder
            # TODO: Implement actual embeddings when needed
            return GoogleEmbeddingsWrapper(config)
            
        else:
            raise ValueError(f"Embeddings not yet supported for provider: {provider}")


class GoogleEmbeddingsWrapper:
    """Placeholder for Google embeddings."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    def embed_text(self, text: str) -> list[float]:
        """Embed text using Google embeddings."""
        # TODO: Implement actual embeddings
        raise NotImplementedError("Embeddings not yet implemented")
