#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Semantic Diff Tool 演示脚本

这个脚本演示了如何使用语义diff工具来比较代码文件。
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from semantic_diff import SemanticDiff


def run_cli_demo():
    """演示命令行工具的使用"""
    print("=" * 60)
    print("命令行工具演示")
    print("=" * 60)
    
    examples_dir = Path(__file__).parent
    old_file = examples_dir / "sample_code_old.py"
    new_file = examples_dir / "sample_code_new.py"
    
    if not old_file.exists() or not new_file.exists():
        print("示例文件不存在，请先确保示例文件已创建")
        return
    
    print(f"比较文件:")
    print(f"  旧版本: {old_file}")
    print(f"  新版本: {new_file}")
    print()
    
    # 执行命令行比较
    try:
        # 注意：这里假设semantic-diff命令已经安装
        cmd = [
            sys.executable, "-m", "semantic_diff.cli.main", 
            "compare", str(old_file), str(new_file),
            "--format", "plain"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print("CLI输出:")
            print(result.stdout)
        else:
            print("CLI执行失败:")
            print(result.stderr)
            
    except Exception as e:
        print(f"执行CLI命令时发生错误: {e}")
        print("尝试直接使用Python API...")
        run_api_demo()


def run_api_demo():
    """演示Python API的使用"""
    print("=" * 60)
    print("Python API 演示")
    print("=" * 60)
    
    examples_dir = Path(__file__).parent
    old_file = examples_dir / "sample_code_old.py"
    new_file = examples_dir / "sample_code_new.py"
    
    if not old_file.exists() or not new_file.exists():
        print("示例文件不存在，跳过API演示")
        return
    
    try:
        # 使用语义diff工具
        print("正在初始化语义diff工具...")
        
        # 注意：由于没有实际的Qwen模型，这里会使用模拟模式
        with SemanticDiff() as diff_tool:
            print("工具初始化成功")
            
            print(f"比较文件:")
            print(f"  旧版本: {old_file}")
            print(f"  新版本: {new_file}")
            print()
            
            print("正在执行语义分析...")
            result = diff_tool.compare_files(str(old_file), str(new_file))
            
            print("分析完成！")
            print()
            
            # 显示结果
            print(f"相似度评分: {result.similarity_score:.2%}")
            print(f"发现差异数量: {len(result.differences)}")
            print(f"分析耗时: {result.execution_time:.3f}秒")
            print()
            
            print("差异摘要:")
            print(result.summary)
            print()
            
            if result.differences:
                print("详细差异:")
                for i, diff in enumerate(result.differences[:5], 1):  # 只显示前5个差异
                    print(f"{i}. {diff.description}")
                    print(f"   类型: {diff.type} | 严重程度: {diff.severity} | 置信度: {diff.confidence:.1%}")
                    print()
                
                if len(result.differences) > 5:
                    print(f"... 还有 {len(result.differences) - 5} 个差异")
                    print()
            
            if result.recommendations:
                print("建议:")
                for i, rec in enumerate(result.recommendations, 1):
                    print(f"{i}. {rec}")
                print()
            
            # 获取统计信息
            stats = diff_tool.get_statistics()
            print("工具统计:")
            print(f"  总比较文件数: {stats.get('files_compared', 0)}")
            print(f"  缓存命中次数: {stats.get('cache_hits', 0)}")
            
    except Exception as e:
        print(f"API演示发生错误: {e}")
        print("这可能是因为没有安装Qwen模型或相关依赖")
        run_mock_demo()


def run_mock_demo():
    """运行模拟演示，不依赖实际模型"""
    print("=" * 60)
    print("模拟演示（无需模型）")
    print("=" * 60)
    
    # 读取示例文件内容
    examples_dir = Path(__file__).parent
    old_file = examples_dir / "sample_code_old.py"
    new_file = examples_dir / "sample_code_new.py"
    
    if old_file.exists() and new_file.exists():
        with open(old_file, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        with open(new_file, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        print("文件内容分析:")
        print(f"旧文件行数: {len(old_content.splitlines())}")
        print(f"新文件行数: {len(new_content.splitlines())}")
        print()
        
        # 简单的文本差异分析
        old_lines = set(old_content.splitlines())
        new_lines = set(new_content.splitlines())
        
        added_lines = new_lines - old_lines
        removed_lines = old_lines - new_lines
        
        print(f"新增行数: {len(added_lines)}")
        print(f"删除行数: {len(removed_lines)}")
        print(f"文本相似度: {len(old_lines & new_lines) / len(old_lines | new_lines):.2%}")
        print()
        
        print("主要变化（基于文本分析）:")
        print("- 类名从 Calculator 改为 AdvancedCalculator")
        print("- 增加了类型注解和详细文档")
        print("- 新增了日志功能")
        print("- 增加了阶乘和百分比计算功能")
        print("- 重命名了一些方法名")
        print("- 改进了错误处理")
        
    else:
        print("示例文件不存在，无法进行演示")


def create_sample_comparison():
    """创建一个简单的代码比较示例"""
    print("=" * 60)
    print("创建简单比较示例")
    print("=" * 60)
    
    # 创建两个简单的代码片段进行比较
    code1 = '''
def calculate_area(radius):
    """计算圆的面积"""
    pi = 3.14159
    area = pi * radius * radius
    return area

def main():
    r = 5
    result = calculate_area(r)
    print(f"半径为 {r} 的圆面积是: {result}")
'''
    
    code2 = '''
import math

def compute_circle_area(r):
    """计算圆形区域的面积"""
    return math.pi * r ** 2

def main():
    radius = 5
    area = compute_circle_area(radius)
    print(f"半径为 {radius} 的圆面积是: {area:.2f}")
'''
    
    print("代码片段1:")
    print(code1)
    print("\n" + "=" * 40 + "\n")
    print("代码片段2:")
    print(code2)
    print("\n" + "=" * 40 + "\n")
    
    print("主要差异分析:")
    print("1. 函数名变化: calculate_area → compute_circle_area")
    print("2. 参数名变化: radius → r")
    print("3. 实现方式: 自定义pi值 → 使用math.pi")
    print("4. 计算方式: 连乘 → 使用幂运算")
    print("5. 输出格式: 无格式化 → 保留2位小数")
    print("6. 导入依赖: 无 → import math")
    
    print("\n语义分析:")
    print("✓ 核心功能保持一致（计算圆面积）")
    print("✓ 改进了代码质量（使用标准库）")
    print("✓ 提高了精度（math.pi vs 3.14159）")
    print("✓ 改善了用户体验（格式化输出）")
    print("→ 总体评价: 这是一次积极的重构")


def main():
    """主函数"""
    print("Semantic Diff Tool 演示")
    print("=" * 60)
    print()
    
    print("本演示将展示语义diff工具的各种使用方式:")
    print("1. 命令行工具使用")
    print("2. Python API使用")
    print("3. 模拟演示")
    print("4. 简单比较示例")
    print()
    
    # 检查示例文件是否存在
    examples_dir = Path(__file__).parent
    old_file = examples_dir / "sample_code_old.py"
    new_file = examples_dir / "sample_code_new.py"
    
    if old_file.exists() and new_file.exists():
        print("✓ 示例文件已准备就绪")
    else:
        print("⚠ 示例文件缺失，部分演示可能无法运行")
    
    print()
    
    try:
        # 运行各种演示
        run_cli_demo()
        print("\n")
        
        run_api_demo()
        print("\n")
        
        create_sample_comparison()
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    
    print("\n演示结束。感谢使用Semantic Diff Tool！")


if __name__ == "__main__":
    main() 