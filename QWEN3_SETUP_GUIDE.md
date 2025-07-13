# Qwen3-4B 模型安装和配置指南

本指南将帮助您配置语义差异工具使用 Qwen3-4B 模型。

## 📋 前提条件

- Linux 系统
- Python 3.8+
- 4GB+ 可用内存
- 网络连接良好

## 🚀 快速安装

### 步骤 1: 安装 Ollama

```bash
# 下载并安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama 服务
sudo systemctl start ollama
sudo systemctl enable ollama

# 验证安装
ollama --version
```

### 步骤 2: 下载 Qwen3-4B 模型

```bash
# 下载模型（这可能需要一些时间）
ollama pull qwen3:4b

# 验证模型下载
ollama list
```

### 步骤 3: 测试模型

```bash
# 简单测试
ollama run qwen3:4b "你好，请介绍一下自己"
```

## ⚙️ 配置语义差异工具

### 更新配置文件

确保 `config.yaml` 配置正确：

```yaml
# 模型配置
model:
  # 模型类型: transformers, ollama, vllm
  type: "ollama"
  
  # 模型名称
  name: "qwen3:4b"  # ollama中的Qwen3-4B模型名称
  
  # API配置 (仅对 ollama 和 vllm 有效)
  api:
    base_url: "http://localhost:11434"  # ollama默认端口
    timeout: 30
    
  # 生成参数
  generation:
    max_length: 2048
    temperature: 0.1
    top_p: 0.9
```

### 测试配置

```bash
# 运行测试脚本
python3 test_qwen_api.py

# 或运行演示
./run_demo.sh
```

## 🔧 故障排除

### 问题 1: Ollama 服务无法启动

```bash
# 检查服务状态
sudo systemctl status ollama

# 重启服务
sudo systemctl restart ollama

# 查看日志
sudo journalctl -u ollama -f
```

### 问题 2: 模型下载失败

```bash
# 检查网络连接
ping ollama.com

# 尝试重新下载
ollama rm qwen3:4b
ollama pull qwen3:4b
```

### 问题 3: API 连接失败

```bash
# 检查端口是否开放
netstat -tlnp | grep 11434

# 测试 API 连接
curl http://localhost:11434/api/tags
```

### 问题 4: 权限问题

```bash
# 添加用户到 ollama 组
sudo usermod -a -G ollama $USER

# 重新登录或刷新组权限
newgrp ollama
```

## 📊 性能优化

### GPU 加速（如果可用）

```bash
# 检查 NVIDIA GPU
nvidia-smi

# Ollama 会自动使用 GPU（如果可用）
# 检查 GPU 使用情况
nvidia-smi -l 1
```

### 内存优化

如果系统内存不足，可以：

1. 使用更小的模型：
   ```bash
   ollama pull qwen3:1.5b
   ```
   然后更新配置文件中的模型名称。

2. 调整生成参数：
   ```yaml
   generation:
     max_length: 1024  # 减少最大长度
   ```

## 🎯 使用示例

### 基本命令行使用

```bash
# 比较两个文件
python3 -m semantic_diff.cli.main compare examples/sample_code_old.py examples/sample_code_new.py

# 交互模式
python3 -m semantic_diff.cli.main interactive

# 查看帮助
python3 -m semantic_diff.cli.main --help
```

### Python API 使用

```python
from semantic_diff import SemanticDiff

# 初始化
diff_tool = SemanticDiff()

# 比较代码
code1 = "def hello(): return 'Hello'"
code2 = "def greet(): return 'Hi'"

result = diff_tool.compare_code(code1, code2, "python")
print(f"相似度: {result.similarity_score}")
print(f"差异: {len(result.differences)}")

# 关闭
diff_tool.shutdown()
```

## 🔄 VLLM 替代方案

如果您更喜欢使用 VLLM：

1. 安装 VLLM：
   ```bash
   pip install vllm
   ```

2. 启动 VLLM 服务：
   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen3-4B-Chat \
     --served-model-name qwen3-4b \
     --port 8000
   ```

3. 更新配置：
   ```yaml
   model:
     type: "vllm"
     name: "qwen3-4b"
     api:
       base_url: "http://localhost:8000"
   ```

## 📝 配置文件说明

完整的配置文件示例：

```yaml
# 模型配置
model:
  type: "ollama"           # 模型类型
  name: "qwen3:4b"         # 模型名称
  api:
    base_url: "http://localhost:11434"
    timeout: 30
  generation:
    max_length: 2048
    temperature: 0.1
    top_p: 0.9

# 语义分析配置
semantic_analysis:
  depth: "medium"
  features:
    - "function_signatures"
    - "variable_names"
    - "control_flow"
    - "data_structures"
    - "comments"
    - "imports"

# 输出配置
output:
  format: "rich"           # plain, rich, json, html
  show_line_numbers: true
  show_context: true
  context_lines: 3

# 性能配置
performance:
  max_file_size: 1048576   # 1MB
  parallel_processing: true
  max_workers: 4
  cache_enabled: true

# 日志配置
logging:
  level: "INFO"
  file: "semantic_diff.log"
```

## 🆘 获取帮助

如果遇到问题：

1. 检查日志文件：`semantic_diff.log`
2. 运行测试：`python3 test_qwen_api.py`
3. 查看 Ollama 状态：`sudo systemctl status ollama`
4. 检查模型列表：`ollama list`

## 🎉 完成！

配置完成后，您就可以使用基于 Qwen3-4B 的语义差异分析工具了！

主要命令：
- `./run_demo.sh` - 运行演示
- `python3 test_qwen_api.py` - 测试配置
- `python3 -m semantic_diff.cli.main --help` - 查看帮助 