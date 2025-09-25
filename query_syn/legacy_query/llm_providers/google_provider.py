from typing import List
from .base_provider import LLMProvider

try:
    from google import genai
except ImportError as e:
    raise ImportError("google-genai is required. Install with: pip install google-genai") from e


class GoogleProvider(LLMProvider):
    """Google GenAI provider implementation."""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def generate_content(self, model: str, contents: List[str]) -> str:
        """Generate content using Google GenAI."""
        response = self.client.models.generate_content(
            model=model,
            contents=contents
        )
        return str(getattr(response, 'text', '') or '')
