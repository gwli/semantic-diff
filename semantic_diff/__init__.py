#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Semantic Diff Tool - 基于Qwen3-4B的语义理解DIFF工具

一个能够理解代码语义的智能diff工具，而不仅仅是简单的文本比较。
"""

__version__ = "0.1.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

# Main components - import on demand to avoid dependency issues
try:
    from .core.semantic_diff import SemanticDiff
except ImportError:
    SemanticDiff = None

try:
    from .models.qwen_model import QwenModel
except ImportError:
    QwenModel = None

try:
    from .utils.code_parser import CodeParser
except ImportError:
    CodeParser = None

__all__ = [
    "SemanticDiff",
    "QwenModel", 
    "CodeParser",
] 