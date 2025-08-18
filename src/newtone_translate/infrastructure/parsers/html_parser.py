"""
HTML Parser Infrastructure.

Moved from parsers/html_parser.py to infrastructure layer.
"""

from typing import Dict, List
from bs4 import BeautifulSoup, NavigableString, Doctype, Comment, ProcessingInstruction, Declaration
from ..logging import get_logger
import re


class HTMLParser:
    """Infrastructure service for parsing HTML content."""
    
    kind = "html"

    def __init__(self):
        """Initialize HTML parser."""
        self.logger = get_logger("newtone_translate")
        self.doctype = None
        self.is_fragment = False

    def parse(self, html: str):
        """Parse HTML content into BeautifulSoup object."""
        self.logger.info("Parsing HTML input.")
        # Capture original DOCTYPE text up front
        m = re.search(r'<!DOCTYPE[^>]*>', html, re.IGNORECASE)
        if m:
            self.doctype = m.group(0)
            self.logger.info(f"Found DOCTYPE: {self.doctype}")

        # Check if input is a complete HTML document or just a fragment
        has_html_tag = bool(re.search(r'<html[^>]*>', html, re.IGNORECASE))
        has_body_tag = bool(re.search(r'<body[^>]*>', html, re.IGNORECASE))
        
        self.is_fragment = not (has_html_tag or has_body_tag)
        self.logger.info(f"Input is {'fragment' if self.is_fragment else 'complete document'}")

        soup = BeautifulSoup(html, "html5lib")

        # Remove any Doctype node from the soup so it never becomes a text segment
        for node in list(soup.contents):
            if isinstance(node, Doctype):
                node.extract()

        return soup

    def extract_segments(self, soup) -> List[Dict]:
        """Extract text segments from parsed HTML."""
        segments, counter = [], 0
        self.logger.info("Extracting text segments from HTML DOM.")

        # Skip special string-like nodes that html5lib may expose
        skip_types = (Comment, Doctype, ProcessingInstruction, Declaration)

        for node in soup.find_all(string=True):
            if not isinstance(node, NavigableString):
                self.logger.info(f"Skipping non-NavigableString node: {type(node)}")
                continue
            if isinstance(node, skip_types):
                self.logger.info("Skipping DOCTYPE/comment/PI/declaration.")
                continue
            if not str(node).strip():
                self.logger.info("Skipping empty or whitespace-only node.")
                continue

            parent = node.parent
            if parent and parent.name in {"script", "style"}:
                self.logger.info(f"Skipping node inside <{parent.name}> tag.")
                continue

            counter += 1
            seg_id = f"n{counter}"
            self.logger.info(f"Segment {seg_id}: '{str(node)}'")
            segments.append({"id": seg_id, "text": str(node)})
            node.replace_with(f"⟦SEG_{seg_id}⟧")

        self.logger.info(f"Extracted {len(segments)} segments.")
        return segments

    def apply_translations(self, soup, translations: Dict[str, str]):
        """Apply translations to parsed HTML."""
        self.logger.info(f"Applying translations to {len(translations)} segments.")

        # Replace placeholders in-place without converting to string or reparsing
        for seg_id, txt in translations.items():
            placeholder = f"⟦SEG_{seg_id}⟧"
            for node in list(soup.find_all(string=placeholder)):
                node.replace_with(txt)

        # Also handle cases where multiple placeholders are in one text node
        pattern = re.compile(r"⟦SEG_(n\d+)⟧")
        for node in list(soup.find_all(string=pattern)):
            s = str(node)
            for seg_id in pattern.findall(s):
                if seg_id in translations:
                    s = s.replace(f"⟦SEG_{seg_id}⟧", translations[seg_id])
            node.replace_with(s)

        return soup

    def serialize(self, soup) -> str:
        """Serialize parsed HTML back to string."""
        self.logger.info("Serializing soup to HTML string.")
        
        if self.is_fragment:
            # For fragments, return only the body contents (skip html/head/body wrapper)
            self.logger.info("Serializing as HTML fragment (excluding html/head/body wrapper)")
            body = soup.find("body")
            if body:
                # Return the inner content of body tag
                html_content = "".join(str(child) for child in body.children)
            else:
                # Fallback if no body tag found
                html_content = str(soup)
        else:
            # For complete documents, return everything
            self.logger.info("Serializing as complete HTML document")
            html_tag = soup.find("html")
            html_content = str(html_tag) if html_tag else str(soup)

        if self.doctype:
            self.logger.info(f"Adding DOCTYPE: {self.doctype}")
            return f"{self.doctype}\n{html_content}"
        
        return html_content
