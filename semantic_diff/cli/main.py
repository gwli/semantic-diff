#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command line interface for semantic diff tool.
"""

import sys
import os
import click
import json
from pathlib import Path
from typing import Optional, List

# 使用相对导入
from ..core.semantic_diff import SemanticDiff
from ..utils.formatter import DiffFormatter
from ..utils.config_loader import ConfigLoader


@click.group()
@click.version_option(version='0.1.0')
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--quiet', '-q', is_flag=True, help='静默模式')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), 
              help='日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.pass_context
def cli(ctx, config, verbose, quiet, log_level):
    """
    基于Qwen3-4B的语义理解DIFF工具
    
    一个能够理解代码语义的智能diff工具，而不仅仅是简单的文本比较。
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    ctx.obj['log_level'] = log_level


@cli.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--language', '-l', help='指定编程语言')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['plain', 'rich', 'json', 'html']), 
              default='rich', help='输出格式')
@click.option('--no-color', is_flag=True, help='禁用颜色输出')
@click.option('--context', '-C', type=int, default=3, help='上下文行数')
@click.pass_context
def compare(ctx, file1, file2, language, output, format, no_color, context):
    """
    比较两个文件的语义差异
    
    FILE1: 第一个文件路径
    FILE2: 第二个文件路径
    """
    try:
        # 初始化工具
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            if not ctx.obj['quiet']:
                click.echo(f"正在比较文件: {file1} 和 {file2}")
            
            # 执行比较
            result = diff_tool.compare_files(file1, file2, language)
            
            # 格式化输出
            formatter = DiffFormatter(
                format=format,
                no_color=no_color,
                context_lines=context
            )
            
            formatted_output = formatter.format_result(result, file1, file2)
            
            # 输出结果
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                if not ctx.obj['quiet']:
                    click.echo(f"结果已保存到: {output}")
            else:
                click.echo(formatted_output)
            
            # 显示摘要
            if not ctx.obj['quiet']:
                click.echo(f"\n分析完成！相似度: {result.similarity_score:.2%}")
                click.echo(f"发现 {len(result.differences)} 个差异")
                if result.cache_hit:
                    click.echo("(使用了缓存结果)")
                    
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('dir1', type=click.Path(exists=True, file_okay=False))
@click.argument('dir2', type=click.Path(exists=True, file_okay=False))
@click.option('--recursive', '-r', is_flag=True, default=True, help='递归比较子目录')
@click.option('--extensions', '-e', multiple=True, help='文件扩展名过滤')
@click.option('--output', '-o', type=click.Path(), help='输出目录')
@click.option('--format', '-f', type=click.Choice(['plain', 'rich', 'json', 'html']), 
              default='rich', help='输出格式')
@click.option('--summary-only', is_flag=True, help='只显示摘要')
@click.pass_context
def compare_dirs(ctx, dir1, dir2, recursive, extensions, output, format, summary_only):
    """
    比较两个目录中的文件
    
    DIR1: 第一个目录路径
    DIR2: 第二个目录路径
    """
    try:
        # 初始化工具
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            if not ctx.obj['quiet']:
                click.echo(f"正在比较目录: {dir1} 和 {dir2}")
            
            # 处理扩展名过滤
            file_extensions = list(extensions) if extensions else None
            
            # 执行比较
            results = diff_tool.compare_directories(
                dir1, dir2, recursive, file_extensions
            )
            
            # 格式化输出
            formatter = DiffFormatter(format=format)
            
            if summary_only:
                # 生成摘要
                summary = formatter.format_directory_summary(results)
                click.echo(summary)
            else:
                # 详细输出
                for file_path, result in results.items():
                    if not ctx.obj['quiet']:
                        click.echo(f"\n{'='*60}")
                        click.echo(f"文件: {file_path}")
                        click.echo(f"{'='*60}")
                    
                    formatted_output = formatter.format_result(
                        result, 
                        os.path.join(dir1, file_path), 
                        os.path.join(dir2, file_path)
                    )
                    
                    if output:
                        # 保存到输出目录
                        os.makedirs(output, exist_ok=True)
                        output_file = os.path.join(output, f"{file_path}.diff")
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(formatted_output)
                    else:
                        click.echo(formatted_output)
            
            # 显示总体统计
            if not ctx.obj['quiet']:
                total_files = len(results)
                high_diff_count = sum(1 for r in results.values() 
                                    if len([d for d in r.differences if d.severity == 'high']) > 0)
                avg_similarity = sum(r.similarity_score for r in results.values()) / total_files if total_files > 0 else 0
                
                click.echo(f"\n总计比较了 {total_files} 个文件")
                click.echo(f"平均相似度: {avg_similarity:.2%}")
                click.echo(f"高严重程度差异的文件数: {high_diff_count}")
                
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--language', '-l', help='指定编程语言')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['plain', 'rich', 'json', 'html']), 
              default='rich', help='输出格式')
@click.pass_context
def analyze(ctx, file, language, output, format):
    """
    分析单个文件的结构和语义
    
    FILE: 要分析的文件路径
    """
    try:
        # 初始化工具
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            if not ctx.obj['quiet']:
                click.echo(f"正在分析文件: {file}")
            
            # 执行分析
            result = diff_tool.analyze_single_file(file, language)
            
            # 格式化输出
            formatter = DiffFormatter(format=format)
            formatted_output = formatter.format_analysis(result)
            
            # 输出结果
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                if not ctx.obj['quiet']:
                    click.echo(f"结果已保存到: {output}")
            else:
                click.echo(formatted_output)
                
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--language', '-l', help='指定编程语言')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['plain', 'rich', 'json', 'html']), 
              default='rich', help='输出格式')
@click.pass_context
def interactive(ctx, language, output, format):
    """
    交互式代码比较模式
    """
    try:
        # 初始化工具
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            click.echo("欢迎使用语义diff工具的交互模式!")
            click.echo("请输入两段代码进行比较。输入 'END' 结束输入。")
            
            # 获取第一段代码
            click.echo("\n请输入第一段代码:")
            code1_lines = []
            while True:
                line = click.prompt("", default="", show_default=False)
                if line.upper() == 'END':
                    break
                code1_lines.append(line)
            code1 = '\n'.join(code1_lines)
            
            # 获取第二段代码
            click.echo("\n请输入第二段代码:")
            code2_lines = []
            while True:
                line = click.prompt("", default="", show_default=False)
                if line.upper() == 'END':
                    break
                code2_lines.append(line)
            code2 = '\n'.join(code2_lines)
            
            # 获取语言（如果未指定）
            if not language:
                language = click.prompt("请指定编程语言", default="python")
            
            # 执行比较
            click.echo("\n正在分析...")
            result = diff_tool.compare_code(code1, code2, language)
            
            # 格式化输出
            formatter = DiffFormatter(format=format)
            formatted_output = formatter.format_result(result, "代码1", "代码2")
            
            # 输出结果
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                click.echo(f"结果已保存到: {output}")
            else:
                click.echo(formatted_output)
                
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx):
    """
    显示当前配置信息
    """
    try:
        config_loader = ConfigLoader(ctx.obj['config'])
        config = config_loader.load_config()
        
        click.echo("当前配置:")
        click.echo(f"  模型名称: {config.model.name}")
        click.echo(f"  设备: {config.model.device}")
        click.echo(f"  最大长度: {config.model.max_length}")
        click.echo(f"  温度: {config.model.temperature}")
        click.echo(f"  支持的语言: {', '.join(config.supported_languages)}")
        click.echo(f"  输出格式: {config.output.format}")
        click.echo(f"  缓存启用: {config.performance.cache_enabled}")
        click.echo(f"  最大工作线程: {config.performance.max_workers}")
        click.echo(f"  日志级别: {config.logging.level}")
        
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def languages(ctx):
    """
    显示支持的编程语言
    """
    try:
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            supported_languages = diff_tool.get_supported_languages()
            
            click.echo("支持的编程语言:")
            for i, lang in enumerate(supported_languages, 1):
                click.echo(f"  {i:2d}. {lang}")
                
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx):
    """
    显示使用统计信息
    """
    try:
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            statistics = diff_tool.get_statistics()
            
            click.echo("使用统计:")
            click.echo(f"  比较的文件数: {statistics.get('files_compared', 0)}")
            click.echo(f"  比较的代码片段数: {statistics.get('code_snippets_compared', 0)}")
            click.echo(f"  总分析时间: {statistics.get('total_analysis_time', 0):.2f} 秒")
            click.echo(f"  缓存命中数: {statistics.get('cache_hits', 0)}")
            click.echo(f"  错误数: {statistics.get('errors', 0)}")
            
            if statistics.get('files_compared', 0) > 0:
                click.echo(f"  平均分析时间: {statistics.get('avg_file_analysis_time', 0):.2f} 秒/文件")
            
            if 'cache_hit_rate' in statistics:
                click.echo(f"  缓存命中率: {statistics['cache_hit_rate']:.2%}")
                
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def clear_cache(ctx):
    """
    清除缓存
    """
    try:
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            diff_tool.clear_cache()
            click.echo("缓存已清除")
            
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def warmup(ctx):
    """
    预热系统（加载模型）
    """
    try:
        with SemanticDiff(ctx.obj['config'], log_level=ctx.obj['log_level']) as diff_tool:
            click.echo("正在预热系统...")
            diff_tool.warm_up()
            click.echo("系统预热完成")
            
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('output_path', type=click.Path())
@click.pass_context
def export_config(ctx, output_path):
    """
    导出当前配置到文件
    
    OUTPUT_PATH: 输出配置文件路径
    """
    try:
        config_loader = ConfigLoader(ctx.obj['config'])
        config_loader.save_config(output_path)
        click.echo(f"配置已导出到: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


def main():
    """主入口点"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        click.echo(f"未知错误: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 