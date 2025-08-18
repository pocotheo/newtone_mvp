"""
Configuration Service.

Handles loading and managing application configuration.
"""

import os
import json
from typing import Dict, List
from ..infrastructure.storage import FileStorage


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self):
        """Initialize configuration service."""
        self.config_dir = "config"
        self.file_storage = FileStorage()
    
    def load_brand_config(self, brand_name: str = "default") -> Dict:
        """Load brand guidelines."""
        try:
            config_path = os.path.join(self.config_dir, "brand", brand_name, "brand_guidelines.json")
            content = self.file_storage.read_file(config_path)
            return json.loads(content)
        except FileNotFoundError:
            return {"tone": "professional", "notes": "maintain brand voice"}
    
    def load_glossary(self, domain: str = "default") -> Dict[str, str]:
        """Load glossary for specific domain."""
        try:
            glossary_path = os.path.join(self.config_dir, "brand", domain, "glossary.json")
            content = self.file_storage.read_file(glossary_path)
            return json.loads(content)
        except FileNotFoundError:
            return {}
    
    def load_dnt_terms(self, domain: str = "default") -> List[str]:
        """Load Do Not Translate terms."""
        try:
            dnt_path = os.path.join(self.config_dir, "brand", domain, "dnt.json")
            content = self.file_storage.read_file(dnt_path)
            data = json.loads(content)
            return data if isinstance(data, list) else data.get("terms", [])
        except FileNotFoundError:
            return []
