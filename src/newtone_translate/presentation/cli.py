#!/usr/bin/env python3
"""
Command-line interface for the translation system.

This module provides the main entry point for CLI usage.
"""

import os
import sys
from typing import Dict, List

from ..application.translation_service import TranslationService
from ..application.config_service import ConfigService
from ..domain.models import TranslationRequest
from ..infrastructure.storage import FileStorage


class CLI:
    """Command-line interface for translation system."""
    
    def __init__(self):
        """Initialize CLI with services."""
        self.config_service = ConfigService()
        self.translation_service = TranslationService()
        self.file_storage = FileStorage()
    
    def run(self) -> None:
        """Main CLI entry point."""
        # Example input and configuration
        input_text = '<p>New Season arrivals at Newtone. <a href="/shop">Shop Now</a>.</p>'
        target = "fr"
        glossary = {"Shop Now": "Acheter", "New Season": "Nouvelle saison"}
        dnt = ["Newtone"]
        brand = {"tone": "elegant, minimal, premium", "notes": "avoid exclamation marks"}
        input_filename = None

        # Handle command line arguments
        if len(sys.argv) > 1:
            if os.path.isfile(sys.argv[1]):
                input_filename = sys.argv[1]
                input_text = self.file_storage.read_file(sys.argv[1])
            else:
                input_text = sys.argv[1]
        
        if len(sys.argv) > 2:
            target = sys.argv[2]

        # Create translation request
        request = TranslationRequest(
            text=input_text,
            target_lang=target,
            glossary=glossary,
            dnt_terms=dnt,
            brand_guide=brand,
            input_filename=input_filename
        )

        # Execute translation
        result = self.translation_service.translate(request)

        # Display results
        self._display_results(result)
    
    def _display_results(self, result) -> None:
        """Display translation results to user."""
        print("=== Translated Output ===")
        print(result.translated_text)
        print(f"\nDetected language: {result.detected_language}")
        print(f"Notes: {result.notes}")
        print(f"Glossary applied: {result.applied_terms}")
        print(f"Usage: {result.usage}")
        print(f"Output file: {result.output_filepath}")


def main():
    """CLI entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
