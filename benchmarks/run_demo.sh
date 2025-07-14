#!/bin/bash

# Semantic Diff Benchmark Demo Script
# 演示如何运行benchmark测试

set -e

echo "🚀 Semantic Diff Benchmark Demo"
echo "================================"

# 检查Python和依赖
echo "📋 检查环境..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3 已安装"

# 检查依赖包
echo "📦 检查依赖包..."
python3 -c "import psutil, pandas, matplotlib, seaborn, scipy" 2>/dev/null && echo "✅ 依赖包已安装" || {
    echo "⚠️  正在安装依赖包..."
    pip install psutil pandas matplotlib seaborn scipy
}

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p benchmarks/{results,reports,temp}

# 检查测试数据
echo "🔍 检查测试数据..."
test_count=$(find benchmarks/data -name "*_old.*" 2>/dev/null | wc -l)
if [ $test_count -gt 0 ]; then
    echo "✅ 发现 $test_count 个测试用例"
else
    echo "⚠️  未发现测试用例，将只运行性能测试"
fi

# 运行演示测试
echo ""
echo "🎯 运行演示测试..."
echo "=================="

# 1. 运行小规模测试
echo "1️⃣  运行Python基本变更测试（如果有数据）..."
if [ $test_count -gt 0 ]; then
    python3 benchmarks/scripts/benchmark_runner.py \
        --suite basic_changes \
        --language python \
        --workers 1 \
        2>/dev/null || echo "⚠️  测试运行遇到问题，继续..."
else
    echo "   跳过（无测试数据）"
fi

# 2. 运行性能测试
echo ""
echo "2️⃣  运行性能基准测试..."
python3 benchmarks/scripts/benchmark_runner.py \
    --performance \
    2>/dev/null || echo "⚠️  性能测试运行遇到问题，继续..."

# 3. 查找最新结果文件
echo ""
echo "3️⃣  查找测试结果..."
latest_result=$(ls -t benchmarks/results/benchmark_results_*.json 2>/dev/null | head -1)

if [ -n "$latest_result" ]; then
    echo "✅ 找到结果文件: $latest_result"
    
    # 4. 分析结果
    echo ""
    echo "4️⃣  分析测试结果..."
    python3 benchmarks/scripts/metrics_analyzer.py "$latest_result" 2>/dev/null || {
        echo "⚠️  分析过程遇到问题，但结果文件已生成"
    }
    
    # 5. 生成报告
    echo ""
    echo "5️⃣  生成HTML报告..."
    python3 benchmarks/scripts/report_generator.py "$latest_result" --format html 2>/dev/null || {
        echo "⚠️  报告生成遇到问题，但可以手动运行"
    }
    
    # 查找生成的报告
    run_id=$(basename "$latest_result" .json | sed 's/benchmark_results_//')
    report_file="benchmarks/reports/$run_id/benchmark_report.html"
    
    if [ -f "$report_file" ]; then
        echo "✅ HTML报告已生成: $report_file"
    fi
    
else
    echo "❌ 未找到测试结果文件"
fi

echo ""
echo "📊 演示完成!"
echo "============"

# 显示结果摘要
if [ -n "$latest_result" ]; then
    echo ""
    echo "📋 结果摘要:"
    echo "  结果文件: $latest_result"
    
    if [ -f "$report_file" ]; then
        echo "  HTML报告: $report_file"
        echo ""
        echo "💡 提示:"
        echo "  - 在浏览器中打开HTML报告查看详细结果"
        echo "  - 使用以下命令运行完整测试:"
        echo "    python3 benchmarks/scripts/benchmark_runner.py"
    fi
else
    echo ""
    echo "💡 提示:"
    echo "  - 添加更多测试数据到 benchmarks/data/ 目录"
    echo "  - 确保LLM服务正在运行 (ollama)"
    echo "  - 查看 benchmarks/README.md 获取详细使用说明"
fi

echo ""
echo "🎉 感谢使用 Semantic Diff Benchmark!" 