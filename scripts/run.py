#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动应用脚本
简化启动流程
"""

import subprocess
import sys
import os

def main():
    """启动应用"""
    print("🚀 启动公式识别器...")
    
    # 检查端口是否被占用（可选）
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8081))
        sock.close()
        
        if result == 0:
            print("⚠️  端口8081已被占用，请检查其他应用")
            response = input("是否强制启动？(y/N): ")
            if response.lower() != 'y':
                print("启动取消")
                return
    except:
        pass  # 忽略端口检查错误
    
    # 启动Flask应用
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['FLASK_DEBUG'] = '1'
        
        print("🌐 应用将在 http://localhost:8081 启动")
        print("📱 打开浏览器访问上述地址")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        # 运行应用
        subprocess.run([sys.executable, 'app.py'], env=env)
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()