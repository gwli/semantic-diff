#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code parser for multiple programming languages using tree-sitter.
"""

import logging
import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
import hashlib

# 尝试导入 tree-sitter，如果失败则使用降级模式
try:
    import tree_sitter
    from tree_sitter import Language, Parser, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logging.getLogger(__name__).warning("Tree-sitter not available, using fallback regex parsing")


@dataclass
class CodeFunction:
    """代码函数信息"""
    name: str
    start_line: int
    end_line: int
    parameters: List[str]
    return_type: Optional[str]
    body: str
    decorators: List[str]
    docstring: Optional[str]
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False


@dataclass
class CodeClass:
    """代码类信息"""
    name: str
    start_line: int
    end_line: int
    base_classes: List[str]
    methods: List[CodeFunction]
    attributes: List[str]
    docstring: Optional[str]
    decorators: List[str]


@dataclass
class CodeVariable:
    """代码变量信息"""
    name: str
    line: int
    type_hint: Optional[str]
    value: Optional[str]
    scope: str  # global, local, class


@dataclass
class CodeImport:
    """代码导入信息"""
    module: str
    names: List[str]
    alias: Optional[str]
    line: int
    is_from_import: bool


@dataclass
class CodeStructure:
    """代码结构信息"""
    functions: List[CodeFunction]
    classes: List[CodeClass]
    variables: List[CodeVariable]
    imports: List[CodeImport]
    comments: List[str]
    complexity: int
    lines_of_code: int


class CodeParser:
    """
    多语言代码解析器
    """
    
    def __init__(self):
        """初始化解析器"""
        self.logger = logging.getLogger(__name__)
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self.fallback_mode = not TREE_SITTER_AVAILABLE
        self._warned_languages = set()  # 记录已警告的语言，避免重复警告
        
        # 支持的语言映射
        self.language_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rs": "rust",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
        }
        
        # 降级模式的正则表达式模式
        self.fallback_patterns = {
            "python": {
                "functions": r"^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:",
                "classes": r"^\s*class\s+(\w+)(?:\s*\([^)]*\))?\s*:",
                "imports": r"^\s*(?:from\s+(\S+)\s+)?import\s+(.+)",
                "variables": r"^\s*(\w+)\s*=\s*(.+)",
                "comments": r"^\s*#.*|^\s*'''.*'''|^\s*\"\"\".*\"\"\""
            },
            "javascript": {
                "functions": r"^\s*(?:function\s+(\w+)\s*\(([^)]*)\)|(\w+)\s*:\s*function\s*\(([^)]*)\)|(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=]+)\s*=>)",
                "classes": r"^\s*class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{",
                "imports": r"^\s*(?:import\s+.+\s+from\s+['\"](.+)['\"]|import\s+['\"](.+)['\"]|const\s+.+\s+=\s+require\s*\(\s*['\"](.+)['\"]\s*\))",
                "variables": r"^\s*(?:const|let|var)\s+(\w+)\s*=\s*(.+)",
                "comments": r"^\s*//.*|^\s*/\*.*\*/"
            },
            "java": {
                "functions": r"^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:\w+\s+)?(\w+)\s*\(([^)]*)\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{",
                "classes": r"^\s*(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{",
                "imports": r"^\s*import\s+(?:static\s+)?([^;]+);",
                "variables": r"^\s*(?:public|private|protected)?\s*(?:static|final)?\s*(\w+)\s+(\w+)\s*=\s*(.+);",
                "comments": r"^\s*//.*|^\s*/\*.*\*/"
            }
        }
        
        # 如果tree-sitter可用，加载语言
        if TREE_SITTER_AVAILABLE:
            self.queries = self._setup_tree_sitter_queries()
            self._load_languages()
        else:
            self.logger.info("Using fallback regex parsing mode")
    
    def _setup_tree_sitter_queries(self):
        """设置Tree-sitter查询"""
        return {
            "python": {
                "functions": """
                (function_definition
                    name: (identifier) @function_name
                    parameters: (parameters) @function_params
                    body: (block) @function_body
                ) @function_def
                """,
                "classes": """
                (class_definition
                    name: (identifier) @class_name
                    superclasses: (argument_list)? @class_bases
                    body: (block) @class_body
                ) @class_def
                """,
                "imports": """
                (import_statement 
                    name: (dotted_name) @import_name
                ) @import
                
                (import_from_statement
                    module_name: (dotted_name) @from_module
                    name: (dotted_name) @from_name
                ) @from_import
                """,
                "variables": """
                (assignment
                    left: (identifier) @var_name
                    right: (_) @var_value
                ) @assignment
                """,
                "comments": """
                (comment) @comment
                """
            },
            "javascript": {
                "functions": """
                (function_declaration
                    name: (identifier) @function_name
                    parameters: (formal_parameters) @function_params
                    body: (statement_block) @function_body
                ) @function_def
                
                (arrow_function
                    parameters: (formal_parameters) @function_params
                    body: (_) @function_body
                ) @arrow_function
                """,
                "classes": """
                (class_declaration
                    name: (identifier) @class_name
                    superclass: (class_heritage)? @class_extends
                    body: (class_body) @class_body
                ) @class_def
                """,
                "imports": """
                (import_statement
                    source: (string) @import_source
                ) @import
                """,
                "variables": """
                (variable_declaration
                    (variable_declarator
                        name: (identifier) @var_name
                        value: (_)? @var_value
                    )
                ) @var_decl
                """,
                "comments": """
                (comment) @comment
                """
            }
        }
    
    def _load_languages(self):
        """加载Tree-sitter语言"""
        if not TREE_SITTER_AVAILABLE:
            self.logger.info("Tree-sitter not available, using fallback regex parsing")
            return
            
        try:
            # 语言包映射，包含特殊的函数名
            language_packages = {
                "python": ("tree_sitter_python", "language"),
                "javascript": ("tree_sitter_javascript", "language"),
                "typescript": ("tree_sitter_typescript", "language_typescript"),
                "java": ("tree_sitter_java", "language"),
                "cpp": ("tree_sitter_cpp", "language"),
                "c": ("tree_sitter_c", "language"),
                "rust": ("tree_sitter_rust", "language"),
                "go": ("tree_sitter_go", "language"),
            }
            
            missing_languages = []
            loaded_languages = []
            
            for lang_name, (package_name, func_name) in language_packages.items():
                try:
                    # 尝试导入语言包
                    package = __import__(package_name)
                    
                    # 获取语言函数
                    lang_func = getattr(package, func_name)
                    lang_obj = lang_func()
                    
                    # 创建Language对象
                    language = Language(lang_obj)
                    self.languages[lang_name] = language
                    
                    # 创建Parser（新版本API需要language参数）
                    parser = Parser(language)
                    self.parsers[lang_name] = parser
                    
                    loaded_languages.append(lang_name)
                    
                except ImportError:
                    missing_languages.append(lang_name)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "Incompatible Language version" in error_msg:
                        self.logger.info(f"Language {lang_name} has incompatible ABI version, using fallback parsing")
                    else:
                        self.logger.error(f"Failed to load {lang_name} parser: {error_msg}")
                    missing_languages.append(lang_name)
            
            # 只在初始化时报告一次语言库状态
            if loaded_languages:
                self.logger.info(f"Loaded Tree-sitter parsers for: {', '.join(loaded_languages)}")
            
            if missing_languages:
                # 过滤掉已经单独处理的版本不兼容语言
                unavailable_langs = []
                for lang in missing_languages:
                    try:
                        package_name = language_packages[lang][0]
                        package = __import__(package_name)
                        # 如果能导入但不能使用，说明是版本问题，不需要重复警告
                        continue
                    except ImportError:
                        unavailable_langs.append(lang)
                
                if unavailable_langs:
                    self.logger.warning(f"Tree-sitter parsers not available for: {', '.join(unavailable_langs)}. Using fallback regex parsing.")
                    self.logger.info("To install Tree-sitter language libraries, run: pip install tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-java tree-sitter-cpp tree-sitter-c tree-sitter-rust tree-sitter-go")
                    
        except Exception as e:
            self.logger.error(f"Failed to load languages: {str(e)}")
    
    def detect_language(self, filename: str) -> Optional[str]:
        """
        检测文件编程语言
        
        Args:
            filename: 文件名
            
        Returns:
            编程语言名称
        """
        _, ext = os.path.splitext(filename.lower())
        return self.language_extensions.get(ext)
    
    def parse_code(self, code: str, language: str) -> Optional[CodeStructure]:
        """
        解析代码结构
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            代码结构信息
        """
        # 如果Tree-sitter可用且解析器存在，使用Tree-sitter
        if TREE_SITTER_AVAILABLE and language in self.parsers:
            return self._parse_with_tree_sitter(code, language)
        else:
            # 使用降级模式
            return self._parse_with_fallback(code, language)
    
    def _parse_with_tree_sitter(self, code: str, language: str) -> Optional[CodeStructure]:
        """使用Tree-sitter解析代码"""
        try:
            parser = self.parsers[language]
            tree = parser.parse(code.encode('utf-8'))
            
            # 提取代码结构
            structure = self._extract_structure(tree.root_node, code, language)
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Failed to parse code with tree-sitter: {str(e)}")
            # 失败时降级到正则表达式解析
            return self._parse_with_fallback(code, language)
    
    def _parse_with_fallback(self, code: str, language: str) -> Optional[CodeStructure]:
        """使用降级模式解析代码（正则表达式）"""
        try:
            lines = code.split('\n')
            
            # 使用正则表达式提取信息
            functions = self._extract_functions_fallback(lines, language)
            classes = self._extract_classes_fallback(lines, language)
            variables = self._extract_variables_fallback(lines, language)
            imports = self._extract_imports_fallback(lines, language)
            comments = self._extract_comments_fallback(lines, language)
            
            # 计算简单的复杂度指标
            complexity = self._calculate_complexity_fallback(lines, language)
            
            return CodeStructure(
                functions=functions,
                classes=classes,
                variables=variables,
                imports=imports,
                comments=comments,
                complexity=complexity,
                lines_of_code=len([line for line in lines if line.strip()])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse code with fallback: {str(e)}")
            return None
    
    def _extract_functions_fallback(self, lines: List[str], language: str) -> List[CodeFunction]:
        """使用正则表达式提取函数"""
        functions = []
        
        if language not in self.fallback_patterns:
            return functions
        
        pattern = self.fallback_patterns[language]["functions"]
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if language == "python":
                    name = match.group(1)
                    params = match.group(2).split(',') if match.group(2) else []
                    params = [p.strip() for p in params if p.strip()]
                    
                    functions.append(CodeFunction(
                        name=name,
                        start_line=i + 1,
                        end_line=i + 1,  # 简化，只记录开始行
                        parameters=params,
                        return_type=None,
                        body="",
                        decorators=[],
                        docstring=None
                    ))
                elif language == "javascript":
                    # JavaScript函数解析更复杂，简化处理
                    if match.group(1):  # function declaration
                        name = match.group(1)
                        params = match.group(2).split(',') if match.group(2) else []
                    else:  # arrow function or method
                        name = match.group(3) or match.group(5) or "anonymous"
                        params = match.group(4).split(',') if match.group(4) else []
                    
                    params = [p.strip() for p in params if p.strip()]
                    
                    functions.append(CodeFunction(
                        name=name,
                        start_line=i + 1,
                        end_line=i + 1,
                        parameters=params,
                        return_type=None,
                        body="",
                        decorators=[],
                        docstring=None
                    ))
        
        return functions
    
    def _extract_classes_fallback(self, lines: List[str], language: str) -> List[CodeClass]:
        """使用正则表达式提取类"""
        classes = []
        
        if language not in self.fallback_patterns:
            return classes
        
        pattern = self.fallback_patterns[language]["classes"]
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                name = match.group(1)
                
                classes.append(CodeClass(
                    name=name,
                    start_line=i + 1,
                    end_line=i + 1,
                    base_classes=[],
                    methods=[],
                    attributes=[],
                    docstring=None,
                    decorators=[]
                ))
        
        return classes
    
    def _extract_variables_fallback(self, lines: List[str], language: str) -> List[CodeVariable]:
        """使用正则表达式提取变量"""
        variables = []
        
        if language not in self.fallback_patterns:
            return variables
        
        pattern = self.fallback_patterns[language]["variables"]
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if language == "python":
                    name = match.group(1)
                    value = match.group(2)
                elif language in ["javascript", "java"]:
                    name = match.group(1) if language == "javascript" else match.group(2)
                    value = match.group(2) if language == "javascript" else match.group(3)
                else:
                    continue
                
                variables.append(CodeVariable(
                    name=name,
                    line=i + 1,
                    type_hint=None,
                    value=value.strip(),
                    scope="global"
                ))
        
        return variables
    
    def _extract_imports_fallback(self, lines: List[str], language: str) -> List[CodeImport]:
        """使用正则表达式提取导入"""
        imports = []
        
        if language not in self.fallback_patterns:
            return imports
        
        pattern = self.fallback_patterns[language]["imports"]
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if language == "python":
                    module = match.group(1) if match.group(1) else "builtins"
                    names = [n.strip() for n in match.group(2).split(',')]
                    is_from_import = match.group(1) is not None
                elif language == "javascript":
                    module = match.group(1) or match.group(2) or match.group(3)
                    names = ["*"]  # 简化处理
                    is_from_import = True
                elif language == "java":
                    module = match.group(1)
                    names = [module.split('.')[-1]]
                    is_from_import = False
                else:
                    continue
                
                imports.append(CodeImport(
                    module=module,
                    names=names,
                    alias=None,
                    line=i + 1,
                    is_from_import=is_from_import
                ))
        
        return imports
    
    def _extract_comments_fallback(self, lines: List[str], language: str) -> List[str]:
        """使用正则表达式提取注释"""
        comments = []
        
        if language not in self.fallback_patterns:
            return comments
        
        pattern = self.fallback_patterns[language]["comments"]
        
        for line in lines:
            if re.match(pattern, line):
                comments.append(line.strip())
        
        return comments
    
    def _calculate_complexity_fallback(self, lines: List[str], language: str) -> int:
        """计算简单的复杂度指标"""
        complexity = 1  # 基础复杂度
        
        # 基于关键字计算复杂度
        keywords = {
            "python": ["if", "elif", "else", "for", "while", "try", "except", "finally", "with"],
            "javascript": ["if", "else", "for", "while", "try", "catch", "finally", "switch", "case"],
            "java": ["if", "else", "for", "while", "try", "catch", "finally", "switch", "case"]
        }
        
        if language in keywords:
            for line in lines:
                for keyword in keywords[language]:
                    if re.search(r'\b' + keyword + r'\b', line):
                        complexity += 1
        
        return complexity
    
    def _extract_structure(self, root_node: Node, code: str, language: str) -> CodeStructure:
        """
        提取代码结构
        
        Args:
            root_node: 语法树根节点
            code: 代码字符串
            language: 编程语言
            
        Returns:
            代码结构信息
        """
        lines = code.split('\n')
        
        # 提取各种代码元素
        functions = self._extract_functions(root_node, lines, language)
        classes = self._extract_classes(root_node, lines, language)
        variables = self._extract_variables(root_node, lines, language)
        imports = self._extract_imports(root_node, lines, language)
        comments = self._extract_comments(root_node, lines, language)
        
        # 计算复杂度
        complexity = self._calculate_complexity(root_node, language)
        
        return CodeStructure(
            functions=functions,
            classes=classes,
            variables=variables,
            imports=imports,
            comments=comments,
            complexity=complexity,
            lines_of_code=len([line for line in lines if line.strip()])
        )
    
    def _extract_functions(self, root_node: Node, lines: List[str], language: str) -> List[CodeFunction]:
        """提取函数信息"""
        functions = []
        
        def traverse_functions(node: Node):
            if node.type in ['function_definition', 'function_declaration', 'arrow_function']:
                func = self._parse_function_node(node, lines, language)
                if func:
                    functions.append(func)
            
            for child in node.children:
                traverse_functions(child)
        
        traverse_functions(root_node)
        return functions
    
    def _parse_function_node(self, node: Node, lines: List[str], language: str) -> Optional[CodeFunction]:
        """解析函数节点"""
        try:
            name = "anonymous"
            parameters = []
            return_type = None
            decorators = []
            docstring = None
            is_async = False
            is_static = False
            is_classmethod = False
            
            # 提取函数名
            for child in node.children:
                if child.type == 'identifier':
                    name = self._get_node_text(child, lines)
                    break
            
            # 提取参数
            for child in node.children:
                if child.type in ['parameters', 'formal_parameters']:
                    parameters = self._extract_parameters(child, lines)
                    break
            
            # 提取函数体
            body_node = None
            for child in node.children:
                if child.type in ['block', 'statement_block']:
                    body_node = child
                    break
            
            if body_node:
                body = self._get_node_text(body_node, lines)
                
                # 提取docstring (对于Python)
                if language == "python":
                    docstring = self._extract_docstring(body_node, lines)
            else:
                body = ""
            
            return CodeFunction(
                name=name,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parameters=parameters,
                return_type=return_type,
                body=body,
                decorators=decorators,
                docstring=docstring,
                is_async=is_async,
                is_static=is_static,
                is_classmethod=is_classmethod
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse function node: {str(e)}")
            return None
    
    def _extract_classes(self, root_node: Node, lines: List[str], language: str) -> List[CodeClass]:
        """提取类信息"""
        classes = []
        
        def traverse_classes(node: Node):
            if node.type in ['class_definition', 'class_declaration']:
                cls = self._parse_class_node(node, lines, language)
                if cls:
                    classes.append(cls)
            
            for child in node.children:
                traverse_classes(child)
        
        traverse_classes(root_node)
        return classes
    
    def _parse_class_node(self, node: Node, lines: List[str], language: str) -> Optional[CodeClass]:
        """解析类节点"""
        try:
            name = "UnknownClass"
            base_classes = []
            methods = []
            attributes = []
            docstring = None
            decorators = []
            
            # 提取类名
            for child in node.children:
                if child.type == 'identifier':
                    name = self._get_node_text(child, lines)
                    break
            
            # 提取基类
            for child in node.children:
                if child.type in ['argument_list', 'class_heritage']:
                    base_classes = self._extract_base_classes(child, lines)
                    break
            
            # 提取方法
            for child in node.children:
                if child.type in ['block', 'class_body']:
                    methods = self._extract_methods(child, lines, language)
                    break
            
            return CodeClass(
                name=name,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                base_classes=base_classes,
                methods=methods,
                attributes=attributes,
                docstring=docstring,
                decorators=decorators
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse class node: {str(e)}")
            return None
    
    def _extract_variables(self, root_node: Node, lines: List[str], language: str) -> List[CodeVariable]:
        """提取变量信息"""
        variables = []
        
        def traverse_variables(node: Node, scope: str = "global"):
            if node.type in ['assignment', 'variable_declaration', 'variable_declarator']:
                var = self._parse_variable_node(node, lines, language, scope)
                if var:
                    variables.append(var)
            
            # 递归处理子节点
            for child in node.children:
                new_scope = scope
                if child.type in ['function_definition', 'function_declaration']:
                    new_scope = "local"
                elif child.type in ['class_definition', 'class_declaration']:
                    new_scope = "class"
                
                traverse_variables(child, new_scope)
        
        traverse_variables(root_node)
        return variables
    
    def _parse_variable_node(self, node: Node, lines: List[str], language: str, scope: str) -> Optional[CodeVariable]:
        """解析变量节点"""
        try:
            name = "unknown"
            type_hint = None
            value = None
            
            # 根据语言类型提取变量信息
            if language == "python":
                # Python赋值语句
                for child in node.children:
                    if child.type == 'identifier':
                        name = self._get_node_text(child, lines)
                        break
            elif language == "javascript":
                # JavaScript变量声明
                for child in node.children:
                    if child.type == 'identifier':
                        name = self._get_node_text(child, lines)
                        break
            
            return CodeVariable(
                name=name,
                line=node.start_point[0] + 1,
                type_hint=type_hint,
                value=value,
                scope=scope
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse variable node: {str(e)}")
            return None
    
    def _extract_imports(self, root_node: Node, lines: List[str], language: str) -> List[CodeImport]:
        """提取导入信息"""
        imports = []
        
        def traverse_imports(node: Node):
            if node.type in ['import_statement', 'import_from_statement']:
                imp = self._parse_import_node(node, lines, language)
                if imp:
                    imports.append(imp)
            
            for child in node.children:
                traverse_imports(child)
        
        traverse_imports(root_node)
        return imports
    
    def _parse_import_node(self, node: Node, lines: List[str], language: str) -> Optional[CodeImport]:
        """解析导入节点"""
        try:
            module = ""
            names = []
            alias = None
            is_from_import = node.type == 'import_from_statement'
            
            # 提取模块名和导入的名称
            for child in node.children:
                if child.type in ['dotted_name', 'string']:
                    text = self._get_node_text(child, lines)
                    if not module:
                        module = text.strip('"\'')
                    else:
                        names.append(text)
            
            return CodeImport(
                module=module,
                names=names,
                alias=alias,
                line=node.start_point[0] + 1,
                is_from_import=is_from_import
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse import node: {str(e)}")
            return None
    
    def _extract_comments(self, root_node: Node, lines: List[str], language: str) -> List[str]:
        """提取注释信息"""
        comments = []
        
        def traverse_comments(node: Node):
            if node.type == 'comment':
                comment_text = self._get_node_text(node, lines)
                comments.append(comment_text)
            
            for child in node.children:
                traverse_comments(child)
        
        traverse_comments(root_node)
        return comments
    
    def _calculate_complexity(self, root_node: Node, language: str) -> int:
        """计算代码复杂度"""
        complexity = 1  # 基础复杂度
        
        def traverse_complexity(node: Node):
            nonlocal complexity
            
            # 增加复杂度的节点类型
            complexity_nodes = [
                'if_statement', 'while_statement', 'for_statement',
                'try_statement', 'except_clause', 'with_statement',
                'conditional_expression', 'switch_statement', 'case_clause'
            ]
            
            if node.type in complexity_nodes:
                complexity += 1
            
            for child in node.children:
                traverse_complexity(child)
        
        traverse_complexity(root_node)
        return complexity
    
    def _get_node_text(self, node: Node, lines: List[str]) -> str:
        """获取节点文本"""
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        start_col = node.start_point[1]
        end_col = node.end_point[1]
        
        if start_line == end_line:
            return lines[start_line][start_col:end_col]
        else:
            result = lines[start_line][start_col:]
            for i in range(start_line + 1, end_line):
                result += '\n' + lines[i]
            result += '\n' + lines[end_line][:end_col]
            return result
    
    def _extract_parameters(self, node: Node, lines: List[str]) -> List[str]:
        """提取函数参数"""
        parameters = []
        
        def traverse_params(node: Node):
            if node.type == 'identifier':
                param_name = self._get_node_text(node, lines)
                parameters.append(param_name)
            
            for child in node.children:
                traverse_params(child)
        
        traverse_params(node)
        return parameters
    
    def _extract_base_classes(self, node: Node, lines: List[str]) -> List[str]:
        """提取基类"""
        base_classes = []
        
        def traverse_bases(node: Node):
            if node.type == 'identifier':
                base_name = self._get_node_text(node, lines)
                base_classes.append(base_name)
            
            for child in node.children:
                traverse_bases(child)
        
        traverse_bases(node)
        return base_classes
    
    def _extract_methods(self, node: Node, lines: List[str], language: str) -> List[CodeFunction]:
        """提取类方法"""
        methods = []
        
        def traverse_methods(node: Node):
            if node.type in ['function_definition', 'function_declaration']:
                method = self._parse_function_node(node, lines, language)
                if method:
                    methods.append(method)
            
            for child in node.children:
                traverse_methods(child)
        
        traverse_methods(node)
        return methods
    
    def _extract_docstring(self, node: Node, lines: List[str]) -> Optional[str]:
        """提取docstring"""
        # 简单实现，寻找第一个字符串字面量
        for child in node.children:
            if child.type == 'expression_statement':
                for grandchild in child.children:
                    if grandchild.type == 'string':
                        return self._get_node_text(grandchild, lines).strip('"""\'\'\'')
        return None
    
    def compare_structures(self, struct1: CodeStructure, struct2: CodeStructure) -> Dict[str, Any]:
        """
        比较两个代码结构
        
        Args:
            struct1: 第一个代码结构
            struct2: 第二个代码结构
            
        Returns:
            比较结果
        """
        result = {
            "functions": {
                "added": [],
                "removed": [],
                "modified": []
            },
            "classes": {
                "added": [],
                "removed": [],
                "modified": []
            },
            "variables": {
                "added": [],
                "removed": [],
                "modified": []
            },
            "imports": {
                "added": [],
                "removed": []
            },
            "complexity_change": struct2.complexity - struct1.complexity,
            "loc_change": struct2.lines_of_code - struct1.lines_of_code
        }
        
        # 比较函数
        func1_names = {f.name for f in struct1.functions}
        func2_names = {f.name for f in struct2.functions}
        
        result["functions"]["added"] = list(func2_names - func1_names)
        result["functions"]["removed"] = list(func1_names - func2_names)
        
        # 比较类
        class1_names = {c.name for c in struct1.classes}
        class2_names = {c.name for c in struct2.classes}
        
        result["classes"]["added"] = list(class2_names - class1_names)
        result["classes"]["removed"] = list(class1_names - class2_names)
        
        # 比较变量
        var1_names = {v.name for v in struct1.variables}
        var2_names = {v.name for v in struct2.variables}
        
        result["variables"]["added"] = list(var2_names - var1_names)
        result["variables"]["removed"] = list(var1_names - var2_names)
        
        # 比较导入
        import1_modules = {i.module for i in struct1.imports}
        import2_modules = {i.module for i in struct2.imports}
        
        result["imports"]["added"] = list(import2_modules - import1_modules)
        result["imports"]["removed"] = list(import1_modules - import2_modules)
        
        return result
    
    def get_code_hash(self, code: str) -> str:
        """
        获取代码的哈希值
        
        Args:
            code: 代码字符串
            
        Returns:
            哈希值
        """
        return hashlib.sha256(code.encode('utf-8')).hexdigest()
    
    def normalize_code(self, code: str, language: str) -> str:
        """
        标准化代码（去除无关紧要的空格、注释等）
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            标准化后的代码
        """
        lines = code.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # 简单的注释过滤
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines) 