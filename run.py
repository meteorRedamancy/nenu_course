#!/usr/bin/env python3
"""
东北师范大学抢课爬虫启动脚本
"""

import webbrowser
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 50)
    print("东北师范大学抢课系统")
    print("=" * 50)
    print()
    
    # 检查依赖
    try:
        import flask
        import requests
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 启动Flask应用
    try:
        from app import app
        
        # 在后台启动服务器
        import threading
        
        def run_server():
            app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        print("✓ 服务器启动中...")
        time.sleep(3)  # 等待服务器启动
        
        # 打开浏览器
        url = "http://localhost:5000"
        print(f"✓ 正在打开浏览器: {url}")
        webbrowser.open(url)
        
        print()
        print("使用说明:")
        print("1. 在网页中选择登录方式（Cookie或账号密码）")
        print("2. 选择课程类型进行查询")
        print("3. 可以立即选课或启动监控抢课")
        print("4. 监控任务会自动在后台运行")
        print()
        print("按 Ctrl+C 退出程序")
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        print("请检查app.py文件是否正确")

if __name__ == "__main__":
    main()