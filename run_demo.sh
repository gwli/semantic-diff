#!/bin/bash

# Semantic Diff Tool 演示脚本

echo "=========================================="
echo "  Semantic Diff Tool 演示"
echo "=========================================="
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查项目目录
if [ ! -f "semantic_diff/__init__.py" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

echo "✓ Python环境检查通过"
echo "✓ 项目目录检查通过"
echo

# 设置Python路径
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "1. 运行Python演示脚本..."
echo "----------------------------------------"
python3 examples/demo.py
echo

echo "2. 运行测试套件..."
echo "----------------------------------------"
python3 tests/test_semantic_diff.py
echo

echo "3. 显示支持的语言..."
echo "----------------------------------------"
python3 -c "
from semantic_diff.utils.language_detector import LanguageDetector
detector = LanguageDetector()
languages = detector.get_supported_languages()
print('支持的编程语言:')
for i, lang in enumerate(languages, 1):
    print(f'  {i:2d}. {lang}')
print(f'\\n总计: {len(languages)} 种语言')
"
echo

echo "4. 显示配置信息..."
echo "----------------------------------------"
python3 -c "
from semantic_diff.utils.config_loader import ConfigLoader
loader = ConfigLoader()
config = loader.load_config()
print('默认配置:')
print(f'  模型名称: {config.model.name}')
print(f'  设备: {config.model.device}')
print(f'  输出格式: {config.output.format}')
print(f'  缓存启用: {config.performance.cache_enabled}')
print(f'  日志级别: {config.logging.level}')
"
echo

echo "=========================================="
echo "  演示完成"
echo "=========================================="
echo
echo "使用方法:"
echo "  # 比较两个文件"
echo "  python3 -m semantic_diff.cli.main compare file1.py file2.py"
echo
echo "  # 查看帮助"
echo "  python3 -m semantic_diff.cli.main --help"
echo
echo "  # 运行交互模式"
echo "  python3 -m semantic_diff.cli.main interactive" 