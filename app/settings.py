#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser


class SettingsWindow:
    """设置窗口类"""
    
    def __init__(self, config_manager, stock_manager, parent_window, main_ui=None):
        self.config_manager = config_manager
        self.stock_manager = stock_manager
        self.parent_window = parent_window
        self.main_ui = main_ui  # 保存主UI实例引用
        
        self.window = None
        self.create_settings_ui()
    
    def create_settings_ui(self):
        """创建设置窗口UI"""
        self.window = tk.Toplevel()
        self.window.title("股票工具栏设置")
        self.window.geometry("450x600")
        # 设置窗口使用固定的背景颜色，不受主界面影响
        self.settings_bg_color = '#f0f0f0'
        self.window.configure(bg=self.settings_bg_color)
        self.window.attributes('-topmost', True)
        self.window.resizable(False, False)
        
        # 确保设置窗口是独立的，不会被主窗口的重新创建影响
        self.window.transient(self.parent_window)
        
        # 绑定窗口关闭事件，确保配置被保存
        self.window.protocol("WM_DELETE_WINDOW", self.on_settings_close)
        
        # 创建Notebook用于tab页面
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建两个tab页面，使用固定背景色
        stock_tab = tk.Frame(notebook, bg=self.settings_bg_color)
        settings_tab = tk.Frame(notebook, bg=self.settings_bg_color)
        
        notebook.add(stock_tab, text="📈 股票管理")
        notebook.add(settings_tab, text="⚙️ 参数设置")
        
        # 创建股票管理tab内容
        self.create_stock_management_tab(stock_tab)
        
        # 创建参数设置tab内容
        self.create_parameters_tab(settings_tab)
        


    
    def create_stock_management_tab(self, parent):
        """创建股票管理tab页面"""
        # 标题
        tk.Label(parent, text="📈 股票代码管理", font=("Microsoft YaHei", 12, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 10))
        
        # 说明文字
        tk.Label(parent, text="请输入股票代码，一行一个（如：000001、600519）", 
                font=("Microsoft YaHei", 9), bg=self.settings_bg_color, fg='#666').pack(anchor='w', padx=20, pady=(0, 10))
        
        # 股票代码文本框
        text_frame = tk.Frame(parent, bg=self.settings_bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 创建文本框和滚动条
        self.stock_text = tk.Text(text_frame, height=12, font=("Consolas", 10), 
                                  bg='white', fg='#333', relief=tk.SUNKEN, bd=1)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.stock_text.yview)
        self.stock_text.configure(yscrollcommand=scrollbar.set)
        
        self.stock_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充当前股票代码
        self.load_stock_codes()
        
        # 应用按钮
        button_frame = tk.Frame(parent, bg=self.settings_bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def apply_stock_codes():
            """应用股票代码"""
            try:
                # 获取文本框内容
                content = self.stock_text.get("1.0", tk.END).strip()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                if not lines:
                    messagebox.showwarning("提示", "请输入至少一个股票代码")
                    return
                
                # 转换为股票对象格式
                new_stocks = []
                for line in lines:
                    # 清理行内容
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析输入行，支持多种格式：
                    # 1. 纯代码：600519
                    # 2. 代码+名称：600519 (贵州茅台)
                    # 3. 纯名称：贵州茅台
                    
                    # 先尝试提取括号中的代码
                    code = None
                    name = None
                    
                    # 格式2：代码+名称 (600519 (贵州茅台))
                    if '(' in line and ')' in line:
                        # 提取括号内的内容
                        bracket_start = line.find('(')
                        bracket_end = line.rfind(')')
                        if bracket_start < bracket_end:
                            bracket_content = line[bracket_start+1:bracket_end].strip()
                            
                            # 检查括号外是否是代码
                            outside_bracket = line[:bracket_start].strip()
                            if outside_bracket.isdigit() and len(outside_bracket) == 6:
                                code = outside_bracket
                                name = bracket_content
                            # 检查括号内是否是代码
                            elif bracket_content.isdigit() and len(bracket_content) == 6:
                                code = bracket_content
                                name = line[:bracket_start].strip()
                    
                    # 格式1：纯代码
                    if not code and line.isdigit() and len(line) == 6:
                        code = line
                    
                    # 格式3：纯名称
                    if not code:
                        # 尝试根据名称搜索代码
                        name = line
                        code = self.stock_manager.search_stock_by_name(name)
                        if not code:
                            messagebox.showwarning("提示", f"无法找到股票名称 '{name}' 对应的代码")
                            continue
                    
                    if code and len(code) == 6:
                        new_stock = {
                            "name": name if name and not name.startswith('股票') else f"股票{code}",
                            "symbol": code,
                            "price": "0.00",
                            "change": "+0.00%"
                        }
                        new_stocks.append(new_stock)
                
                if new_stocks:
                    # 更新股票列表
                    self.stock_manager.stocks = new_stocks
                    self.config_manager.config['stocks'] = [stock['symbol'] for stock in new_stocks]
                    
                    # 保存配置到文件
                    self.config_manager.save_config()
                    
                    # 重新加载股票代码到文本框（显示代码和名称）
                    self.load_stock_codes()
                    
                else:
                    messagebox.showwarning("提示", "没有有效的股票代码")
                
            except Exception as e:
                print(f"应用股票代码失败: {e}")
                messagebox.showerror("错误", f"应用股票代码失败: {str(e)}")
        

        
        tk.Button(button_frame, text="应用股票代码", command=apply_stock_codes,
                 bg='#0078d4', fg='white', font=("Microsoft YaHei", 9), padx=20).pack(side=tk.LEFT, padx=5)
    
    def create_parameters_tab(self, parent):
        """创建参数设置tab页面"""
        # 工具栏尺寸设置
        tk.Label(parent, text="📏 工具栏尺寸", font=("Microsoft YaHei", 11, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 5))
        
        # 窗口宽度
        width_frame = tk.Frame(parent, bg=self.settings_bg_color)
        width_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(width_frame, text="宽度 (像素):", width=12, anchor='w', 
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=str(self.config_manager.config.get('window_width', 350)))
        width_entry = tk.Entry(width_frame, textvariable=self.width_var, width=15)
        width_entry.pack(side=tk.LEFT, padx=5)
        
        # 宽度提示标签
        self.width_hint_label = tk.Label(width_frame, text="", 
                                       bg=self.settings_bg_color, fg='#666', 
                                       font=("Microsoft YaHei", 8))
        self.width_hint_label.pack(side=tk.LEFT, padx=5)
        
        
        # 绑定提示更新
        if hasattr(self, 'show_chart_var'):
            self.show_chart_var.trace('w', update_width_hint)
        
        # 窗口高度
        height_frame = tk.Frame(parent, bg=self.settings_bg_color)
        height_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(height_frame, text="高度 (像素):", width=12, anchor='w',
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=str(self.config_manager.config.get('window_height', 60)))
        tk.Entry(height_frame, textvariable=self.height_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 外观设置
        tk.Label(parent, text="🎨 外观设置", font=("Microsoft YaHei", 11, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 5))
        
        # 透明度设置
        opacity_frame = tk.Frame(parent, bg=self.settings_bg_color)
        opacity_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(opacity_frame, text="透明度:", width=12, anchor='w',
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        self.opacity_var = tk.StringVar(value=str(self.config_manager.config.get('bg_opacity', 0.95)))
        opacity_scale = tk.Scale(opacity_frame, from_=0.1, to=1.0, resolution=0.05,
                               orient=tk.HORIZONTAL, variable=tk.DoubleVar(value=self.config_manager.config.get('bg_opacity', 0.95)),
                               bg=self.settings_bg_color, fg='#333', highlightthickness=0, length=150,
                               command=lambda v: self.opacity_var.set(f"{float(v):.2f}"))
        opacity_scale.pack(side=tk.LEFT, padx=5)
        
        # 背景颜色设置
        color_frame = tk.Frame(parent, bg=self.settings_bg_color)
        color_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(color_frame, text="背景颜色:", width=12, anchor='w',
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        
        self.color_var = tk.StringVar(value=self.config_manager.config.get('bg_color', '#1e1e1e'))
        
        # 颜色预览框
        self.color_preview = tk.Label(color_frame, text="    ", bg=self.color_var.get(), 
                                     relief=tk.RAISED, bd=2)
        self.color_preview.pack(side=tk.LEFT, padx=(5, 10))
        
        # 选择颜色按钮
        def choose_color():
            """选择颜色"""
            color = colorchooser.askcolor(initialcolor=self.color_var.get(), 
                                         title="选择背景颜色")
            if color[1]:  # color[1]是十六进制颜色值
                self.color_var.set(color[1])
                # 颜色变量的变化会自动触发实时更新和UI重新创建

        self.color_label = tk.Label(color_frame, text=self.color_var.get(), 
                                   bg=self.settings_bg_color, fg='#333',
                                   font=("Consolas", 9))
        self.color_label.pack(side=tk.LEFT, padx=5)

        tk.Button(color_frame, text="选择颜色", command=choose_color,
                 bg='#0078d4', fg='white', font=("Microsoft YaHei", 9), 
                 padx=10).pack(side=tk.LEFT, padx=5)
        
        
        # 功能设置
        tk.Label(parent, text="⚙️ 功能设置", font=("Microsoft YaHei", 11, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 5))
        
        # 更新间隔
        interval_frame = tk.Frame(parent, bg=self.settings_bg_color)
        interval_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(interval_frame, text="更新间隔 (秒):", width=12, anchor='w',
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=str(self.config_manager.config.get('update_interval', 3)))
        tk.Entry(interval_frame, textvariable=self.interval_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 置顶设置
        self.top_var = tk.BooleanVar(value=self.config_manager.config.get('always_on_top', True))
        tk.Checkbutton(parent, text="窗口始终置顶", variable=self.top_var,
                      bg=self.settings_bg_color, fg='#333', selectcolor=self.settings_bg_color,
                      font=("Microsoft YaHei", 9)).pack(anchor='w', padx=20, pady=5)
        
        # 股票信息显示设置
        tk.Label(parent, text="📊 股票信息显示", font=("Microsoft YaHei", 11, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 5))
        
        # 显示现价设置
        self.show_price_var = tk.BooleanVar(value=self.config_manager.config.get('show_price', True))
        tk.Checkbutton(parent, text="显示现价", variable=self.show_price_var,
                      bg=self.settings_bg_color, fg='#333', selectcolor=self.settings_bg_color,
                      font=("Microsoft YaHei", 9)).pack(anchor='w', padx=20, pady=5)
        
        # 分时图设置
        tk.Label(parent, text="📈 分时图设置", font=("Microsoft YaHei", 11, "bold"),
                bg=self.settings_bg_color, fg='#333').pack(anchor='w', padx=20, pady=(15, 5))
        
        # 分时图开关
        self.show_chart_var = tk.BooleanVar(value=self.config_manager.config.get('show_chart', True))
        tk.Checkbutton(parent, text="显示分时图", variable=self.show_chart_var,
                      bg=self.settings_bg_color, fg='#333', selectcolor=self.settings_bg_color,
                      font=("Microsoft YaHei", 9)).pack(anchor='w', padx=20, pady=5)
        
        # 固定最大百分比显示
        self.fixed_percentage_var = tk.BooleanVar(value=self.config_manager.config.get('chart_fixed_percentage', True))
        tk.Checkbutton(parent, text="固定最大百分比显示", variable=self.fixed_percentage_var,
                      bg=self.settings_bg_color, fg='#333', selectcolor=self.settings_bg_color,
                      font=("Microsoft YaHei", 9)).pack(anchor='w', padx=20, pady=5)
        
        # 最大百分比设置
        percentage_frame = tk.Frame(parent, bg=self.settings_bg_color)
        percentage_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(percentage_frame, text="最大百分比 (%):", width=12, anchor='w',
                bg=self.settings_bg_color, fg='#333').pack(side=tk.LEFT)
        self.max_percentage_var = tk.StringVar(value=str(self.config_manager.config.get('chart_max_percentage', 10)))
        percentage_options = ['5', '10', '20', '30', '50']
        self.max_percentage_combo = ttk.Combobox(percentage_frame, textvariable=self.max_percentage_var, 
                                             values=percentage_options, width=10, state='readonly')
        self.max_percentage_combo.pack(side=tk.LEFT, padx=5)
        
        # 说明文字
        tk.Label(parent, text="说明：主板股票通常用10%，科创/创业板用20%，ST股用5%",
                font=("Microsoft YaHei", 8), bg=self.settings_bg_color, fg='#666').pack(anchor='w', padx=20, pady=(5, 0))
        
        # 绑定实时更新事件
        self.bind_realtime_updates()
    
    def load_stock_codes(self):
        """加载当前股票代码到文本框（带股票名称）"""
        if hasattr(self, 'stock_text'):
            self.stock_text.delete("1.0", tk.END)
            for stock in self.stock_manager.stocks:
                # 显示格式：股票代码 (股票名称)
                if stock.get('name') and not stock['name'].startswith('股票'):
                    self.stock_text.insert(tk.END, f"{stock['symbol']} ({stock['name']})\n")
                else:
                    self.stock_text.insert(tk.END, stock['symbol'] + '\n')
    
    def on_settings_close(self):
        """设置窗口关闭时的处理"""
        try:
            # 确保保存所有配置
            self.config_manager.save_config()
        except Exception as e:
            print(f"保存配置失败: {e}")
        finally:
            # 关闭设置窗口
            if self.window:
                self.window.destroy()
                self.window = None
    
    def bind_realtime_updates(self):
        """绑定实时更新事件"""
        def apply_realtime_changes():
            """实时应用参数变化"""
            try:
                # 获取当前分时图显示状态
                current_show_chart = self.show_chart_var.get() if hasattr(self, 'show_chart_var') else self.config_manager.config.get('show_chart', True)
                
                # 获取当前值并进行验证
                try:
                    new_width = int(self.width_var.get()) if self.width_var.get() else self.config_manager.config.get('window_width', 350)
                except:
                    new_width = self.config_manager.config.get('window_width', 350)
                
                try:
                    new_height = int(self.height_var.get()) if self.height_var.get() else self.config_manager.config.get('window_height', 60)
                except:
                    new_height = self.config_manager.config.get('window_height', 60)
                
                try:
                    new_opacity = float(self.opacity_var.get()) if self.opacity_var.get() else self.config_manager.config.get('bg_opacity', 0.95)
                    new_opacity = max(0.1, min(1.0, new_opacity))
                except:
                    new_opacity = self.config_manager.config.get('bg_opacity', 0.95)
                
                new_color = self.color_var.get() if self.color_var.get() else self.config_manager.config.get('bg_color', '#1e1e1e')
                new_top = self.top_var.get() if hasattr(self, 'top_var') else self.config_manager.config.get('always_on_top', True)
                new_show_chart = self.show_chart_var.get() if hasattr(self, 'show_chart_var') else self.config_manager.config.get('show_chart', True)
                new_show_price = self.show_price_var.get() if hasattr(self, 'show_price_var') else self.config_manager.config.get('show_price', True)
                
                # 更新配置管理器
                self.config_manager.config['window_width'] = new_width
                self.config_manager.config['window_height'] = new_height
                self.config_manager.config['bg_opacity'] = new_opacity
                self.config_manager.config['bg_color'] = new_color
                self.config_manager.config['always_on_top'] = new_top
                self.config_manager.config['show_chart'] = new_show_chart
                self.config_manager.config['show_price'] = new_show_price
                
                # 更新分时图配置
                if hasattr(self, 'fixed_percentage_var'):
                    self.config_manager.config['chart_fixed_percentage'] = self.fixed_percentage_var.get()
                if hasattr(self, 'max_percentage_var'):
                    try:
                        self.config_manager.config['chart_max_percentage'] = int(self.max_percentage_var.get())
                    except:
                        self.config_manager.config['chart_max_percentage'] = 10
                
                # 保存配置到文件
                self.config_manager.save_config()
                
                # 应用设置到窗口
                if self.parent_window:
                    self.parent_window.attributes('-topmost', new_top)
                    self.parent_window.attributes('-alpha', new_opacity)
                    self.parent_window.configure(bg=new_color)
                    
                    # 更新窗口尺寸
                    current_x = self.parent_window.winfo_x()
                    current_y = self.parent_window.winfo_y()
                    self.parent_window.geometry(f"{new_width}x{new_height}+{current_x}+{current_y}")
                    
                    # 更新所有子组件的背景色
                    if self.main_ui and hasattr(self.main_ui, 'update_widget_bg'):
                        self.main_ui.update_widget_bg(self.parent_window, new_color)
            except Exception as e:
                print(f"实时更新失败: {e}")
        
        def apply_interval_change():
            """应用更新间隔变化"""
            try:
                if hasattr(self, 'interval_var'):
                    new_interval = int(self.interval_var.get())
                    if new_interval > 0:
                        self.config_manager.config['update_interval'] = new_interval
                        self.config_manager.set_update_interval(new_interval)
                        # 保存配置到文件
                        self.config_manager.save_config()
            except:
                pass
        
        # 绑定实时更新事件
        if hasattr(self, 'color_var'):
            def on_color_change(*args):
                """颜色改变时的回调"""
                apply_realtime_changes()
                # 更新颜色预览和标签
                if hasattr(self, 'color_preview'):
                    self.color_preview.configure(bg=self.color_var.get())
                if hasattr(self, 'color_label'):
                    self.color_label.configure(text=self.color_var.get())
                
                # 立即重新创建主界面以应用新的背景颜色
                if self.main_ui and hasattr(self.main_ui, 'recreate_ui'):
                    def delayed_recreate():
                        try:
                            self.main_ui.recreate_ui()
                        except Exception as e:
                            print(f"延迟重新创建UI失败: {e}")
                    self.window.after(100, delayed_recreate)
            self.color_var.trace('w', on_color_change)
        if hasattr(self, 'opacity_var'):
            self.opacity_var.trace('w', lambda *args: apply_realtime_changes())
        if hasattr(self, 'width_var'):
            self.width_var.trace('w', lambda *args: apply_realtime_changes())
        if hasattr(self, 'height_var'):
            self.height_var.trace('w', lambda *args: apply_realtime_changes())
        if hasattr(self, 'top_var'):
            self.top_var.trace('w', lambda *args: apply_realtime_changes())
        if hasattr(self, 'interval_var'):
            self.interval_var.trace('w', lambda *args: apply_interval_change())
        if hasattr(self, 'show_chart_var'):
            def on_show_chart_change(*args):
                # 获取当前状态和用户设置的宽度
                current_show_chart = self.show_chart_var.get()
                # 使用用户设置的宽度，而不是当前实际宽度
                user_set_width = int(self.width_var.get()) if self.width_var.get() else self.config_manager.config.get('window_width', 350)
                
                # 计算新宽度
                if current_show_chart:
                    # 从"未开启分时图"切换到"开启分时图"
                    # 用户设置的宽度是未开启分时图时的宽度（股票信息区域，25%）
                    # 开启分时图后，总宽度应该是：用户设置的宽度 / 0.25
                    new_width = int(user_set_width / 0.25)
                else:
                    # 从"开启分时图"切换到"未开启分时图"
                    # 用户设置的宽度是开启分时图时的总宽度
                    # 关闭分时图后，宽度应该是：用户设置的宽度 * 0.25
                    new_width = int(user_set_width * 0.25)
                
                # 确保新宽度至少为100px
                new_width = max(new_width, 100)
                
                # 应用新宽度
                self.width_var.set(str(new_width))
                self.config_manager.config['window_width'] = new_width
                
                # 直接保存配置到文件，确保新宽度被写入
                self.config_manager.save_config()
                
                # 更新配置
                apply_realtime_changes()
                
                # 分时图显示切换需要重新创建UI
                if self.main_ui and hasattr(self.main_ui, 'recreate_ui'):
                    def delayed_recreate():
                        try:
                            self.main_ui.recreate_ui()
                        except Exception as e:
                            print(f"延迟重新创建UI失败: {e}")
                    self.window.after(100, delayed_recreate)
            self.show_chart_var.trace('w', on_show_chart_change)
        if hasattr(self, 'show_price_var'):
            def on_show_price_change(*args):
                # 先更新配置
                apply_realtime_changes()
                # 延迟重新创建UI，避免影响设置窗口
                if self.main_ui and hasattr(self.main_ui, 'recreate_ui'):
                    # 使用after方法延迟执行，避免在设置窗口操作过程中关闭
                    def delayed_recreate():
                        try:
                            self.main_ui.recreate_ui()
                        except Exception as e:
                            print(f"延迟重新创建UI失败: {e}")
                    self.window.after(100, delayed_recreate)
            self.show_price_var.trace('w', on_show_price_change)
        
        # 绑定新的分时图配置项
        if hasattr(self, 'fixed_percentage_var'):
            def on_fixed_percentage_change(*args):
                apply_realtime_changes()
                # 强制重新绘制图表
                if self.main_ui and hasattr(self.main_ui, 'current_stock') and self.main_ui.current_stock:
                    self.main_ui.draw_chart(self.main_ui.current_stock)
            self.fixed_percentage_var.trace('w', on_fixed_percentage_change)
        if hasattr(self, 'max_percentage_var'):
            def on_max_percentage_change(*args):
                apply_realtime_changes()
                # 强制重新绘制图表
                if self.main_ui and hasattr(self.main_ui, 'current_stock') and self.main_ui.current_stock:
                    self.main_ui.draw_chart(self.main_ui.current_stock)
            self.max_percentage_var.trace('w', on_max_percentage_change)