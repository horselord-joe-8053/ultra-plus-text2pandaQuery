#!/usr/bin/env python3
"""
Provider configuration for the default profile.
"""

from config.providers.registry import ProviderConfig


def get_provider_config() -> ProviderConfig:
    """Get the provider configuration for this profile."""
    from .config_api_keys import GCP_API_KEY
    
    return ProviderConfig(
        provider="google",
        generation_model="gemini-1.5-flash",
        embedding_model="text-embedding-004",  # For future use
        credentials={"api_key": GCP_API_KEY},
        extras={
            "temperature": 0.1,
            "max_tokens": 1024
        },
        # LangChain integration options
        use_langchain=False,  # Set to True to enable LangChain
        langchain_provider="openai"  # Which LangChain provider to use
    )
