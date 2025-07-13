#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Output formatter for semantic diff results.
"""

import json
import html
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..core.semantic_analyzer import SemanticAnalysisResult, SemanticDifference


class DiffFormatter:
    """
    语义diff结果格式化器
    """
    
    def __init__(self, format: str = "rich", no_color: bool = False, 
                 context_lines: int = 3, show_line_numbers: bool = True):
        """
        初始化格式化器
        
        Args:
            format: 输出格式 (plain, rich, json, html)
            no_color: 禁用颜色
            context_lines: 上下文行数
            show_line_numbers: 显示行号
        """
        self.format = format
        self.no_color = no_color
        self.context_lines = context_lines
        self.show_line_numbers = show_line_numbers
        
        # 初始化Rich控制台
        if RICH_AVAILABLE and format == "rich" and not no_color:
            self.console = Console()
        else:
            self.console = None
    
    def format_result(self, result: SemanticAnalysisResult, 
                     file1_name: str, file2_name: str) -> str:
        """
        格式化分析结果
        
        Args:
            result: 语义分析结果
            file1_name: 第一个文件名
            file2_name: 第二个文件名
            
        Returns:
            格式化后的输出
        """
        if self.format == "json":
            return self._format_json(result, file1_name, file2_name)
        elif self.format == "html":
            return self._format_html(result, file1_name, file2_name)
        elif self.format == "rich" and self.console:
            return self._format_rich(result, file1_name, file2_name)
        else:
            return self._format_plain(result, file1_name, file2_name)
    
    def _format_plain(self, result: SemanticAnalysisResult, 
                     file1_name: str, file2_name: str) -> str:
        """纯文本格式"""
        lines = []
        
        # 标题
        lines.append("=" * 80)
        lines.append(f"语义差异分析报告")
        lines.append("=" * 80)
        lines.append(f"文件1: {file1_name}")
        lines.append(f"文件2: {file2_name}")
        lines.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"相似度: {result.similarity_score:.2%}")
        lines.append(f"执行时间: {result.execution_time:.3f}秒")
        if result.cache_hit:
            lines.append("缓存命中: 是")
        lines.append("")
        
        # 摘要
        lines.append("摘要:")
        lines.append("-" * 40)
        lines.append(result.summary)
        lines.append("")
        
        # 差异详情
        if result.differences:
            lines.append(f"差异详情 ({len(result.differences)} 个):")
            lines.append("-" * 40)
            
            for i, diff in enumerate(result.differences, 1):
                lines.append(f"{i}. {diff.description}")
                lines.append(f"   类型: {diff.type}")
                lines.append(f"   严重程度: {diff.severity}")
                lines.append(f"   分类: {diff.category}")
                lines.append(f"   语义影响: {diff.semantic_impact}")
                lines.append(f"   置信度: {diff.confidence:.2%}")
                
                if diff.old_content:
                    lines.append(f"   原内容: {diff.old_content[:100]}...")
                if diff.new_content:
                    lines.append(f"   新内容: {diff.new_content[:100]}...")
                lines.append("")
        else:
            lines.append("未发现显著差异")
            lines.append("")
        
        # 建议
        if result.recommendations:
            lines.append("建议:")
            lines.append("-" * 40)
            for i, rec in enumerate(result.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # 技术细节
        if hasattr(result, 'model_analysis') and result.model_analysis:
            lines.append("AI模型分析:")
            lines.append("-" * 40)
            if 'comparison' in result.model_analysis:
                comp = result.model_analysis['comparison']
                if isinstance(comp, dict):
                    for key, value in comp.items():
                        if key != 'semantic_similarity_score':
                            lines.append(f"  {key}: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_rich(self, result: SemanticAnalysisResult, 
                    file1_name: str, file2_name: str) -> str:
        """Rich格式 (带颜色和样式)"""
        if not self.console:
            return self._format_plain(result, file1_name, file2_name)
        
        output = []
        
        # 标题面板
        title_text = Text("语义差异分析报告", style="bold cyan")
        info_text = f"""
文件1: {file1_name}
文件2: {file2_name}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
相似度: {result.similarity_score:.2%}
执行时间: {result.execution_time:.3f}秒
"""
        if result.cache_hit:
            info_text += "缓存命中: 是"
        
        title_panel = Panel(info_text.strip(), title=title_text, border_style="cyan")
        
        # 使用控制台渲染并捕获输出
        with self.console.capture() as capture:
            self.console.print(title_panel)
        output.append(capture.get())
        
        # 相似度指示器
        similarity_color = "green" if result.similarity_score > 0.8 else \
                          "yellow" if result.similarity_score > 0.5 else "red"
        
        similarity_text = Text(f"相似度: {result.similarity_score:.2%}", 
                              style=f"bold {similarity_color}")
        
        with self.console.capture() as capture:
            self.console.print(similarity_text)
        output.append(capture.get())
        
        # 摘要
        summary_panel = Panel(result.summary, title="摘要", border_style="blue")
        with self.console.capture() as capture:
            self.console.print(summary_panel)
        output.append(capture.get())
        
        # 差异表格
        if result.differences:
            diff_table = Table(title=f"差异详情 ({len(result.differences)} 个)")
            diff_table.add_column("序号", style="cyan", width=4)
            diff_table.add_column("描述", style="white")
            diff_table.add_column("类型", style="magenta", width=12)
            diff_table.add_column("严重程度", style="yellow", width=8)
            diff_table.add_column("置信度", style="green", width=8)
            
            for i, diff in enumerate(result.differences, 1):
                severity_style = "red" if diff.severity == "high" else \
                               "yellow" if diff.severity == "medium" else "green"
                
                diff_table.add_row(
                    str(i),
                    diff.description[:50] + "..." if len(diff.description) > 50 else diff.description,
                    diff.type,
                    Text(diff.severity, style=severity_style),
                    f"{diff.confidence:.1%}"
                )
            
            with self.console.capture() as capture:
                self.console.print(diff_table)
            output.append(capture.get())
        else:
            no_diff_panel = Panel("未发现显著差异", title="差异", 
                                 border_style="green", style="green")
            with self.console.capture() as capture:
                self.console.print(no_diff_panel)
            output.append(capture.get())
        
        # 建议
        if result.recommendations:
            rec_text = "\n".join(f"• {rec}" for rec in result.recommendations)
            rec_panel = Panel(rec_text, title="建议", border_style="yellow")
            with self.console.capture() as capture:
                self.console.print(rec_panel)
            output.append(capture.get())
        
        return "\n".join(output)
    
    def _format_json(self, result: SemanticAnalysisResult, 
                    file1_name: str, file2_name: str) -> str:
        """JSON格式"""
        data = {
            "analysis_info": {
                "file1": file1_name,
                "file2": file2_name,
                "timestamp": datetime.now().isoformat(),
                "execution_time": result.execution_time,
                "cache_hit": result.cache_hit
            },
            "similarity_score": result.similarity_score,
            "summary": result.summary,
            "differences": [
                {
                    "type": diff.type,
                    "severity": diff.severity,
                    "category": diff.category,
                    "description": diff.description,
                    "semantic_impact": diff.semantic_impact,
                    "confidence": diff.confidence,
                    "old_content": diff.old_content,
                    "new_content": diff.new_content,
                    "old_location": {
                        "start_line": diff.old_location[0],
                        "end_line": diff.old_location[1]
                    },
                    "new_location": {
                        "start_line": diff.new_location[0],
                        "end_line": diff.new_location[1]
                    }
                }
                for diff in result.differences
            ],
            "recommendations": result.recommendations,
            "model_analysis": result.model_analysis,
            "structural_analysis": result.structural_analysis
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_html(self, result: SemanticAnalysisResult, 
                    file1_name: str, file2_name: str) -> str:
        """HTML格式"""
        
        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>语义差异分析报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 2px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .title {
            color: #2c3e50;
            font-size: 2.5em;
            margin: 0;
            text-align: center;
        }
        .meta-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .similarity-score {
            font-size: 1.5em;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        .section {
            margin: 30px 0;
        }
        .section-title {
            color: #34495e;
            font-size: 1.5em;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .diff-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .diff-table th, .diff-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .diff-table th {
            background-color: #3498db;
            color: white;
        }
        .diff-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .severity-high { color: #e74c3c; font-weight: bold; }
        .severity-medium { color: #f39c12; font-weight: bold; }
        .severity-low { color: #27ae60; font-weight: bold; }
        .recommendations {
            background: #e8f5e8;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }
        .recommendations ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        .timestamp {
            text-align: right;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">语义差异分析报告</h1>
        </div>
        
        <div class="meta-info">
            <strong>文件1:</strong> {file1}<br>
            <strong>文件2:</strong> {file2}<br>
            <strong>执行时间:</strong> {execution_time:.3f}秒<br>
            {cache_info}
        </div>
        
        <div class="similarity-score {score_class}">
            相似度: {similarity_score:.2%}
        </div>
        
        <div class="section">
            <h2 class="section-title">摘要</h2>
            <p>{summary}</p>
        </div>
        
        {differences_section}
        
        {recommendations_section}
        
        <div class="timestamp">
            生成时间: {timestamp}
        </div>
    </div>
</body>
</html>
        """
        
        # 确定相似度等级样式
        if result.similarity_score > 0.8:
            score_class = "score-high"
        elif result.similarity_score > 0.5:
            score_class = "score-medium"
        else:
            score_class = "score-low"
        
        # 缓存信息
        cache_info = "<strong>缓存命中:</strong> 是<br>" if result.cache_hit else ""
        
        # 差异部分
        if result.differences:
            diff_rows = []
            for i, diff in enumerate(result.differences, 1):
                severity_class = f"severity-{diff.severity}"
                diff_rows.append(f"""
                <tr>
                    <td>{i}</td>
                    <td>{html.escape(diff.description)}</td>
                    <td>{html.escape(diff.type)}</td>
                    <td class="{severity_class}">{html.escape(diff.severity)}</td>
                    <td>{html.escape(diff.category)}</td>
                    <td>{diff.confidence:.1%}</td>
                </tr>
                """)
            
            differences_section = f"""
            <div class="section">
                <h2 class="section-title">差异详情 ({len(result.differences)} 个)</h2>
                <table class="diff-table">
                    <thead>
                        <tr>
                            <th>序号</th>
                            <th>描述</th>
                            <th>类型</th>
                            <th>严重程度</th>
                            <th>分类</th>
                            <th>置信度</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(diff_rows)}
                    </tbody>
                </table>
            </div>
            """
        else:
            differences_section = """
            <div class="section">
                <h2 class="section-title">差异详情</h2>
                <p style="color: #27ae60; font-weight: bold;">未发现显著差异</p>
            </div>
            """
        
        # 建议部分
        if result.recommendations:
            rec_items = "\n".join(f"<li>{html.escape(rec)}</li>" 
                                 for rec in result.recommendations)
            recommendations_section = f"""
            <div class="section">
                <h2 class="section-title">建议</h2>
                <div class="recommendations">
                    <ul>
                        {rec_items}
                    </ul>
                </div>
            </div>
            """
        else:
            recommendations_section = ""
        
        # 填充模板
        return html_template.format(
            file1=html.escape(file1_name),
            file2=html.escape(file2_name),
            execution_time=result.execution_time,
            cache_info=cache_info,
            similarity_score=result.similarity_score,
            score_class=score_class,
            summary=html.escape(result.summary),
            differences_section=differences_section,
            recommendations_section=recommendations_section,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def format_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """
        格式化单文件分析结果
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            格式化后的输出
        """
        if self.format == "json":
            return json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        lines = []
        
        # 标题
        lines.append("=" * 60)
        lines.append("文件分析报告")
        lines.append("=" * 60)
        lines.append(f"文件路径: {analysis_result.get('file_path', 'Unknown')}")
        lines.append(f"编程语言: {analysis_result.get('language', 'Unknown')}")
        lines.append(f"代码行数: {analysis_result.get('lines_of_code', 0)}")
        lines.append(f"文件哈希: {analysis_result.get('code_hash', 'Unknown')[:16]}...")
        lines.append("")
        
        # 结构信息
        structure = analysis_result.get('structure')
        if structure:
            lines.append("代码结构:")
            lines.append("-" * 30)
            lines.append(f"函数数量: {len(structure.functions)}")
            lines.append(f"类数量: {len(structure.classes)}")
            lines.append(f"变量数量: {len(structure.variables)}")
            lines.append(f"导入数量: {len(structure.imports)}")
            lines.append(f"复杂度: {structure.complexity}")
            lines.append("")
            
            # 函数详情
            if structure.functions:
                lines.append("函数列表:")
                for func in structure.functions[:10]:  # 限制显示数量
                    params = ", ".join(func.parameters)
                    lines.append(f"  - {func.name}({params}) [行 {func.start_line}-{func.end_line}]")
                if len(structure.functions) > 10:
                    lines.append(f"  ... 还有 {len(structure.functions) - 10} 个函数")
                lines.append("")
            
            # 类详情
            if structure.classes:
                lines.append("类列表:")
                for cls in structure.classes[:5]:  # 限制显示数量
                    bases = ", ".join(cls.base_classes) if cls.base_classes else "无"
                    lines.append(f"  - {cls.name} (继承: {bases}) [行 {cls.start_line}-{cls.end_line}]")
                    lines.append(f"    方法数量: {len(cls.methods)}")
                if len(structure.classes) > 5:
                    lines.append(f"  ... 还有 {len(structure.classes) - 5} 个类")
                lines.append("")
        
        # AI特征分析
        features = analysis_result.get('features')
        if features and isinstance(features, dict):
            lines.append("AI特征分析:")
            lines.append("-" * 30)
            if 'analysis' in features:
                lines.append(features['analysis'])
            lines.append("")
        
        return "\n".join(lines)
    
    def format_directory_summary(self, results: Dict[str, SemanticAnalysisResult]) -> str:
        """
        格式化目录比较摘要
        
        Args:
            results: 目录比较结果
            
        Returns:
            格式化后的摘要
        """
        if not results:
            return "没有找到要比较的文件"
        
        # 统计信息
        total_files = len(results)
        total_differences = sum(len(r.differences) for r in results.values())
        avg_similarity = sum(r.similarity_score for r in results.values()) / total_files
        
        high_diff_files = [
            (path, len([d for d in result.differences if d.severity == 'high']))
            for path, result in results.items()
        ]
        high_diff_files = [(path, count) for path, count in high_diff_files if count > 0]
        high_diff_files.sort(key=lambda x: x[1], reverse=True)
        
        if self.format == "json":
            summary_data = {
                "total_files": total_files,
                "total_differences": total_differences,
                "average_similarity": avg_similarity,
                "high_severity_files": high_diff_files[:10],
                "file_results": {
                    path: {
                        "similarity_score": result.similarity_score,
                        "differences_count": len(result.differences),
                        "high_severity_count": len([d for d in result.differences if d.severity == 'high'])
                    }
                    for path, result in results.items()
                }
            }
            return json.dumps(summary_data, ensure_ascii=False, indent=2)
        
        lines = []
        lines.append("=" * 80)
        lines.append("目录比较摘要")
        lines.append("=" * 80)
        lines.append(f"总文件数: {total_files}")
        lines.append(f"总差异数: {total_differences}")
        lines.append(f"平均相似度: {avg_similarity:.2%}")
        lines.append("")
        
        if high_diff_files:
            lines.append("高严重程度差异的文件:")
            lines.append("-" * 40)
            for path, count in high_diff_files[:10]:
                lines.append(f"  {path}: {count} 个高严重程度差异")
            lines.append("")
        
        # 相似度分布
        score_ranges = [
            (0.9, 1.0, "非常相似"),
            (0.7, 0.9, "相当相似"),
            (0.5, 0.7, "部分相似"),
            (0.0, 0.5, "差异较大")
        ]
        
        lines.append("相似度分布:")
        lines.append("-" * 40)
        for min_score, max_score, label in score_ranges:
            count = sum(1 for r in results.values() 
                       if min_score <= r.similarity_score < max_score)
            percentage = count / total_files * 100 if total_files > 0 else 0
            lines.append(f"  {label} ({min_score:.1%}-{max_score:.1%}): {count} 文件 ({percentage:.1f}%)")
        
        return "\n".join(lines) 