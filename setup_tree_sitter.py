#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tree-sitter语言库安装脚本
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 支持的语言和对应的git仓库
LANGUAGES = {
    'python': 'https://github.com/tree-sitter/tree-sitter-python.git',
    'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript.git', 
    'typescript': 'https://github.com/tree-sitter/tree-sitter-typescript.git',
    'java': 'https://github.com/tree-sitter/tree-sitter-java.git',
    'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp.git',
    'c': 'https://github.com/tree-sitter/tree-sitter-c.git',
    'rust': 'https://github.com/tree-sitter/tree-sitter-rust.git',
    'go': 'https://github.com/tree-sitter/tree-sitter-go.git',
}

def check_dependencies():
    """检查依赖"""
    try:
        import tree_sitter
        logger.info("tree-sitter Python包已安装")
        return True
    except ImportError:
        logger.error("tree-sitter Python包未安装，请先运行: pip install tree-sitter")
        return False

def setup_directories():
    """创建必要的目录"""
    base_dir = Path('.')
    
    # 创建目录
    langs_dir = base_dir / 'tree-sitter-langs'
    build_dir = base_dir / 'languages'
    
    langs_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    
    return langs_dir, build_dir

def clone_language_repo(language, repo_url, langs_dir):
    """克隆语言仓库"""
    lang_dir = langs_dir / f'tree-sitter-{language}'
    
    if lang_dir.exists():
        logger.info(f"{language}语言仓库已存在，跳过克隆")
        return lang_dir
    
    try:
        logger.info(f"正在克隆{language}语言仓库...")
        subprocess.run(['git', 'clone', repo_url, str(lang_dir)], 
                      check=True, capture_output=True)
        logger.info(f"{language}语言仓库克隆成功")
        return lang_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"克隆{language}语言仓库失败: {e}")
        return None

def compile_language_library(language, lang_dir, build_dir):
    """编译语言库"""
    try:
        from tree_sitter import Language
        
        # 对于特殊的语言，需要指定子目录
        if language == 'typescript':
            # TypeScript有两个子项目
            typescript_dir = lang_dir / 'typescript'
            tsx_dir = lang_dir / 'tsx'
            
            if typescript_dir.exists():
                Language.build_library(
                    str(build_dir / f'{language}.so'),
                    [str(typescript_dir)]
                )
                logger.info(f"{language}语言库编译成功")
                return True
        else:
            # 大多数语言直接编译
            Language.build_library(
                str(build_dir / f'{language}.so'),
                [str(lang_dir)]
            )
            logger.info(f"{language}语言库编译成功")
            return True
            
    except Exception as e:
        logger.error(f"编译{language}语言库失败: {e}")
        return False

def install_language_libraries():
    """安装语言库"""
    if not check_dependencies():
        return False
    
    langs_dir, build_dir = setup_directories()
    
    success_count = 0
    
    for language, repo_url in LANGUAGES.items():
        logger.info(f"正在处理{language}语言...")
        
        # 克隆仓库
        lang_dir = clone_language_repo(language, repo_url, langs_dir)
        if not lang_dir:
            continue
        
        # 编译库
        if compile_language_library(language, lang_dir, build_dir):
            success_count += 1
    
    logger.info(f"成功编译{success_count}/{len(LANGUAGES)}个语言库")
    
    # 清理临时文件
    if langs_dir.exists():
        try:
            shutil.rmtree(langs_dir)
            logger.info("清理临时文件成功")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
    
    return success_count > 0

def verify_installation():
    """验证安装"""
    build_dir = Path('languages')
    
    if not build_dir.exists():
        logger.error("语言库目录不存在")
        return False
    
    success_count = 0
    
    for language in LANGUAGES.keys():
        lib_file = build_dir / f'{language}.so'
        if lib_file.exists():
            logger.info(f"✓ {language}语言库已安装")
            success_count += 1
        else:
            logger.warning(f"✗ {language}语言库未找到")
    
    logger.info(f"验证完成: {success_count}/{len(LANGUAGES)}个语言库可用")
    return success_count > 0

def main():
    """主函数"""
    logger.info("开始安装Tree-sitter语言库...")
    
    try:
        if install_language_libraries():
            logger.info("语言库安装完成")
            
            if verify_installation():
                logger.info("验证通过，所有语言库已就绪")
                return 0
            else:
                logger.warning("验证失败，某些语言库可能不可用")
                return 1
        else:
            logger.error("语言库安装失败")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断安装")
        return 1
    except Exception as e:
        logger.error(f"安装过程发生错误: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 