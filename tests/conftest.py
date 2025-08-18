"""
Pytest configuration and shared fixtures.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Test data
SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Product Page</title>
</head>
<body>
    <h1>Luxury Handbag Collection</h1>
    <p>Experience the finest <strong>craftsmanship</strong> with our exclusive handbags.</p>
    <a href="https://example.com/shop">Shop Now</a>
    <div class="price">$599.99</div>
</body>
</html>"""

SAMPLE_MARKDOWN = """# Product Description

Our **premium leather goods** are crafted with attention to detail.

## Features
- Genuine Italian leather
- Hand-stitched details
- Premium hardware

[Visit our store](https://example.com/store)
"""

SAMPLE_TEXT = "Welcome to our luxury fashion boutique. We offer premium quality items."

BRAND_GUIDELINES = {
    "tone": "elegant and sophisticated",
    "voice": "premium luxury brand",
    "notes": "Maintain exclusivity and craftsmanship focus",
    "target_audience": "affluent customers seeking quality"
}

GLOSSARY = {
    "handbag": "sac à main",
    "luxury": "luxe",
    "craftsmanship": "savoir-faire",
    "premium": "haut de gamme"
}

DNT_TERMS = [
    "https://example.com/shop",
    "https://example.com/store", 
    "$599.99",
    "Italian"
]


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return SAMPLE_HTML


@pytest.fixture
def sample_markdown():
    """Sample Markdown content for testing."""
    return SAMPLE_MARKDOWN


@pytest.fixture
def sample_text():
    """Sample plain text for testing."""
    return SAMPLE_TEXT


@pytest.fixture
def brand_guidelines():
    """Sample brand guidelines."""
    return BRAND_GUIDELINES.copy()


@pytest.fixture
def glossary():
    """Sample translation glossary."""
    return GLOSSARY.copy()


@pytest.fixture
def dnt_terms():
    """Sample Do Not Translate terms."""
    return DNT_TERMS.copy()


@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "config"
        brand_dir = config_dir / "brand" / "default"
        brand_dir.mkdir(parents=True)
        
        # Create config files
        (brand_dir / "brand_guidelines.json").write_text(
            json.dumps(BRAND_GUIDELINES, indent=2)
        )
        (brand_dir / "glossary.json").write_text(
            json.dumps(GLOSSARY, indent=2)
        )
        (brand_dir / "dnt.json").write_text(
            json.dumps(DNT_TERMS, indent=2)
        )
        
        yield str(config_dir)


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "data"
        
        # Create input directories
        input_dir = data_dir / "input" / "html"
        input_dir.mkdir(parents=True)
        
        # Create output directories  
        output_dir = data_dir / "output" / "html"
        output_dir.mkdir(parents=True)
        
        # Create sample files
        (input_dir / "sample.html").write_text(SAMPLE_HTML)
        
        yield str(data_dir)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "translations": {
                        "t1": "Bienvenue dans notre boutique de mode de luxe."
                    },
                    "detected_language": "en"
                })
            }
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    }


@pytest.fixture
def translation_request_data():
    """Sample translation request data."""
    return {
        "text": SAMPLE_TEXT,
        "target_lang": "fr",
        "glossary": GLOSSARY,
        "dnt_terms": DNT_TERMS,
        "brand_guide": BRAND_GUIDELINES,
        "input_filename": "test.txt"
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment
    os.environ["NEWTONE_ENV"] = "test"
    
    # Mock OpenAI API key for tests
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = "test-api-key"
    
    yield
    
    # Cleanup
    if "NEWTONE_ENV" in os.environ:
        del os.environ["NEWTONE_ENV"]


@pytest.fixture
def mock_provider_response():
    """Standard mock provider response."""
    return {
        "t1": "Texte traduit en français"
    }, {"tokens": 100}, "en"
