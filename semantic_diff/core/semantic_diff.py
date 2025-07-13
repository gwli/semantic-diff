#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main semantic diff implementation.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

from .semantic_analyzer import SemanticAnalyzer, SemanticAnalysisResult
from ..models.qwen_model import QwenModel
from ..models.api_model import ApiModel
from ..models.base_model import BaseModel
from ..utils.config_loader import ConfigLoader, Config
from ..utils.code_parser import CodeParser
from ..utils.language_detector import LanguageDetector


class SemanticDiff:
    """
    语义差异分析器主类
    
    提供文件和代码的语义比较功能
    """
    
    def __init__(self, config_path: Optional[str] = None, model_path: Optional[str] = None, log_level: Optional[str] = None):
        """
        初始化语义差异分析器
        
        Args:
            config_path: 配置文件路径
            model_path: 模型路径（可选）
            log_level: 日志级别（可选）
        """
        # 加载配置
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # 设置日志
        self._setup_logging(log_level)
        
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing Semantic Diff Tool")
        
        # 如果指定了模型路径，覆盖配置
        if model_path:
            self.config.model.name = model_path
        
        # 初始化组件
        self.language_detector = LanguageDetector()
        self.code_parser = CodeParser()
        
        # 延迟初始化模型和分析器
        self._model = None
        self._analyzer = None
        
        # 统计信息
        self.stats = {
            "files_compared": 0,
            "code_snippets_compared": 0,
            "total_analysis_time": 0.0,
            "cache_hits": 0,
            "errors": 0
        }
        
        self.logger.debug("Semantic Diff Tool initialized successfully")
    
    def _setup_logging(self, log_level: Optional[str] = None):
        """设置日志
        
        Args:
            log_level: 日志级别，如果为None则使用配置文件中的级别
        """
        # 确定日志级别
        if log_level:
            level = getattr(logging, log_level.upper())
        else:
            level = getattr(logging, self.config.logging.level)
            
        # 清除现有的handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        # 设置日志配置
        logging.basicConfig(
            level=level,
            format=self.config.logging.format,
            handlers=[
                logging.FileHandler(self.config.logging.file),
                logging.StreamHandler()
            ]
        )
    
    @property
    def model(self) -> BaseModel:
        """延迟加载模型"""
        if self._model is None:
            self.logger.debug("Loading AI model...")
            self._model = self._create_model_from_config()
        return self._model

    def _create_model_from_config(self) -> BaseModel:
        """
        根据配置创建模型实例
        
        Returns:
            模型实例
        """
        model_type = getattr(self.config.model, 'type', 'transformers')
        
        if model_type == 'ollama':
            return ApiModel(
                model_name=self.config.model.name,
                api_type="ollama",
                base_url=self.config.model.api.base_url,
                timeout=self.config.model.api.timeout,
                max_length=self.config.model.generation.max_length,
                temperature=self.config.model.generation.temperature,
                top_p=self.config.model.generation.top_p
            )
        elif model_type == 'vllm':
            return ApiModel(
                model_name=self.config.model.name,
                api_type="vllm",
                base_url=self.config.model.api.base_url,
                timeout=self.config.model.api.timeout,
                max_length=self.config.model.generation.max_length,
                temperature=self.config.model.generation.temperature,
                top_p=self.config.model.generation.top_p
            )
        elif model_type == 'transformers':
            return QwenModel(
                model_name=self.config.model.name,
                device=self.config.model.device,
                max_length=self.config.model.generation.max_length,
                temperature=self.config.model.generation.temperature,
                top_p=self.config.model.generation.top_p
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    @property
    def analyzer(self) -> SemanticAnalyzer:
        """延迟加载分析器"""
        if self._analyzer is None:
            self.logger.debug("Initializing semantic analyzer...")
            self._analyzer = SemanticAnalyzer(self.config, self.model)
        return self._analyzer
    
    def compare_files(self, file1_path: str, file2_path: str, 
                     language: Optional[str] = None) -> SemanticAnalysisResult:
        """
        比较两个文件的语义差异
        
        Args:
            file1_path: 第一个文件路径
            file2_path: 第二个文件路径
            language: 编程语言（可选，自动检测）
            
        Returns:
            语义分析结果
        """
        start_time = time.time()
        
        try:
            # 验证文件存在
            if not os.path.exists(file1_path):
                raise FileNotFoundError(f"File not found: {file1_path}")
            if not os.path.exists(file2_path):
                raise FileNotFoundError(f"File not found: {file2_path}")
            
            # 检查文件大小
            file1_size = os.path.getsize(file1_path)
            file2_size = os.path.getsize(file2_path)
            max_size = self.config.performance.max_file_size
            
            if file1_size > max_size or file2_size > max_size:
                raise ValueError(f"File too large. Max size: {max_size} bytes")
            
            # 读取文件内容
            with open(file1_path, 'r', encoding='utf-8') as f:
                code1 = f.read()
            
            with open(file2_path, 'r', encoding='utf-8') as f:
                code2 = f.read()
            
            # 检测语言
            if language is None:
                language = self.language_detector.detect_language(file1_path)
                if language is None:
                    language = self.language_detector.detect_language(file2_path)
                if language is None:
                    language = "text"  # 默认为文本
            
            # 验证语言支持
            if language not in self.config.supported_languages:
                self.logger.warning(f"Language {language} not fully supported, using basic analysis")
            
            # 执行分析
            result = self.analyzer.analyze(code1, code2, language, file1_path, file2_path)
            
            # 更新统计
            self.stats["files_compared"] += 1
            self.stats["total_analysis_time"] += time.time() - start_time
            if result.cache_hit:
                self.stats["cache_hits"] += 1
            
            self.logger.debug(f"File comparison completed: {file1_path} vs {file2_path}")
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"File comparison failed: {str(e)}")
            raise
    
    def compare_code(self, code1: str, code2: str, language: str, 
                    name1: str = "code1", name2: str = "code2") -> SemanticAnalysisResult:
        """
        比较两段代码的语义差异
        
        Args:
            code1: 第一段代码
            code2: 第二段代码
            language: 编程语言
            name1: 第一段代码的名称
            name2: 第二段代码的名称
            
        Returns:
            语义分析结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            if not code1 or not code2:
                raise ValueError("Code snippets cannot be empty")
            
            if language not in self.config.supported_languages:
                self.logger.warning(f"Language {language} not fully supported, using basic analysis")
            
            # 执行分析
            result = self.analyzer.analyze(code1, code2, language, name1, name2)
            
            # 更新统计
            self.stats["code_snippets_compared"] += 1
            self.stats["total_analysis_time"] += time.time() - start_time
            if result.cache_hit:
                self.stats["cache_hits"] += 1
            
            self.logger.debug(f"Code comparison completed: {name1} vs {name2}")
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Code comparison failed: {str(e)}")
            raise
    
    def compare_directories(self, dir1_path: str, dir2_path: str, 
                          recursive: bool = True, 
                          file_extensions: Optional[List[str]] = None) -> Dict[str, SemanticAnalysisResult]:
        """
        比较两个目录中的文件
        
        Args:
            dir1_path: 第一个目录路径
            dir2_path: 第二个目录路径
            recursive: 是否递归比较子目录
            file_extensions: 要比较的文件扩展名列表
            
        Returns:
            文件比较结果字典
        """
        results = {}
        
        try:
            # 验证目录存在
            if not os.path.isdir(dir1_path):
                raise NotADirectoryError(f"Directory not found: {dir1_path}")
            if not os.path.isdir(dir2_path):
                raise NotADirectoryError(f"Directory not found: {dir2_path}")
            
            # 获取文件列表
            files1 = self._get_files_in_directory(dir1_path, recursive, file_extensions)
            files2 = self._get_files_in_directory(dir2_path, recursive, file_extensions)
            
            # 找到共同的文件
            common_files = set(files1.keys()) & set(files2.keys())
            
            self.logger.debug(f"Found {len(common_files)} common files to compare")
            
            # 比较每个文件
            for relative_path in common_files:
                file1_full = files1[relative_path]
                file2_full = files2[relative_path]
                
                try:
                    result = self.compare_files(file1_full, file2_full)
                    results[relative_path] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to compare {relative_path}: {str(e)}")
                    self.stats["errors"] += 1
            
            # 报告只在一个目录中存在的文件
            only_in_dir1 = set(files1.keys()) - set(files2.keys())
            only_in_dir2 = set(files2.keys()) - set(files1.keys())
            
            if only_in_dir1:
                self.logger.debug(f"Files only in {dir1_path}: {list(only_in_dir1)}")
            if only_in_dir2:
                self.logger.debug(f"Files only in {dir2_path}: {list(only_in_dir2)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Directory comparison failed: {str(e)}")
            raise
    
    def _get_files_in_directory(self, directory: str, recursive: bool, 
                              file_extensions: Optional[List[str]]) -> Dict[str, str]:
        """获取目录中的文件列表"""
        files = {}
        directory_path = Path(directory)
        
        # 设置文件扩展名过滤
        if file_extensions is None:
            # 使用配置中支持的语言对应的扩展名
            file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go']
        
        # 遍历目录
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                # 检查文件扩展名
                if file_extensions and file_path.suffix not in file_extensions:
                    continue
                
                # 获取相对路径
                relative_path = file_path.relative_to(directory_path)
                files[str(relative_path)] = str(file_path)
        
        return files
    
    def analyze_single_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            language: 编程语言（可选）
            
        Returns:
            分析结果
        """
        try:
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 检测语言
            if language is None:
                language = self.language_detector.detect_language(file_path)
                if language is None:
                    language = "text"
            
            # 分析代码结构
            structure = self.code_parser.parse_code(code, language)
            
            # 分析语义
            features = self.model.extract_code_features(code, language)
            
            return {
                "file_path": file_path,
                "language": language,
                "structure": structure,
                "features": features,
                "code_hash": self.code_parser.get_code_hash(code),
                "lines_of_code": len(code.split('\n'))
            }
            
        except Exception as e:
            self.logger.error(f"Single file analysis failed: {str(e)}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的编程语言列表"""
        return self.config.supported_languages.copy()
    
    def get_configuration(self) -> Config:
        """获取当前配置"""
        return self.config
    
    def update_configuration(self, **kwargs):
        """更新配置"""
        self.config_loader.update_config(**kwargs)
        self.config = self.config_loader.get_config()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 添加分析器统计
        if self._analyzer:
            analyzer_stats = self._analyzer.get_stats()
            stats.update(analyzer_stats)
        
        # 计算平均值
        if stats["files_compared"] > 0:
            stats["avg_file_analysis_time"] = (
                stats["total_analysis_time"] / stats["files_compared"]
            )
        
        return stats
    
    def clear_cache(self):
        """清除缓存"""
        if self._analyzer:
            self._analyzer.clear_cache()
        self.logger.debug("Cache cleared")
    
    def warm_up(self):
        """预热系统（加载模型等）"""
        self.logger.debug("Warming up system...")
        
        # 加载模型
        _ = self.model
        
        # 加载分析器
        _ = self.analyzer
        
        # 执行一次小的分析来预热
        try:
            sample_code = "def hello():\n    return 'world'"
            self.compare_code(sample_code, sample_code, "python", "warmup1", "warmup2")
        except Exception as e:
            self.logger.warning(f"Warmup failed: {str(e)}")
        
        self.logger.debug("System warmup completed")
    
    def shutdown(self):
        """关闭系统，清理资源"""
        self.logger.debug("Shutting down Semantic Diff Tool...")
        
        try:
            # 卸载模型
            if self._model and self._model.is_model_loaded():
                self._model.unload_model()
            
            # 清除缓存
            self.clear_cache()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
        
        self.logger.debug("Semantic Diff Tool shutdown completed")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()
    
    def __del__(self):
        """析构函数"""
        try:
            self.shutdown()
        except:
            pass 