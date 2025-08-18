"""
Newtone Translation System

A professional translation system with brand consistency and format preservation.
Built using layered architecture for maintainability and scalability.
"""

__version__ = "1.0.0"
__author__ = "Newtone"

# Main API exports
from .application.translation_service import TranslationService
from .domain.models import TranslationRequest, TranslationResult
from .infrastructure.providers import OpenAIProvider, MockProvider

__all__ = [
    "TranslationService",
    "TranslationRequest", 
    "TranslationResult",
    "OpenAIProvider",
    "MockProvider"
]
