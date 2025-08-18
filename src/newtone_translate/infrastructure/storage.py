"""
File Storage Infrastructure.

Handles file I/O operations for the translation system.
"""

import os
import datetime
from .logging import get_logger

logger = get_logger("newtone_translate")


class FileStorage:
    """Infrastructure service for file operations."""
    
    def __init__(self):
        """Initialize file storage with default directories."""
        self.data_dir = "data"
        self.output_dir = os.path.join(self.data_dir, "output")
    
    def save_translation(self, output_text: str, input_format: str, 
                        target_lang: str, input_filename: str = None) -> str:
        """
        Save translated output to appropriate directory.
        
        Args:
            output_text: Translated content
            input_format: Format type (html, markdown, text)
            target_lang: Target language
            input_filename: Original filename (optional)
            
        Returns:
            Path to saved file
        """
        # Create output directory structure
        format_dir = os.path.join(self.output_dir, input_format)
        os.makedirs(format_dir, exist_ok=True)
        
        # Determine file extension based on input format
        extension_map = {
            "html": "html",
            "markdown": "md", 
            "text": "txt"
        }
        extension = extension_map.get(input_format, "txt")
        
        # Generate filename
        if input_filename:
            # Extract base name without extension and add _translated suffix
            base_name = os.path.splitext(os.path.basename(input_filename))[0]
            filename = f"{base_name}_translated_{target_lang}.{extension}"
        else:
            # Fallback to timestamp-based naming
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"translated_{target_lang}_{timestamp}.{extension}"
        
        filepath = os.path.join(format_dir, filename)
        
        # Save the translated output
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output_text)
        
        logger.info(f"Translated output saved to: {filepath}")
        return filepath
    
    def read_file(self, filepath: str) -> str:
        """
        Read content from file.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content as string
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
