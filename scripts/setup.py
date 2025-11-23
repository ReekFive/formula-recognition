#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发环境设置脚本
自动安装依赖并检查环境
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并检查结果"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print("✅ Python版本符合要求")
    return True

def install_dependencies():
    """安装项目依赖"""
    print("开始安装项目依赖...")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装项目依赖"):
        return False
    
    return True

def check_dependencies():
    """检查关键依赖是否安装成功"""
    print("检查依赖安装情况...")
    
    dependencies = [
        'pix2text', 'flask', 'pillow', 'numpy', 
        'opencv-python', 'latex2mathml', 'matplotlib', 'sympy'
    ]
    
    all_good = True
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))  # 处理包名中的连字符
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
            all_good = False
    
    return all_good

def main():
    """主函数"""
    print("=" * 60)
    print("公式识别器 - 开发环境设置")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 部分依赖检查失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 开发环境设置完成！")
    print("可以运行以下命令启动应用：")
    print("  python app.py")
    print("=" * 60)

if __name__ == '__main__':
    main()