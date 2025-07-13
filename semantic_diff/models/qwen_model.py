#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qwen3-4B model integration for semantic analysis.
"""

import torch
import json
import logging
from typing import Dict, Any, Optional, List
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from .base_model import BaseModel


class QwenModel(BaseModel):
    """
    Qwen3-4B模型实现，用于代码语义分析
    """
    
    def __init__(self, model_name: str = "Qwen/Qwen-VL-Chat", device: str = "auto", 
                 max_length: int = 2048, temperature: float = 0.1, top_p: float = 0.9):
        """
        初始化Qwen模型
        
        Args:
            model_name: 模型名称或路径
            device: 运行设备
            max_length: 最大生成长度
            temperature: 温度参数
            top_p: Top-p参数
        """
        super().__init__(model_name, device)
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        
        self.tokenizer = None
        self.model = None
        self.generation_config = None
        
        self.logger = logging.getLogger(__name__)
        
        # 语义分析的提示词模板
        self.prompts = {
            "analyze_semantics": """
请分析以下{language}代码的语义结构和功能:

```{language}
{code}
```

请从以下维度分析代码:
1. 主要功能和目的
2. 数据结构和变量
3. 控制流程
4. 函数和方法
5. 依赖关系
6. 潜在问题

请以JSON格式返回分析结果。
""",
            
            "compare_semantics": """
请比较以下两段{language}代码的语义差异:

代码1:
```{language}
{code1}
```

代码2:
```{language}
{code2}
```

请从以下维度比较:
1. 功能变化
2. 逻辑差异
3. 性能影响
4. 代码质量变化
5. 安全性影响
6. 重构类型判断

请以JSON格式返回比较结果，包含semantic_similarity_score(0-1)。
""",
            
            "extract_features": """
请提取以下{language}代码的关键特征:

```{language}
{code}
```

请提取以下特征:
1. 函数签名
2. 变量名和类型
3. 控制结构
4. 数据结构
5. 导入和依赖
6. 注释和文档

请以JSON格式返回特征信息。
""",
            
            "explain_differences": """
请解释以下代码差异的含义和影响:

差异信息:
{diff_info}

请提供:
1. 差异类型分类
2. 影响程度评估
3. 改进建议
4. 潜在风险
5. 语义等价性判断

请用中文详细解释。
"""
        }
    
    def load_model(self) -> None:
        """
        加载Qwen模型
        """
        try:
            self.logger.info(f"Loading Qwen model: {self.model_name}")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device if self.device != "auto" else None,
                trust_remote_code=True
            )
            
            # 设置生成配置
            self.generation_config = GenerationConfig(
                max_new_tokens=self.max_length,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.is_loaded = True
            self.logger.info("Qwen model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load Qwen model: {str(e)}")
            raise
    
    def unload_model(self) -> None:
        """
        卸载模型
        """
        try:
            if self.model is not None:
                del self.model
                self.model = None
                
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
                
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            self.is_loaded = False
            self.logger.info("Qwen model unloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to unload Qwen model: {str(e)}")
    
    def _generate_response(self, prompt: str) -> str:
        """
        生成模型响应
        
        Args:
            prompt: 输入提示
            
        Returns:
            生成的响应
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
        
        try:
            # 编码输入
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # 生成响应
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    generation_config=self.generation_config,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码输出
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {str(e)}")
            raise
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从响应中提取JSON数据
        
        Args:
            response: 模型响应
            
        Returns:
            解析的JSON数据
        """
        try:
            # 尝试直接解析JSON
            if response.startswith('{') and response.endswith('}'):
                return json.loads(response)
            
            # 寻找JSON块
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                return json.loads(json_str)
            
            # 如果没有找到JSON，返回结构化的默认结果
            return {
                "analysis": response,
                "extracted": True,
                "confidence": 0.5
            }
            
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON from response")
            return {
                "analysis": response,
                "extracted": False,
                "confidence": 0.3
            }
    
    def analyze_code_semantics(self, code: str, language: str) -> Dict[str, Any]:
        """
        分析代码语义
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            语义分析结果
        """
        prompt = self.prompts["analyze_semantics"].format(
            language=language,
            code=code
        )
        
        response = self._generate_response(prompt)
        result = self._extract_json_from_response(response)
        
        # 添加元数据
        result["model_info"] = self.get_model_info()
        result["language"] = language
        result["code_length"] = len(code)
        
        return result
    
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
        prompt = self.prompts["compare_semantics"].format(
            language=language,
            code1=code1,
            code2=code2
        )
        
        response = self._generate_response(prompt)
        result = self._extract_json_from_response(response)
        
        # 确保有相似度分数
        if "semantic_similarity_score" not in result:
            result["semantic_similarity_score"] = 0.5
        
        # 添加元数据
        result["model_info"] = self.get_model_info()
        result["language"] = language
        result["code1_length"] = len(code1)
        result["code2_length"] = len(code2)
        
        return result
    
    def extract_code_features(self, code: str, language: str) -> Dict[str, Any]:
        """
        提取代码特征
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            代码特征
        """
        prompt = self.prompts["extract_features"].format(
            language=language,
            code=code
        )
        
        response = self._generate_response(prompt)
        result = self._extract_json_from_response(response)
        
        # 添加元数据
        result["model_info"] = self.get_model_info()
        result["language"] = language
        result["code_length"] = len(code)
        
        return result
    
    def explain_differences(self, diff_result: Dict[str, Any]) -> str:
        """
        解释差异
        
        Args:
            diff_result: 差异结果
            
        Returns:
            差异解释
        """
        prompt = self.prompts["explain_differences"].format(
            diff_info=json.dumps(diff_result, ensure_ascii=False, indent=2)
        )
        
        response = self._generate_response(prompt)
        return response
    
    def batch_analyze(self, code_pairs: List[tuple], language: str) -> List[Dict[str, Any]]:
        """
        批量分析代码对
        
        Args:
            code_pairs: 代码对列表
            language: 编程语言
            
        Returns:
            分析结果列表
        """
        results = []
        
        for code1, code2 in code_pairs:
            try:
                result = self.compare_code_semantics(code1, code2, language)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to analyze code pair: {str(e)}")
                results.append({
                    "error": str(e),
                    "semantic_similarity_score": 0.0
                })
        
        return results 