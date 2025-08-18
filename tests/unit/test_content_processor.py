"""
Unit tests for ContentProcessor.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.newtone_translate.domain.content_processor import ContentProcessor


class TestContentProcessor:
    """Test ContentProcessor domain service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ContentProcessor()
    
    def test_process_text_format(self):
        """Test processing plain text content."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.translate_segments.return_value = (
            {"t1": "Bonjour le monde"},
            {"tokens": 10},
            "en"
        )
        
        text = "Hello world"
        result = self.processor.process(
            frozen_text=text,
            content_format="text",
            provider=mock_provider,
            target_lang="fr",
            brand_guide={},
            glossary={}
        )
        
        translated_text, usage, detected_lang = result
        
        # Verify provider was called correctly
        mock_provider.translate_segments.assert_called_once_with(
            segments=[{"id": "t1", "text": text}],
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        # Verify results
        assert translated_text == "Bonjour le monde"
        assert usage == {"tokens": 10}
        assert detected_lang == "en"
    
    def test_process_markdown_format(self):
        """Test processing markdown content."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.translate_segments.return_value = (
            {"t1": "# Bonjour le monde\n\nCeci est du texte."},
            {"tokens": 15},
            "en"
        )
        
        text = "# Hello world\n\nThis is some text."
        result = self.processor.process(
            frozen_text=text,
            content_format="markdown",
            provider=mock_provider,
            target_lang="fr",
            brand_guide={"tone": "casual"},
            glossary={"hello": "bonjour"}
        )
        
        translated_text, usage, detected_lang = result
        
        # Verify provider was called correctly
        mock_provider.translate_segments.assert_called_once_with(
            segments=[{"id": "t1", "text": text}],
            target_lang="fr",
            source_lang="auto",
            brand_guide={"tone": "casual"},
            glossary={"hello": "bonjour"}
        )
        
        # Verify results
        assert "Bonjour le monde" in translated_text
        assert usage == {"tokens": 15}
        assert detected_lang == "en"
    
    def test_process_html_format(self, monkeypatch):
        """Test processing HTML content."""
        # Mock HTML parser
        mock_parser_class = Mock()
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        # Mock soup and parsing methods
        mock_soup = Mock()
        mock_parser.parse.return_value = mock_soup
        mock_parser.extract_segments.return_value = [
            {"id": "h1_1", "text": "Hello world"},
            {"id": "p_1", "text": "Welcome to our site"}
        ]
        mock_parser.apply_translations.return_value = mock_soup
        mock_parser.serialize.return_value = "<h1>Bonjour le monde</h1><p>Bienvenue sur notre site</p>"
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.translate_segments.return_value = (
            {
                "h1_1": "Bonjour le monde",
                "p_1": "Bienvenue sur notre site"
            },
            {"tokens": 20},
            "en"
        )
        
        # Patch the HTMLParser import at the correct location
        monkeypatch.setattr(
            "src.newtone_translate.infrastructure.parsers.html_parser.HTMLParser", 
            mock_parser_class
        )
        
        html = "<h1>Hello world</h1><p>Welcome to our site</p>"
        result = self.processor.process(
            frozen_text=html,
            content_format="html",
            provider=mock_provider,
            target_lang="fr",
            brand_guide={},
            glossary={}
        )
        
        translated_text, usage, detected_lang = result
        
        # Verify HTML parser was used correctly
        mock_parser.parse.assert_called_once_with(html)
        mock_parser.extract_segments.assert_called_once_with(mock_soup)
        mock_parser.apply_translations.assert_called_once()
        mock_parser.serialize.assert_called_once_with(mock_soup)
        
        # Verify provider was called correctly
        mock_provider.translate_segments.assert_called_once()
        
        # Verify results
        assert "Bonjour le monde" in translated_text
        assert "Bienvenue sur notre site" in translated_text
        assert usage == {"tokens": 20}
        assert detected_lang == "en"
    
    def test_process_html_with_missing_translations(self, monkeypatch):
        """Test HTML processing when provider doesn't return all translations."""
        # Mock HTML parser
        mock_parser_class = Mock()
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        mock_soup = Mock()
        mock_parser.parse.return_value = mock_soup
        mock_parser.extract_segments.return_value = [
            {"id": "h1_1", "text": "Hello world"},
            {"id": "p_1", "text": "Welcome to our site"}
        ]
        mock_parser.apply_translations.return_value = mock_soup
        mock_parser.serialize.return_value = "<h1>Hello world</h1><p>Bienvenue sur notre site</p>"
        
        # Mock provider that returns incomplete translations
        mock_provider = Mock()
        mock_provider.translate_segments.return_value = (
            {"p_1": "Bienvenue sur notre site"},  # Missing h1_1 translation
            {"tokens": 10},
            "en"
        )
        
        monkeypatch.setattr(
            "src.newtone_translate.infrastructure.parsers.html_parser.HTMLParser", 
            mock_parser_class
        )
        
        html = "<h1>Hello world</h1><p>Welcome to our site</p>"
        result = self.processor.process(
            frozen_text=html,
            content_format="html",
            provider=mock_provider,
            target_lang="fr",
            brand_guide={},
            glossary={}
        )
        
        translated_text, usage, detected_lang = result
        
        # Verify missing translation was filled with original text
        expected_translations = {
            "h1_1": "Hello world",  # Original text used as fallback
            "p_1": "Bienvenue sur notre site"
        }
        mock_parser.apply_translations.assert_called_once_with(mock_soup, expected_translations)
        
        assert usage == {"tokens": 10}
        assert detected_lang == "en"
    
    def test_process_with_none_values(self):
        """Test processing with None brand guide and glossary."""
        mock_provider = Mock()
        mock_provider.translate_segments.return_value = (
            {"t1": "Bonjour"},
            {"tokens": 5},
            "en"
        )
        
        result = self.processor.process(
            frozen_text="Hello",
            content_format="text",
            provider=mock_provider,
            target_lang="fr",
            brand_guide=None,
            glossary=None
        )
        
        translated_text, usage, detected_lang = result
        
        # Verify None values are converted to empty dicts
        mock_provider.translate_segments.assert_called_once_with(
            segments=[{"id": "t1", "text": "Hello"}],
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        assert translated_text == "Bonjour"
