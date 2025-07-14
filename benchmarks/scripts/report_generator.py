#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Benchmark Report Generator
生成美观的HTML benchmark报告
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, results_file: str, output_dir: Optional[str] = None):
        """初始化报告生成器"""
        self.results_file = Path(results_file)
        self.results_data = self._load_results()
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("benchmarks/reports") / self.results_data['run_id']
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_results(self) -> Dict[str, Any]:
        """加载测试结果"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_analysis_report(self) -> Optional[Dict[str, Any]]:
        """加载分析报告"""
        report_file = self.output_dir / 'comprehensive_report.json'
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为base64字符串"""
        if image_path.exists():
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return ""
    
    def generate_html_report(self) -> str:
        """生成HTML报告"""
        analysis_report = self._load_analysis_report()
        
        # 加载图片
        performance_chart = self._encode_image(self.output_dir / 'performance_analysis.png')
        accuracy_chart = self._encode_image(self.output_dir / 'accuracy_analysis.png')
        comparison_chart = self._encode_image(self.output_dir / 'comparison_analysis.png')
        
        # 生成HTML内容
        html_content = self._generate_html_template(
            analysis_report, performance_chart, accuracy_chart, comparison_chart
        )
        
        # 保存HTML文件
        html_file = self.output_dir / 'benchmark_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_file)
    
    def _generate_html_template(self, analysis_report: Optional[Dict[str, Any]],
                               performance_chart: str, accuracy_chart: str, 
                               comparison_chart: str) -> str:
        """生成HTML模板"""
        run_id = self.results_data['run_id']
        timestamp = datetime.fromtimestamp(self.results_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        # 基本统计
        total_tests = self.results_data['total_tests']
        completed_tests = self.results_data['completed_tests']
        failed_tests = self.results_data['failed_tests']
        success_rate = (completed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 性能和准确性指标
        perf_metrics = analysis_report['performance_metrics'] if analysis_report else {}
        acc_metrics = analysis_report['accuracy_metrics'] if analysis_report else {}
        qual_metrics = analysis_report['quality_metrics'] if analysis_report else {}
        
        # 语言分析
        lang_analysis = analysis_report['language_analysis'] if analysis_report else {}
        
        # 建议
        recommendations = analysis_report['recommendations'] if analysis_report else []
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semantic Diff Benchmark Report - {run_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 20px;
        }}
        
        .header .meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .header .meta-item {{
            text-align: center;
        }}
        
        .header .meta-item .label {{
            color: #95a5a6;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .header .meta-item .value {{
            color: #2c3e50;
            font-size: 1.4em;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-card .icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .metric-card .label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .info {{ color: #3498db; }}
        
        .section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .section h3 {{
            color: #34495e;
            font-size: 1.4em;
            margin: 20px 0 15px 0;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metrics-group {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .metrics-group h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .metric-row:last-child {{
            border-bottom: none;
        }}
        
        .metric-row .name {{
            color: #495057;
        }}
        
        .metric-row .value {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .language-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .language-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        
        .language-card .name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .language-card .stats {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .language-card .stat {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
        }}
        
        .recommendations {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .recommendations h4 {{
            color: #1565c0;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            list-style: none;
            padding: 0;
        }}
        
        .recommendations li {{
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: relative;
            padding-left: 50px;
        }}
        
        .recommendations li:before {{
            content: "💡";
            position: absolute;
            left: 15px;
            top: 15px;
            font-size: 1.2em;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
        
        .footer a {{
            color: #ecf0f1;
            text-decoration: none;
        }}
        
        .progress-bar {{
            background: #ecf0f1;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔍 Semantic Diff Benchmark Report</h1>
            <div class="subtitle">Performance and Accuracy Analysis</div>
            <div class="meta">
                <div class="meta-item">
                    <div class="label">Run ID</div>
                    <div class="value">{run_id}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Generated</div>
                    <div class="value">{timestamp}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Total Tests</div>
                    <div class="value">{total_tests}</div>
                </div>
            </div>
        </div>
        
        <!-- Dashboard -->
        <div class="dashboard">
            <div class="metric-card">
                <div class="icon success">✅</div>
                <div class="value success">{completed_tests}</div>
                <div class="label">Successful Tests</div>
            </div>
            <div class="metric-card">
                <div class="icon error">❌</div>
                <div class="value error">{failed_tests}</div>
                <div class="label">Failed Tests</div>
            </div>
            <div class="metric-card">
                <div class="icon info">📊</div>
                <div class="value info">{success_rate:.1f}%</div>
                <div class="label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="icon warning">⚡</div>
                <div class="value warning">{perf_metrics.get('avg_execution_time', 0):.2f}s</div>
                <div class="label">Avg Execution Time</div>
            </div>
        </div>
        
        <!-- Performance Metrics -->
        <div class="section">
            <h2>🚀 Performance Metrics</h2>
            <div class="metrics-grid">
                <div class="metrics-group">
                    <h4>Execution Time</h4>
                    <div class="metric-row">
                        <span class="name">Average</span>
                        <span class="value">{perf_metrics.get('avg_execution_time', 0):.2f}s</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Median</span>
                        <span class="value">{perf_metrics.get('median_execution_time', 0):.2f}s</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">P95</span>
                        <span class="value">{perf_metrics.get('p95_execution_time', 0):.2f}s</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Max</span>
                        <span class="value">{perf_metrics.get('max_execution_time', 0):.2f}s</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Resource Usage</h4>
                    <div class="metric-row">
                        <span class="name">Avg Memory</span>
                        <span class="value">{perf_metrics.get('avg_memory_usage', 0):.1f}MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Max Memory</span>
                        <span class="value">{perf_metrics.get('max_memory_usage', 0):.1f}MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Avg CPU</span>
                        <span class="value">{perf_metrics.get('avg_cpu_usage', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Cache Hit Rate</span>
                        <span class="value">{perf_metrics.get('cache_hit_rate', 0):.1f}%</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Throughput</h4>
                    <div class="metric-row">
                        <span class="name">Tests/Second</span>
                        <span class="value">{perf_metrics.get('throughput_tests_per_second', 0):.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Total Time</span>
                        <span class="value">{perf_metrics.get('avg_execution_time', 0) * total_tests:.1f}s</span>
                    </div>
                </div>
            </div>
            
            {f'<div class="chart-container"><img src="data:image/png;base64,{performance_chart}" alt="Performance Analysis"></div>' if performance_chart else ''}
        </div>
        
        <!-- Accuracy Metrics -->
        <div class="section">
            <h2>🎯 Accuracy Metrics</h2>
            <div class="metrics-grid">
                <div class="metrics-group">
                    <h4>Similarity Analysis</h4>
                    <div class="metric-row">
                        <span class="name">Avg Similarity Score</span>
                        <span class="value">{acc_metrics.get('avg_similarity_score', 0):.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Median Score</span>
                        <span class="value">{acc_metrics.get('median_similarity_score', 0):.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Score Std Dev</span>
                        <span class="value">{acc_metrics.get('similarity_score_std', 0):.3f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Confidence</span>
                        <span class="value">{acc_metrics.get('confidence_score', 0):.1f}%</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Analysis Success Rates</h4>
                    <div class="metric-row">
                        <span class="name">Semantic Analysis</span>
                        <span class="value">{acc_metrics.get('semantic_analysis_success_rate', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Structural Analysis</span>
                        <span class="value">{acc_metrics.get('structural_analysis_success_rate', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Overall Success</span>
                        <span class="value">{acc_metrics.get('overall_success_rate', 0):.1f}%</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Error Estimates</h4>
                    <div class="metric-row">
                        <span class="name">False Positive Rate</span>
                        <span class="value">{acc_metrics.get('false_positive_rate', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">False Negative Rate</span>
                        <span class="value">{acc_metrics.get('false_negative_rate', 0):.1f}%</span>
                    </div>
                </div>
            </div>
            
            {f'<div class="chart-container"><img src="data:image/png;base64,{accuracy_chart}" alt="Accuracy Analysis"></div>' if accuracy_chart else ''}
        </div>
        
        <!-- Quality Metrics -->
        <div class="section">
            <h2>💎 Quality Metrics</h2>
            <div class="metrics-grid">
                <div class="metrics-group">
                    <h4>Difference Detection</h4>
                    <div class="metric-row">
                        <span class="name">Avg Differences Found</span>
                        <span class="value">{qual_metrics.get('avg_differences_detected', 0):.1f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Detection Consistency</span>
                        <span class="value">{qual_metrics.get('difference_detection_consistency', 0):.1f}%</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Analysis Quality</h4>
                    <div class="metric-row">
                        <span class="name">Explanation Completeness</span>
                        <span class="value">{qual_metrics.get('explanation_completeness', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Recommendation Relevance</span>
                        <span class="value">{qual_metrics.get('recommendation_relevance', 0):.1f}%</span>
                    </div>
                </div>
                <div class="metrics-group">
                    <h4>Reliability</h4>
                    <div class="metric-row">
                        <span class="name">Error Rate</span>
                        <span class="value">{qual_metrics.get('error_rate', 0):.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="name">Timeout Rate</span>
                        <span class="value">{qual_metrics.get('timeout_rate', 0):.1f}%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Language Analysis -->
        {self._generate_language_analysis_html(lang_analysis) if lang_analysis else ''}
        
        <!-- Comparison Charts -->
        {f'<div class="section"><h2>📈 Comparative Analysis</h2><div class="chart-container"><img src="data:image/png;base64,{comparison_chart}" alt="Comparison Analysis"></div></div>' if comparison_chart else ''}
        
        <!-- Recommendations -->
        {self._generate_recommendations_html(recommendations) if recommendations else ''}
        
        <!-- Footer -->
        <div class="footer">
            <p>Generated by <a href="#">Semantic Diff Benchmark Tool</a> | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_language_analysis_html(self, lang_analysis: Dict[str, Any]) -> str:
        """生成语言分析HTML"""
        if not lang_analysis:
            return ""
        
        cards_html = ""
        for language, stats in lang_analysis.items():
            cards_html += f"""
            <div class="language-card">
                <div class="name">{language.upper()}</div>
                <div class="stats">
                    <div class="stat">
                        <span>Tests:</span>
                        <span>{stats['total_tests']}</span>
                    </div>
                    <div class="stat">
                        <span>Success Rate:</span>
                        <span>{stats['success_rate']:.1f}%</span>
                    </div>
                    <div class="stat">
                        <span>Avg Time:</span>
                        <span>{stats['avg_execution_time']:.2f}s</span>
                    </div>
                    <div class="stat">
                        <span>Avg Similarity:</span>
                        <span>{stats['avg_similarity_score']:.2f}</span>
                    </div>
                    <div class="stat">
                        <span>Semantic Success:</span>
                        <span>{stats['semantic_success_rate']:.1f}%</span>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🌐 Language Analysis</h2>
            <div class="language-grid">
                {cards_html}
            </div>
        </div>
        """
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """生成建议HTML"""
        if not recommendations:
            return ""
        
        recommendations_html = ""
        for rec in recommendations:
            recommendations_html += f"<li>{rec}</li>"
        
        return f"""
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div class="recommendations">
                <h4>Based on the analysis, here are our recommendations for improvement:</h4>
                <ul>
                    {recommendations_html}
                </ul>
            </div>
        </div>
        """
    
    def generate_markdown_report(self) -> str:
        """生成Markdown报告"""
        analysis_report = self._load_analysis_report()
        run_id = self.results_data['run_id']
        timestamp = datetime.fromtimestamp(self.results_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        # 基本统计
        total_tests = self.results_data['total_tests']
        completed_tests = self.results_data['completed_tests']
        failed_tests = self.results_data['failed_tests']
        success_rate = (completed_tests / total_tests * 100) if total_tests > 0 else 0
        
        markdown_content = f"""# Semantic Diff Benchmark Report

**Run ID:** {run_id}  
**Generated:** {timestamp}  
**Total Tests:** {total_tests}

## Executive Summary

- **Successful Tests:** {completed_tests}
- **Failed Tests:** {failed_tests}
- **Success Rate:** {success_rate:.1f}%

## Performance Metrics
"""
        
        if analysis_report:
            perf_metrics = analysis_report['performance_metrics']
            acc_metrics = analysis_report['accuracy_metrics']
            qual_metrics = analysis_report['quality_metrics']
            
            markdown_content += f"""
### Execution Performance
- **Average Execution Time:** {perf_metrics.get('avg_execution_time', 0):.2f}s
- **Median Execution Time:** {perf_metrics.get('median_execution_time', 0):.2f}s
- **P95 Execution Time:** {perf_metrics.get('p95_execution_time', 0):.2f}s
- **Maximum Execution Time:** {perf_metrics.get('max_execution_time', 0):.2f}s

### Resource Usage
- **Average Memory Usage:** {perf_metrics.get('avg_memory_usage', 0):.1f}MB
- **Maximum Memory Usage:** {perf_metrics.get('max_memory_usage', 0):.1f}MB
- **Average CPU Usage:** {perf_metrics.get('avg_cpu_usage', 0):.1f}%
- **Cache Hit Rate:** {perf_metrics.get('cache_hit_rate', 0):.1f}%

### Throughput
- **Tests per Second:** {perf_metrics.get('throughput_tests_per_second', 0):.2f}

## Accuracy Metrics

### Similarity Analysis
- **Average Similarity Score:** {acc_metrics.get('avg_similarity_score', 0):.2f}
- **Median Similarity Score:** {acc_metrics.get('median_similarity_score', 0):.2f}
- **Similarity Score Standard Deviation:** {acc_metrics.get('similarity_score_std', 0):.3f}
- **Confidence Score:** {acc_metrics.get('confidence_score', 0):.1f}%

### Analysis Success Rates
- **Semantic Analysis Success Rate:** {acc_metrics.get('semantic_analysis_success_rate', 0):.1f}%
- **Structural Analysis Success Rate:** {acc_metrics.get('structural_analysis_success_rate', 0):.1f}%
- **Overall Success Rate:** {acc_metrics.get('overall_success_rate', 0):.1f}%

## Quality Metrics

### Difference Detection
- **Average Differences Detected:** {qual_metrics.get('avg_differences_detected', 0):.1f}
- **Detection Consistency:** {qual_metrics.get('difference_detection_consistency', 0):.1f}%

### Analysis Quality
- **Explanation Completeness:** {qual_metrics.get('explanation_completeness', 0):.1f}%
- **Recommendation Relevance:** {qual_metrics.get('recommendation_relevance', 0):.1f}%

### Reliability
- **Error Rate:** {qual_metrics.get('error_rate', 0):.1f}%
- **Timeout Rate:** {qual_metrics.get('timeout_rate', 0):.1f}%
"""
            
            # 语言分析
            if 'language_analysis' in analysis_report:
                markdown_content += "\n## Language Analysis\n\n"
                for language, stats in analysis_report['language_analysis'].items():
                    markdown_content += f"""### {language.upper()}
- **Total Tests:** {stats['total_tests']}
- **Success Rate:** {stats['success_rate']:.1f}%
- **Average Execution Time:** {stats['avg_execution_time']:.2f}s
- **Average Similarity Score:** {stats['avg_similarity_score']:.2f}
- **Semantic Analysis Success Rate:** {stats['semantic_success_rate']:.1f}%

"""
            
            # 建议
            if 'recommendations' in analysis_report and analysis_report['recommendations']:
                markdown_content += "\n## Recommendations\n\n"
                for i, rec in enumerate(analysis_report['recommendations'], 1):
                    markdown_content += f"{i}. {rec}\n"
        
        # 保存Markdown文件
        md_file = self.output_dir / 'benchmark_report.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(md_file)
    
    def generate_json_report(self) -> str:
        """生成JSON报告"""
        analysis_report = self._load_analysis_report()
        
        # 合并所有数据
        combined_report = {
            'metadata': {
                'run_id': self.results_data['run_id'],
                'timestamp': self.results_data['timestamp'],
                'generated_at': time.time()
            },
            'summary': {
                'total_tests': self.results_data['total_tests'],
                'completed_tests': self.results_data['completed_tests'],
                'failed_tests': self.results_data['failed_tests']
            },
            'raw_results': self.results_data['results']
        }
        
        if analysis_report:
            combined_report.update(analysis_report)
        
        # 保存JSON文件
        json_file = self.output_dir / 'benchmark_report.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(combined_report, f, indent=2, ensure_ascii=False)
        
        return str(json_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark Report Generator')
    parser.add_argument('results_file', help='Benchmark结果文件路径')
    parser.add_argument('--output-dir', help='输出目录（可选）')
    parser.add_argument('--format', choices=['html', 'markdown', 'json', 'all'], 
                       default='all', help='报告格式')
    
    args = parser.parse_args()
    
    # 创建报告生成器
    generator = ReportGenerator(args.results_file, args.output_dir)
    
    print("正在生成benchmark报告...")
    
    generated_files = []
    
    # 生成指定格式的报告
    if args.format in ['html', 'all']:
        html_file = generator.generate_html_report()
        generated_files.append(('HTML报告', html_file))
    
    if args.format in ['markdown', 'all']:
        md_file = generator.generate_markdown_report()
        generated_files.append(('Markdown报告', md_file))
    
    if args.format in ['json', 'all']:
        json_file = generator.generate_json_report()
        generated_files.append(('JSON报告', json_file))
    
    # 显示结果
    print(f"\n{'='*60}")
    print("报告生成完成")
    print(f"{'='*60}")
    
    for report_type, file_path in generated_files:
        print(f"{report_type}: {file_path}")
    
    print(f"\n所有报告文件已保存到: {generator.output_dir}")


if __name__ == "__main__":
    main() 