"""
Unit tests for PlaceholderManager.
"""

import pytest
from src.newtone_translate.domain.placeholder_manager import PlaceholderManager


class TestPlaceholderManager:
    """Test PlaceholderManager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PlaceholderManager()
    
    def test_freeze_urls(self):
        """Test URL freezing and restoration."""
        text = "Visit our website at https://example.com for more info."
        
        frozen, placeholders = self.manager.freeze_all(text, [])
        
        # URL should be replaced with placeholder
        assert "https://example.com" not in frozen
        assert "⟦PH_" in frozen
        
        # Restore should bring back original URL
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
    
    def test_freeze_emails(self):
        """Test email freezing and restoration."""
        text = "Contact us at support@example.com for help."
        
        frozen, placeholders = self.manager.freeze_all(text, [])
        
        # Email should be replaced with placeholder
        assert "support@example.com" not in frozen
        assert "⟦PH_" in frozen
        
        # Restore should bring back original email
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
    
    def test_freeze_dnt_terms(self):
        """Test Do Not Translate terms freezing."""
        text = "Our brand is Premium Luxury and we offer Italian leather."
        dnt_terms = ["Premium Luxury", "Italian"]
        
        frozen, placeholders = self.manager.freeze_all(text, dnt_terms)
        
        # DNT terms should be replaced with placeholders
        assert "Premium Luxury" not in frozen
        assert "Italian" not in frozen
        assert "⟦PH_" in frozen
        
        # Restore should bring back original terms
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
    
    def test_freeze_numbers_with_symbols(self):
        """Test freezing numbers with currency symbols."""
        text = "The price is $299.99 or €250.00."
        
        frozen, placeholders = self.manager.freeze_all(text, [])
        
        # Prices should be replaced with placeholders
        assert "$299.99" not in frozen
        assert "€250.00" not in frozen
        assert "⟦PH_" in frozen
        
        # Restore should bring back original prices
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
    
    
    def test_complex_text_with_multiple_patterns(self):
        """Test text with multiple patterns to freeze."""
        text = '''
        <h1>Contact Information</h1>
        <p>Visit https://example.com or email info@company.com</p>
        <div class="price">Price: $199.99</div>
        <p>Made with Italian leather by Premium Brand</p>
        '''
        dnt_terms = ["Premium Brand", "Italian"]
        
        frozen, placeholders = self.manager.freeze_all(text, dnt_terms)
        
        # All patterns should be frozen
        assert "https://example.com" not in frozen
        assert "info@company.com" not in frozen
        assert "$199.99" not in frozen
        assert "Premium Brand" not in frozen
        assert "Italian" not in frozen
        
        # Placeholders should be present
        assert "⟦PH_" in frozen
        
        # Regular text should remain
        assert "Contact Information" in frozen
        assert "leather by" in frozen
        
        # Restore should bring back everything
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored.strip() == text.strip()
    
    def test_empty_text(self):
        """Test handling of empty text."""
        frozen, placeholders = self.manager.freeze_all("", [])
        
        assert frozen == ""
        assert len(placeholders) == 0
        
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == ""
    
    def test_text_with_no_patterns(self):
        """Test text with no patterns to freeze."""
        text = "This is just regular text with no special patterns."
        
        frozen, placeholders = self.manager.freeze_all(text, [])
        
        assert frozen == text
        assert len(placeholders) == 0
        
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
    
    def test_overlapping_dnt_terms(self):
        """Test handling of overlapping DNT terms."""
        text = "Italian Premium Italian Leather Goods"
        dnt_terms = ["Italian Premium", "Italian Leather", "Premium Italian"]
        
        frozen, placeholders = self.manager.freeze_all(text, dnt_terms)
        
        # Should handle overlapping terms gracefully
        restored = self.manager.restore_all(frozen, placeholders)
        assert "Italian" in restored
        assert "Premium" in restored
        assert "Leather" in restored
    
    def test_case_sensitivity(self):
        """Test case sensitivity in DNT terms."""
        text = "Visit EXAMPLE.COM or example.com for more info."
        dnt_terms = ["example.com"]
        
        frozen, placeholders = self.manager.freeze_all(text, dnt_terms)
        
        # Should be case sensitive for DNT terms
        assert "EXAMPLE.COM" in frozen  # Uppercase not in DNT
        assert "example.com" not in frozen  # Lowercase is in DNT
        
        restored = self.manager.restore_all(frozen, placeholders)
        assert restored == text
