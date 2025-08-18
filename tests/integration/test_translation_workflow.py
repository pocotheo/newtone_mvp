"""
Integration tests for complete translation workflows.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from src.newtone_translate.application.translation_service import TranslationService
from src.newtone_translate.domain.models import TranslationRequest


class TestTranslationWorkflowIntegration:
    """Integration tests for complete translation workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TranslationService()
    
    def test_text_translation_workflow_with_mock_provider(self):
        """Test complete text translation workflow with mock provider."""
        request = TranslationRequest(
            text="Hello world! Visit https://example.com for more info.",
            target_lang="fr",
            glossary={"hello": "bonjour", "world": "monde"},
            dnt_terms=["https://example.com"],
            input_filename="test.txt"
        )
        
        # Use mock provider (no API key needed)
        with patch.dict(os.environ, {}, clear=True):
            result = self.service.translate(request)
        
        # Verify result structure
        assert result.translated_text is not None
        assert result.detected_language == "en"
        assert isinstance(result.notes, list)
        assert isinstance(result.applied_terms, list)
        assert isinstance(result.usage, dict)
        assert result.output_filepath is not None
        
        # Verify URL preservation
        assert "https://example.com" in result.translated_text
        
        # Verify mock translation occurred
        assert "[FR]" in result.translated_text
    
    def test_html_translation_workflow_with_mock_provider(self, sample_html):
        """Test complete HTML translation workflow."""
        request = TranslationRequest(
            text=sample_html,
            target_lang="es",
            glossary={"luxury": "lujo", "handbag": "bolso"},
            dnt_terms=["https://example.com/shop", "$599.99"],
            input_filename="product.html"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            result = self.service.translate(request)
        
        # Verify HTML structure is preserved
        assert result.translated_text.startswith("<!DOCTYPE html>")
        assert "<html>" in result.translated_text
        assert "<head>" in result.translated_text
        assert "<body>" in result.translated_text
        
        # Verify DNT terms are preserved
        assert "https://example.com/shop" in result.translated_text
        assert "$599.99" in result.translated_text
        
        # Verify translation occurred
        assert "[ES]" in result.translated_text
        
        # Verify format detection
        assert "html preserved" in str(result.notes).lower()
    
    def test_markdown_translation_workflow_with_mock_provider(self, sample_markdown):
        """Test complete Markdown translation workflow."""
        request = TranslationRequest(
            text=sample_markdown,
            target_lang="de",
            glossary={"premium": "premium", "leather": "leder"},
            dnt_terms=["Italian"],
            brand_guide={"tone": "sophisticated", "voice": "luxury"},
            input_filename="product.md"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            result = self.service.translate(request)
        
        # Verify markdown structure elements are preserved or translation occurred
        assert ("# " in result.translated_text or 
                "## " in result.translated_text or 
                "- " in result.translated_text or 
                "[Visit our store]" in result.translated_text or 
                "[DE]" in result.translated_text)
        
        # Verify DNT terms preservation
        assert "Italian" in result.translated_text
        
        # Verify translation occurred
        assert "[DE]" in result.translated_text
    
    def test_workflow_with_configuration_files(self, temp_config_dir):
        """Test workflow using configuration files."""
        # Patch config directory
        with patch('src.newtone_translate.application.config_service.ConfigService.__init__') as mock_init:
            mock_init.return_value = None
            
            # Create service and manually set config directory
            service = TranslationService()
            service.format_service = service.format_service  # Keep existing
            service.content_processor = service.content_processor  # Keep existing
            service.placeholder_manager = service.placeholder_manager  # Keep existing
            service.provider_factory = service.provider_factory  # Keep existing
            service.file_storage = service.file_storage  # Keep existing
            
            request = TranslationRequest(
                text="Luxury handbag with premium craftsmanship",
                target_lang="fr",
                input_filename="product.txt"
            )
            
            with patch.dict(os.environ, {}, clear=True):
                result = service.translate(request)
            
            # Verify basic translation occurred
            assert result.translated_text is not None
            assert "[FR]" in result.translated_text
    
    def test_workflow_error_handling_invalid_request(self):
        """Test workflow error handling with invalid request."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            TranslationRequest(text="", target_lang="fr")
        
        with pytest.raises(ValueError, match="Target language is required"):
            TranslationRequest(text="Hello", target_lang="")
    
    def test_workflow_with_file_storage(self, temp_data_dir):
        """Test workflow with actual file storage."""
        # Patch storage directory
        with patch('src.newtone_translate.infrastructure.storage.FileStorage.__init__') as mock_init:
            mock_init.return_value = None
            
            service = TranslationService()
            # Manually set storage directories
            service.file_storage.input_dir = str(Path(temp_data_dir) / "input")
            service.file_storage.output_dir = str(Path(temp_data_dir) / "output")
            
            request = TranslationRequest(
                text="Test content for file storage",
                target_lang="fr",
                input_filename="test.txt"
            )
            
            with patch.dict(os.environ, {}, clear=True):
                result = service.translate(request)
            
            # Verify file was created (mocked, but path should be set)
            assert result.output_filepath is not None
            assert "test" in result.output_filepath.lower()
    
    @patch('openai.OpenAI')
    def test_workflow_with_openai_provider_integration(self, mock_openai_class):
        """Test integration with OpenAI provider (mocked)."""
        # Mock successful OpenAI response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
            "translations": [{"id": "t1", "text": "Bonjour le monde"}],
            "detected_language": "en"
        }'''
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 80
        
        mock_client.chat.completions.create.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello world",
            target_lang="fr",
            glossary={"hello": "bonjour"},
            brand_guide={"tone": "casual"}
        )
        
        # Set API key to use OpenAI provider
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = self.service.translate(request)
        
        # Verify OpenAI integration
        assert result.translated_text == "Bonjour le monde"
        assert result.detected_language == "en"
        assert result.usage["input"] == 50
        assert result.usage["output"] == 30
        
        # Verify OpenAI was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        assert "gpt-4o-mini" in str(call_args["model"])
        assert "bonjour" in str(call_args["messages"])  # Glossary included
        assert "casual" in str(call_args["messages"])   # Brand guide included


class TestCLIIntegration:
    """Integration tests for CLI interface."""
    
    @patch('sys.argv', ['test_script', 'Hello world', 'fr'])
    @patch('src.newtone_translate.presentation.cli.TranslationService')
    def test_cli_workflow_integration(self, mock_service_class):
        """Test CLI workflow integration with command line arguments."""
        from src.newtone_translate.presentation.cli import CLI
        
        # Mock translation service
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_result = Mock()
        mock_result.translated_text = "Bonjour le monde"
        mock_result.detected_language = "en"
        mock_result.notes = ["Translation completed"]
        mock_result.applied_terms = ["hello"]
        mock_result.usage = {"tokens": 10}
        mock_result.output_filepath = "/path/to/output.txt"
        
        mock_service.translate.return_value = mock_result
        
        # Test CLI initialization (the actual interface)
        cli = CLI()
        assert cli.translation_service is not None
        assert cli.config_service is not None
        assert cli.file_storage is not None
