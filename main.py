#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 股票信息工具栏 - 主程序入口
"""

import os
import sys
import tempfile
from app import Win11StockBar


class SingleInstance:
    """单实例管理器"""
    
    def __init__(self, lock_file="stockbar.lock"):
        self.lock_file = os.path.join(tempfile.gettempdir(), lock_file)
        self.lock_fd = None
        
    def __enter__(self):
        try:
            # 检查锁文件是否已存在
            if os.path.exists(self.lock_file):
                # 尝试读取锁文件内容，检查进程是否还在运行
                try:
                    with open(self.lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # 检查进程是否还在运行
                    if self.is_process_running(pid):
                        return False
                    else:
                        # 进程已结束，删除旧的锁文件
                        os.unlink(self.lock_file)
                except (ValueError, IOError):
                    # 锁文件损坏，删除它
                    if os.path.exists(self.lock_file):
                        os.unlink(self.lock_file)
            
            # 创建新的锁文件
            self.lock_fd = open(self.lock_file, 'w')
            self.lock_fd.write(f"{os.getpid()}\n")
            self.lock_fd.flush()
            
            # 在Windows上尝试锁定文件
            if os.name == 'nt':
                try:
                    import msvcrt
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                except (ImportError, IOError):
                    # 如果无法锁定，继续执行（但可能会有竞态条件）
                    pass
            else:
                # Unix系统使用fcntl
                try:
                    import fcntl
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (ImportError, IOError):
                    pass
            
            return True
            
        except (IOError, OSError):
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            return False
    
    def is_process_running(self, pid):
        """检查进程是否还在运行"""
        if os.name == 'nt':
            # Windows系统
            try:
                import psutil
                return psutil.pid_exists(pid)
            except ImportError:
                # 如果没有psutil，使用更简单的方法
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.OpenProcess(0x1000, False, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        return True
                    return False
                except:
                    return True  # 假设进程还在运行，更安全
        else:
            # Unix系统
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            try:
                # 释放锁
                if os.name == 'nt':
                    try:
                        import msvcrt
                        msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                    except (ImportError, IOError):
                        pass
                else:
                    try:
                        import fcntl
                        fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                    except (ImportError, IOError):
                        pass
                
                self.lock_fd.close()
                
                # 删除锁文件
                if os.path.exists(self.lock_file):
                    os.unlink(self.lock_file)
            except:
                pass


def main():
    """主函数"""
    # 检查是否已有实例运行
    with SingleInstance() as single:
        if not single:
            print("股票工具栏已在运行中，请勿重复启动！")
            # 尝试激活已有窗口
            try:
                import win32gui
                import win32con
                # 查找并激活股票工具栏窗口
                def callback(hwnd, hwnd_list):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if "股票工具栏" in window_title and "设置" not in window_title:
                            hwnd_list.append(hwnd)
                    return True
                
                hwnd_list = []
                win32gui.EnumWindows(callback, hwnd_list)
                
                if hwnd_list:
                    # 激活第一个找到的窗口
                    hwnd = hwnd_list[0]
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    print("已激活已有的股票工具栏窗口")
            except ImportError:
                print("请安装pywin32以支持窗口激活功能")
            except Exception as e:
                print(f"激活窗口失败: {e}")
            
            sys.exit(1)
    
    print("启动股票工具栏...")
    app = Win11StockBar()
    app.run()


if __name__ == "__main__":
    main()