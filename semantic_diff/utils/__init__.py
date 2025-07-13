#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities module for helper functions and classes.
"""

# Conditional imports to handle missing dependencies
try:
    from .code_parser import CodeParser
except ImportError:
    CodeParser = None

try:
    from .language_detector import LanguageDetector
except ImportError:
    LanguageDetector = None

try:
    from .config_loader import ConfigLoader
except ImportError:
    ConfigLoader = None

try:
    from .formatter import DiffFormatter
except ImportError:
    DiffFormatter = None

__all__ = [
    "CodeParser",
    "LanguageDetector",
    "ConfigLoader",
    "DiffFormatter",
] 