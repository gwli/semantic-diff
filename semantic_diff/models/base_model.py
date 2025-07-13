#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base model interface for semantic analysis.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class BaseModel(ABC):
    """
    基础模型接口，定义了语义分析模型需要实现的方法
    """
    
    def __init__(self, model_name: str, device: str = "auto"):
        """
        初始化模型
        
        Args:
            model_name: 模型名称或路径
            device: 运行设备 (auto, cpu, cuda)
        """
        self.model_name = model_name
        self.device = device
        self.is_loaded = False
        
    @abstractmethod
    def load_model(self) -> None:
        """
        加载模型
        """
        pass
    
    @abstractmethod
    def unload_model(self) -> None:
        """
        卸载模型
        """
        pass
    
    @abstractmethod
    def analyze_code_semantics(self, code: str, language: str) -> Dict[str, Any]:
        """
        分析代码语义
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            语义分析结果
        """
        pass
    
    @abstractmethod
    def compare_code_semantics(self, code1: str, code2: str, language: str) -> Dict[str, Any]:
        """
        比较两段代码的语义
        
        Args:
            code1: 第一段代码
            code2: 第二段代码
            language: 编程语言
            
        Returns:
            语义比较结果
        """
        pass
    
    @abstractmethod
    def extract_code_features(self, code: str, language: str) -> Dict[str, Any]:
        """
        提取代码特征
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            代码特征
        """
        pass
    
    @abstractmethod
    def explain_differences(self, diff_result: Dict[str, Any]) -> str:
        """
        解释差异
        
        Args:
            diff_result: 差异结果
            
        Returns:
            差异解释
        """
        pass
    
    def is_model_loaded(self) -> bool:
        """
        检查模型是否已加载
        
        Returns:
            是否已加载
        """
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息
        """
        return {
            "name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded
        } 