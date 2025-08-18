"""
Mock Translation Provider for testing.

Moved from providers/mock.py to infrastructure layer.
"""

from typing import Dict, List
from .base import TranslationProvider


class MockProvider(TranslationProvider):
    """Mock translation provider for testing and development."""
    
    def translate_segments(self, segments: List[Dict], target_lang: str, source_lang: str,
                          brand_guide: Dict, glossary: Dict[str, str]):
        """
        Mock translation - adds language prefix to text.
        
        Args:
            segments: List of text segments to "translate"
            target_lang: Target language code
            source_lang: Source language code
            brand_guide: Brand guidelines (ignored in mock)
            glossary: Translation glossary (ignored in mock)
            
        Returns:
            Tuple of (mock_translations, usage_stats, detected_language)
        """
        translations = {}
        for seg in segments:
            # Simple mock: add language prefix
            mock_translation = f"[{target_lang.upper()}] {seg['text']}"
            translations[seg["id"]] = mock_translation
        
        usage = {"input": 10, "output": 15}  # Mock usage stats
        detected = "en"  # Mock detected language
        
        return translations, usage, detected
