#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import json
import os


class ConfigManager:
    """配置管理器
    
    统一管理应用配置，提供配置的加载、保存、获取和设置方法。
    支持配置项的分组管理和默认值设置。
    """
    
    def __init__(self, config_file="stock_config.json"):
        """初始化配置管理器"""
        self.config_file = config_file
        self.config = self.get_default_config()
        self.load_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            # 股票配置
            'stocks': ['002624', '000001'],
            
            # 应用配置
            'update_interval': 3,
            'always_on_top': True,
            
            # 窗口配置
            'window_width': 300,
            'window_height': 48,
            'window_x': None,
            'window_y': None,
            
            # 外观配置
            'bg_opacity': 0.95,
            'bg_color': '#1e1e1e',
            
            # 显示配置
            'show_chart': True,
            'show_price': True,
            
            # 分时图配置
            'chart_fixed_percentage': True,
            'chart_max_percentage': 10,
            'chart_height': 120,
        }
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                    # 合并配置，新配置优先，缺失的用默认值
                    for key, default_value in self.get_default_config().items():
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
                        else:
                            self.config[key] = default_value
            else:
                # 使用默认配置并保存
                self.save_config()
                
        except Exception as e:
            print(f"加载配置失败: {e}")
            # 出错时使用默认配置
            self.config = self.get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_config(self, key, default=None):
        """获取配置项
        
        参数:
            key: 配置项键名
            default: 可选，默认值
        
        返回:
            配置项值
        """
        return self.config.get(key, default)
    
    def set_config(self, key, value):
        """设置配置项
        
        参数:
            key: 配置项键名
            value: 配置项值
        """
        self.config[key] = value
    
    def get_stocks(self):
        """获取股票列表"""
        stocks_config = self.config.get('stocks', [])
        stocks = []
        
        for symbol in stocks_config:
            if isinstance(symbol, str) and symbol:
                stocks.append({
                    'name': f"股票{symbol}",
                    'symbol': symbol,
                    'price': '0.00',
                    'change': '+0.00%'
                })
        
        # 如果没有股票，使用默认股票
        if not stocks:
            stocks = self.get_default_stocks()
            self.config['stocks'] = [stock['symbol'] for stock in stocks]
            
        return stocks
    
    def set_stocks(self, stocks):
        """设置股票列表
        
        参数:
            stocks: 股票列表，每个元素为股票对象或股票代码字符串
        """
        if stocks and isinstance(stocks[0], dict):
            # 如果是股票对象列表，提取股票代码
            self.config['stocks'] = [stock['symbol'] for stock in stocks]
        else:
            # 否则直接使用股票代码列表
            self.config['stocks'] = stocks
    
    def get_default_stocks(self):
        """获取默认股票列表"""
        return [
            {"name": "完美世界", "symbol": "002624", "price": "0.00", "change": "+0.00%"},
            {"name": "平安银行", "symbol": "000001", "price": "0.00", "change": "+0.00%"},
            {"name": "万科A", "symbol": "000002", "price": "0.00", "change": "+0.00%"},
            {"name": "中国平安", "symbol": "601318", "price": "0.00", "change": "+0.00%"},
            {"name": "贵州茅台", "symbol": "600519", "price": "0.00", "change": "+0.00%"},
            {"name": "比亚迪", "symbol": "002594", "price": "0.00", "change": "+0.00%"},
            {"name": "宁德时代", "symbol": "300750", "price": "0.00", "change": "+0.00%"},
            {"name": "招商银行", "symbol": "600036", "price": "0.00", "change": "+0.00%"},
            {"name": "五粮液", "symbol": "000858", "price": "0.00", "change": "+0.00%"},
            {"name": "中国石油", "symbol": "601857", "price": "0.00", "change": "+0.00%"}
        ]
    
    def get_update_interval(self):
        """获取更新间隔"""
        return self.config.get('update_interval', 3)
    
    def set_update_interval(self, interval):
        """设置更新间隔"""
        self.config['update_interval'] = interval
    
    def get_window_config(self):
        """获取窗口配置"""
        return {
            'width': self.config.get('window_width', 300),
            'height': self.config.get('window_height', 48),
            'x': self.config.get('window_x'),
            'y': self.config.get('window_y')
        }
    
    def set_window_config(self, window_config):
        """设置窗口配置
        
        参数:
            window_config: 窗口配置字典，包含width、height、x、y等键
        """
        if 'width' in window_config:
            self.config['window_width'] = window_config['width']
        if 'height' in window_config:
            self.config['window_height'] = window_config['height']
        if 'x' in window_config:
            self.config['window_x'] = window_config['x']
        if 'y' in window_config:
            self.config['window_y'] = window_config['y']
    
    def get_appearance_settings(self):
        """获取外观设置"""
        return {
            'bg_opacity': self.config.get('bg_opacity', 0.95),
            'bg_color': self.config.get('bg_color', '#1e1e1e'),
            'show_chart': self.config.get('show_chart', True),
            'chart_height': self.config.get('chart_height', 120),
            'always_on_top': self.config.get('always_on_top', True)
        }
    
    def set_appearance_settings(self, settings):
        """设置外观设置"""
        for key, value in settings.items():
            if key in ['bg_opacity', 'bg_color', 'show_chart', 'chart_height', 'always_on_top']:
                self.config[key] = value
    
    def get_chart_settings(self):
        """获取分时图设置"""
        return {
            'fixed_percentage': self.config.get('chart_fixed_percentage', True),
            'max_percentage': self.config.get('chart_max_percentage', 10),
            'show_chart': self.config.get('show_chart', True)
        }
    
    def set_chart_settings(self, settings):
        """设置分时图设置"""
        for key, value in settings.items():
            if key == 'fixed_percentage':
                self.config['chart_fixed_percentage'] = value
            elif key == 'max_percentage':
                self.config['chart_max_percentage'] = value
            elif key == 'show_chart':
                self.config['show_chart'] = value