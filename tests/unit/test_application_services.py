"""
Unit tests for application services.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.newtone_translate.application.config_service import ConfigService
from src.newtone_translate.application.format_service import FormatService
from src.newtone_translate.application.translation_service import TranslationService
from src.newtone_translate.domain.models import TranslationRequest


class TestConfigService:
    """Test ConfigService functionality."""
    
    def test_load_brand_config_success(self, temp_config_dir):
        """Test loading brand configuration successfully."""
        service = ConfigService()
        service.config_dir = temp_config_dir
        
        config = service.load_brand_config("default")
        
        assert config["tone"] == "elegant and sophisticated"
        assert config["voice"] == "premium luxury brand"
    
    def test_load_brand_config_missing_file(self):
        """Test loading brand config when file doesn't exist."""
        service = ConfigService()
        service.config_dir = "/nonexistent"
        
        config = service.load_brand_config("missing")
        
        # Should return default values
        assert config["tone"] == "professional"
        assert config["notes"] == "maintain brand voice"
    
    def test_load_glossary_success(self, temp_config_dir):
        """Test loading glossary successfully."""
        service = ConfigService()
        service.config_dir = temp_config_dir
        
        glossary = service.load_glossary("default")
        
        assert glossary["luxury"] == "luxe"
        assert glossary["handbag"] == "sac à main"
    
    def test_load_glossary_missing_file(self):
        """Test loading glossary when file doesn't exist."""
        service = ConfigService()
        service.config_dir = "/nonexistent"
        
        glossary = service.load_glossary("missing")
        
        assert glossary == {}
    
    def test_load_dnt_terms_success(self, temp_config_dir):
        """Test loading DNT terms successfully."""
        service = ConfigService()
        service.config_dir = temp_config_dir
        
        dnt_terms = service.load_dnt_terms("default")
        
        assert "https://example.com/shop" in dnt_terms
        assert "Italian" in dnt_terms
    
    def test_load_dnt_terms_missing_file(self):
        """Test loading DNT terms when file doesn't exist."""
        service = ConfigService()
        service.config_dir = "/nonexistent"
        
        dnt_terms = service.load_dnt_terms("missing")
        
        assert dnt_terms == []


class TestFormatService:
    """Test FormatService functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = FormatService()
    
    def test_detect_html_format(self):
        """Test detecting HTML format."""
        html_content = "<html><body><h1>Title</h1></body></html>"
        
        format_type = self.service.detect_format(html_content)
        
        assert format_type == "html"
    
    def test_detect_html_format_with_tags(self):
        """Test detecting HTML format with various tags."""
        test_cases = [
            "<div>Content</div>",
            "<p>Paragraph</p>",
            "<span class='test'>Text</span>",
            "Text with <strong>bold</strong> words",
        ]
        
        for content in test_cases:
            format_type = self.service.detect_format(content)
            assert format_type == "html", f"Failed for: {content}"
    
    def test_detect_markdown_format(self):
        """Test detecting Markdown format."""
        test_cases = [
            "# Heading 1",
            "## Heading 2", 
            "**Bold text**",
            "*Italic text*",
            "[Link](http://example.com)",
        ]
        
        for content in test_cases:
            format_type = self.service.detect_format(content)
            assert format_type == "markdown", f"Failed for: {content}"
    
    def test_detect_text_format(self):
        """Test detecting plain text format."""
        test_cases = [
            "Just plain text",
            "Text with numbers 123",
            "Text with punctuation!",
            "Multi-line\ntext content",
            "Text with special chars: @#$%",
        ]
        
        for content in test_cases:
            format_type = self.service.detect_format(content)
            assert format_type == "text", f"Failed for: {content}"
    
    def test_detect_format_edge_cases(self):
        """Test format detection edge cases."""
        # Empty string
        assert self.service.detect_format("") == "text"
        
        # Whitespace only
        assert self.service.detect_format("   \n\t   ") == "text"
        
        # HTML-like but not valid HTML
        assert self.service.detect_format("< not html >") == "text"


class TestTranslationService:
    """Test TranslationService workflow orchestration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TranslationService()
    
    @patch('src.newtone_translate.application.translation_service.FormatService')
    @patch('src.newtone_translate.application.translation_service.ContentProcessor')
    @patch('src.newtone_translate.application.translation_service.PlaceholderManager')
    @patch('src.newtone_translate.application.translation_service.ProviderFactory')
    @patch('src.newtone_translate.application.translation_service.FileStorage')
    def test_translate_full_workflow(self, mock_storage, mock_factory, 
                                   mock_placeholder, mock_processor, mock_format):
        """Test complete translation workflow."""
        # Set up mocks
        mock_format_service = Mock()
        mock_format.return_value = mock_format_service
        mock_format_service.detect_format.return_value = "text"
        
        mock_placeholder_manager = Mock()
        mock_placeholder.return_value = mock_placeholder_manager
        mock_placeholder_manager.freeze_all.return_value = ("frozen text", {"p1": "original"})
        mock_placeholder_manager.restore_all.return_value = "Bonjour le monde"
        
        mock_content_processor = Mock()
        mock_processor.return_value = mock_content_processor
        mock_content_processor.process.return_value = ("processed text", {"tokens": 10}, "en")
        
        mock_provider_factory = Mock()
        mock_factory.return_value = mock_provider_factory
        mock_provider = Mock()
        mock_provider_factory.get_provider.return_value = mock_provider
        
        mock_file_storage = Mock()
        mock_storage.return_value = mock_file_storage
        mock_file_storage.save_translation.return_value = "/path/to/output.txt"
        
        # Create fresh service instance
        service = TranslationService()
        
        # Create request
        request = TranslationRequest(
            text="Hello world",
            target_lang="fr",
            glossary={"hello": "bonjour"},
            dnt_terms=["world"]
        )
        
        # Execute translation
        result = service.translate(request)
        
        # Verify workflow steps
        mock_placeholder_manager.freeze_all.assert_called_once_with("Hello world", ["world"])
        mock_format_service.detect_format.assert_called_once_with("frozen text")
        mock_content_processor.process.assert_called_once()
        mock_placeholder_manager.restore_all.assert_called_once_with("processed text", {"p1": "original"})
        mock_file_storage.save_translation.assert_called_once()
        
        # Verify result
        assert result.translated_text == "Bonjour le monde"
        assert result.detected_language == "en"
        assert result.usage == {"tokens": 10}
        assert result.output_filepath == "/path/to/output.txt"
    
    def test_generate_metadata_with_glossary(self):
        """Test metadata generation with glossary terms."""
        output = "This is a luxe handbag made with haut de gamme materials."
        glossary = {
            "luxury": "luxe",
            "premium": "haut de gamme", 
            "handbag": "sac à main"
        }
        
        notes, applied_terms = self.service._generate_metadata(output, "text", glossary)
        
        assert "text preserved" in notes[0].lower()
        assert "luxury" in applied_terms  # Source term should be in applied_terms
        assert "premium" in applied_terms
        # handbag not in applied_terms because "sac à main" is not in output
    
    def test_generate_metadata_with_unresolved_segments(self):
        """Test metadata generation with unresolved segment markers."""
        output = "Some text with ⟦SEG_123⟧ unresolved marker."
        
        notes, applied_terms = self.service._generate_metadata(output, "html", {})
        
        assert "unresolved segment marker found" in notes[0].lower()
        assert applied_terms == []
    
    def test_generate_metadata_no_glossary_matches(self):
        """Test metadata generation with no glossary matches."""
        output = "This is regular text."
        glossary = {"luxury": "luxe", "premium": "haut de gamme"}
        
        notes, applied_terms = self.service._generate_metadata(output, "markdown", glossary)
        
        assert "markdown preserved" in notes[0].lower()
        assert applied_terms == []
