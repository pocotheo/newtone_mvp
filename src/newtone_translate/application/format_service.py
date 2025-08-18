"""
Format Detection Service.

Detects the format of the input text with priority: Markdown > HTML > Text.

This service is responsible for detecting the format of the input text and returning the format as a string.

The format detection is done by checking for the presence of HTML tags and Markdown patterns in the text.

"""

import re


class FormatService:
    """Service for detecting content formats."""
    
    def detect_format(self, text: str) -> str:
        """Detect the format of the input text with priority: Markdown > HTML > Text."""
        if self._is_markdown_text(text):
            return "markdown"
        elif self._is_html_text(text):
            return "html"
        else:
            return "text"
    
    def _is_html_text(self, text: str) -> bool:
        """More robust HTML detection that checks for proper HTML structure."""
        # Check for HTML tags with proper structure
        html_tags = re.findall(r'<[^>]+>', text)
        if not html_tags:
            return False
        
        # Check for common HTML patterns
        has_opening_tags = any(not tag.startswith('</') for tag in html_tags)
        has_closing_tags = any(tag.startswith('</') for tag in html_tags)
        has_self_closing = any(tag.endswith('/>') for tag in html_tags)
        
        # Check for common HTML elements
        common_html_elements = ['html', 'head', 'body', 'div', 'p', 'span', 'a', 'img', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        has_html_elements = any(any(element in tag.lower() for element in common_html_elements) for tag in html_tags)
        
        # Check for proper HTML structure (opening and closing tags)
        if has_opening_tags and (has_closing_tags or has_self_closing):
            return True
        
        # Check for common HTML attributes
        has_attributes = any('=' in tag for tag in html_tags)
        if has_attributes and has_html_elements:
            return True
        
        return False

    def _is_markdown_text(self, text: str) -> bool:
        """Detect if text is Markdown format."""
        markdown_patterns = [
            r'^#+\s+',           # Headers (# ## ###)
            r'^\*\s+',           # Lists (* item)
            r'^\d+\.\s+',        # Numbered lists (1. item)
            r'^\>\s+',           # Blockquotes (> text)
            r'\[([^\]]+)\]\(([^)]+)\)',  # Links [text](url)
            r'\*\*([^*]+)\*\*',  # Bold **text**
            r'\*([^*]+)\*',      # Italic *text*
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)

