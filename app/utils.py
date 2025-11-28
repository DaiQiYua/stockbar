#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块，包含公共方法和工具函数
"""

import tkinter as tk


def calculate_luminance(hex_color):
    """计算颜色的相对亮度（0-1之间）
    
    参数:
        hex_color: 十六进制颜色值，如 '#ffffff'
    
    返回:
        颜色的相对亮度值，范围0-1
    """
    # 移除#号并转换为RGB
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # 计算相对亮度（WCAG标准）
    r = r if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return luminance


def get_contrast_color(hex_color):
    """根据背景颜色返回对比度最佳的字体颜色（白色或黑色）
    
    参数:
        hex_color: 十六进制背景颜色值
    
    返回:
        对比度最佳的字体颜色，'#000000'（黑色）或 '#ffffff'（白色）
    """
    luminance = calculate_luminance(hex_color)
    
    # 使用WCAG对比度标准
    # 如果背景较亮（亮度>0.5），使用黑色字体；如果背景较暗，使用白色字体
    if luminance > 0.5:
        return '#000000'  # 黑色
    else:
        return '#ffffff'  # 白色


def update_text_label(label, text, fg_color=None):
    """更新Text标签的公共方法
    
    参数:
        label: 要更新的Text标签
        text: 新的文本内容
        fg_color: 可选，新的字体颜色
    """
    if label:
        label.config(state=tk.NORMAL)
        label.delete('1.0', tk.END)
        label.insert('1.0', text)
        label.tag_add("center", "1.0", "end")
        if fg_color:
            label.config(fg=fg_color)
        label.config(state=tk.DISABLED)
