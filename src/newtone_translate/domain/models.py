"""
Domain Models - Core business entities.

These models represent the core concepts in our translation domain.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TranslationRequest:
    """Model for translation operations."""
    
    text: str
    target_lang: str = "fr"
    glossary: Optional[Dict[str, str]] = None
    dnt_terms: Optional[List[str]] = None
    brand_guide: Optional[Dict] = None
    input_filename: Optional[str] = None
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.text.strip():
            raise ValueError("Text cannot be empty")
        if not self.target_lang:
            raise ValueError("Target language is required")


@dataclass 
class TranslationResult:
    """Result model for translation operations."""
    
    translated_text: str
    detected_language: str
    notes: List[str]
    applied_terms: List[str]
    usage: Dict
    output_filepath: str


@dataclass
class ProcessedContent:
    """Intermediate model for processed content."""
    
    segments: List[Dict]
    format_type: str
    metadata: Dict
