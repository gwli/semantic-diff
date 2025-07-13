#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Language detection utilities.
"""

import os
import re
from typing import Optional, Dict, List
from pathlib import Path


class LanguageDetector:
    """
    编程语言检测器
    """
    
    def __init__(self):
        """初始化语言检测器"""
        # 文件扩展名到语言的映射
        self.extension_map = {
            '.py': 'python',
            '.pyw': 'python',
            '.js': 'javascript',
            '.mjs': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.hxx': 'cpp',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.fs': 'fsharp',
            '.vb': 'vb.net',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.r': 'r',
            '.R': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.lua': 'lua',
            '.dart': 'dart',
            '.elm': 'elm',
            '.ex': 'elixir',
            '.exs': 'elixir',
            '.erl': 'erlang',
            '.hrl': 'erlang',
            '.jl': 'julia',
            '.nim': 'nim',
            '.cr': 'crystal',
            '.d': 'd',
            '.pas': 'pascal',
            '.ada': 'ada',
            '.adb': 'ada',
            '.ads': 'ada',
            '.f': 'fortran',
            '.f90': 'fortran',
            '.f95': 'fortran',
            '.cob': 'cobol',
            '.cbl': 'cobol',
        }
        
        # 文件名模式到语言的映射
        self.filename_patterns = {
            'Dockerfile': 'dockerfile',
            'dockerfile': 'dockerfile',
            'Makefile': 'makefile',
            'makefile': 'makefile',
            'CMakeLists.txt': 'cmake',
            'requirements.txt': 'requirements',
            'package.json': 'json',
            'tsconfig.json': 'json',
            'composer.json': 'json',
            'Cargo.toml': 'toml',
            'pyproject.toml': 'toml',
            'Pipfile': 'toml',
            '.gitignore': 'gitignore',
            '.gitattributes': 'gitattributes',
            '.editorconfig': 'editorconfig',
            '.eslintrc': 'json',
            '.prettierrc': 'json',
            'README.md': 'markdown',
            'README.rst': 'rst',
            'setup.py': 'python',
            'manage.py': 'python',
            'gulpfile.js': 'javascript',
            'webpack.config.js': 'javascript',
            'babel.config.js': 'javascript',
        }
        
        # 基于内容的语言检测模式
        self.content_patterns = {
            'python': [
                r'^\s*#.*?coding[:=]\s*([-\w.]+)',
                r'^\s*def\s+\w+\s*\(',
                r'^\s*class\s+\w+\s*\(',
                r'^\s*import\s+\w+',
                r'^\s*from\s+\w+\s+import',
                r'print\s*\(',
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            ],
            'javascript': [
                r'^\s*function\s+\w+\s*\(',
                r'^\s*const\s+\w+\s*=',
                r'^\s*let\s+\w+\s*=',
                r'^\s*var\s+\w+\s*=',
                r'console\.log\s*\(',
                r'require\s*\(',
                r'module\.exports\s*=',
            ],
            'typescript': [
                r'^\s*interface\s+\w+\s*\{',
                r'^\s*type\s+\w+\s*=',
                r':\s*\w+\s*=',
                r'^\s*export\s+\w+',
                r'^\s*import\s+.*\s+from\s+[\'"]',
            ],
            'java': [
                r'^\s*public\s+class\s+\w+',
                r'^\s*package\s+[\w\.]+;',
                r'^\s*import\s+[\w\.]+;',
                r'^\s*public\s+static\s+void\s+main',
                r'System\.out\.println\s*\(',
            ],
            'cpp': [
                r'^\s*#include\s*<\w+>',
                r'^\s*#include\s*"\w+\.h"',
                r'^\s*using\s+namespace\s+std;',
                r'^\s*class\s+\w+\s*\{',
                r'std::\w+',
                r'cout\s*<<',
                r'cin\s*>>',
            ],
            'c': [
                r'^\s*#include\s*<\w+\.h>',
                r'^\s*#include\s*"\w+\.h"',
                r'^\s*int\s+main\s*\(',
                r'printf\s*\(',
                r'scanf\s*\(',
            ],
            'rust': [
                r'^\s*fn\s+\w+\s*\(',
                r'^\s*use\s+\w+',
                r'^\s*struct\s+\w+\s*\{',
                r'^\s*enum\s+\w+\s*\{',
                r'println!\s*\(',
                r'match\s+\w+\s*\{',
            ],
            'go': [
                r'^\s*package\s+\w+',
                r'^\s*import\s+\(',
                r'^\s*func\s+\w+\s*\(',
                r'^\s*type\s+\w+\s+struct\s*\{',
                r'fmt\.Printf\s*\(',
                r'fmt\.Println\s*\(',
            ],
            'shell': [
                r'^\s*#!/bin/\w*sh',
                r'^\s*#!/usr/bin/env\s+\w*sh',
                r'^\s*#.*bash',
                r'^\s*echo\s+',
                r'^\s*if\s+\[',
                r'^\s*for\s+\w+\s+in\s+',
            ],
        }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        检测文件的编程语言
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的语言，如果无法检测则返回None
        """
        if not os.path.exists(file_path):
            return None
        
        path = Path(file_path)
        
        # 1. 首先检查文件扩展名
        extension = path.suffix.lower()
        if extension in self.extension_map:
            return self.extension_map[extension]
        
        # 2. 检查文件名模式
        filename = path.name
        if filename in self.filename_patterns:
            return self.filename_patterns[filename]
        
        # 3. 基于内容检测
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)  # 只读取前4KB
                
            detected_lang = self.detect_language_from_content(content)
            if detected_lang:
                return detected_lang
                
        except Exception:
            pass
        
        # 4. 基于shebang检测
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                
            shebang_lang = self.detect_language_from_shebang(first_line)
            if shebang_lang:
                return shebang_lang
                
        except Exception:
            pass
        
        return None
    
    def detect_language_from_content(self, content: str) -> Optional[str]:
        """
        基于内容检测语言
        
        Args:
            content: 文件内容
            
        Returns:
            检测到的语言
        """
        # 统计各语言的匹配分数
        scores = {}
        
        for language, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                scores[language] = score
        
        # 返回得分最高的语言
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def detect_language_from_shebang(self, first_line: str) -> Optional[str]:
        """
        基于shebang检测语言
        
        Args:
            first_line: 文件第一行
            
        Returns:
            检测到的语言
        """
        if not first_line.startswith('#!'):
            return None
        
        # 常见的shebang模式
        shebang_patterns = {
            r'python\d*': 'python',
            r'node': 'javascript',
            r'ruby': 'ruby',
            r'perl': 'perl',
            r'bash': 'shell',
            r'sh': 'shell',
            r'zsh': 'shell',
            r'fish': 'shell',
            r'php': 'php',
            r'lua': 'lua',
            r'R': 'r',
        }
        
        for pattern, language in shebang_patterns.items():
            if re.search(pattern, first_line, re.IGNORECASE):
                return language
        
        return None
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言列表
        
        Returns:
            支持的语言列表
        """
        languages = set()
        languages.update(self.extension_map.values())
        languages.update(self.filename_patterns.values())
        languages.update(self.content_patterns.keys())
        
        return sorted(list(languages))
    
    def get_extensions_for_language(self, language: str) -> List[str]:
        """
        获取指定语言的文件扩展名
        
        Args:
            language: 编程语言
            
        Returns:
            文件扩展名列表
        """
        extensions = []
        for ext, lang in self.extension_map.items():
            if lang == language:
                extensions.append(ext)
        
        return extensions
    
    def is_text_file(self, file_path: str) -> bool:
        """
        检查文件是否为文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为文本文件
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                
            # 检查是否包含null字节
            if b'\0' in chunk:
                return False
            
            # 检查是否大部分是可打印字符
            printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
            return printable_chars / len(chunk) > 0.7 if chunk else True
            
        except Exception:
            return False
    
    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码
        """
        try:
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(10240)  # 读取前10KB
                
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
            
        except ImportError:
            # 如果没有chardet，使用简单的编码检测
            encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1024)
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            return 'utf-8'
    
    def get_file_info(self, file_path: str) -> Dict[str, str]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        info = {
            'path': file_path,
            'language': None,
            'encoding': None,
            'is_text': False,
            'size': 0,
        }
        
        try:
            if os.path.exists(file_path):
                info['size'] = os.path.getsize(file_path)
                info['is_text'] = self.is_text_file(file_path)
                
                if info['is_text']:
                    info['language'] = self.detect_language(file_path)
                    info['encoding'] = self.detect_encoding(file_path)
                    
        except Exception:
            pass
        
        return info 