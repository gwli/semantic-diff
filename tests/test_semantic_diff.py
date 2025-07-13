#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语义diff工具的测试模块
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from semantic_diff import SemanticDiff
from semantic_diff.core.semantic_analyzer import SemanticAnalyzer, SemanticAnalysisResult, SemanticDifference
from semantic_diff.utils.code_parser import CodeParser, CodeStructure
from semantic_diff.utils.language_detector import LanguageDetector
from semantic_diff.utils.config_loader import ConfigLoader


class TestSemanticDiff(unittest.TestCase):
    """语义diff工具主要功能测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_file1 = os.path.join(self.temp_dir, "test1.py")
        self.test_file2 = os.path.join(self.temp_dir, "test2.py")
        
        with open(self.test_file1, 'w') as f:
            f.write('''
def hello(name):
    """打招呼函数"""
    return f"Hello, {name}!"

def main():
    print(hello("World"))
''')
        
        with open(self.test_file2, 'w') as f:
            f.write('''
def greet(username):
    """问候函数"""
    return f"Hello, {username}!"

def main():
    print(greet("World"))
''')
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('semantic_diff.core.semantic_diff.QwenModel')
    def test_compare_files(self, mock_qwen):
        """测试文件比较功能"""
        # 模拟Qwen模型
        mock_model = MagicMock()
        mock_model.is_model_loaded.return_value = True
        mock_model.compare_code_semantics.return_value = {
            "semantic_similarity_score": 0.85,
            "functional_changes": [],
            "logical_differences": []
        }
        mock_model.extract_code_features.return_value = {
            "functions": ["hello", "main"],
            "complexity": 2
        }
        mock_qwen.return_value = mock_model
        
        # 创建SemanticDiff实例
        diff_tool = SemanticDiff()
        
        try:
            # 执行比较
            result = diff_tool.compare_files(self.test_file1, self.test_file2)
            
            # 验证结果
            self.assertIsInstance(result, SemanticAnalysisResult)
            self.assertGreaterEqual(result.similarity_score, 0.0)
            self.assertLessEqual(result.similarity_score, 1.0)
            self.assertIsInstance(result.differences, list)
            self.assertIsInstance(result.summary, str)
            
        finally:
            diff_tool.shutdown()
    
    def test_compare_code_snippets(self):
        """测试代码片段比较功能"""
        code1 = '''
def add(a, b):
    return a + b
'''
        
        code2 = '''
def sum_numbers(x, y):
    result = x + y
    return result
'''
        
        # 这里需要模拟，因为没有实际的模型
        with patch('semantic_diff.core.semantic_diff.QwenModel') as mock_qwen:
            mock_model = MagicMock()
            mock_model.is_model_loaded.return_value = True
            mock_model.compare_code_semantics.return_value = {
                "semantic_similarity_score": 0.90
            }
            mock_qwen.return_value = mock_model
            
            diff_tool = SemanticDiff()
            
            try:
                result = diff_tool.compare_code(code1, code2, "python")
                
                self.assertIsInstance(result, SemanticAnalysisResult)
                self.assertGreater(result.similarity_score, 0.0)
                
            finally:
                diff_tool.shutdown()


class TestCodeParser(unittest.TestCase):
    """代码解析器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.parser = CodeParser()
    
    def test_detect_language(self):
        """测试语言检测"""
        # 测试Python文件
        self.assertEqual(self.parser.detect_language("test.py"), "python")
        self.assertEqual(self.parser.detect_language("test.js"), "javascript")
        self.assertEqual(self.parser.detect_language("test.java"), "java")
        
        # 测试不存在的扩展名
        self.assertIsNone(self.parser.detect_language("test.unknown"))
    
    def test_normalize_code(self):
        """测试代码标准化"""
        code = '''
# 这是注释
def hello():
    # 另一个注释
    return "Hello"
        '''
        
        normalized = self.parser.normalize_code(code, "python")
        
        # 标准化后应该去除注释和多余空行
        self.assertNotIn("# 这是注释", normalized)
        self.assertIn("def hello():", normalized)
    
    def test_get_code_hash(self):
        """测试代码哈希计算"""
        code1 = "def hello(): return 'Hello'"
        code2 = "def hello(): return 'Hello'"
        code3 = "def greet(): return 'Hi'"
        
        hash1 = self.parser.get_code_hash(code1)
        hash2 = self.parser.get_code_hash(code2)
        hash3 = self.parser.get_code_hash(code3)
        
        # 相同代码应该有相同哈希
        self.assertEqual(hash1, hash2)
        
        # 不同代码应该有不同哈希
        self.assertNotEqual(hash1, hash3)


class TestLanguageDetector(unittest.TestCase):
    """语言检测器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.detector = LanguageDetector()
    
    def test_extension_detection(self):
        """测试基于扩展名的检测"""
        test_cases = [
            ("test.py", "python"),
            ("script.js", "javascript"),
            ("App.java", "java"),
            ("main.cpp", "cpp"),
            ("program.c", "c"),
            ("lib.rs", "rust"),
            ("server.go", "go"),
        ]
        
        for filename, expected_lang in test_cases:
            with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as f:
                f.write(b"# test content")
                temp_path = f.name
            
            try:
                detected = self.detector.detect_language(temp_path)
                self.assertEqual(detected, expected_lang, f"Failed for {filename}")
            finally:
                os.unlink(temp_path)
    
    def test_content_detection(self):
        """测试基于内容的检测"""
        python_code = """
def hello():
    import os
    print("Hello, World!")
"""
        
        detected = self.detector.detect_language_from_content(python_code)
        self.assertEqual(detected, "python")
        
        javascript_code = """
function hello() {
    console.log("Hello, World!");
}
"""
        
        detected = self.detector.detect_language_from_content(javascript_code)
        self.assertEqual(detected, "javascript")
    
    def test_shebang_detection(self):
        """测试基于shebang的检测"""
        test_cases = [
            ("#!/usr/bin/env python", "python"),
            ("#!/usr/bin/env python3", "python"),
            ("#!/usr/bin/env node", "javascript"),
            ("#!/bin/bash", "shell"),
            ("#!/usr/bin/env ruby", "ruby"),
        ]
        
        for shebang, expected_lang in test_cases:
            detected = self.detector.detect_language_from_shebang(shebang)
            self.assertEqual(detected, expected_lang, f"Failed for {shebang}")
    
    def test_get_supported_languages(self):
        """测试获取支持的语言列表"""
        languages = self.detector.get_supported_languages()
        
        self.assertIsInstance(languages, list)
        self.assertIn("python", languages)
        self.assertIn("javascript", languages)
        self.assertIn("java", languages)
        
        # 确保列表已排序
        self.assertEqual(languages, sorted(languages))


class TestConfigLoader(unittest.TestCase):
    """配置加载器测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        loader = ConfigLoader()
        config = loader.load_config()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.model)
        self.assertIsNotNone(config.semantic_analysis)
        self.assertIsNotNone(config.output)
        self.assertIsNotNone(config.performance)
        self.assertIsNotNone(config.logging)
    
    def test_config_validation(self):
        """测试配置验证"""
        loader = ConfigLoader()
        config = loader.load_config()
        
        errors = loader.validate_config()
        
        # 默认配置应该是有效的
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
    
    def test_custom_config(self):
        """测试自定义配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('''
model:
  name: "custom-model"
  temperature: 0.5

output:
  format: "json"
  show_line_numbers: false
''')
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            config = loader.load_config()
            
            self.assertEqual(config.model.name, "custom-model")
            self.assertEqual(config.model.temperature, 0.5)
            self.assertEqual(config.output.format, "json")
            self.assertEqual(config.output.show_line_numbers, False)
            
        finally:
            os.unlink(config_path)


class TestMockFunctionality(unittest.TestCase):
    """测试模拟功能（无需实际模型）"""
    
    def test_semantic_difference_creation(self):
        """测试语义差异对象创建"""
        diff = SemanticDifference(
            type="functional",
            severity="medium",
            category="function",
            old_content="def hello():",
            new_content="def greet():",
            old_location=(1, 2),
            new_location=(1, 2),
            description="函数名从hello改为greet",
            semantic_impact="功能保持不变",
            confidence=0.9
        )
        
        self.assertEqual(diff.type, "functional")
        self.assertEqual(diff.severity, "medium")
        self.assertEqual(diff.confidence, 0.9)
    
    def test_analysis_result_creation(self):
        """测试分析结果对象创建"""
        differences = [
            SemanticDifference(
                type="structural",
                severity="low",
                category="variable",
                old_content="name",
                new_content="username",
                old_location=(1, 1),
                new_location=(1, 1),
                description="变量重命名",
                semantic_impact="无功能影响",
                confidence=0.95
            )
        ]
        
        result = SemanticAnalysisResult(
            similarity_score=0.85,
            differences=differences,
            summary="代码基本相似，只有少量重命名",
            model_analysis={},
            structural_analysis={},
            recommendations=["这是正常的重构"],
            execution_time=1.5
        )
        
        self.assertEqual(result.similarity_score, 0.85)
        self.assertEqual(len(result.differences), 1)
        self.assertIn("相似", result.summary)
        self.assertEqual(result.execution_time, 1.5)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestSemanticDiff,
        TestCodeParser,
        TestLanguageDetector,
        TestConfigLoader,
        TestMockFunctionality,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("运行Semantic Diff Tool测试...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✓ 所有测试通过!")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1) 