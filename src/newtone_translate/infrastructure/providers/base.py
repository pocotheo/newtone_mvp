"""
Base Translation Provider Interface.

Moved from providers/base.py to infrastructure layer.
"""

from typing import Dict, List, Tuple
from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    """Abstract base class for translation providers."""
    
    @abstractmethod
    def translate_segments(self, segments: List[Dict], target_lang: str, source_lang: str,
                          brand_guide: Dict, glossary: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, int], str]:
        """
        Translate text segments.
        
        Args:
            segments: List of text segments to translate
            target_lang: Target language code
            source_lang: Source language code (or "auto" for detection)
            brand_guide: Brand guidelines dictionary
            glossary: Translation glossary
            
        Returns:
            Tuple of (translations_dict, usage_stats, detected_language)
        """
        raise NotImplementedError("Subclasses must implement translate_segments")
