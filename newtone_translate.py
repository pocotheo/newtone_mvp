#!/usr/bin/env python3
"""
Main entry point for Newtone Translation System.

This script provides a convenient command-line interface for the translation system
using the layered architecture.
"""

import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.newtone_translate.presentation.cli import main

if __name__ == "__main__":
    main()
