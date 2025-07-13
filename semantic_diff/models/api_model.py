#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API-based model implementation for semantic analysis.
Supports ollama and vllm APIs.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
import requests
from .base_model import BaseModel


class ApiModel(BaseModel):
    """
    基于API的模型实现，支持ollama和vllm
    """
    
    def __init__(self, model_name: str, api_type: str = "ollama",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 30,
                 max_length: int = 8192,
                 temperature: float = 0.1,
                 top_p: float = 0.9):
        """
        初始化API模型
        
        Args:
            model_name: 模型名称
            api_type: API类型 (ollama, vllm)
            base_url: API基础URL
            timeout: 请求超时时间
            max_length: 最大生成长度
            temperature: 温度参数
            top_p: Top-p参数
        """
        super().__init__(model_name, "api")
        self.api_type = api_type
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        
        self.logger = logging.getLogger(__name__)
        self._json_parse_warning_count = 0  # 记录JSON解析警告次数
        self._max_json_warnings = 3  # 最大警告次数
        
        # 配置API端点
        self._setup_api_endpoints()
        
        # 语义分析提示词模板
        self.prompts = {
            "analyze_semantics": """You are a JSON-only code analysis tool. Your response must be valid JSON with no additional text.

RULES:
- Output ONLY valid JSON
- No explanations, comments, or text before/after JSON
- Do not start with "I need to" or any explanatory text
- Your entire response must be parseable as JSON

Analyze this {language} code:
```{language}
{code}
```

Output format (respond with JSON only):
{{
    "main_purpose": "代码的主要功能和目的",
    "data_structures": ["数据结构列表"],
    "variables": ["变量列表"],
    "control_flow": ["控制流程描述"],
    "functions": ["函数列表"],
    "dependencies": ["依赖关系"],
    "potential_issues": ["潜在问题"]
}}""",
            
            "compare_semantics": """You are a JSON-only code comparison tool. Your response must be valid JSON with no additional text.

RULES:
- Output ONLY valid JSON
- No explanations, comments, or text before/after JSON
- Do not start with "I need to" or any explanatory text
- Your entire response must be parseable as JSON

Compare these {language} code snippets:

Code 1:
```{language}
{code1}
```

Code 2:
```{language}
{code2}
```

Output format (respond with JSON only):
{{
    "semantic_similarity_score": 0.8,
    "functional_changes": [
        {{
            "description": "功能变化描述",
            "severity": "high|medium|low",
            "impact": "影响描述",
            "confidence": 0.9
        }}
    ],
    "logical_differences": [
        {{
            "description": "逻辑差异描述", 
            "severity": "high|medium|low",
            "impact": "逻辑变更",
            "confidence": 0.8
        }}
    ],
    "performance_impact": "性能影响评估",
    "code_quality": "代码质量变化",
    "security_impact": "安全性影响"
}}""",
            
            "extract_features": """You are a JSON-only code feature extractor. Your response must be valid JSON with no additional text.

RULES:
- Output ONLY valid JSON
- No explanations, comments, or text before/after JSON
- Do not start with "I need to" or any explanatory text
- Your entire response must be parseable as JSON

Extract features from this {language} code:
```{language}
{code}
```

Output format (respond with JSON only):
{{
    "function_signatures": ["函数签名列表"],
    "variable_names_and_types": ["变量名和类型"],
    "control_structures": ["控制结构列表"],
    "data_structures": ["数据结构列表"],
    "imports_and_dependencies": ["导入和依赖"],
    "comments_and_documentation": ["注释和文档"]
}}""",
            
            "explain_differences": """请解释以下代码差异的含义和影响：

差异信息:
{diff_info}

请提供详细的中文解释，包括：
1. 差异类型分类
2. 影响程度评估
3. 改进建议
4. 潜在风险
5. 语义等价性判断

请用中文详细解释，不需要JSON格式。"""
        }
    
    def _setup_api_endpoints(self):
        """设置API端点"""
        if self.api_type == "ollama":
            self.generate_endpoint = f"{self.base_url}/api/generate"
            self.chat_endpoint = f"{self.base_url}/api/chat"
            self.model_endpoint = f"{self.base_url}/api/tags"
        elif self.api_type == "vllm":
            self.generate_endpoint = f"{self.base_url}/generate"
            self.chat_endpoint = f"{self.base_url}/v1/chat/completions"
            self.model_endpoint = f"{self.base_url}/v1/models"
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")
    
    def load_model(self) -> None:
        """
        检查模型是否可用
        """
        try:
            self.logger.debug(f"Connecting to {self.api_type} API at {self.base_url}")
            
            # 检查API是否可用
            if not self._check_api_availability():
                raise ConnectionError(f"Cannot connect to {self.api_type} API")
            
            # 检查模型是否可用
            if not self._check_model_availability():
                raise RuntimeError(f"Model {self.model_name} not available")
            
            self.is_loaded = True
            self.logger.debug(f"Successfully connected to {self.api_type} API")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.api_type} API: {str(e)}")
            raise
    
    def unload_model(self) -> None:
        """
        断开API连接
        """
        self.is_loaded = False
        self.logger.debug(f"Disconnected from {self.api_type} API")
    
    def _check_api_availability(self) -> bool:
        """检查API是否可用"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_model_availability(self) -> bool:
        """检查模型是否可用"""
        try:
            response = requests.get(self.model_endpoint, timeout=self.timeout)
            if response.status_code != 200:
                return False
            
            if self.api_type == "ollama":
                models = response.json().get("models", [])
                return any(model.get("name") == self.model_name for model in models)
            elif self.api_type == "vllm":
                models = response.json().get("data", [])
                return any(model.get("id") == self.model_name for model in models)
            
            return True
        except Exception:
            return False
    
    def _generate_response(self, prompt: str, task_type: str = "default") -> str:
        """
        生成模型响应
        
        Args:
            prompt: 输入提示
            task_type: 任务类型，用于调整长度限制
            
        Returns:
            生成的响应
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
        
        # 为不同任务类型设置不同的长度限制
        task_max_length = {
            "extract_features": self.max_length * 3,  # 特征提取需要更长的响应
            "compare_semantics": self.max_length * 2, # 语义比较需要较长的响应
            "analyze_semantics": self.max_length,     # 语义分析使用默认长度
            "explain_differences": self.max_length * 2, # 差异解释需要较长的响应
            "default": self.max_length               # 默认长度
        }.get(task_type, self.max_length)
        
        try:
            if self.api_type == "ollama":
                return self._generate_ollama_response(prompt, task_max_length)
            elif self.api_type == "vllm":
                return self._generate_vllm_response(prompt, task_max_length)
            else:
                raise ValueError(f"Unsupported API type: {self.api_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate response: {str(e)}")
            raise
    
    def _generate_ollama_response(self, prompt: str, max_length: int = None) -> str:
        """通过ollama API生成响应"""
        if max_length is None:
            max_length = self.max_length
            
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": max_length
            }
        }
        
        response = requests.post(
            self.generate_endpoint,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"API request failed: {response.status_code}")
        
        result = response.json()
        return result.get("response", "")
    
    def _generate_vllm_response(self, prompt: str, max_length: int = None) -> str:
        """通过vllm API生成响应"""
        if max_length is None:
            max_length = self.max_length
            
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": max_length
        }
        
        response = requests.post(
            self.chat_endpoint,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"API request failed: {response.status_code}")
        
        result = response.json()
        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError("No response from API")
        
        return choices[0].get("message", {}).get("content", "")
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从响应中提取JSON数据
        
        Args:
            response: 模型响应
            
        Returns:
            解析的JSON数据
        """
        if not response or not response.strip():
            return {
                "analysis": "Empty response received",
                "extracted": False,
                "confidence": 0.0,
                "error": "empty_response"
            }
        
        # 清理响应文本
        cleaned_response = response.strip()
        
        # 处理思考标签（<think>标签）
        if '<think>' in cleaned_response and '</think>' in cleaned_response:
            think_end = cleaned_response.find('</think>')
            if think_end != -1:
                cleaned_response = cleaned_response[think_end + 8:].strip()
        
        # 如果响应不是直接以JSON开始，尝试找到JSON块
        if not cleaned_response.startswith('{'):
            # 查找第一个JSON块的开始位置
            json_start = cleaned_response.find('{')
            if json_start > 0:
                cleaned_response = cleaned_response[json_start:].strip()
        
        # 方法1: 直接解析完整响应
        try:
            if cleaned_response.startswith('{') and cleaned_response.endswith('}'):
                result = json.loads(cleaned_response)
                # 验证这是一个有效的分析结果
                if isinstance(result, dict):
                    return result
        except json.JSONDecodeError:
            pass
        
        # 方法2: 查找JSON块（改进的大括号匹配）
        try:
            # 寻找最外层的JSON块
            start_idx = cleaned_response.find('{')
            if start_idx != -1:
                # 使用栈来匹配大括号
                brace_count = 0
                end_idx = start_idx
                in_string = False
                escape_next = False
                
                for i in range(start_idx, len(cleaned_response)):
                    char = cleaned_response[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                
                if brace_count == 0:  # 找到了完整的JSON块
                    json_str = cleaned_response[start_idx:end_idx + 1]
                    result = json.loads(json_str)
                    if isinstance(result, dict):
                        return result
        except json.JSONDecodeError:
            pass
        
        # 方法3: 处理markdown格式的JSON代码块
        try:
            if '```json' in cleaned_response:
                start = cleaned_response.find('```json') + 7
                end = cleaned_response.find('```', start)
                if end != -1:
                    json_str = cleaned_response[start:end].strip()
                    result = json.loads(json_str)
                    if isinstance(result, dict):
                        return result
            
            # 处理简单的代码块
            if '```' in cleaned_response:
                parts = cleaned_response.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('{') and part.endswith('}'):
                        try:
                            result = json.loads(part)
                            if isinstance(result, dict) and len(result) > 0:
                                return result
                        except json.JSONDecodeError:
                            continue
        except json.JSONDecodeError:
            pass
        
        # 方法4: 尝试修复常见的JSON格式问题
        try:
            if '{' in cleaned_response and '}' in cleaned_response:
                first_brace = cleaned_response.find('{')
                last_brace = cleaned_response.rfind('}')
                if first_brace < last_brace:
                    json_str = cleaned_response[first_brace:last_brace + 1]
                    
                    # 尝试修复常见问题
                    import re
                    # 移除可能的注释
                    json_str = re.sub(r'//.*?\n', '\n', json_str)
                    # 修复单引号
                    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
                    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
                    
                    result = json.loads(json_str)
                    if isinstance(result, dict):
                        return result
        except (json.JSONDecodeError, Exception):
            pass
        
        # 如果所有方法都失败了，尝试从响应中提取语义信息
        semantic_similarity = self._extract_similarity_from_text(cleaned_response)
        
        # 只在前几次失败时记录警告，避免日志过多
        if self._json_parse_warning_count < self._max_json_warnings:
            response_len = len(cleaned_response)
            # 检查JSON是否看起来被截断
            is_truncated = (cleaned_response.startswith('{') and 
                           not cleaned_response.endswith('}') and 
                           response_len > 100)
            
            truncated_info = " (Response appears truncated)" if is_truncated else ""
            self.logger.warning(f"Failed to parse JSON from response. "
                              f"Length: {response_len}{truncated_info}. "
                              f"Preview: {cleaned_response[:200]}...")
            
            # 如果响应看起来被截断，记录更多信息
            if is_truncated:
                self.logger.warning(f"Response ends with: ...{cleaned_response[-50:]}")
            
            self._json_parse_warning_count += 1
            if self._json_parse_warning_count == self._max_json_warnings:
                self.logger.info("Further JSON parsing warnings will be suppressed")
        
        # 返回结构化的默认结果
        return {
            "analysis": cleaned_response,
            "extracted": False,
            "confidence": 0.3,
            "semantic_similarity_score": semantic_similarity,
            "error": "json_parse_failed",
            "response_length": len(cleaned_response)
        }
    
    def _extract_similarity_from_text(self, text: str) -> float:
        """
        从文本响应中尝试提取相似度信息
        
        Args:
            text: 响应文本
            
        Returns:
            相似度分数
        """
        import re
        
        # 查找百分比形式的相似度
        percentage_patterns = [
            r'相似度[：:]\s*(\d+\.?\d*)%',
            r'similarity[：:]\s*(\d+\.?\d*)%',
            r'(\d+\.?\d*)%\s*相似',
            r'(\d+\.?\d*)%\s*similar',
        ]
        
        for pattern in percentage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0]) / 100.0
                except ValueError:
                    pass
        
        # 查找小数形式的相似度
        decimal_patterns = [
            r'相似度[：:]\s*(0\.\d+)',
            r'similarity[：:]\s*(0\.\d+)',
            r'score[：:]\s*(0\.\d+)',
        ]
        
        for pattern in decimal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    pass
        
        # 根据关键词判断相似度
        if any(word in text.lower() for word in ['identical', '完全相同', '一致']):
            return 1.0
        elif any(word in text.lower() for word in ['very similar', '非常相似', '高度相似']):
            return 0.9
        elif any(word in text.lower() for word in ['similar', '相似', '类似']):
            return 0.7
        elif any(word in text.lower() for word in ['different', '不同', '差异']):
            return 0.3
        elif any(word in text.lower() for word in ['very different', '完全不同', '截然不同']):
            return 0.1
        
        # 默认中等相似度
        return 0.5
    
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
        
        response = self._generate_response(prompt, "analyze_semantics")
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
        
        response = self._generate_response(prompt, "compare_semantics")
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
        
        response = self._generate_response(prompt, "extract_features")
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
        
        response = self._generate_response(prompt, "explain_differences")
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
        
        for i, (code1, code2) in enumerate(code_pairs):
            self.logger.debug(f"Processing pair {i+1}/{len(code_pairs)}")
            
            try:
                result = self.compare_code_semantics(code1, code2, language)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to analyze pair {i+1}: {str(e)}")
                results.append({
                    "error": str(e),
                    "pair_index": i
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息
        """
        return {
            "name": self.model_name,
            "type": self.api_type,
            "base_url": self.base_url,
            "loaded": self.is_loaded
        } 