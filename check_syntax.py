#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import py_compile

# 检查所有Python文件的语法
def check_syntax():
    """检查所有Python文件的语法"""
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    py_compile.compile(file_path, doraise=True)
                    print(f"✓ {file_path} - 语法正确")
                except py_compile.PyCompileError as e:
                    print(f"✗ {file_path} - 语法错误: {e}")
                except Exception as e:
                    print(f"✗ {file_path} - 其他错误: {e}")

if __name__ == "__main__":
    check_syntax()
