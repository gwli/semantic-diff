#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration loader for semantic diff tool.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ApiConfig:
    """API配置"""
    base_url: str = "http://localhost:11434"
    timeout: int = 30


@dataclass
class GenerationConfig:
    """生成参数配置"""
    max_length: int = 2048
    temperature: float = 0.1
    top_p: float = 0.9


@dataclass
class ModelConfig:
    """模型配置"""
    type: str = "transformers"  # transformers, ollama, vllm
    name: str = "Qwen/Qwen-VL-Chat"
    device: str = "auto"
    api: ApiConfig = field(default_factory=ApiConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    
    # 向后兼容
    max_length: int = 2048
    temperature: float = 0.1
    top_p: float = 0.9


@dataclass
class SemanticAnalysisConfig:
    """语义分析配置"""
    depth: str = "medium"
    features: List[str] = field(default_factory=lambda: [
        "function_signatures", "variable_names", "control_flow",
        "data_structures", "comments", "imports"
    ])
    ignore_differences: List[str] = field(default_factory=lambda: [
        "whitespace", "comments_only", "variable_rename", "code_formatting"
    ])


@dataclass
class OutputConfig:
    """输出配置"""
    format: str = "rich"
    show_line_numbers: bool = True
    show_context: bool = True
    context_lines: int = 3
    highlight_syntax: bool = True
    color_scheme: str = "monokai"


@dataclass
class PerformanceConfig:
    """性能配置"""
    max_file_size: int = 1048576  # 1MB
    parallel_processing: bool = True
    max_workers: int = 4
    cache_enabled: bool = True
    cache_dir: str = ".semantic_diff_cache"


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "WARNING"
    file: str = "semantic_diff.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class Config:
    """完整配置"""
    model: ModelConfig = field(default_factory=ModelConfig)
    semantic_analysis: SemanticAnalysisConfig = field(default_factory=SemanticAnalysisConfig)
    supported_languages: List[str] = field(default_factory=lambda: [
        "python", "javascript", "java", "cpp", "c", "rust", "go", "typescript"
    ])
    output: OutputConfig = field(default_factory=OutputConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self._find_config_file()
        self.logger = logging.getLogger(__name__)
        self._config: Optional[Config] = None
    
    def _find_config_file(self) -> Optional[str]:
        """查找配置文件"""
        possible_paths = [
            "config.yaml",
            "config.yml",
            "semantic_diff.yaml",
            "semantic_diff.yml",
            os.path.expanduser("~/.semantic_diff.yaml"),
            os.path.expanduser("~/.semantic_diff.yml"),
            "/etc/semantic_diff.yaml",
            "/etc/semantic_diff.yml",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def load_config(self) -> Config:
        """
        加载配置
        
        Returns:
            配置对象
        """
        if self._config is not None:
            return self._config
        
        # 创建默认配置
        self._config = Config()
        
        # 如果找到配置文件，加载配置
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data:
                    self._merge_config(config_data)
                    self.logger.debug(f"Configuration loaded from {self.config_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to load config file {self.config_path}: {str(e)}")
                self.logger.debug("Using default configuration")
        else:
            self.logger.debug("No config file found, using default configuration")
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
        
        return self._config
    
    def _merge_config(self, config_data: Dict[str, Any]):
        """合并配置数据"""
        # 合并模型配置
        if "model" in config_data:
            model_data = config_data["model"]
            if "type" in model_data:
                self._config.model.type = model_data["type"]
            if "name" in model_data:
                self._config.model.name = model_data["name"]
            if "device" in model_data:
                self._config.model.device = model_data["device"]
            
            # API配置
            if "api" in model_data:
                api_data = model_data["api"]
                if "base_url" in api_data:
                    self._config.model.api.base_url = api_data["base_url"]
                if "timeout" in api_data:
                    self._config.model.api.timeout = api_data["timeout"]
            
            # 生成参数配置
            if "generation" in model_data:
                gen_data = model_data["generation"]
                if "max_length" in gen_data:
                    self._config.model.generation.max_length = gen_data["max_length"]
                if "temperature" in gen_data:
                    self._config.model.generation.temperature = gen_data["temperature"]
                if "top_p" in gen_data:
                    self._config.model.generation.top_p = gen_data["top_p"]
            
            # 向后兼容
            if "max_length" in model_data:
                self._config.model.max_length = model_data["max_length"]
                self._config.model.generation.max_length = model_data["max_length"]
            if "temperature" in model_data:
                self._config.model.temperature = model_data["temperature"]
                self._config.model.generation.temperature = model_data["temperature"]
            if "top_p" in model_data:
                self._config.model.top_p = model_data["top_p"]
                self._config.model.generation.top_p = model_data["top_p"]
        
        # 合并语义分析配置
        if "semantic_analysis" in config_data:
            sa_data = config_data["semantic_analysis"]
            if "depth" in sa_data:
                self._config.semantic_analysis.depth = sa_data["depth"]
            if "features" in sa_data:
                self._config.semantic_analysis.features = sa_data["features"]
            if "ignore_differences" in sa_data:
                self._config.semantic_analysis.ignore_differences = sa_data["ignore_differences"]
        
        # 合并支持的语言
        if "supported_languages" in config_data:
            self._config.supported_languages = config_data["supported_languages"]
        
        # 合并输出配置
        if "output" in config_data:
            output_data = config_data["output"]
            if "format" in output_data:
                self._config.output.format = output_data["format"]
            if "show_line_numbers" in output_data:
                self._config.output.show_line_numbers = output_data["show_line_numbers"]
            if "show_context" in output_data:
                self._config.output.show_context = output_data["show_context"]
            if "context_lines" in output_data:
                self._config.output.context_lines = output_data["context_lines"]
            if "highlight_syntax" in output_data:
                self._config.output.highlight_syntax = output_data["highlight_syntax"]
            if "color_scheme" in output_data:
                self._config.output.color_scheme = output_data["color_scheme"]
        
        # 合并性能配置
        if "performance" in config_data:
            perf_data = config_data["performance"]
            if "max_file_size" in perf_data:
                self._config.performance.max_file_size = perf_data["max_file_size"]
            if "parallel_processing" in perf_data:
                self._config.performance.parallel_processing = perf_data["parallel_processing"]
            if "max_workers" in perf_data:
                self._config.performance.max_workers = perf_data["max_workers"]
            if "cache_enabled" in perf_data:
                self._config.performance.cache_enabled = perf_data["cache_enabled"]
            if "cache_dir" in perf_data:
                self._config.performance.cache_dir = perf_data["cache_dir"]
        
        # 合并日志配置
        if "logging" in config_data:
            log_data = config_data["logging"]
            if "level" in log_data:
                self._config.logging.level = log_data["level"]
            if "file" in log_data:
                self._config.logging.file = log_data["file"]
            if "format" in log_data:
                self._config.logging.format = log_data["format"]
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 模型配置
        if os.getenv("SEMANTIC_DIFF_MODEL_NAME"):
            self._config.model.name = os.getenv("SEMANTIC_DIFF_MODEL_NAME")
        
        if os.getenv("SEMANTIC_DIFF_DEVICE"):
            self._config.model.device = os.getenv("SEMANTIC_DIFF_DEVICE")
        
        if os.getenv("SEMANTIC_DIFF_MAX_LENGTH"):
            try:
                self._config.model.max_length = int(os.getenv("SEMANTIC_DIFF_MAX_LENGTH"))
            except ValueError:
                self.logger.warning("Invalid SEMANTIC_DIFF_MAX_LENGTH value, using default")
        
        if os.getenv("SEMANTIC_DIFF_TEMPERATURE"):
            try:
                self._config.model.temperature = float(os.getenv("SEMANTIC_DIFF_TEMPERATURE"))
            except ValueError:
                self.logger.warning("Invalid SEMANTIC_DIFF_TEMPERATURE value, using default")
        
        # 输出配置
        if os.getenv("SEMANTIC_DIFF_OUTPUT_FORMAT"):
            self._config.output.format = os.getenv("SEMANTIC_DIFF_OUTPUT_FORMAT")
        
        if os.getenv("SEMANTIC_DIFF_NO_COLOR"):
            self._config.output.highlight_syntax = False
        
        # 性能配置
        if os.getenv("SEMANTIC_DIFF_CACHE_DIR"):
            self._config.performance.cache_dir = os.getenv("SEMANTIC_DIFF_CACHE_DIR")
        
        if os.getenv("SEMANTIC_DIFF_MAX_WORKERS"):
            try:
                self._config.performance.max_workers = int(os.getenv("SEMANTIC_DIFF_MAX_WORKERS"))
            except ValueError:
                self.logger.warning("Invalid SEMANTIC_DIFF_MAX_WORKERS value, using default")
        
        # 日志配置
        if os.getenv("SEMANTIC_DIFF_LOG_LEVEL"):
            self._config.logging.level = os.getenv("SEMANTIC_DIFF_LOG_LEVEL")
        
        if os.getenv("SEMANTIC_DIFF_LOG_FILE"):
            self._config.logging.file = os.getenv("SEMANTIC_DIFF_LOG_FILE")
    
    def get_config(self) -> Config:
        """
        获取配置
        
        Returns:
            配置对象
        """
        if self._config is None:
            return self.load_config()
        return self._config
    
    def save_config(self, config_path: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        if self._config is None:
            raise ValueError("No configuration to save")
        
        output_path = config_path or self.config_path or "config.yaml"
        
        try:
            config_dict = self._config_to_dict()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.debug(f"Configuration saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config to {output_path}: {str(e)}")
            raise
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "model": {
                "name": self._config.model.name,
                "device": self._config.model.device,
                "max_length": self._config.model.max_length,
                "temperature": self._config.model.temperature,
                "top_p": self._config.model.top_p,
            },
            "semantic_analysis": {
                "depth": self._config.semantic_analysis.depth,
                "features": self._config.semantic_analysis.features,
                "ignore_differences": self._config.semantic_analysis.ignore_differences,
            },
            "supported_languages": self._config.supported_languages,
            "output": {
                "format": self._config.output.format,
                "show_line_numbers": self._config.output.show_line_numbers,
                "show_context": self._config.output.show_context,
                "context_lines": self._config.output.context_lines,
                "highlight_syntax": self._config.output.highlight_syntax,
                "color_scheme": self._config.output.color_scheme,
            },
            "performance": {
                "max_file_size": self._config.performance.max_file_size,
                "parallel_processing": self._config.performance.parallel_processing,
                "max_workers": self._config.performance.max_workers,
                "cache_enabled": self._config.performance.cache_enabled,
                "cache_dir": self._config.performance.cache_dir,
            },
            "logging": {
                "level": self._config.logging.level,
                "file": self._config.logging.file,
                "format": self._config.logging.format,
            },
        }
    
    def update_config(self, **kwargs):
        """
        更新配置
        
        Args:
            **kwargs: 配置更新参数
        """
        if self._config is None:
            self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                self.logger.warning(f"Unknown config key: {key}")
    
    def validate_config(self) -> List[str]:
        """
        验证配置
        
        Returns:
            验证错误列表
        """
        errors = []
        
        if self._config is None:
            errors.append("Configuration not loaded")
            return errors
        
        # 验证模型配置
        if not self._config.model.name:
            errors.append("Model name is required")
        
        if self._config.model.device not in ["auto", "cpu", "cuda"]:
            errors.append("Device must be 'auto', 'cpu', or 'cuda'")
        
        if self._config.model.max_length <= 0:
            errors.append("Max length must be positive")
        
        if not (0 <= self._config.model.temperature <= 2):
            errors.append("Temperature must be between 0 and 2")
        
        if not (0 <= self._config.model.top_p <= 1):
            errors.append("Top_p must be between 0 and 1")
        
        # 验证语义分析配置
        if self._config.semantic_analysis.depth not in ["shallow", "medium", "deep"]:
            errors.append("Depth must be 'shallow', 'medium', or 'deep'")
        
        # 验证输出配置
        if self._config.output.format not in ["plain", "rich", "json", "html"]:
            errors.append("Output format must be 'plain', 'rich', 'json', or 'html'")
        
        if self._config.output.context_lines < 0:
            errors.append("Context lines must be non-negative")
        
        # 验证性能配置
        if self._config.performance.max_file_size <= 0:
            errors.append("Max file size must be positive")
        
        if self._config.performance.max_workers <= 0:
            errors.append("Max workers must be positive")
        
        # 验证日志配置
        if self._config.logging.level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        return errors 