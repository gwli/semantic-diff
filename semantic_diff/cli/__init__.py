#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Line Interface module.
"""

# 延迟导入main函数，避免循环导入警告
def main():
    """CLI主入口点"""
    from .main import main as _main
    return _main()

__all__ = [
    "main",
] 