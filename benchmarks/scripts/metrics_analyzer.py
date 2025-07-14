#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Benchmark Metrics Analyzer
分析benchmark结果并计算各种性能和准确性指标
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


@dataclass
class PerformanceMetrics:
    """性能指标"""
    avg_execution_time: float
    median_execution_time: float
    p95_execution_time: float
    p99_execution_time: float
    min_execution_time: float
    max_execution_time: float
    std_execution_time: float
    avg_memory_usage: float
    max_memory_usage: float
    avg_cpu_usage: float
    cache_hit_rate: float
    throughput_tests_per_second: float


@dataclass
class AccuracyMetrics:
    """准确性指标"""
    avg_similarity_score: float
    median_similarity_score: float
    similarity_score_std: float
    semantic_analysis_success_rate: float
    structural_analysis_success_rate: float
    overall_success_rate: float
    false_positive_rate: float
    false_negative_rate: float
    confidence_score: float


@dataclass
class QualityMetrics:
    """质量指标"""
    avg_differences_detected: float
    difference_detection_consistency: float
    explanation_completeness: float
    recommendation_relevance: float
    error_rate: float
    timeout_rate: float


class MetricsAnalyzer:
    """指标分析器"""
    
    def __init__(self, results_file: str):
        """初始化分析器"""
        self.results_file = Path(results_file)
        self.results_data = self._load_results()
        self.results = self.results_data['results']
        self.config = self.results_data['config']
        
        # 创建DataFrame以便分析
        self.df = pd.DataFrame(self.results)
        
        # 输出目录
        self.output_dir = Path("benchmarks/reports") / self.results_data['run_id']
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_results(self) -> Dict[str, Any]:
        """加载测试结果"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_performance_metrics(self) -> PerformanceMetrics:
        """计算性能指标"""
        # 过滤成功的测试
        successful_tests = self.df[self.df['error_message'].isna()]
        
        if len(successful_tests) == 0:
            return PerformanceMetrics(
                avg_execution_time=0, median_execution_time=0, p95_execution_time=0,
                p99_execution_time=0, min_execution_time=0, max_execution_time=0,
                std_execution_time=0, avg_memory_usage=0, max_memory_usage=0,
                avg_cpu_usage=0, cache_hit_rate=0, throughput_tests_per_second=0
            )
        
        execution_times = successful_tests['execution_time']
        memory_usages = successful_tests['memory_usage_mb']
        cpu_usages = successful_tests['cpu_usage_percent']
        cache_hits = successful_tests['cache_hit']
        
        # 计算吞吐量
        total_time = execution_times.sum()
        throughput = len(successful_tests) / total_time if total_time > 0 else 0
        
        return PerformanceMetrics(
            avg_execution_time=execution_times.mean(),
            median_execution_time=execution_times.median(),
            p95_execution_time=execution_times.quantile(0.95),
            p99_execution_time=execution_times.quantile(0.99),
            min_execution_time=execution_times.min(),
            max_execution_time=execution_times.max(),
            std_execution_time=execution_times.std(),
            avg_memory_usage=memory_usages.mean(),
            max_memory_usage=memory_usages.max(),
            avg_cpu_usage=cpu_usages.mean(),
            cache_hit_rate=cache_hits.mean() * 100,
            throughput_tests_per_second=throughput
        )
    
    def calculate_accuracy_metrics(self) -> AccuracyMetrics:
        """计算准确性指标"""
        # 过滤成功的测试
        successful_tests = self.df[self.df['error_message'].isna()]
        
        if len(successful_tests) == 0:
            return AccuracyMetrics(
                avg_similarity_score=0, median_similarity_score=0, similarity_score_std=0,
                semantic_analysis_success_rate=0, structural_analysis_success_rate=0,
                overall_success_rate=0, false_positive_rate=0, false_negative_rate=0,
                confidence_score=0
            )
        
        similarity_scores = successful_tests['similarity_score']
        semantic_success = self.df['semantic_analysis_success']
        structural_success = self.df['structural_analysis_success']
        
        # 计算成功率
        total_tests = len(self.df)
        semantic_success_rate = semantic_success.mean() * 100
        structural_success_rate = structural_success.mean() * 100
        overall_success_rate = (len(successful_tests) / total_tests * 100) if total_tests > 0 else 0
        
        # 计算置信度分数（基于结果一致性）
        confidence_score = self._calculate_confidence_score(successful_tests)
        
        # TODO: 如果有真实标签，可以计算真正的假阳性和假阴性率
        # 现在使用启发式方法
        false_positive_rate, false_negative_rate = self._estimate_error_rates(successful_tests)
        
        return AccuracyMetrics(
            avg_similarity_score=similarity_scores.mean(),
            median_similarity_score=similarity_scores.median(),
            similarity_score_std=similarity_scores.std(),
            semantic_analysis_success_rate=semantic_success_rate,
            structural_analysis_success_rate=structural_success_rate,
            overall_success_rate=overall_success_rate,
            false_positive_rate=false_positive_rate,
            false_negative_rate=false_negative_rate,
            confidence_score=confidence_score
        )
    
    def calculate_quality_metrics(self) -> QualityMetrics:
        """计算质量指标"""
        successful_tests = self.df[self.df['error_message'].isna()]
        
        if len(successful_tests) == 0:
            return QualityMetrics(
                avg_differences_detected=0, difference_detection_consistency=0,
                explanation_completeness=0, recommendation_relevance=0,
                error_rate=100, timeout_rate=0
            )
        
        differences_counts = successful_tests['differences_count']
        
        # 错误率和超时率
        total_tests = len(self.df)
        error_rate = (len(self.df[self.df['error_message'].notna()]) / total_tests * 100) if total_tests > 0 else 0
        
        # 假设超时错误包含"timeout"字样
        timeout_errors = self.df[self.df['error_message'].str.contains('timeout', case=False, na=False)]
        timeout_rate = (len(timeout_errors) / total_tests * 100) if total_tests > 0 else 0
        
        # 差异检测一致性（变异系数）
        consistency = (differences_counts.std() / differences_counts.mean()) if differences_counts.mean() > 0 else 0
        consistency = max(0, 100 - consistency * 100)  # 转换为一致性分数
        
        # 质量评分（简化版本）
        explanation_completeness = self._assess_explanation_completeness(successful_tests)
        recommendation_relevance = self._assess_recommendation_relevance(successful_tests)
        
        return QualityMetrics(
            avg_differences_detected=differences_counts.mean(),
            difference_detection_consistency=consistency,
            explanation_completeness=explanation_completeness,
            recommendation_relevance=recommendation_relevance,
            error_rate=error_rate,
            timeout_rate=timeout_rate
        )
    
    def _calculate_confidence_score(self, tests_df: pd.DataFrame) -> float:
        """计算置信度分数"""
        # 基于结果的一致性和稳定性
        if len(tests_df) < 2:
            return 50.0
        
        # 相似度分数的一致性
        similarity_cv = tests_df['similarity_score'].std() / tests_df['similarity_score'].mean()
        
        # 执行时间的稳定性
        time_cv = tests_df['execution_time'].std() / tests_df['execution_time'].mean()
        
        # 差异数量的一致性
        diff_cv = tests_df['differences_count'].std() / (tests_df['differences_count'].mean() + 1)
        
        # 综合计算置信度
        confidence = 100 - (similarity_cv + time_cv + diff_cv) * 100 / 3
        return max(0, min(100, confidence))
    
    def _estimate_error_rates(self, tests_df: pd.DataFrame) -> Tuple[float, float]:
        """估计假阳性和假阴性率"""
        # 这是一个简化的启发式方法
        # 在实际应用中，需要有标准答案来计算真正的错误率
        
        # 假设极高或极低的相似度分数可能是错误的
        similarity_scores = tests_df['similarity_score']
        
        # 假阳性：报告差异但实际相似的情况（低相似度但可能实际相似）
        potentially_false_positive = len(similarity_scores[similarity_scores < 0.1])
        
        # 假阴性：未报告差异但实际不同的情况（高相似度但可能实际不同）
        potentially_false_negative = len(similarity_scores[similarity_scores > 0.9])
        
        total = len(similarity_scores)
        false_positive_rate = (potentially_false_positive / total * 100) if total > 0 else 0
        false_negative_rate = (potentially_false_negative / total * 100) if total > 0 else 0
        
        return false_positive_rate, false_negative_rate
    
    def _assess_explanation_completeness(self, tests_df: pd.DataFrame) -> float:
        """评估解释完整性"""
        # 基于检测到的差异数量和类型
        avg_differences = tests_df['differences_count'].mean()
        
        # 简单的评分：更多差异类型表明更完整的分析
        if avg_differences >= 20:
            return 90.0
        elif avg_differences >= 10:
            return 75.0
        elif avg_differences >= 5:
            return 60.0
        elif avg_differences >= 1:
            return 40.0
        else:
            return 20.0
    
    def _assess_recommendation_relevance(self, tests_df: pd.DataFrame) -> float:
        """评估建议相关性"""
        # 基于语义分析成功率和结果一致性
        semantic_success_rate = tests_df['semantic_analysis_success'].mean() * 100
        
        # 简化评分
        if semantic_success_rate >= 90:
            return 85.0
        elif semantic_success_rate >= 70:
            return 70.0
        elif semantic_success_rate >= 50:
            return 55.0
        else:
            return 30.0
    
    def analyze_by_language(self) -> Dict[str, Dict[str, Any]]:
        """按编程语言分析"""
        language_analysis = {}
        
        # 从test_id提取语言信息
        if 'test_id' in self.df.columns:
            self.df['language'] = self.df['test_id'].str.split('_').str[1]
        
        for language in self.df['language'].unique():
            if pd.isna(language):
                continue
                
            lang_df = self.df[self.df['language'] == language]
            successful_tests = lang_df[lang_df['error_message'].isna()]
            
            if len(successful_tests) == 0:
                continue
            
            language_analysis[language] = {
                'total_tests': len(lang_df),
                'successful_tests': len(successful_tests),
                'success_rate': len(successful_tests) / len(lang_df) * 100,
                'avg_execution_time': successful_tests['execution_time'].mean(),
                'avg_similarity_score': successful_tests['similarity_score'].mean(),
                'avg_differences_count': successful_tests['differences_count'].mean(),
                'semantic_success_rate': lang_df['semantic_analysis_success'].mean() * 100
            }
        
        return language_analysis
    
    def analyze_by_complexity(self) -> Dict[str, Dict[str, Any]]:
        """按复杂度分析"""
        complexity_analysis = {}
        
        # 从test_id或其他字段提取复杂度信息
        # 这里假设测试套件名称反映复杂度
        if 'test_id' in self.df.columns:
            self.df['suite'] = self.df['test_id'].str.split('_').str[0]
        
        suite_complexity_map = {
            'basic': 'simple',
            'refactoring': 'medium',
            'feature': 'complex',
            'bug': 'medium',
            'architectural': 'high'
        }
        
        for suite in self.df['suite'].unique():
            if pd.isna(suite):
                continue
                
            complexity = suite_complexity_map.get(suite, 'medium')
            suite_df = self.df[self.df['suite'] == suite]
            successful_tests = suite_df[suite_df['error_message'].isna()]
            
            if len(successful_tests) == 0:
                continue
            
            complexity_analysis[complexity] = {
                'total_tests': len(suite_df),
                'successful_tests': len(successful_tests),
                'success_rate': len(successful_tests) / len(suite_df) * 100,
                'avg_execution_time': successful_tests['execution_time'].mean(),
                'avg_similarity_score': successful_tests['similarity_score'].mean(),
                'semantic_success_rate': suite_df['semantic_analysis_success'].mean() * 100
            }
        
        return complexity_analysis
    
    def generate_performance_plots(self):
        """生成性能相关的图表"""
        successful_tests = self.df[self.df['error_message'].isna()]
        
        if len(successful_tests) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Performance Analysis', fontsize=16)
        
        # 执行时间分布
        axes[0, 0].hist(successful_tests['execution_time'], bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Execution Time Distribution')
        axes[0, 0].set_xlabel('Execution Time (seconds)')
        axes[0, 0].set_ylabel('Frequency')
        
        # 内存使用分布
        axes[0, 1].hist(successful_tests['memory_usage_mb'], bins=20, alpha=0.7, color='lightgreen')
        axes[0, 1].set_title('Memory Usage Distribution')
        axes[0, 1].set_xlabel('Memory Usage (MB)')
        axes[0, 1].set_ylabel('Frequency')
        
        # 执行时间 vs 相似度分数
        axes[1, 0].scatter(successful_tests['execution_time'], successful_tests['similarity_score'], 
                          alpha=0.6, color='orange')
        axes[1, 0].set_title('Execution Time vs Similarity Score')
        axes[1, 0].set_xlabel('Execution Time (seconds)')
        axes[1, 0].set_ylabel('Similarity Score')
        
        # 差异数量分布
        axes[1, 1].hist(successful_tests['differences_count'], bins=20, alpha=0.7, color='lightcoral')
        axes[1, 1].set_title('Differences Count Distribution')
        axes[1, 1].set_xlabel('Number of Differences')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_accuracy_plots(self):
        """生成准确性相关的图表"""
        successful_tests = self.df[self.df['error_message'].isna()]
        
        if len(successful_tests) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Accuracy Analysis', fontsize=16)
        
        # 相似度分数分布
        axes[0, 0].hist(successful_tests['similarity_score'], bins=20, alpha=0.7, color='lightblue')
        axes[0, 0].set_title('Similarity Score Distribution')
        axes[0, 0].set_xlabel('Similarity Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # 成功率对比
        success_data = [
            self.df['semantic_analysis_success'].mean() * 100,
            self.df['structural_analysis_success'].mean() * 100,
            (len(successful_tests) / len(self.df) * 100) if len(self.df) > 0 else 0
        ]
        success_labels = ['Semantic Analysis', 'Structural Analysis', 'Overall']
        axes[0, 1].bar(success_labels, success_data, color=['lightgreen', 'lightcoral', 'lightyellow'])
        axes[0, 1].set_title('Success Rates')
        axes[0, 1].set_ylabel('Success Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 按语言的相似度分数
        if 'language' in self.df.columns:
            lang_similarity = self.df.groupby('language')['similarity_score'].mean()
            axes[1, 0].bar(lang_similarity.index, lang_similarity.values, color='lightsteelblue')
            axes[1, 0].set_title('Average Similarity Score by Language')
            axes[1, 0].set_xlabel('Language')
            axes[1, 0].set_ylabel('Average Similarity Score')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 相似度分数箱线图
        axes[1, 1].boxplot(successful_tests['similarity_score'])
        axes[1, 1].set_title('Similarity Score Box Plot')
        axes[1, 1].set_ylabel('Similarity Score')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'accuracy_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_comparison_plots(self):
        """生成对比分析图表"""
        if 'language' not in self.df.columns:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Comparative Analysis', fontsize=16)
        
        # 按语言的执行时间对比
        lang_time = self.df.groupby('language')['execution_time'].mean()
        axes[0, 0].bar(lang_time.index, lang_time.values, color='skyblue')
        axes[0, 0].set_title('Average Execution Time by Language')
        axes[0, 0].set_xlabel('Language')
        axes[0, 0].set_ylabel('Execution Time (seconds)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 按语言的成功率对比
        lang_success = self.df.groupby('language').apply(
            lambda x: len(x[x['error_message'].isna()]) / len(x) * 100
        )
        axes[0, 1].bar(lang_success.index, lang_success.values, color='lightgreen')
        axes[0, 1].set_title('Success Rate by Language')
        axes[0, 1].set_xlabel('Language')
        axes[0, 1].set_ylabel('Success Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 按语言的差异检测数量
        lang_diffs = self.df.groupby('language')['differences_count'].mean()
        axes[1, 0].bar(lang_diffs.index, lang_diffs.values, color='lightcoral')
        axes[1, 0].set_title('Average Differences Detected by Language')
        axes[1, 0].set_xlabel('Language')
        axes[1, 0].set_ylabel('Average Differences Count')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 语义vs结构分析成功率对比
        semantic_by_lang = self.df.groupby('language')['semantic_analysis_success'].mean() * 100
        structural_by_lang = self.df.groupby('language')['structural_analysis_success'].mean() * 100
        
        x = range(len(semantic_by_lang.index))
        width = 0.35
        axes[1, 1].bar([i - width/2 for i in x], semantic_by_lang.values, width, 
                      label='Semantic', color='lightblue')
        axes[1, 1].bar([i + width/2 for i in x], structural_by_lang.values, width,
                      label='Structural', color='lightcoral')
        axes[1, 1].set_title('Analysis Success Rate by Language')
        axes[1, 1].set_xlabel('Language')
        axes[1, 1].set_ylabel('Success Rate (%)')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(semantic_by_lang.index, rotation=45)
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'comparison_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成全面的分析报告"""
        performance_metrics = self.calculate_performance_metrics()
        accuracy_metrics = self.calculate_accuracy_metrics()
        quality_metrics = self.calculate_quality_metrics()
        
        language_analysis = self.analyze_by_language()
        complexity_analysis = self.analyze_by_complexity()
        
        # 生成图表
        self.generate_performance_plots()
        self.generate_accuracy_plots()
        self.generate_comparison_plots()
        
        # 综合报告
        report = {
            'summary': {
                'run_id': self.results_data['run_id'],
                'timestamp': self.results_data['timestamp'],
                'total_tests': len(self.df),
                'successful_tests': len(self.df[self.df['error_message'].isna()]),
                'failed_tests': len(self.df[self.df['error_message'].notna()])
            },
            'performance_metrics': performance_metrics.__dict__,
            'accuracy_metrics': accuracy_metrics.__dict__,
            'quality_metrics': quality_metrics.__dict__,
            'language_analysis': language_analysis,
            'complexity_analysis': complexity_analysis,
            'recommendations': self._generate_recommendations(
                performance_metrics, accuracy_metrics, quality_metrics
            )
        }
        
        # 保存报告
        report_file = self.output_dir / 'comprehensive_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def _generate_recommendations(self, perf: PerformanceMetrics, 
                                 acc: AccuracyMetrics, qual: QualityMetrics) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 性能建议
        if perf.avg_execution_time > 10:
            recommendations.append("执行时间较长，建议优化算法或增加缓存")
        
        if perf.max_memory_usage > 1000:
            recommendations.append("内存使用量较高，建议优化内存管理")
        
        if perf.cache_hit_rate < 50:
            recommendations.append("缓存命中率较低，建议优化缓存策略")
        
        # 准确性建议
        if acc.semantic_analysis_success_rate < 80:
            recommendations.append("语义分析成功率较低，建议检查模型配置或提示词")
        
        if acc.avg_similarity_score < 0.3:
            recommendations.append("平均相似度分数较低，可能需要调整评分算法")
        
        # 质量建议
        if qual.error_rate > 10:
            recommendations.append("错误率较高，建议增强错误处理和输入验证")
        
        if qual.difference_detection_consistency < 60:
            recommendations.append("差异检测一致性较低，建议改进算法稳定性")
        
        return recommendations


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark Metrics Analyzer')
    parser.add_argument('results_file', help='Benchmark结果文件路径')
    parser.add_argument('--output-dir', help='输出目录（可选）')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = MetricsAnalyzer(args.results_file)
    
    if args.output_dir:
        analyzer.output_dir = Path(args.output_dir)
        analyzer.output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成全面报告
    print("正在分析benchmark结果...")
    report = analyzer.generate_comprehensive_report()
    
    # 显示关键指标
    print(f"\n{'='*60}")
    print("BENCHMARK 分析结果")
    print(f"{'='*60}")
    
    summary = report['summary']
    print(f"总测试数: {summary['total_tests']}")
    print(f"成功测试数: {summary['successful_tests']}")
    print(f"失败测试数: {summary['failed_tests']}")
    
    perf = report['performance_metrics']
    print(f"\n性能指标:")
    print(f"  平均执行时间: {perf['avg_execution_time']:.2f}秒")
    print(f"  P95执行时间: {perf['p95_execution_time']:.2f}秒")
    print(f"  平均内存使用: {perf['avg_memory_usage']:.1f}MB")
    print(f"  缓存命中率: {perf['cache_hit_rate']:.1f}%")
    print(f"  吞吐量: {perf['throughput_tests_per_second']:.2f} tests/sec")
    
    acc = report['accuracy_metrics']
    print(f"\n准确性指标:")
    print(f"  平均相似度分数: {acc['avg_similarity_score']:.2f}")
    print(f"  语义分析成功率: {acc['semantic_analysis_success_rate']:.1f}%")
    print(f"  结构分析成功率: {acc['structural_analysis_success_rate']:.1f}%")
    print(f"  整体成功率: {acc['overall_success_rate']:.1f}%")
    print(f"  置信度分数: {acc['confidence_score']:.1f}")
    
    qual = report['quality_metrics']
    print(f"\n质量指标:")
    print(f"  平均差异检测数: {qual['avg_differences_detected']:.1f}")
    print(f"  检测一致性: {qual['difference_detection_consistency']:.1f}%")
    print(f"  错误率: {qual['error_rate']:.1f}%")
    
    # 显示建议
    recommendations = report['recommendations']
    if recommendations:
        print(f"\n改进建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print(f"\n详细报告和图表已保存到: {analyzer.output_dir}")


if __name__ == "__main__":
    main() 