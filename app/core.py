#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心应用类 - 主控制器
"""

import tkinter as tk
import threading
import time
from .ui import StockBarUI
from .config import ConfigManager
from .stock import StockDataManager



class Win11StockBar:
    """股票工具栏主类"""
    
    def __init__(self):
        self.running = True
        self.root = None
        
        # 初始化各个管理器
        self.config_manager = ConfigManager()
        self.stock_manager = StockDataManager()
        self.ui = None
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 配置管理器会自动加载配置
        self.stock_manager.stocks = self.config_manager.get_stocks()
    
    def create_ui(self):
        """创建UI界面"""
        self.root = tk.Tk()
        self.root.title("股票工具栏")
        self.root.overrideredirect(True)  # 无边框窗口
        
        # 创建UI组件
        self.ui = StockBarUI(
            self.root, 
            self.config_manager, 
            self.stock_manager
        )
        
        # 启动更新线程
        self.start_update_thread()
    
    def start_update_thread(self):
        """启动更新线程"""
        def update_loop():
            while self.running:
                if self.root:
                    self.root.after(0, self.update_stock_info)
                time.sleep(self.config_manager.get_update_interval())
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def update_stock_info(self):
        """更新股票信息"""
        if self.ui:
            self.ui.update_stock_display()
    
    def run(self):
        """运行应用"""
        self.create_ui()
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close_app()
    
    def close_app(self):
        """关闭应用"""
        self.running = False
        if self.root:
            self.root.quit()
            
        # 保存配置
        self.config_manager.save_config()