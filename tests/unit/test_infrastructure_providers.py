"""
Unit tests for infrastructure providers.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.newtone_translate.infrastructure.providers.mock_provider import MockProvider
from src.newtone_translate.infrastructure.providers.openai_provider import OpenAIProvider
from src.newtone_translate.infrastructure.providers.provider_factory import ProviderFactory


class TestMockProvider:
    """Test MockProvider functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = MockProvider()
    
    def test_translate_segments_single_segment(self):
        """Test translating a single segment."""
        segments = [{"id": "t1", "text": "Hello world"}]
        
        translations, usage, detected_lang = self.provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        assert "t1" in translations
        assert "[FR]" in translations["t1"]
        assert "Hello world" in translations["t1"]
        assert usage["input"] > 0
        assert detected_lang == "en"
    
    def test_translate_segments_multiple_segments(self):
        """Test translating multiple segments."""
        segments = [
            {"id": "h1", "text": "Welcome"},
            {"id": "p1", "text": "This is a paragraph"}
        ]
        
        translations, usage, detected_lang = self.provider.translate_segments(
            segments=segments,
            target_lang="es",
            source_lang="en",
            brand_guide={},
            glossary={}
        )
        
        assert len(translations) == 2
        assert "h1" in translations
        assert "p1" in translations
        assert "[ES]" in translations["h1"]
        assert "[ES]" in translations["p1"]
        assert "Welcome" in translations["h1"]
        assert "This is a paragraph" in translations["p1"]
    
    def test_translate_segments_with_glossary(self):
        """Test translation with glossary terms."""
        segments = [{"id": "t1", "text": "Premium handbag"}]
        glossary = {"premium": "haut de gamme", "handbag": "sac à main"}
        
        translations, usage, detected_lang = self.provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary=glossary
        )
        
        # Mock provider should include glossary note
        translation = translations["t1"]
        assert "[FR]" in translation
        assert "Premium handbag" in translation
    
    def test_translate_segments_with_brand_guide(self):
        """Test translation with brand guidelines."""
        segments = [{"id": "t1", "text": "Luxury products"}]
        brand_guide = {"tone": "elegant", "voice": "sophisticated"}
        
        translations, usage, detected_lang = self.provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide=brand_guide,
            glossary={}
        )
        
        translation = translations["t1"]
        assert "[FR]" in translation
        assert "Luxury products" in translation
    
    def test_translate_segments_empty_input(self):
        """Test handling of empty segments."""
        translations, usage, detected_lang = self.provider.translate_segments(
            segments=[],
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        assert translations == {}
        assert usage["input"] == 10
        assert detected_lang == "en"


class TestOpenAIProvider:
    """Test OpenAIProvider functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = OpenAIProvider()
    
    @patch('openai.OpenAI')
    def test_translate_segments_success(self, mock_openai_class):
        """Test successful translation."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "translations": [{"id": "t1", "text": "Bonjour le monde"}],
            "detected_language": "en"
        })
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 80
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create provider instance after mocking
        provider = OpenAIProvider()
        
        segments = [{"id": "t1", "text": "Hello world"}]
        translations, usage, detected_lang = provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        assert translations == {"t1": "Bonjour le monde"}
        assert detected_lang == "en"
        assert usage["input"] == 50
        assert usage["output"] == 30
    
    @patch('openai.OpenAI')
    def test_translate_segments_with_glossary_and_brand_guide(self, mock_openai_class):
        """Test translation with glossary and brand guide."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "translations": [{"id": "t1", "text": "Sac à main haut de gamme"}],
            "detected_language": "en"
        })
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = mock_response
        
        provider = OpenAIProvider()
        
        segments = [{"id": "t1", "text": "Premium handbag"}]
        glossary = {"premium": "haut de gamme", "handbag": "sac à main"}
        brand_guide = {"tone": "elegant", "voice": "luxury"}
        
        translations, usage, detected_lang = provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide=brand_guide,
            glossary=glossary
        )
        
        # Verify the payload included glossary and brand guide
        call_args = mock_client.chat.completions.create.call_args[1]
        user_content = call_args["messages"][1]["content"]
        
        assert "haut de gamme" in user_content
        assert "sac à main" in user_content
        assert "elegant" in user_content
        assert "luxury" in user_content
        
        assert translations == {"t1": "Sac à main haut de gamme"}
    
    @patch('openai.OpenAI')
    def test_translate_segments_api_error(self, mock_openai_class):
        """Test handling of API errors."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        provider = OpenAIProvider()
        
        segments = [{"id": "t1", "text": "Hello world"}]
        
        # Should handle error gracefully and return original text
        translations, usage, detected_lang = provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        # Should fallback to original text when API fails
        assert translations == {"t1": "Hello world"}
        assert detected_lang == "auto"
        assert usage["input"] == 0
        assert usage["output"] == 0
    
    @patch('openai.OpenAI')
    def test_translate_segments_invalid_json_response(self, mock_openai_class):
        """Test handling of invalid JSON response."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        
        provider = OpenAIProvider()
        
        segments = [{"id": "t1", "text": "Hello world"}]
        
        # Should handle invalid JSON gracefully and return original text
        translations, usage, detected_lang = provider.translate_segments(
            segments=segments,
            target_lang="fr",
            source_lang="auto",
            brand_guide={},
            glossary={}
        )
        
        # Should fallback to original text when JSON is invalid
        assert translations == {"t1": "Hello world"}
        assert detected_lang == "auto"
        assert usage["input"] == 10
        assert usage["output"] == 5


class TestProviderFactory:
    """Test ProviderFactory functionality."""
    
    def setup_method(self):
        """Set up test fixtures.""" 
        self.factory = ProviderFactory()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_get_provider_with_openai_key(self):
        """Test getting OpenAI provider when API key is available."""
        provider = self.factory.get_provider()
        assert isinstance(provider, OpenAIProvider)
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_provider_without_openai_key(self):
        """Test falling back to MockProvider when no API key."""
        provider = self.factory.get_provider()
        assert isinstance(provider, MockProvider)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': ''})
    def test_get_provider_with_empty_openai_key(self):
        """Test falling back to MockProvider when API key is empty."""
        provider = self.factory.get_provider()
        assert isinstance(provider, MockProvider)
