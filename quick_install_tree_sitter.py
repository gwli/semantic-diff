#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速安装Tree-sitter Python语言库
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

def install_python_parser():
    """安装Python语言解析器"""
    print("正在安装Tree-sitter Python解析器...")
    
    try:
        # 检查是否已安装tree-sitter
        import tree_sitter
        print("✓ tree-sitter Python包已安装")
    except ImportError:
        print("❌ tree-sitter Python包未安装")
        print("请先运行: pip install tree-sitter")
        return False
    
    # 创建语言库目录
    lang_dir = Path("languages")
    lang_dir.mkdir(exist_ok=True)
    
    # 检查是否已存在
    python_lib = lang_dir / "python.so"
    if python_lib.exists():
        print("✓ Python语言库已存在")
        return True
    
    try:
        from tree_sitter import Language
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            print("正在下载tree-sitter-python...")
            
            # 克隆Python语言仓库
            subprocess.run([
                'git', 'clone', 
                'https://github.com/tree-sitter/tree-sitter-python.git',
                str(temp_path / 'tree-sitter-python')
            ], check=True, capture_output=True)
            
            print("正在编译Python语言库...")
            
            # 编译语言库
            Language.build_library(
                str(python_lib),
                [str(temp_path / 'tree-sitter-python')]
            )
            
            print("✓ Python语言库安装成功")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git克隆失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译失败: {e}")
        return False

def main():
    """主函数"""
    print("Tree-sitter Python语言库快速安装工具")
    print("=" * 40)
    
    if install_python_parser():
        print("\n🎉 安装完成！")
        print("现在可以运行语义差异分析工具了。")
        return 0
    else:
        print("\n❌ 安装失败")
        print("请检查网络连接和依赖环境。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 