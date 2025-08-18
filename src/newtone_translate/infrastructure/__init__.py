"""
Infrastructure Layer - External Services and Technical Concerns

This layer handles:
- Translation providers (OpenAI, etc.)
- Content parsers
- File storage
- Logging
- External APIs
"""

from .providers import ProviderFactory, OpenAIProvider, MockProvider
from .storage import FileStorage
from .logging import get_logger

__all__ = [
    "ProviderFactory",
    "OpenAIProvider", 
    "MockProvider",
    "FileStorage",
    "get_logger"
]
