#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Semantic Diff Benchmark Runner
负责执行benchmark测试并收集性能数据
"""

import os
import sys
import time
import json
import yaml
import logging
import traceback
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_diff.core.semantic_diff import SemanticDiff


@dataclass
class BenchmarkTest:
    """单个benchmark测试"""
    id: str
    name: str
    language: str
    category: str
    suite: str
    file1_path: str
    file2_path: str
    expected_similarity: Optional[float] = None
    expected_changes: Optional[List[str]] = None
    complexity: str = "medium"
    size: str = "medium"


@dataclass
class BenchmarkResult:
    """benchmark测试结果"""
    test_id: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    similarity_score: float
    differences_count: int
    differences: List[Dict[str, Any]]
    semantic_analysis_success: bool
    structural_analysis_success: bool
    cache_hit: bool
    error_message: Optional[str] = None
    model_info: Optional[Dict[str, Any]] = None


class BenchmarkRunner:
    """Benchmark测试运行器"""
    
    def __init__(self, config_path: str = "benchmarks/benchmark_config.yaml"):
        """初始化测试运行器"""
        self.config_path = config_path
        self.config = self._load_config()
        self.results_dir = Path("benchmarks/results")
        self.results_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 测试计数器
        self.total_tests = 0
        self.completed_tests = 0
        self.failed_tests = 0
        
        # 性能监控
        self.process = psutil.Process()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """设置日志"""
        log_file = self.results_dir / "benchmark.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def discover_tests(self) -> List[BenchmarkTest]:
        """发现所有测试用例"""
        tests = []
        data_dir = Path("benchmarks/data")
        
        for suite_config in self.config['test_suites']:
            suite_name = suite_config['name']
            languages = suite_config['languages']
            categories = suite_config['categories']
            complexity = suite_config['complexity']
            
            for language in languages:
                for category in categories:
                    category_dir = data_dir / language / suite_name / category
                    if not category_dir.exists():
                        continue
                    
                    # 查找配对的文件
                    old_files = list(category_dir.glob("*_old.*"))
                    for old_file in old_files:
                        base_name = old_file.stem.replace("_old", "")
                        new_file = category_dir / f"{base_name}_new{old_file.suffix}"
                        
                        if new_file.exists():
                            test_id = f"{suite_name}_{language}_{category}_{base_name}"
                            test = BenchmarkTest(
                                id=test_id,
                                name=f"{category.replace('_', ' ').title()} - {base_name}",
                                language=language,
                                category=category,
                                suite=suite_name,
                                file1_path=str(new_file),
                                file2_path=str(old_file),
                                complexity=complexity
                            )
                            tests.append(test)
        
        self.logger.info(f"发现 {len(tests)} 个测试用例")
        return tests
    
    def run_single_test(self, test: BenchmarkTest, 
                       model_config: Optional[Dict[str, Any]] = None) -> BenchmarkResult:
        """运行单个测试"""
        start_time = time.time()
        
        try:
            # 记录初始内存使用
            initial_memory = self.process.memory_info().rss / 1024 / 1024
            
            # 创建SemanticDiff实例
            semantic_diff = SemanticDiff()
            
            # 如果提供了模型配置，更新配置
            if model_config:
                for key, value in model_config.items():
                    setattr(semantic_diff.config.model, key, value)
            
            # 执行比较
            result = semantic_diff.compare_files(test.file1_path, test.file2_path, test.language)
            
            # 记录结束时的内存使用
            final_memory = self.process.memory_info().rss / 1024 / 1024
            memory_usage = final_memory - initial_memory
            
            # 获取CPU使用率（近似值）
            cpu_usage = self.process.cpu_percent()
            
            execution_time = time.time() - start_time
            
            # 创建结果对象
            benchmark_result = BenchmarkResult(
                test_id=test.id,
                execution_time=execution_time,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                similarity_score=result.similarity_score,
                differences_count=len(result.differences),
                differences=[asdict(diff) for diff in result.differences],
                semantic_analysis_success=result.model_analysis.get('error') is None,
                structural_analysis_success=result.structural_analysis.get('error') is None,
                cache_hit=result.cache_hit,
                model_info=result.model_analysis.get('model_info')
            )
            
            self.logger.info(f"✓ 测试 {test.id} 完成 ({execution_time:.2f}s)")
            return benchmark_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"{type(e).__name__}: {str(e)}"
            
            self.logger.error(f"✗ 测试 {test.id} 失败: {error_message}")
            
            return BenchmarkResult(
                test_id=test.id,
                execution_time=execution_time,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                similarity_score=0,
                differences_count=0,
                differences=[],
                semantic_analysis_success=False,
                structural_analysis_success=False,
                cache_hit=False,
                error_message=error_message
            )
    
    def run_test_worker(self, args: Tuple[BenchmarkTest, Optional[Dict[str, Any]]]) -> BenchmarkResult:
        """测试工作进程"""
        test, model_config = args
        return self.run_single_test(test, model_config)
    
    def run_benchmark_suite(self, tests: List[BenchmarkTest], 
                           parallel: bool = True,
                           max_workers: Optional[int] = None) -> List[BenchmarkResult]:
        """运行完整的benchmark套件"""
        self.total_tests = len(tests)
        self.completed_tests = 0
        self.failed_tests = 0
        
        results = []
        
        if parallel and max_workers != 1:
            # 并行执行
            if max_workers is None:
                max_workers = min(self.config['execution']['max_workers'], 
                                multiprocessing.cpu_count())
            
            self.logger.info(f"使用 {max_workers} 个进程并行执行测试")
            
            # 准备参数
            test_args = [(test, None) for test in tests]
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_test = {
                    executor.submit(self.run_test_worker, args): args[0] 
                    for args in test_args
                }
                
                # 收集结果
                for future in as_completed(future_to_test):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if result.error_message:
                            self.failed_tests += 1
                        else:
                            self.completed_tests += 1
                            
                        # 显示进度
                        progress = (len(results) / self.total_tests) * 100
                        self.logger.info(f"进度: {len(results)}/{self.total_tests} ({progress:.1f}%)")
                        
                    except Exception as e:
                        test = future_to_test[future]
                        self.logger.error(f"任务执行失败 {test.id}: {e}")
                        self.failed_tests += 1
        else:
            # 串行执行
            self.logger.info("串行执行测试")
            for test in tests:
                result = self.run_single_test(test)
                results.append(result)
                
                if result.error_message:
                    self.failed_tests += 1
                else:
                    self.completed_tests += 1
                
                # 显示进度
                progress = (len(results) / self.total_tests) * 100
                self.logger.info(f"进度: {len(results)}/{self.total_tests} ({progress:.1f}%)")
        
        return results
    
    def save_results(self, results: List[BenchmarkResult], 
                    run_id: Optional[str] = None) -> str:
        """保存测试结果"""
        if run_id is None:
            run_id = time.strftime("%Y%m%d_%H%M%S")
        
        # 保存详细结果
        results_data = {
            'run_id': run_id,
            'timestamp': time.time(),
            'config': self.config,
            'total_tests': self.total_tests,
            'completed_tests': self.completed_tests,
            'failed_tests': self.failed_tests,
            'results': [asdict(result) for result in results]
        }
        
        # 保存为JSON
        json_file = self.results_dir / f"benchmark_results_{run_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"结果已保存到 {json_file}")
        return str(json_file)
    
    def run_performance_test(self, file_sizes: List[str] = None) -> Dict[str, Any]:
        """运行性能测试"""
        if file_sizes is None:
            file_sizes = [config['name'] for config in self.config['performance_tests']['file_sizes']]
        
        performance_results = {}
        
        for size in file_sizes:
            self.logger.info(f"运行 {size} 文件大小性能测试")
            
            # 生成对应大小的测试文件
            test_files = self._generate_test_files(size)
            
            # 运行测试
            start_time = time.time()
            semantic_diff = SemanticDiff()
            result = semantic_diff.compare_files(test_files[0], test_files[1])
            end_time = time.time()
            
            performance_results[size] = {
                'execution_time': end_time - start_time,
                'memory_usage': self.process.memory_info().rss / 1024 / 1024,
                'similarity_score': result.similarity_score,
                'differences_count': len(result.differences)
            }
            
            # 清理临时文件
            for file_path in test_files:
                os.unlink(file_path)
        
        return performance_results
    
    def _generate_test_files(self, size: str) -> List[str]:
        """生成指定大小的测试文件"""
        size_config = next(
            config for config in self.config['performance_tests']['file_sizes']
            if config['name'] == size
        )
        max_lines = size_config['max_lines']
        
        # 生成简单的Python代码
        lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "",
            "class GeneratedClass:",
            "    def __init__(self):",
            "        self.value = 0",
            ""
        ]
        
        # 添加方法直到达到指定行数
        method_count = 0
        while len(lines) < max_lines:
            method_count += 1
            lines.extend([
                f"    def method_{method_count}(self, x):",
                f"        \"\"\"Generated method {method_count}\"\"\"",
                f"        return x * {method_count}",
                ""
            ])
        
        # 保存文件
        temp_dir = Path("benchmarks/temp")
        temp_dir.mkdir(exist_ok=True)
        
        file1 = temp_dir / f"test_{size}_old.py"
        file2 = temp_dir / f"test_{size}_new.py"
        
        # 文件1：原始版本
        with open(file1, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # 文件2：修改版本（添加一个方法）
        modified_lines = lines + [
            f"    def method_new(self, x, y):",
            f"        \"\"\"New method added\"\"\"",
            f"        return x + y",
            ""
        ]
        
        with open(file2, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))
        
        return [str(file1), str(file2)]
    
    def generate_summary_report(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """生成汇总报告"""
        if not results:
            return {}
        
        # 基本统计
        total = len(results)
        successful = len([r for r in results if r.error_message is None])
        failed = total - successful
        
        # 性能统计
        execution_times = [r.execution_time for r in results if r.error_message is None]
        memory_usages = [r.memory_usage_mb for r in results if r.error_message is None]
        similarity_scores = [r.similarity_score for r in results if r.error_message is None]
        
        # 语义分析成功率
        semantic_success = len([r for r in results if r.semantic_analysis_success])
        structural_success = len([r for r in results if r.structural_analysis_success])
        
        summary = {
            'overview': {
                'total_tests': total,
                'successful_tests': successful,
                'failed_tests': failed,
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'semantic_analysis_success_rate': (semantic_success / total * 100) if total > 0 else 0,
                'structural_analysis_success_rate': (structural_success / total * 100) if total > 0 else 0
            },
            'performance': {
                'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
                'max_execution_time': max(execution_times) if execution_times else 0,
                'min_execution_time': min(execution_times) if execution_times else 0,
                'avg_memory_usage': sum(memory_usages) / len(memory_usages) if memory_usages else 0,
                'max_memory_usage': max(memory_usages) if memory_usages else 0
            },
            'accuracy': {
                'avg_similarity_score': sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
                'similarity_score_distribution': self._calculate_distribution(similarity_scores)
            }
        }
        
        return summary
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, int]:
        """计算值的分布"""
        if not values:
            return {}
        
        distribution = {
            '0.0-0.2': 0,
            '0.2-0.4': 0,
            '0.4-0.6': 0,
            '0.6-0.8': 0,
            '0.8-1.0': 0
        }
        
        for value in values:
            if value < 0.2:
                distribution['0.0-0.2'] += 1
            elif value < 0.4:
                distribution['0.2-0.4'] += 1
            elif value < 0.6:
                distribution['0.4-0.6'] += 1
            elif value < 0.8:
                distribution['0.6-0.8'] += 1
            else:
                distribution['0.8-1.0'] += 1
        
        return distribution


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Semantic Diff Benchmark Runner')
    parser.add_argument('--config', default='benchmarks/benchmark_config.yaml',
                       help='配置文件路径')
    parser.add_argument('--parallel', action='store_true', default=True,
                       help='并行执行测试')
    parser.add_argument('--workers', type=int, default=None,
                       help='工作进程数量')
    parser.add_argument('--suite', choices=['basic_changes', 'refactoring', 'feature_development', 'bug_fixes'],
                       help='指定测试套件')
    parser.add_argument('--language', choices=['python', 'javascript', 'java', 'cpp', 'go', 'rust'],
                       help='指定编程语言')
    parser.add_argument('--performance', action='store_true',
                       help='运行性能测试')
    
    args = parser.parse_args()
    
    # 创建运行器
    runner = BenchmarkRunner(args.config)
    
    # 发现测试
    all_tests = runner.discover_tests()
    
    # 过滤测试
    tests = all_tests
    if args.suite:
        tests = [t for t in tests if t.suite == args.suite]
    if args.language:
        tests = [t for t in tests if t.language == args.language]
    
    print(f"将运行 {len(tests)} 个测试")
    
    # 运行测试
    start_time = time.time()
    results = runner.run_benchmark_suite(tests, args.parallel, args.workers)
    total_time = time.time() - start_time
    
    # 保存结果
    results_file = runner.save_results(results)
    
    # 生成汇总报告
    summary = runner.generate_summary_report(results)
    
    # 显示结果
    print(f"\n{'='*60}")
    print("BENCHMARK 结果汇总")
    print(f"{'='*60}")
    
    if summary and 'overview' in summary:
        print(f"总测试数: {summary['overview']['total_tests']}")
        print(f"成功: {summary['overview']['successful_tests']}")
        print(f"失败: {summary['overview']['failed_tests']}")
        print(f"成功率: {summary['overview']['success_rate']:.1f}%")
        print(f"语义分析成功率: {summary['overview']['semantic_analysis_success_rate']:.1f}%")
        print(f"总执行时间: {total_time:.2f}秒")
        print(f"平均执行时间: {summary['performance']['avg_execution_time']:.2f}秒")
        print(f"平均相似度分数: {summary['accuracy']['avg_similarity_score']:.2f}")
    else:
        print(f"总测试数: {len(tests)}")
        print(f"成功: {len([r for r in results if not r.error_message])}")
        print(f"失败: {len([r for r in results if r.error_message])}")
        print(f"总执行时间: {total_time:.2f}秒")
        print("⚠️  无测试数据，无法生成详细统计")
    
    # 运行性能测试
    if args.performance:
        print(f"\n运行性能测试...")
        perf_results = runner.run_performance_test()
        print("性能测试结果:")
        for size, metrics in perf_results.items():
            print(f"  {size}: {metrics['execution_time']:.2f}s, {metrics['memory_usage']:.1f}MB")
    
    print(f"\n详细结果已保存到: {results_file}")


if __name__ == "__main__":
    main() 