"""
Content Processor - Domain service for processing different content types.

Coordinates content processing based on format type.
"""

from typing import Dict, Tuple
from ..infrastructure.logging import get_logger


class ContentProcessor:
    """
    Domain service for processing content based on format.
    
    Coordinates between different processing strategies without external dependencies.
    """
    
    def __init__(self):
        """Initialize content processor."""
        self.logger = get_logger("newtone_translate")
    
    def process(self, frozen_text: str, content_format: str, provider, 
                target_lang: str, brand_guide: Dict, glossary: Dict) -> Tuple[str, Dict, str]:
        """
        Process content based on its format.
        
        Args:
            frozen_text: Text with placeholders frozen
            content_format: Detected format (html, markdown, text)
            provider: Translation provider
            target_lang: Target language
            brand_guide: Brand guidelines
            glossary: Translation glossary
            
        Returns:
            Tuple of (processed_text, usage_stats, detected_language)
        """
        self.logger.info(f"Processing content as {content_format}")
        
        if content_format == "html":
            return self._process_html(frozen_text, provider, target_lang, brand_guide, glossary)
        elif content_format == "markdown":
            return self._process_markdown(frozen_text, provider, target_lang, brand_guide, glossary)
        else:
            return self._process_text(frozen_text, provider, target_lang, brand_guide, glossary)
    
    def _process_html(self, frozen_text: str, provider, target_lang: str, 
                     brand_guide: Dict, glossary: Dict) -> Tuple[str, Dict, str]:
        """Process HTML content using HTML parser."""
        # Import here to avoid circular dependencies
        from ..infrastructure.parsers.html_parser import HTMLParser
        
        self.logger.info("Processing as HTML format.")
        parser = HTMLParser()
        soup = parser.parse(frozen_text)
        segments = parser.extract_segments(soup)
        
        self.logger.info(f"Extracted {len(segments)} segments: {str(segments)[:200]}{'...' if len(str(segments)) > 200 else ''}")
        self.logger.info("Calling provider.translate_segments for HTML segments.")
        
        translations, usage, detected = provider.translate_segments(
            segments=segments,
            target_lang=target_lang,
            source_lang="auto",
            brand_guide=brand_guide or {},
            glossary=glossary or {},
        )
        
        self.logger.info(f"Provider returned translations for {len(translations)} segments. Detected language: {detected}")
        
        # Ensure no missing ids remain after provider call
        missing = [s["id"] for s in segments if s["id"] not in translations]
        if missing:
            self.logger.info(f"Missing translations for segment IDs: {missing}")
        for mid in missing:
            src_txt = next(s["text"] for s in segments if s["id"] == mid)
            translations[mid] = src_txt
        
        soup2 = parser.apply_translations(soup, translations)
        out = parser.serialize(soup2)
        self.logger.info(f"Final HTML output: {out[:200]}{'...' if len(out) > 200 else ''}")
        
        return out, usage, detected
    
    def _process_markdown(self, frozen_text: str, provider, target_lang: str,
                         brand_guide: Dict, glossary: Dict) -> Tuple[str, Dict, str]:
        """Process Markdown content."""
        self.logger.info("Processing as markdown format.")
        segments = [{"id": "t1", "text": frozen_text}]
        self.logger.info(f"Markdown segment: {segments[0]}")
        self.logger.info("Calling provider.translate_segments for markdown.")
        
        translations, usage, detected = provider.translate_segments(
            segments=segments,
            target_lang=target_lang,
            source_lang="auto",
            brand_guide=brand_guide or {},
            glossary=glossary or {},
        )
        
        self.logger.info(f"Provider returned translations. Detected language: {detected}")
        out = translations.get("t1", frozen_text)
        self.logger.info(f"Final markdown output: {out[:200]}{'...' if len(out) > 200 else ''}")
        
        return out, usage, detected
    
    def _process_text(self, frozen_text: str, provider, target_lang: str,
                     brand_guide: Dict, glossary: Dict) -> Tuple[str, Dict, str]:
        """Process plain text content."""
        self.logger.info("Processing as plain text format.")
        segments = [{"id": "t1", "text": frozen_text}]
        self.logger.info(f"Text segment: {segments[0]}")
        self.logger.info("Calling provider.translate_segments for plain text.")
        
        translations, usage, detected = provider.translate_segments(
            segments=segments,
            target_lang=target_lang,
            source_lang="auto",
            brand_guide=brand_guide or {},
            glossary=glossary or {},
        )
        
        self.logger.info(f"Provider returned translations. Detected language: {detected}")
        out = translations.get("t1", frozen_text)
        self.logger.info(f"Final text output: {out[:200]}{'...' if len(out) > 200 else ''}")
        
        return out, usage, detected
