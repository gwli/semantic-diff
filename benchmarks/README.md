# Semantic Diff Benchmark Suite

这是一个全面的benchmark套件，用于测试和评估语义差异分析工具的性能、准确性和质量。

## 📁 目录结构

```
benchmarks/
├── benchmark_config.yaml      # 主配置文件
├── data/                      # 测试数据
│   ├── python/               # Python测试用例
│   ├── javascript/           # JavaScript测试用例
│   ├── java/                # Java测试用例
│   └── ...                  # 其他语言
├── scripts/                  # 核心脚本
│   ├── benchmark_runner.py   # 测试运行器
│   ├── metrics_analyzer.py   # 指标分析器
│   └── report_generator.py   # 报告生成器
├── results/                  # 测试结果
└── reports/                  # 生成的报告
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install psutil pandas matplotlib seaborn scipy
```

### 2. 运行基础测试

```bash
# 运行所有测试
python benchmarks/scripts/benchmark_runner.py

# 运行特定语言的测试
python benchmarks/scripts/benchmark_runner.py --language python

# 运行特定测试套件
python benchmarks/scripts/benchmark_runner.py --suite basic_changes

# 运行性能测试
python benchmarks/scripts/benchmark_runner.py --performance
```

### 3. 分析结果

```bash
# 分析最新的测试结果
python benchmarks/scripts/metrics_analyzer.py benchmarks/results/benchmark_results_YYYYMMDD_HHMMSS.json

# 生成报告
python benchmarks/scripts/report_generator.py benchmarks/results/benchmark_results_YYYYMMDD_HHMMSS.json
```

## 📊 测试套件

### 1. 基本变更测试 (basic_changes)
- **目的**: 测试基本代码变更的检测能力
- **类型**: 函数添加、删除、修改，变量变更，导入变更
- **支持语言**: Python, JavaScript, Java, C++, Go, Rust
- **复杂度**: 简单

### 2. 代码重构测试 (refactoring)
- **目的**: 测试重构识别和分析能力
- **类型**: 方法重命名、类提取、方法提取、参数变更
- **支持语言**: Python, JavaScript, Java
- **复杂度**: 中等

### 3. 功能开发测试 (feature_development)
- **目的**: 测试新功能开发的语义理解
- **类型**: 新类添加、API增强、算法优化
- **支持语言**: Python, JavaScript, Java
- **复杂度**: 复杂

### 4. Bug修复测试 (bug_fixes)
- **目的**: 测试bug修复的识别能力
- **类型**: 逻辑错误修复、空指针修复、边界条件修复
- **支持语言**: Python, JavaScript, Java, C++
- **复杂度**: 各种

### 5. 架构变更测试 (architectural_changes)
- **目的**: 测试大型架构变更的理解
- **类型**: MVC到MVP、单体到微服务、同步到异步
- **支持语言**: Python, JavaScript, Java
- **复杂度**: 高

## 📈 评估指标

### 性能指标
- **执行时间**: 平均、中位数、P95、P99、最大值
- **内存使用**: 平均、最大内存占用
- **CPU使用率**: 平均CPU占用百分比
- **缓存命中率**: 缓存使用效率
- **吞吐量**: 每秒处理的测试数

### 准确性指标
- **相似度分数**: 平均、中位数、标准差
- **语义分析成功率**: LLM分析成功的百分比
- **结构分析成功率**: AST分析成功的百分比
- **整体成功率**: 总体分析成功率
- **假阳性率**: 错误报告差异的估计比率
- **假阴性率**: 遗漏差异的估计比率
- **置信度分数**: 结果一致性和稳定性评分

### 质量指标
- **差异检测数量**: 平均检测到的差异数
- **检测一致性**: 差异检测的稳定性
- **解释完整性**: 分析解释的完整度
- **建议相关性**: 改进建议的相关性
- **错误率**: 总体错误百分比
- **超时率**: 超时错误百分比

## 🔧 配置说明

### 主要配置项

```yaml
# 测试套件配置
test_suites:
  - name: "basic_changes"
    languages: ["python", "javascript", "java"]
    categories: ["function_addition", "function_removal"]
    complexity: "simple"

# 性能测试配置
performance_tests:
  file_sizes:
    - name: "small"
      max_lines: 100
    - name: "large"
      max_lines: 2000

# 执行配置
execution:
  parallel: true
  max_workers: 4
  timeout_per_test: 120
```

### 环境变量

```bash
# 设置模型配置
export SEMANTIC_DIFF_MODEL_NAME="qwen3:4b"
export SEMANTIC_DIFF_TEMPERATURE="0.1"
export SEMANTIC_DIFF_MAX_LENGTH="2048"

# 设置输出配置
export SEMANTIC_DIFF_OUTPUT_FORMAT="rich"
export SEMANTIC_DIFF_LOG_LEVEL="INFO"
```

## 📋 使用示例

### 运行完整benchmark

```bash
# 1. 运行所有测试
python benchmarks/scripts/benchmark_runner.py --parallel --workers 4

# 2. 分析结果
python benchmarks/scripts/metrics_analyzer.py benchmarks/results/benchmark_results_20240101_120000.json

# 3. 生成HTML报告
python benchmarks/scripts/report_generator.py benchmarks/results/benchmark_results_20240101_120000.json --format html
```

### 运行特定测试

```bash
# 只测试Python的基本变更
python benchmarks/scripts/benchmark_runner.py --suite basic_changes --language python

# 运行重构测试并生成报告
python benchmarks/scripts/benchmark_runner.py --suite refactoring
python benchmarks/scripts/report_generator.py benchmarks/results/benchmark_results_latest.json
```

### 性能基准测试

```bash
# 运行性能测试
python benchmarks/scripts/benchmark_runner.py --performance

# 分析性能数据
python benchmarks/scripts/metrics_analyzer.py benchmarks/results/benchmark_results_perf.json
```

## 📊 报告格式

### HTML报告
- 交互式仪表板
- 性能图表和分析
- 语言对比分析
- 改进建议

### Markdown报告
- 适合文档集成
- 清晰的指标展示
- 易于版本控制

### JSON报告
- 机器可读格式
- 包含完整的原始数据
- 适合进一步分析

## 🛠 添加新测试用例

### 1. 创建测试文件

```bash
# 在对应目录创建测试对
touch benchmarks/data/python/basic_changes/new_feature_old.py
touch benchmarks/data/python/basic_changes/new_feature_new.py
```

### 2. 编写测试代码

```python
# new_feature_old.py
class SimpleClass:
    def method1(self):
        return "old"

# new_feature_new.py  
class SimpleClass:
    def method1(self):
        return "old"
    
    def method2(self):  # 新增方法
        return "new"
```

### 3. 运行测试

```bash
python benchmarks/scripts/benchmark_runner.py --suite basic_changes --language python
```

## 🎯 最佳实践

### 1. 测试设计
- **渐进复杂度**: 从简单到复杂的变更
- **真实场景**: 基于实际开发中的变更模式
- **语言特性**: 充分利用各语言的特色功能
- **边界情况**: 包含极端和特殊情况

### 2. 性能优化
- **并行执行**: 利用多核处理器
- **缓存策略**: 避免重复计算
- **内存管理**: 监控内存使用
- **超时控制**: 防止长时间运行

### 3. 结果分析
- **趋势监控**: 跟踪性能趋势
- **异常检测**: 识别异常结果
- **对比分析**: 不同版本间的对比
- **持续改进**: 基于结果进行优化

## 🔍 故障排除

### 常见问题

1. **内存不足**
   ```bash
   # 减少并发数
   python benchmarks/scripts/benchmark_runner.py --workers 2
   ```

2. **超时错误**
   ```yaml
   # 增加超时时间
   execution:
     timeout_per_test: 300
   ```

3. **模型加载失败**
   ```bash
   # 检查模型服务状态
   curl http://localhost:11434/api/tags
   ```

### 日志分析

```bash
# 查看详细日志
tail -f benchmarks/results/benchmark.log

# 过滤错误信息
grep "ERROR" benchmarks/results/benchmark.log
```

## 📞 支持和贡献

### 问题报告
如果遇到问题，请提供以下信息：
- 错误信息和堆栈跟踪
- 运行的具体命令
- 系统环境信息
- 配置文件内容

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 添加测试用例
4. 提交Pull Request

### 许可证
MIT License - 详见LICENSE文件

---

**Happy Benchmarking! 🚀** 