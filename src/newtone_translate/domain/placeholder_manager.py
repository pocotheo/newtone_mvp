"""
Placeholder Manager - Domain service for managing placeholders and DNT terms.

Moved from placeholders.py to domain layer as it contains business logic.
"""

import re
from typing import Dict, List, Tuple
from ..infrastructure.logging import get_logger


class PlaceholderManager:
    """
    Domain service for freezing and restoring placeholders.
    
    Handles URLs, emails, SKUs, and custom Do Not Translate (DNT) items.
    """
    
    def __init__(self):
        """Initialize placeholder manager with predefined rules."""
        self.rules = {
            "URL": r"https?://[^\s\"'>]+|(?<=href=\")/[^\"']+",
            "EMAIL": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            "SKU": r"\bSKU-[A-Z0-9]+\b",
            "MARKDOWN_LINK": r"\[([^\]]+)\]\(([^)]+)\)",
            "CURRENCY": r"[$€£¥]\d+(?:\.\d{2})?",
            "HTML_TAG": r"<[^>]+>",
        }
        self.logger = get_logger("newtone_translate")

    def freeze_all(self, text: str, dnt_patterns: List[str]) -> Tuple[str, Dict[str, str]]:
        """
        Freeze placeholders and DNT items in text.
        
        Args:
            text: Input text to process
            dnt_patterns: List of Do Not Translate patterns
            
        Returns:
            Tuple of (frozen_text, placeholder_mapping)
        """
        mapping, idx = {}, 0
        patterns = list(self.rules.values()) + list(dnt_patterns or [])
        self.logger.info(f"Freeze step: Using patterns: {patterns}")

        def replace_once(t, src):
            nonlocal idx, mapping
            # avoid duplicating mapping for same src
            if src in mapping.values():
                self.logger.info(f"Already mapped: {src}, skipping replacement.")
                return t
            idx += 1
            token = f"⟦PH_{idx}⟧"
            mapping[token] = src
            self.logger.info(f"Replacing '{src}' with token '{token}'")
            return t.replace(src, token, 1)

        # Process markdown links first (special case)
        if self.rules["MARKDOWN_LINK"] in patterns:
            self.logger.info("Processing markdown links first...")
            markdown_pattern = self.rules["MARKDOWN_LINK"]
            for m in re.finditer(markdown_pattern, text):
                link_text = m.group(1)  # The text part from [text]/(url)
                url = m.group(2)        # The URL part
                self.logger.info(f"Found markdown link: '{link_text}' -> '{url}'")
                # Only replace the URL part with a placeholder
                if url not in mapping.values():
                    idx += 1
                    token = f"⟦PH_{idx}⟧"
                    mapping[token] = url
                    self.logger.info(f"Replacing URL '{url}' with token '{token}'")
                    # Replace the URL part in the original text
                    text = text.replace(f"({url})", f"({token})", 1)
            # Remove markdown pattern from regular processing
            patterns.remove(self.rules["MARKDOWN_LINK"])

        # Process all other patterns
        for pat in patterns:
            self.logger.info(f"Searching for pattern: {pat}")
            for m in re.finditer(pat, text):
                src = m.group(0)
                self.logger.info(f"Found match: '{src}'")
                text = replace_once(text, src)
        
        self.logger.info(f"Final mapping: {mapping}")
        return text, mapping

    def restore_all(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restore placeholders in text.
        
        Args:
            text: Text with placeholder tokens
            mapping: Mapping of tokens to original values
            
        Returns:
            Text with restored original values
        """
        for token, src in mapping.items():
            text = text.replace(token, src)
        return text
