#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速验证脚本 - 检查Qwen3-4B配置
"""

def check_config():
    """检查配置文件"""
    print("🔍 检查配置文件...")
    
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        model_config = config.get('model', {})
        print(f"✓ 模型类型: {model_config.get('type', 'unknown')}")
        print(f"✓ 模型名称: {model_config.get('name', 'unknown')}")
        
        if 'api' in model_config:
            api_config = model_config['api']
            print(f"✓ API地址: {api_config.get('base_url', 'unknown')}")
            print(f"✓ 超时时间: {api_config.get('timeout', 'unknown')}秒")
        
        if 'generation' in model_config:
            gen_config = model_config['generation']
            print(f"✓ 最大长度: {gen_config.get('max_length', 'unknown')}")
            print(f"✓ 温度参数: {gen_config.get('temperature', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"✗ 配置文件错误: {e}")
        return False

def check_imports():
    """检查关键导入"""
    print("\n📦 检查Python模块...")
    
    modules = [
        ('yaml', 'PyYAML'),
        ('requests', 'requests'),
        ('semantic_diff', '语义差异工具')
    ]
    
    all_good = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✓ {name} 可用")
        except ImportError:
            print(f"✗ {name} 缺失")
            all_good = False
    
    return all_good

def create_example_usage():
    """创建使用示例"""
    print("\n📝 生成使用示例...")
    
    usage_commands = [
        "# 下载 Qwen3-4B 模型",
        "ollama pull qwen3:4b",
        "",
        "# 测试模型",
        "ollama run qwen3:4b '你好'",
        "",
        "# 运行语义差异工具",
        "python3 -m semantic_diff.cli.main compare examples/sample_code_old.py examples/sample_code_new.py",
        "",
        "# 或运行演示",
        "./run_demo.sh",
        "",
        "# 测试API连接",
        "python3 test_qwen_api.py"
    ]
    
    with open('qwen3_commands.sh', 'w') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Qwen3-4B 使用命令\n\n")
        for cmd in usage_commands:
            if cmd.startswith('#'):
                f.write(f"{cmd}\n")
            elif cmd == "":
                f.write("\n")
            else:
                f.write(f"{cmd}\n")
    
    print("✓ 使用命令已保存到 qwen3_commands.sh")

def main():
    """主函数"""
    print("=" * 50)
    print("  Qwen3-4B 配置验证")
    print("=" * 50)
    
    config_ok = check_config()
    imports_ok = check_imports()
    
    create_example_usage()
    
    print("\n" + "=" * 50)
    print("  验证结果")
    print("=" * 50)
    
    if config_ok and imports_ok:
        print("🎉 配置验证通过！")
        print("\n下一步:")
        print("1. 确保 Ollama 服务正在运行")
        print("2. 下载模型: ollama pull qwen3:4b")
        print("3. 测试: ollama run qwen3:4b '你好'")
        print("4. 运行: python3 test_qwen_api.py")
    else:
        print("⚠️  发现配置问题，请检查上述错误")
    
    print(f"\n配置摘要:")
    print(f"- 模型类型: ollama")
    print(f"- 模型名称: qwen3:4b") 
    print(f"- API地址: http://localhost:11434")
    print(f"- 配置文件: config.yaml")

if __name__ == "__main__":
    main() 