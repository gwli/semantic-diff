#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Semantic analyzer that combines code parsing with AI model analysis.
"""

import logging
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from ..models.base_model import BaseModel
from ..models.qwen_model import QwenModel
from ..models.api_model import ApiModel
from ..utils.code_parser import CodeParser, CodeStructure
from ..utils.config_loader import Config


@dataclass
class SemanticDifference:
    """语义差异"""
    type: str  # structural, functional, style
    severity: str  # low, medium, high
    category: str  # function, class, variable, import
    old_content: str
    new_content: str
    old_location: Tuple[int, int]  # (start_line, end_line)
    new_location: Tuple[int, int]  # (start_line, end_line)
    description: str
    semantic_impact: str
    confidence: float


@dataclass
class SemanticAnalysisResult:
    """语义分析结果"""
    similarity_score: float
    differences: List[SemanticDifference]
    summary: str
    model_analysis: Dict[str, Any]
    structural_analysis: Dict[str, Any]
    recommendations: List[str]
    execution_time: float
    cache_hit: bool = False


class SemanticAnalyzer:
    """
    语义分析器
    
    结合代码结构分析和AI模型语义理解，提供全面的代码比较分析
    """
    
    def __init__(self, config: Config, model: Optional[BaseModel] = None):
        """
        初始化语义分析器
        
        Args:
            config: 配置对象
            model: AI模型实例
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.code_parser = CodeParser()
        self.model = model or self._create_model_from_config(config)
        
        # 缓存
        self.cache = {}
        self.cache_enabled = config.performance.cache_enabled
        
        # 分析统计
        self.stats = {
            "total_analyses": 0,
            "cache_hits": 0,
            "structural_analyses": 0,
            "semantic_analyses": 0,
            "total_time": 0.0
        }
    
    def _create_model_from_config(self, config: Config) -> BaseModel:
        """
        根据配置创建模型实例
        
        Args:
            config: 配置对象
            
        Returns:
            模型实例
        """
        model_type = getattr(config.model, 'type', 'transformers')
        
        if model_type == 'ollama':
            return ApiModel(
                model_name=config.model.name,
                api_type="ollama",
                base_url=config.model.api.base_url,
                timeout=config.model.api.timeout,
                max_length=config.model.generation.max_length,
                temperature=config.model.generation.temperature,
                top_p=config.model.generation.top_p
            )
        elif model_type == 'vllm':
            return ApiModel(
                model_name=config.model.name,
                api_type="vllm",
                base_url=config.model.api.base_url,
                timeout=config.model.api.timeout,
                max_length=config.model.generation.max_length,
                temperature=config.model.generation.temperature,
                top_p=config.model.generation.top_p
            )
        elif model_type == 'transformers':
            return QwenModel(
                model_name=config.model.name,
                device=config.model.device,
                max_length=getattr(config.model, 'max_length', 
                                 config.model.generation.max_length),
                temperature=getattr(config.model, 'temperature', 
                                  config.model.generation.temperature),
                top_p=getattr(config.model, 'top_p', 
                            config.model.generation.top_p)
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def analyze(self, code1: str, code2: str, language: str, 
                file1_path: str = "file1", file2_path: str = "file2") -> SemanticAnalysisResult:
        """
        分析两段代码的语义差异
        
        Args:
            code1: 第一段代码
            code2: 第二段代码
            language: 编程语言
            file1_path: 第一个文件路径
            file2_path: 第二个文件路径
            
        Returns:
            语义分析结果
        """
        import time
        start_time = time.time()
        
        try:
            self.stats["total_analyses"] += 1
            
            # 检查缓存
            cache_key = self._generate_cache_key(code1, code2, language)
            if self.cache_enabled and cache_key in self.cache:
                self.stats["cache_hits"] += 1
                result = self.cache[cache_key]
                result.cache_hit = True
                return result
            
            # 确保模型已加载
            try:
                if not self.model.is_model_loaded():
                    self.logger.debug("Loading AI model...")
                    self.model.load_model()
            except Exception as e:
                self.logger.warning(f"Failed to load AI model: {str(e)}")
                # 继续使用模拟模式
                self.model = None
            
            # 1. 结构分析
            self.logger.debug("Performing structural analysis...")
            structural_result = self._analyze_structure(code1, code2, language)
            self.stats["structural_analyses"] += 1
            
            # 2. 语义分析
            self.logger.debug("Performing semantic analysis...")
            semantic_result = self._analyze_semantics(code1, code2, language)
            self.stats["semantic_analyses"] += 1
            
            # 3. 综合分析
            self.logger.debug("Combining analyses...")
            combined_result = self._combine_analyses(
                structural_result, semantic_result, code1, code2, language
            )
            
            # 4. 生成差异
            differences = self._generate_differences(
                structural_result, semantic_result, code1, code2, language
            )
            
            # 5. 生成建议
            recommendations = self._generate_recommendations(
                differences, structural_result, semantic_result
            )
            
            # 6. 计算相似度分数
            similarity_score = self._calculate_similarity_score(
                structural_result, semantic_result, differences
            )
            
            # 7. 生成摘要
            summary = self._generate_summary(
                similarities=similarity_score,
                differences=differences,
                structural_result=structural_result,
                semantic_result=semantic_result
            )
            
            # 构建结果
            execution_time = time.time() - start_time
            result = SemanticAnalysisResult(
                similarity_score=similarity_score,
                differences=differences,
                summary=summary,
                model_analysis=semantic_result,
                structural_analysis=structural_result,
                recommendations=recommendations,
                execution_time=execution_time,
                cache_hit=False
            )
            
            # 缓存结果
            if self.cache_enabled:
                self.cache[cache_key] = result
            
            self.stats["total_time"] += execution_time
            
            self.logger.debug(f"Analysis completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def _analyze_structure(self, code1: str, code2: str, language: str) -> Dict[str, Any]:
        """结构分析"""
        # 解析代码结构
        struct1 = self.code_parser.parse_code(code1, language)
        struct2 = self.code_parser.parse_code(code2, language)
        
        if not struct1 or not struct2:
            return {
                "error": "Failed to parse code structure",
                "struct1": None,
                "struct2": None,
                "comparison": None
            }
        
        # 比较结构
        comparison = self.code_parser.compare_structures(struct1, struct2)
        
        return {
            "struct1": struct1,
            "struct2": struct2,
            "comparison": comparison,
            "error": None
        }
    
    def _analyze_semantics(self, code1: str, code2: str, language: str) -> Dict[str, Any]:
        """语义分析"""
        try:
            # 检查模型是否可用
            if self.model is None:
                self.logger.warning("AI model not available, skipping semantic analysis")
                return {
                    "comparison": None,
                    "features1": None,
                    "features2": None,
                    "error": "AI model not available"
                }
            
            # 使用AI模型进行语义比较
            result = self.model.compare_code_semantics(code1, code2, language)
            
            # 提取特征
            features1 = self.model.extract_code_features(code1, language)
            features2 = self.model.extract_code_features(code2, language)
            
            return {
                "comparison": result,
                "features1": features1,
                "features2": features2,
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {str(e)}")
            return {
                "comparison": None,
                "features1": None,
                "features2": None,
                "error": str(e)
            }
    
    def _combine_analyses(self, structural: Dict[str, Any], semantic: Dict[str, Any], 
                         code1: str, code2: str, language: str) -> Dict[str, Any]:
        """综合分析结果"""
        combined = {
            "structural_valid": structural["error"] is None,
            "semantic_valid": semantic["error"] is None,
            "analysis_quality": "high"
        }
        
        # 如果结构分析失败，降级为纯语义分析
        if not combined["structural_valid"]:
            combined["analysis_quality"] = "medium"
            self.logger.warning("Structural analysis failed, using semantic analysis only")
        
        # 如果语义分析失败，降级为纯结构分析
        if not combined["semantic_valid"]:
            combined["analysis_quality"] = "low" if not combined["structural_valid"] else "medium"
            self.logger.warning("Semantic analysis failed, using structural analysis only")
        
        return combined
    
    def _generate_differences(self, structural: Dict[str, Any], semantic: Dict[str, Any], 
                            code1: str, code2: str, language: str) -> List[SemanticDifference]:
        """生成差异列表"""
        differences = []
        
        # 从结构分析生成差异
        if structural["error"] is None:
            differences.extend(self._extract_structural_differences(structural, code1, code2))
        
        # 从语义分析生成差异
        if semantic["error"] is None:
            differences.extend(self._extract_semantic_differences(semantic, code1, code2))
        
        # 去重和排序
        differences = self._deduplicate_differences(differences)
        differences.sort(key=lambda d: (d.severity, d.confidence), reverse=True)
        
        return differences
    
    def _extract_structural_differences(self, structural: Dict[str, Any], 
                                      code1: str, code2: str) -> List[SemanticDifference]:
        """从结构分析中提取差异"""
        differences = []
        comparison = structural["comparison"]
        
        if not comparison:
            return differences
        
        # 函数差异
        for func_name in comparison["functions"]["added"]:
            differences.append(SemanticDifference(
                type="structural",
                severity="medium",
                category="function",
                old_content="",
                new_content=func_name,
                old_location=(0, 0),
                new_location=(0, 0),  # 需要实际定位
                description=f"新增函数: {func_name}",
                semantic_impact="功能扩展",
                confidence=0.9
            ))
        
        for func_name in comparison["functions"]["removed"]:
            differences.append(SemanticDifference(
                type="structural",
                severity="high",
                category="function",
                old_content=func_name,
                new_content="",
                old_location=(0, 0),
                new_location=(0, 0),
                description=f"删除函数: {func_name}",
                semantic_impact="功能缺失",
                confidence=0.9
            ))
        
        # 类差异
        for class_name in comparison["classes"]["added"]:
            differences.append(SemanticDifference(
                type="structural",
                severity="medium",
                category="class",
                old_content="",
                new_content=class_name,
                old_location=(0, 0),
                new_location=(0, 0),
                description=f"新增类: {class_name}",
                semantic_impact="架构扩展",
                confidence=0.9
            ))
        
        for class_name in comparison["classes"]["removed"]:
            differences.append(SemanticDifference(
                type="structural",
                severity="high",
                category="class",
                old_content=class_name,
                new_content="",
                old_location=(0, 0),
                new_location=(0, 0),
                description=f"删除类: {class_name}",
                semantic_impact="架构变更",
                confidence=0.9
            ))
        
        # 复杂度变化
        if comparison["complexity_change"] != 0:
            severity = "low" if abs(comparison["complexity_change"]) < 5 else "medium"
            if abs(comparison["complexity_change"]) > 10:
                severity = "high"
            
            differences.append(SemanticDifference(
                type="structural",
                severity=severity,
                category="complexity",
                old_content=str(comparison["complexity_change"]),
                new_content="",
                old_location=(0, 0),
                new_location=(0, 0),
                description=f"复杂度变化: {comparison['complexity_change']:+d}",
                semantic_impact="性能影响" if comparison["complexity_change"] > 0 else "性能改善",
                confidence=0.8
            ))
        
        return differences
    
    def _extract_semantic_differences(self, semantic: Dict[str, Any], 
                                    code1: str, code2: str) -> List[SemanticDifference]:
        """从语义分析中提取差异"""
        differences = []
        comparison = semantic["comparison"]
        
        if not comparison:
            return differences
        
        # 从AI模型分析结果中提取差异
        if isinstance(comparison, dict):
            # 功能变化
            if "functional_changes" in comparison:
                for change in comparison.get("functional_changes", []):
                    differences.append(SemanticDifference(
                        type="functional",
                        severity=change.get("severity", "medium"),
                        category="function",
                        old_content=change.get("old", ""),
                        new_content=change.get("new", ""),
                        old_location=(0, 0),
                        new_location=(0, 0),
                        description=change.get("description", "功能变化"),
                        semantic_impact=change.get("impact", "未知影响"),
                        confidence=change.get("confidence", 0.7)
                    ))
            
            # 逻辑差异
            if "logical_differences" in comparison:
                for diff in comparison.get("logical_differences", []):
                    differences.append(SemanticDifference(
                        type="functional",
                        severity=diff.get("severity", "medium"),
                        category="logic",
                        old_content=diff.get("old", ""),
                        new_content=diff.get("new", ""),
                        old_location=(0, 0),
                        new_location=(0, 0),
                        description=diff.get("description", "逻辑差异"),
                        semantic_impact=diff.get("impact", "逻辑变更"),
                        confidence=diff.get("confidence", 0.6)
                    ))
        
        return differences
    
    def _deduplicate_differences(self, differences: List[SemanticDifference]) -> List[SemanticDifference]:
        """去重差异"""
        seen = set()
        unique_differences = []
        
        for diff in differences:
            # 创建差异的哈希键
            key = (diff.type, diff.category, diff.description, diff.old_content, diff.new_content)
            if key not in seen:
                seen.add(key)
                unique_differences.append(diff)
        
        return unique_differences
    
    def _generate_recommendations(self, differences: List[SemanticDifference], 
                                structural: Dict[str, Any], semantic: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于差异严重程度的建议
        high_severity_count = sum(1 for d in differences if d.severity == "high")
        medium_severity_count = sum(1 for d in differences if d.severity == "medium")
        
        if high_severity_count > 0:
            recommendations.append(f"发现 {high_severity_count} 个高严重程度的差异，需要仔细审查")
        
        if medium_severity_count > 5:
            recommendations.append("中等严重程度的差异较多，建议进行代码重构")
        
        # 基于结构分析的建议
        if structural["error"] is None:
            comparison = structural["comparison"]
            if comparison["complexity_change"] > 10:
                recommendations.append("代码复杂度显著增加，建议重新审查设计")
            elif comparison["complexity_change"] < -5:
                recommendations.append("代码复杂度有所降低，这是一个积极的变化")
            
            if len(comparison["functions"]["removed"]) > 0:
                recommendations.append("删除了函数，请确保这些变化是有意的")
        
        # 基于语义分析的建议
        if semantic["error"] is None and semantic["comparison"]:
            similarity_score = semantic["comparison"].get("semantic_similarity_score", 0.5)
            if similarity_score < 0.3:
                recommendations.append("语义相似度较低，可能是重大重构或功能变更")
            elif similarity_score > 0.9:
                recommendations.append("语义相似度很高，可能只是格式或风格调整")
        
        if not recommendations:
            recommendations.append("代码变更看起来是合理的")
        
        return recommendations
    
    def _calculate_similarity_score(self, structural: Dict[str, Any], 
                                  semantic: Dict[str, Any], 
                                  differences: List[SemanticDifference]) -> float:
        """计算相似度分数"""
        # 基础分数
        base_score = 1.0
        
        # 从语义分析获取分数
        semantic_score = 0.5
        if semantic["error"] is None and semantic["comparison"]:
            semantic_score = semantic["comparison"].get("semantic_similarity_score", 0.5)
        
        # 从结构分析调整分数
        structural_penalty = 0.0
        if structural["error"] is None:
            comparison = structural["comparison"]
            # 基于结构变化调整
            structural_penalty += len(comparison["functions"]["added"]) * 0.05
            structural_penalty += len(comparison["functions"]["removed"]) * 0.1
            structural_penalty += len(comparison["classes"]["added"]) * 0.1
            structural_penalty += len(comparison["classes"]["removed"]) * 0.15
            structural_penalty += abs(comparison["complexity_change"]) * 0.01
        
        # 基于差异调整分数
        difference_penalty = 0.0
        for diff in differences:
            if diff.severity == "high":
                difference_penalty += 0.1
            elif diff.severity == "medium":
                difference_penalty += 0.05
            else:
                difference_penalty += 0.01
        
        # 综合计算
        final_score = max(0.0, min(1.0, 
            semantic_score * 0.6 + 
            (base_score - structural_penalty) * 0.3 + 
            (base_score - difference_penalty) * 0.1
        ))
        
        return final_score
    
    def _generate_summary(self, similarities: float, differences: List[SemanticDifference], 
                         structural_result: Dict[str, Any], semantic_result: Dict[str, Any]) -> str:
        """生成分析摘要"""
        summary_parts = []
        
        # 相似度摘要
        if similarities > 0.8:
            summary_parts.append("代码高度相似，主要是细微调整")
        elif similarities > 0.6:
            summary_parts.append("代码相当相似，有一些重要变化")
        elif similarities > 0.4:
            summary_parts.append("代码有明显差异，可能包含功能变更")
        else:
            summary_parts.append("代码差异很大，可能是重大重构或重写")
        
        # 差异摘要
        if differences:
            high_count = sum(1 for d in differences if d.severity == "high")
            medium_count = sum(1 for d in differences if d.severity == "medium")
            low_count = sum(1 for d in differences if d.severity == "low")
            
            diff_summary = f"发现 {len(differences)} 个差异"
            if high_count > 0:
                diff_summary += f"（{high_count} 个高严重程度）"
            if medium_count > 0:
                diff_summary += f"（{medium_count} 个中等严重程度）"
            if low_count > 0:
                diff_summary += f"（{low_count} 个低严重程度）"
            
            summary_parts.append(diff_summary)
        
        # 结构变化摘要
        if structural_result["error"] is None:
            comparison = structural_result["comparison"]
            if comparison["complexity_change"] != 0:
                summary_parts.append(f"代码复杂度变化: {comparison['complexity_change']:+d}")
            
            if comparison["loc_change"] != 0:
                summary_parts.append(f"代码行数变化: {comparison['loc_change']:+d}")
        
        return "；".join(summary_parts) + "。"
    
    def _generate_cache_key(self, code1: str, code2: str, language: str) -> str:
        """生成缓存键"""
        content = f"{code1}|||{code2}|||{language}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取分析统计"""
        stats = self.stats.copy()
        stats["cache_hit_rate"] = (
            self.stats["cache_hits"] / max(1, self.stats["total_analyses"])
        )
        stats["avg_analysis_time"] = (
            self.stats["total_time"] / max(1, self.stats["total_analyses"])
        )
        return stats
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        self.logger.debug("Cache cleared")
    
    def set_cache_enabled(self, enabled: bool):
        """设置缓存状态"""
        self.cache_enabled = enabled
        if not enabled:
            self.clear_cache()
    
    def __del__(self):
        """析构函数"""
        try:
            if hasattr(self, 'model') and self.model.is_model_loaded():
                self.model.unload_model()
        except:
            pass 