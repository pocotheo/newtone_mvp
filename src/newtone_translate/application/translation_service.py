"""
Translation Service - Main application orchestrator.

This service coordinates the entire translation workflow.
"""

from typing import Dict, List
from ..domain.models import TranslationRequest, TranslationResult
from ..domain.content_processor import ContentProcessor
from ..domain.placeholder_manager import PlaceholderManager
from ..infrastructure.providers import ProviderFactory
from ..infrastructure.storage import FileStorage
from .format_service import FormatService
from ..infrastructure.logging import get_logger

logger = get_logger("newtone_translate")


class TranslationService:
    """Main service orchestrating translation workflows."""
    
    def __init__(self):
        """Initialize translation service with dependencies."""
        self.format_service = FormatService()
        self.content_processor = ContentProcessor()
        self.placeholder_manager = PlaceholderManager()
        self.provider_factory = ProviderFactory()
        self.file_storage = FileStorage()
    
    def translate(self, request: TranslationRequest) -> TranslationResult:
        """
        Execute complete translation workflow.
        
        Args:
            request: Translation request with all parameters
            
        Returns:
            TranslationResult with translated content and metadata
        """
        logger.info(f"Starting translation workflow for target language: {request.target_lang}")
        
        # Step 1: Freeze placeholders and DNT terms
        logger.info("Step 1: Freezing placeholders and DNT terms")
        frozen_text, placeholder_map = self.placeholder_manager.freeze_all(
            request.text, 
            request.dnt_terms or []
        )
        
        # Step 2: Detect content format
        logger.info("Step 2: Detecting content format")
        content_format = self.format_service.detect_format(frozen_text)
        logger.info(f"Detected format: {content_format}")
        
        # Step 3: Process content based on format
        logger.info(f"Step 3: Processing {content_format} content")
        provider = self.provider_factory.get_provider()
        
        processed_output, usage, detected_lang = self.content_processor.process(
            frozen_text=frozen_text,
            content_format=content_format,
            provider=provider,
            target_lang=request.target_lang,
            brand_guide=request.brand_guide,
            glossary=request.glossary
        )
        
        # Step 4: Restore placeholders
        logger.info("Step 4: Restoring placeholders")
        final_output = self.placeholder_manager.restore_all(processed_output, placeholder_map)
        
        # Step 5: Save output file
        logger.info("Step 5: Saving translation output")
        output_filepath = self.file_storage.save_translation(
            final_output, 
            content_format, 
            request.target_lang, 
            request.input_filename
        )
        
        # Step 6: Generate metadata
        notes, applied_terms = self._generate_metadata(
            final_output, 
            content_format, 
            request.glossary
        )
        
        # Log comprehensive summary
        self._log_translation_summary(
            content_format, request.target_lang, detected_lang, 
            usage, notes, applied_terms, final_output, output_filepath
        )
        
        return TranslationResult(
            translated_text=final_output,
            detected_language=detected_lang,
            notes=notes,
            applied_terms=applied_terms,
            usage=usage,
            output_filepath=output_filepath
        )
    
    def _generate_metadata(self, output: str, format_type: str, glossary: Dict) -> tuple:
        """Generate translation notes and applied terms."""
        import re
        
        notes = []
        if "⟦SEG_" in output:
            notes.append("Unresolved segment marker found")
        else:
            notes.append(f"{format_type.capitalize()} preserved")

        applied_terms = []
        for src in (glossary or {}).keys():
            if re.search(re.escape(glossary[src]), output, flags=re.IGNORECASE):
                applied_terms.append(src)
        
        return notes, applied_terms
    
    def _log_translation_summary(self, content_format: str, target_lang: str, 
                                detected_lang: str, usage: Dict, notes: List, 
                                applied_terms: List, output: str, output_path: str) -> None:
        """Log comprehensive translation summary."""
        logger.info("=== TRANSLATION SUMMARY ===")
        logger.info(f"Input format: {content_format}")
        logger.info(f"Target language: {target_lang}")
        logger.info(f"Source language detected: {detected_lang}")
        logger.info(f"Token usage: {usage}")
        logger.info(f"Translation notes: {notes}")
        logger.info(f"Applied glossary terms: {applied_terms}")
        logger.info(f"Final translated output ({len(output)} chars):")
        logger.info(f"{output}")
        logger.info(f"Output saved to: {output_path}")
        logger.info("=== END TRANSLATION SUMMARY ===")
