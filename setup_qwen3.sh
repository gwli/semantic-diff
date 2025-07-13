#!/bin/bash

# Qwen3-4B 模型安装和配置脚本

set -e

echo "=========================================="
echo "  Qwen3-4B 模型安装和配置"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "检测到root用户，建议使用普通用户运行此脚本"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统要求
check_system() {
    print_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "此脚本只支持Linux系统"
        exit 1
    fi
    
    # 检查curl
    if ! command -v curl &> /dev/null; then
        print_error "curl未安装，请先安装curl"
        exit 1
    fi
    
    # 检查GPU (可选)
    if command -v nvidia-smi &> /dev/null; then
        print_success "检测到NVIDIA GPU"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    else
        print_warning "未检测到NVIDIA GPU，将使用CPU模式"
    fi
    
    print_success "系统检查完成"
}

# 安装ollama
install_ollama() {
    print_info "检查ollama安装状态..."
    
    if command -v ollama &> /dev/null; then
        print_success "ollama已安装"
        return 0
    fi
    
    print_info "安装ollama..."
    if ! curl -fsSL https://ollama.com/install.sh | sh; then
        print_error "ollama安装失败"
        exit 1
    fi
    
    # 添加到PATH
    export PATH="/usr/local/bin:$PATH"
    
    print_success "ollama安装完成"
}

# 启动ollama服务
start_ollama() {
    print_info "启动ollama服务..."
    
    # 检查服务状态
    if systemctl is-active --quiet ollama; then
        print_success "ollama服务已运行"
        return 0
    fi
    
    # 启动服务
    if ! sudo systemctl start ollama; then
        print_error "启动ollama服务失败"
        exit 1
    fi
    
    # 等待服务启动
    sleep 3
    
    # 验证服务状态
    if systemctl is-active --quiet ollama; then
        print_success "ollama服务启动成功"
    else
        print_error "ollama服务启动失败"
        exit 1
    fi
}

# 下载Qwen3-4B模型
download_qwen_model() {
    print_info "下载Qwen3-4B模型..."
    
    # 可能的模型名称 (优先使用Qwen3)
    MODEL_NAMES=(
        "qwen3:4b"
        "qwen2.5:4b-chat"
        "qwen2.5:4b"
        "qwen2:4b-chat"
        "qwen2:4b"
        "qwen:4b-chat"
        "qwen:4b"
    )
    
    # 尝试下载模型
    for model_name in "${MODEL_NAMES[@]}"; do
        print_info "尝试下载模型: $model_name"
        
        if timeout 300 ollama pull "$model_name" 2>/dev/null; then
            print_success "成功下载模型: $model_name"
            
            # 更新配置文件
            update_config "$model_name"
            return 0
        else
            print_warning "下载失败: $model_name"
        fi
    done
    
    print_error "所有模型下载失败，请检查网络连接或手动下载"
    return 1
}

# 更新配置文件
update_config() {
    local model_name="$1"
    print_info "更新配置文件..."
    
    if [[ -f "config.yaml" ]]; then
        # 备份原配置
        cp config.yaml config.yaml.bak
        
        # 更新模型名称
        sed -i "s/name: \".*\"/name: \"$model_name\"/" config.yaml
        
        print_success "配置文件已更新，模型名称: $model_name"
        print_info "原配置已备份为 config.yaml.bak"
    else
        print_warning "未找到config.yaml文件"
    fi
}

# 测试模型
test_model() {
    print_info "测试模型..."
    
    # 获取当前配置的模型名称
    local model_name
    if [[ -f "config.yaml" ]]; then
        model_name=$(grep -o 'name: "[^"]*"' config.yaml | cut -d'"' -f2)
    else
        model_name="qwen3:4b"
    fi
    
    print_info "使用模型: $model_name"
    
    # 简单测试
    print_info "发送测试请求..."
    local test_response
    test_response=$(ollama run "$model_name" "你好，请简单介绍一下自己。" 2>/dev/null || echo "ERROR")
    
    if [[ "$test_response" != "ERROR" ]] && [[ -n "$test_response" ]]; then
        print_success "模型测试成功！"
        echo "模型响应: $test_response"
    else
        print_error "模型测试失败"
        return 1
    fi
}

# 运行语义差异工具测试
test_semantic_diff() {
    print_info "测试语义差异工具..."
    
    if [[ -f "test_qwen_api.py" ]]; then
        if python3 test_qwen_api.py; then
            print_success "语义差异工具测试成功！"
        else
            print_warning "语义差异工具测试失败，但模型配置正确"
        fi
    else
        print_warning "未找到test_qwen_api.py测试文件"
    fi
}

# 显示使用说明
show_usage() {
    echo
    echo "=========================================="
    echo "  安装完成！使用说明"
    echo "=========================================="
    echo
    echo "1. 基本使用:"
    echo "   python3 -m semantic_diff.cli.main compare file1.py file2.py"
    echo
    echo "2. 交互模式:"
    echo "   python3 -m semantic_diff.cli.main interactive"
    echo
    echo "3. 查看帮助:"
    echo "   python3 -m semantic_diff.cli.main --help"
    echo
    echo "4. 运行演示:"
    echo "   ./run_demo.sh"
    echo
    echo "5. 测试API连接:"
    echo "   python3 test_qwen_api.py"
    echo
    echo "配置文件: config.yaml"
    echo "日志文件: semantic_diff.log"
    echo
    echo "如需修改模型设置，请编辑 config.yaml 文件"
    echo "=========================================="
}

# 主函数
main() {
    echo "开始安装和配置 Qwen3-4B 模型..."
    echo
    
    check_root
    check_system
    install_ollama
    start_ollama
    
    if download_qwen_model; then
        test_model
        test_semantic_diff
        show_usage
        print_success "Qwen3-4B 模型安装和配置完成！"
    else
        print_error "模型下载失败，请检查网络连接或手动下载"
        echo
        echo "手动下载命令："
        echo "  ollama pull qwen3:4b"
        echo "  或"
        echo "  ollama pull qwen2.5:4b-chat"
        exit 1
    fi
}

# 错误处理
trap 'print_error "脚本执行失败，请检查错误信息"; exit 1' ERR

# 运行主函数
main "$@" 