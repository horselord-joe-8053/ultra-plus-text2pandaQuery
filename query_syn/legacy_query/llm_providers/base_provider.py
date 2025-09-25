from abc import ABC, abstractmethod
from typing import List


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_content(self, model: str, contents: List[str]) -> str:
        """Generate content using the specified model and contents.
        
        Args:
            model: The model name to use
            contents: List of content strings (typically system prompt + user prompt)
            
        Returns:
            Generated text response
        """
        pass
