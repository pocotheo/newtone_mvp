"""
Provider Factory for managing translation provider instances.
"""

from .openai_provider import OpenAIProvider
from .mock_provider import MockProvider
from ..logging import get_logger

logger = get_logger("newtone_translate")


class ProviderFactory:
    """Factory for creating translation provider instances."""
    
    def get_provider(self, provider_name: str = "auto"):
        """
        Get translation provider instance.
        
        Args:
            provider_name: Name of provider ("openai", "mock", "auto")
            
        Returns:
            Translation provider instance
        """
        if provider_name == "auto":
            return self._choose_provider()
        elif provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "mock":
            return MockProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def _choose_provider(self):
        """Choose best available provider automatically."""
        try:
            provider = OpenAIProvider()
            logger.info("Using OpenAI provider")
            return provider
        except Exception as e:
            provider = MockProvider()
            logger.info(f"Using Mock provider: {e}")
            return provider
