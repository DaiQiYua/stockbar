#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票工具栏一键打包脚本
使用方法：python setup.py
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller 安装失败")
            return False

def build_executable():
    """打包可执行文件"""
    print("\n开始打包股票工具栏...")
    
    # 清理之前的打包结果
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=StockBar",
        "--icon=NONE",
        "--noconsole",
        "--add-data=stock_config.json;.",
        "--hidden-import=app.config",
        "--hidden-import=app.core",
        "--hidden-import=app.settings",
        "--hidden-import=app.stock",
        "--hidden-import=app.ui",
        "--hidden-import=app.window",
        "--hidden-import=win32gui",
        "--hidden-import=win32con",
        "--hidden-import=psutil",
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ 打包完成！")
        
        # 检查生成的文件
        exe_path = os.path.join("dist", "StockBar.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✓ 可执行文件: {exe_path}")
            print(f"✓ 文件大小: {file_size:.2f} MB")
            print("\n使用方法：双击运行 'dist\\StockBar.exe'")
        else:
            print("✗ 打包失败，未找到可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("StockBar一键打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return
    
    # 打包
    build_executable()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()