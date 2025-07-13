# Semantic Diff Tool - 基于Qwen3-4B的语义理解DIFF工具

一个能够理解代码语义的智能diff工具，而不仅仅是简单的文本比较。基于Qwen3-4B大语言模型，结合代码结构分析，提供深入的语义差异分析。

## ✨ 特性

- 🧠 **语义理解**: 基于Qwen3-4B模型的深度语义分析
- 🔍 **多语言支持**: 支持Python、JavaScript、Java、C++等多种编程语言
- 📊 **智能分析**: 区分语义差异和格式差异，提供有意义的比较结果
- 🎨 **多种输出格式**: 支持纯文本、Rich、JSON、HTML等输出格式
- ⚡ **高性能**: 缓存机制和并行处理，提升分析速度
- 🛠️ **灵活配置**: 可配置的分析深度和忽略规则
- 📁 **目录比较**: 支持整个项目目录的批量比较

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/semantic-diff.git
cd semantic-diff

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

### 基本使用

```bash
# 比较两个文件
semantic-diff compare file1.py file2.py

# 比较两个目录
semantic-diff compare-dirs project_v1/ project_v2/

# 分析单个文件
semantic-diff analyze myfile.py

# 交互式模式
semantic-diff interactive

# 查看配置
semantic-diff config

# 查看支持的语言
semantic-diff languages
```

## 📖 使用示例

### 文件比较

```bash
# 基本比较
semantic-diff compare old_version.py new_version.py

# 指定输出格式
semantic-diff compare -f json old_version.py new_version.py

# 保存结果到文件
semantic-diff compare -o result.html -f html old_version.py new_version.py

# 指定编程语言
semantic-diff compare -l python script1.txt script2.txt
```

### 目录比较

```bash
# 递归比较目录
semantic-diff compare-dirs src_old/ src_new/

# 只比较特定扩展名的文件
semantic-diff compare-dirs -e .py -e .js project1/ project2/

# 生成摘要报告
semantic-diff compare-dirs --summary-only project1/ project2/
```

### Python API

```python
from semantic_diff import SemanticDiff

# 初始化工具
with SemanticDiff() as diff_tool:
    # 比较两个文件
    result = diff_tool.compare_files("file1.py", "file2.py")
    
    print(f"相似度: {result.similarity_score:.2%}")
    print(f"发现 {len(result.differences)} 个差异")
    
    # 比较代码片段
    code1 = """
    def hello(name):
        return f"Hello, {name}!"
    """
    
    code2 = """
    def greet(username):
        return f"Hello, {username}!"
    """
    
    result = diff_tool.compare_code(code1, code2, "python")
    print(result.summary)
```

## 🔧 配置

工具支持通过配置文件自定义行为：

```yaml
# config.yaml
model:
  name: "Qwen/Qwen-VL-Chat"  # 模型路径
  device: "auto"
  temperature: 0.1

semantic_analysis:
  depth: "medium"  # shallow, medium, deep
  ignore_differences:
    - "whitespace"
    - "comments_only"
    - "variable_rename"

output:
  format: "rich"
  show_line_numbers: true
  context_lines: 3

performance:
  cache_enabled: true
  max_workers: 4
```

## 🎯 工作原理

### 1. 代码解析
使用Tree-sitter解析代码结构，提取：
- 函数和类定义
- 变量声明和使用
- 控制流结构
- 导入依赖

### 2. 语义分析
利用Qwen3-4B模型进行：
- 功能语义理解
- 代码意图分析
- 重构模式识别
- 影响评估

### 3. 智能比较
结合结构和语义分析：
- 识别真正的功能变化
- 忽略无关紧要的格式差异
- 提供置信度评分
- 生成人类可读的解释

## 📊 输出格式

### Rich格式（默认）
彩色终端输出，包含表格和面板展示

### JSON格式
结构化数据，便于程序处理：
```json
{
  "similarity_score": 0.85,
  "differences": [
    {
      "type": "functional",
      "severity": "medium",
      "description": "函数名从 hello 改为 greet",
      "confidence": 0.9
    }
  ],
  "recommendations": ["这是一个简单的重命名，功能保持不变"]
}
```

### HTML格式
美观的网页报告，便于分享和存档

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_semantic_diff.py

# 生成覆盖率报告
pytest --cov=semantic_diff tests/
```

## 🤝 支持的语言

- Python (.py)
- JavaScript (.js, .mjs, .jsx)
- TypeScript (.ts, .tsx)
- Java (.java)
- C++ (.cpp, .cxx, .cc)
- C (.c, .h)
- Rust (.rs)
- Go (.go)
- 还有更多...

## ⚙️ 系统要求

- Python 3.8+
- 内存: 建议4GB+（用于模型加载）
- 显卡: 可选，支持CUDA加速

## 🔗 相关链接

- [Qwen模型](https://github.com/QwenLM/Qwen)
- [Tree-sitter](https://tree-sitter.github.io/)
- [Rich](https://github.com/Textualize/rich)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目。

## ❓ 常见问题

### Q: 工具需要网络连接吗？
A: 首次下载模型需要网络，之后可离线使用。

### Q: 支持自定义模型吗？
A: 是的，可以通过配置文件指定本地模型路径。

### Q: 内存使用量大吗？
A: 模型加载需要约2-4GB内存，分析过程中内存使用较少。

### Q: 可以比较二进制文件吗？
A: 目前只支持文本文件，二进制文件比较在计划中。

## 📈 路线图

- [ ] 支持更多编程语言
- [ ] 二进制文件差异分析
- [ ] Git集成
- [ ] Web界面
- [ ] 插件系统
- [ ] 性能优化

---

如果这个工具对您有帮助，请给个⭐️ Star！

有问题或建议？请[提交Issue](https://github.com/yourusername/semantic-diff/issues)。 