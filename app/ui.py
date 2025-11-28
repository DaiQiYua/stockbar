#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI界面模块
"""

import tkinter as tk
from tkinter import Menu, messagebox
import tkinter.font
from .settings import SettingsWindow
from .utils import calculate_luminance, get_contrast_color, update_text_label


class StockBarUI:
    """股票工具栏UI界面"""
    
    def __init__(self, root, config_manager, stock_manager):
        self.root = root
        self.config_manager = config_manager
        self.stock_manager = stock_manager
        
        # UI组件
        self.stock_name_label = None
        self.stock_price_label = None
        self.stock_change_label = None
        self.stock_label = None
        self.chart_canvas = None
        self.current_stock = None
        self.pankou_window = None
        self.settings_window = None  # 添加设置窗口实例跟踪
        
        # 窗口配置
        self.window_width = self.config_manager.get_config('window_width', 350)
        self.window_height = self.config_manager.get_config('window_height', 60)
        self.window_x = self.config_manager.get_config('window_x')
        self.window_y = self.config_manager.get_config('window_y')
        self.bg_opacity = self.config_manager.get_config('bg_opacity', 0.95)
        self.bg_color = self.config_manager.get_config('bg_color', '#1e1e1e')
        self.always_on_top = self.config_manager.get_config('always_on_top', True)
        self.show_chart = self.config_manager.get_config('show_chart', True)
        self.chart_height = self.config_manager.get_config('chart_height', 120)
        self.info_height = 40
        
        # 创建UI组件
        self.create_ui_components()
        
        # 设置窗口属性
        self.setup_window()
        
        # 添加拖拽功能和右键菜单
        self.make_draggable(self.root)
        self.create_context_menu()
        
        # 设置股票数据更新回调
        self.stock_manager.set_update_callback(self.on_stock_data_updated)
        
        # 添加鼠标悬停事件
        self.root.bind('<Enter>', self.on_mouse_enter)
        self.root.bind('<Leave>', self.on_mouse_leave)
    
    def setup_window(self):
        """设置窗口属性"""
        # 设置窗口属性
        self.root.attributes('-topmost', self.always_on_top)
        self.root.attributes('-alpha', self.bg_opacity)
        
        # 设置窗口大小和位置
        if self.window_x is not None and self.window_y is not None:
            x, y = self.window_x, self.window_y
        else:
            screen_width = self.root.winfo_screenwidth()
            x = (screen_width - self.window_width) // 2
            screen_hight = self.root.winfo_screenheight()
            y = screen_hight - self.window_height
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.root.configure(bg=self.bg_color)
        
        # 绑定窗口事件
        self.bind_window_events()
    
    def bind_window_events(self):
        """绑定窗口事件"""
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event):
        """处理窗口大小变化"""
        if event.widget == self.root:
            new_width = event.width
            new_height = event.height
            
            # 取消窗口尺寸限制，直接使用新尺寸
            
            # 只有当尺寸发生显著变化时才重新计算
            if abs(new_width - self.window_width) > 5 or abs(new_height - self.window_height) > 5:
                self.window_width = new_width
                self.window_height = new_height
                
                # 实时更新字体大小
                self.update_font_sizes()
                
                # 如果显示分时图，重新计算布局
                if self.show_chart and hasattr(self, 'update_layout'):
                    self.update_layout()
                
                # 保存窗口尺寸到配置
                self.save_window_config()
    
    def save_window_config(self):
        """保存窗口配置"""
        self.config_manager.set_config('window_width', self.window_width)
        self.config_manager.set_config('window_height', self.window_height)
        self.config_manager.set_config('window_x', self.window_x)
        self.config_manager.set_config('window_y', self.window_y)
        self.config_manager.save_config()
    
    def make_draggable(self, root):
        """使窗口可拖拽"""
        def start_move(event):
            if event.num == 1:  # 只有左键才能拖拽
                self.x = event.x
                self.y = event.y
        
        def stop_move(event):
            if hasattr(self, 'x') and hasattr(self, 'y') and self.x is not None and self.y is not None:
                # 拖拽结束，保存新位置
                self.window_x = root.winfo_x()
                self.window_y = root.winfo_y()
                # 保存位置到配置
                self.save_window_config()
            
            self.x = None
            self.y = None
        
        def on_move(event):
            if hasattr(self, 'x') and hasattr(self, 'y') and self.x is not None and self.y is not None:
                deltax = event.x - self.x
                deltay = event.y - self.y
                x = root.winfo_x() + deltax
                y = root.winfo_y() + deltay
                root.geometry(f"+{x}+{y}")
        
        root.bind('<Button-1>', start_move)
        root.bind('<ButtonRelease-1>', stop_move)
        root.bind('<B1-Motion>', on_move)
    
    def bring_to_front(self, root):
        """将窗口置于前台（不获取焦点，避免打断用户操作）"""
        if root and self.always_on_top:
            try:
                # 确保窗口置顶但不获取焦点
                root.attributes('-topmost', True)
                # 仅提升窗口但不获取焦点，避免打断用户在其他应用中的操作
                root.lift()
                # 延迟重置置顶属性，确保窗口保持在最上层但不干扰焦点
                root.after(100, lambda: root.attributes('-topmost', True))
            except Exception as e:
                # 如果操作失败，尝试简单的置顶
                try:
                    root.lift()
                    root.attributes('-topmost', True)
                except:
                    pass
    
    def create_ui_components(self):
        """创建UI组件"""
        # 获取配置
        appearance = self.config_manager.get_appearance_settings()
        bg_color = appearance['bg_color']
        show_chart = appearance['show_chart']
        
        # 根据背景颜色智能选择字体颜色
        self.text_color = get_contrast_color(bg_color)
        
        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg=bg_color, relief=tk.FLAT, bd=0, 
                            highlightthickness=1, highlightbackground=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 为所有可见组件添加鼠标悬停事件
        self.bind_mouse_events(self.main_frame)
        
        if show_chart:
            # 分时图模式
            self.create_chart_mode(self.main_frame, bg_color)
        else:
            # 传统模式
            self.create_simple_mode(self.main_frame, bg_color)
    
    def create_chart_mode(self, parent, bg_color):
        """创建分时图模式界面"""
        # 计算合理的布局尺寸
        window_width = self.window_width
        
        # 固定比例分配：分时图75%，股票信息25%
        chart_width = int(window_width * 0.75)
        info_width = int(window_width * 0.25)
        
        # 保存当前的信息区域比例，用于切换分时图显示状态时的宽度计算
        self.info_ratio = 0.25  # 固定比例
        
        # 分时图区域（左侧）
        self.chart_frame = tk.Frame(parent, bg=bg_color, width=chart_width)
        self.chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=0, pady=0)
        self.chart_frame.pack_propagate(False)
        
        # 创建Canvas用于绘制分时图
        self.chart_canvas = tk.Canvas(
            self.chart_frame,
            bg=bg_color,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定Canvas大小变化事件
        self.chart_canvas.bind('<Configure>', self.on_chart_resize)
        
        # 右侧：股票信息显示
        self.info_frame = tk.Frame(parent, bg=bg_color, width=info_width)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        self.info_frame.pack_propagate(False)
        
        # 创建股票信息标签
        self._create_stock_labels(self.info_frame, bg_color)

        
        
    
    def create_simple_mode(self, parent, bg_color):
        """创建传统模式界面"""
        # 传统模式只显示信息，不显示分时图
        # 使用与分时图模式相同的Text控件显示方式
        
        # 创建股票信息标签
        self._create_stock_labels(parent, bg_color)
        
        # 为新创建的组件绑定鼠标悬停事件
        self.bind_mouse_events(parent)
    
    def _create_stock_labels(self, parent, bg_color):
        """创建股票信息标签的公共方法"""
        # 根据背景颜色智能选择字体颜色
        text_color = get_contrast_color(bg_color)
        
        # 根据show_price设置决定显示哪些标签
        show_price = self.config_manager.config.get('show_price', True)
        
        # 定义要创建的标签信息
        labels_info = [
            ("stock_name_label", "正在加载...", "name", "bold", text_color),
            ("stock_price_label", "0.00", "price", "bold", text_color),
            ("stock_change_label", "+0.00%", "change", "normal", '#00ff00')
        ]
        
        # 过滤要显示的标签
        if show_price:
            filtered_labels_info = labels_info  # 显示所有3个标签
        else:
            # 不显示现价，只显示名称和涨跌幅
            filtered_labels_info = [
                ("stock_name_label", "正在加载...", "name", "bold", text_color),
                ("stock_change_label", "+0.00%", "change", "normal", '#00ff00')
            ]
        
        # 根据实际显示的标签数量动态计算字体大小
        label_count = len(filtered_labels_info)
        font_sizes = self.calculate_font_sizes(label_count)
        
        # 创建Text控件用于显示股票信息
        for label_attr, text, font_key, font_weight, fg_color in filtered_labels_info:
            # 创建字体对象
            font = tk.font.Font(family="Microsoft YaHei", size=font_sizes[font_key], weight=font_weight)
            
            text_widget = tk.Text(
                parent,
                font=font,
                bg=bg_color,
                fg=fg_color,
                relief=tk.FLAT,
                bd=0,
                padx=0,
                pady=0,
                height=1,
                wrap=tk.WORD
            )
            text_widget.pack(fill=tk.BOTH, expand=True, pady=0)
            text_widget.insert('1.0', text)
            text_widget.tag_configure("center", justify="center")
            text_widget.tag_add("center", "1.0", "end")
            text_widget.config(state=tk.DISABLED)
            setattr(self, label_attr, text_widget)
    
    def create_context_menu(self):
        """创建右键菜单"""
        # 右键菜单使用固定的样式，不受主界面背景色影响
        self.context_menu = Menu(self.root, tearoff=0, bg='white', fg='black', 
                                activebackground='#0078d4', activeforeground='white',
                                borderwidth=1, relief=tk.RAISED)
        
        self.context_menu.add_command(label="⚙️ 设置", command=self.show_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 关闭", command=self.close_app)
        
        # 绑定右键事件
        self.root.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def update_stock_display(self):
        """更新股票显示"""
        try:
            if not self.stock_manager.stocks:
                return
            
            # 获取当前股票
            stock = self.stock_manager.get_current_stock()
            if not stock:
                return
            
            # 异步获取真实股票数据，不显示加载状态
            self.stock_manager.fetch_stock_data_async(stock)
            
        except Exception as e:
            print(f"更新股票显示失败: {e}")
            self.show_error_message()
    

    def on_stock_data_updated(self, stock):
        """股票数据更新回调（在主线程中执行）"""
        try:
            # 使用after确保在主线程中执行UI更新
            self.root.after(0, self._update_ui_with_stock_data, stock)
        except Exception as e:
            print(f"股票数据更新回调失败: {e}")
    
    def _update_ui_with_stock_data(self, stock):
        """在主线程中更新UI"""
        try:
            # 保存当前股票引用用于绘制分时图
            self.current_stock = stock
            
            # 根据涨跌设置颜色（中国股市习惯：上涨和0为红色，下跌为绿色）
            if stock['change'].startswith('+') or stock['change'] == '0.00%':
                color = '#ff6b6b'  # 红色（涨或平）
            elif stock['change'].startswith('-'):
                color = '#00ff00'  # 绿色（跌）
            else:
                color = '#ff6b6b'  # 默认红色
            
            # 更新显示
            appearance = self.config_manager.get_appearance_settings()
            show_price = self.config_manager.config.get('show_price', True)
            
            # 更新股票名称
            self._update_text_label(self.stock_name_label, stock['name'])
            
            # 更新股票价格
            if self.stock_price_label:
                if show_price:
                    self._update_text_label(self.stock_price_label, stock['price'])
                    self.stock_price_label.pack(fill=tk.BOTH, expand=True, pady=0)
                else:
                    self.stock_price_label.pack_forget()
            
            # 更新涨跌幅
            self._update_text_label(self.stock_change_label, stock['change'], color)
            
            # 绘制分时图
            if appearance['show_chart'] and self.chart_canvas:
                self.draw_chart(stock)
            
            # 将工具栏置于前台
            self.bring_to_front(self.root)
            
        except Exception as e:
            print(f"更新股票显示失败: {e}")
            self.show_error_message()
    
    def show_error_message(self):
        """显示错误消息"""
        show_price = self.config_manager.config.get('show_price', True)
        
        # 更新股票名称为错误信息
        self._update_text_label(self.stock_name_label, "更新失败")
        
        # 更新股票价格
        if self.stock_price_label:
            if show_price:
                self._update_text_label(self.stock_price_label, "--")
                self.stock_price_label.pack(fill=tk.BOTH, expand=True, pady=0)
            else:
                self.stock_price_label.pack_forget()
        
        # 更新涨跌幅
        self._update_text_label(self.stock_change_label, "--")
    
    def _update_text_label(self, label, text, fg_color=None):
        """更新Text标签的公共方法"""
        update_text_label(label, text, fg_color)
    
    def on_chart_resize(self, event):
        """处理Canvas大小变化"""
        if self.current_stock:
            self.draw_chart(self.current_stock)
    
    def draw_chart(self, stock):
        """绘制分时图"""
        if not self.chart_canvas:
            return
        
        try:
            # 清空画布
            self.chart_canvas.delete("all")
            
            # 获取Canvas尺寸
            canvas_width = self.chart_canvas.winfo_width()
            canvas_height = self.chart_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas尚未初始化，延迟绘制
                self.root.after(100, lambda: self.draw_chart(stock))
                return
            
            # 获取分时数据
            chart_data = stock.get('chart_data', [])
            if not chart_data:
                # 没有数据时显示提示
                self.chart_canvas.create_text(
                    canvas_width // 2, canvas_height // 2,
                    text="暂无分时数据",
                    fill='#888888',
                    font=("Microsoft YaHei", 10)
                )
                return
            
            # 绘制简化的分时图
            self.draw_simple_chart(chart_data, canvas_width, canvas_height)
            
        except Exception as e:
            print(f"绘制分时图失败: {e}")
    
    def get_stock_type_info(self, stock_symbol):
        """获取股票类型信息，返回最大涨跌幅限制"""
        if not stock_symbol:
            return 10  # 默认10%
        
        # 获取配置
        fixed_percentage = self.config_manager.config.get('chart_fixed_percentage', True)
        default_max_percentage = self.config_manager.config.get('chart_max_percentage', 10)
        
        if not fixed_percentage:
            return default_max_percentage
        
        # 根据股票代码前缀判断类型
        # 首先检查是否为ST股票（优先级最高）
        if 'ST' in stock_symbol or '*' in stock_symbol:
            return 5  # ST股票
        elif stock_symbol.startswith(('688', '300', '301')):
            return 20  # 科创板、创业板
        elif stock_symbol.startswith(('600', '000', '001', '002', '003')):
            return 10  # 主板股票
        else:
            return default_max_percentage  # 其他类型使用默认值
    
    def get_yesterday_close_price(self, stock):
        """获取昨日收盘价"""
        try:
            # 首先尝试从股票数据中获取昨日收盘价
            if 'yesterday_close' in stock:
                return stock['yesterday_close']
            
            # 如果没有存储昨日收盘价，尝试从API数据中获取
            if 'chart_data' in stock and stock['chart_data']:
                # 如果分时数据中有价格数据，使用第一个价格作为基准（可能是开盘价）
                first_price = stock['chart_data'][0].get('price')
                if first_price and first_price > 0:
                    return first_price
            
            # 如果没有找到昨日收盘价，返回None
            return None
            
        except Exception as e:
            print(f"获取昨日收盘价失败: {e}")
            return None
    
    def draw_simple_chart(self, chart_data, canvas_width, canvas_height):
        """绘制简化的分时图"""
        # 设置合理的边距
        padding = 2
        right_margin = 30  # 为右侧百分比标签留出空间
        left_margin = 2
        
        # 计算实际绘图区域
        chart_left = left_margin
        chart_right = canvas_width - right_margin
        chart_top = padding
        chart_bottom = canvas_height - padding
        
        # 确保绘图区域有效
        if chart_right <= chart_left:
            chart_right = canvas_width - padding
        
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top
        
        # 如果绘图区域太小，不绘制图表
        if chart_width < 20 or chart_height < 10:
            return
        
        # 计算价格范围
        prices = [point['price'] for point in chart_data if point.get('price')]
        if not prices:
            return
        
        # 获取昨日收盘价作为基准（0轴）
        current_stock = getattr(self, 'current_stock', None)
        if not current_stock:
            return
            
        # 从股票数据中获取昨日收盘价
        base_price = self.get_yesterday_close_price(current_stock)
        if not base_price or base_price <= 0:
            # 如果没有昨日收盘价，使用第一个价格作为基准
            base_price = prices[0]
        
        min_price = min(prices)
        max_price = max(prices)
        
        # 获取当前股票的最大涨跌幅限制
        stock_symbol = current_stock.get('symbol', '') if current_stock else ''
        max_percentage = self.get_stock_type_info(stock_symbol)
        
        # 检查是否启用固定百分比显示
        fixed_percentage = self.config_manager.config.get('chart_fixed_percentage', True)
        
        if fixed_percentage:
            # 使用固定的最大百分比
            max_change = base_price * (max_percentage / 100)
        else:
            # 使用实际变化范围
            actual_max_change = max(abs(max_price - base_price), abs(base_price - min_price))
            max_change = actual_max_change if actual_max_change > 0 else base_price * 0.01
        
        if max_change == 0:
            max_change = base_price * 0.01  # 默认1%
        
        # 计算0轴位置（基准价格）- 固定在中间位置
        zero_y = chart_top + chart_height // 2
        
        # 绘制0轴（基准线）
        self.chart_canvas.create_line(
            chart_left, zero_y, chart_right, zero_y,
            fill='#666666',
            width=1,
            dash=(2, 2),
            tags="zero_axis"
        )
        
        # 绘制百分比标签
        font_size = max(6, min(8, canvas_height // 15))
        
        if fixed_percentage:
            # 固定百分比模式：确保正负值绝对值一致
            max_display_percentage = max_percentage
            min_display_percentage = max_percentage  # 使用相同的绝对值
        else:
            # 实际变化模式：显示实际的涨跌幅，但确保正负值绝对值一致
            max_actual_change = ((max_price - base_price) / base_price) * 100
            min_actual_change = ((base_price - min_price) / base_price) * 100
            # 取最大绝对值，确保正负值范围对称
            max_abs_change = max(abs(max_actual_change), abs(min_actual_change))
            max_display_percentage = max_abs_change
            min_display_percentage = max_abs_change
        
        # 显示最大涨幅百分比
        self.chart_canvas.create_text(
            chart_right + 2, chart_top + 5,
            text=f"+{max_display_percentage:.2f}%",
            fill=self.text_color,
            font=("Arial", font_size),
            anchor='w',
            tags="max_label"
        )
        
        # 0轴标签
        self.chart_canvas.create_text(
            chart_right + 2, zero_y,
            text="0.0%",
            fill=self.text_color,
            font=("Arial", font_size),
            anchor='w',
            tags="zero_label"
        )
        
        # 显示最大跌幅百分比
        self.chart_canvas.create_text(
            chart_right + 2, chart_bottom - 5,
            text=f"-{min_display_percentage:.2f}%",
            fill=self.text_color,
            font=("Arial", font_size),
            anchor='w',
            tags="min_label"
        )
        
        # 绘制价格线
        points = []
        for i, point in enumerate(chart_data):
            if point.get('price'):
                x = chart_left + (i / len(chart_data)) * chart_width
                # 根据相对于昨日收盘价的变化计算Y坐标
                price_change = point['price'] - base_price
                # 使用固定的最大变化值来计算Y坐标，确保比例正确
                # 涨跌范围正好对应图表的上下一半区域
                y = zero_y - (price_change / max_change) * (chart_height // 2)
                points.extend([x, y])
        
        # 绘制时间节点竖向虚线
        self.draw_time_grid(chart_left, chart_right, chart_top, chart_bottom, len(chart_data))
        
        # 绘制分时线
        if len(points) >= 4:
            self.chart_canvas.create_line(
                points,
                fill=self.text_color,
                width=1,
                smooth=True,
                tags="chart_line"
            )
            
            # 绘制最后一个点
            if len(points) >= 2:
                last_x = points[-2]
                last_y = points[-1]
                self.chart_canvas.create_oval(
                    last_x - 2, last_y - 2, last_x + 2, last_y + 2,
                    fill=self.text_color,
                    outline=self.text_color,
                    width=1,
                    tags="chart_point"
                )
    
    
    def draw_time_grid(self, chart_left, chart_right, chart_top, chart_bottom, data_points):
        """绘制时间节点竖向虚线"""
        # 定义半小时间隔的时间节点（基于A股交易时间）
        # 9:30-11:30 上午盘，13:00-15:00 下午盘
        # 假设数据点按时间均匀分布，共241个点（每分钟一个）
        
        if data_points < 60:  # 数据不足时不绘制时间线
            return
            
        # 计算半小时间隔的时间节点对应的数据点索引
        # 241个点对应4小时交易时间（240分钟）
        # 半小时 = 30分钟 = 30个数据点
        
        if data_points >= 241:
            # 完整交易日的半小时时间点
            key_times = [
                (0, "09:30"),      # 开盘
                (30, "10:00"),     # 10:00
                (60, "10:30"),     # 10:30
                (90, "11:00"),     # 11:00
                (120, "11:30"),    # 上午收盘
                (150, "13:00"),    # 下午开盘
                (180, "13:30"),    # 13:30
                (210, "14:00"),    # 14:00
                (240, "14:30"),    # 14:30
                (data_points - 1, "15:00")  # 收盘
            ]
        else:
            # 数据不足时按比例计算半小时间隔
            interval = max(30, data_points // 8)  # 至少30个点间隔
            key_times = []
            for i in range(0, data_points, interval):
                if i == 0:
                    key_times.append((i, "开盘"))
                elif i >= data_points - 1:
                    key_times.append((data_points - 1, "收盘"))
                else:
                    key_times.append((i, ""))
        
        # 绘制竖向虚线和时间标签
        font_size = max(6, min(8, (chart_bottom - chart_top) // 20))
        
        for point_index, time_label in key_times:
            if point_index < data_points:
                # 计算x坐标
                x = chart_left + (point_index / (data_points - 1)) * (chart_right - chart_left)
                
                # 判断是否为11:30（上午收盘线）
                is_morning_close = (point_index == 120 and data_points >= 241)
                
                # 绘制竖向虚线，使用与0轴横线相同的颜色
                self.chart_canvas.create_line(
                    x, chart_top, x, chart_bottom,
                    fill='#666666',
                    width=1,
                    dash=(2, 2),
                    tags="time_grid"
                )
                
                # 只在有标签时绘制时间文字
                if time_label:
                    # 11:30标签也使用更突出的颜色
                    label_color = '#aaaaaa' if is_morning_close else '#888888'
                    self.chart_canvas.create_text(
                        x, chart_bottom + 8,
                        text=time_label,
                        fill=self.text_color,
                        font=("Arial", font_size - 1),
                        anchor='n',
                        tags="time_label"
                    )
    
    def calculate_font_sizes(self, label_count=3):
        """根据窗口高度和标签数量动态计算字体大小（字体高度）"""
        # 计算每个标签可用的实际高度
        label_height = int(self.window_height / label_count)
        
        # 字体大小应该小于标签高度，为文字上下留出空间
        # 进一步减小比例，确保所有标签都能显示
        base_font_size = int(label_height * 0.5)
        
        return {
            'name': base_font_size,
            'price': base_font_size,
            'change': base_font_size
        }
    
    def update_font_sizes(self):
        """实时更新字体大小"""
        font_sizes = self.calculate_font_sizes()
        appearance = self.config_manager.get_appearance_settings()
        
        if not appearance['show_chart']:
            # 传统模式：更新单个标签的字体
            if hasattr(self, 'stock_label') and self.stock_label:
                self.stock_label.config(font=("Microsoft YaHei", font_sizes['price'], "bold"))
    
    def update_layout(self):
        """更新布局，重新计算信息栏宽度和标签布局"""
        appearance = self.config_manager.get_appearance_settings()
        
        if appearance['show_chart'] and hasattr(self, 'info_frame'):
            # 使用固定比例分配：分时图75%，股票信息25%
            self.update_layout_ratio()
            
            # 更新标签字体和布局
            self.update_label_layout()
            
            # 重新绘制分时图
            if hasattr(self, 'current_stock') and self.current_stock and hasattr(self, 'chart_canvas'):
                self.draw_chart(self.current_stock)
    
    def update_label_layout(self):
        """更新标签布局，根据实际标签数量平均分配高度"""
        # 根据show_price设置决定哪些标签应该存在
        show_price = self.config_manager.config.get('show_price', True)
        
        if show_price:
            # 显示所有标签
            label_attrs = ['stock_name_label', 'stock_price_label', 'stock_change_label']
        else:
            # 不显示现价标签
            label_attrs = ['stock_name_label', 'stock_change_label']
        
        # 统计实际存在的标签数量
        existing_labels = [(attr, getattr(self, attr)) for attr in label_attrs if hasattr(self, attr) and getattr(self, attr)]
        
        if not existing_labels:
            return
            
        label_count = len(existing_labels)
        
        # 根据标签数量计算字体大小
        font_sizes = self.calculate_font_sizes(label_count)
        
        # 定义每个标签的字体配置
        font_configs = {
            'stock_name_label': ('name', "normal"),
            'stock_price_label': ('price', "normal"),
            'stock_change_label': ('change', "normal")
        }
        
        # 更新每个存在的标签
        for label_attr, label in existing_labels:
            font_key, font_weight = font_configs.get(label_attr, ('name', "normal"))
            label.config(font=tk.font.Font(family="Microsoft YaHei", size=font_sizes[font_key], weight=font_weight))
            label.pack_forget()
            label.pack(fill=tk.BOTH, expand=True)
    
    def update_layout_ratio(self):
        """根据固定比例重新计算布局"""
        try:
            # 获取当前窗口宽度
            window_width = self.window_width
            
            # 固定比例分配：分时图75%，股票信息25%
            chart_width = int(window_width * 0.75)
            info_width = int(window_width * 0.25)
            
            # 保存当前的信息区域比例，用于切换分时图显示状态时的宽度计算
            self.info_ratio = 0.25  # 固定比例
            
            # 更新实际的框架宽度
            self.chart_frame.config(width=chart_width)
            self.info_frame.config(width=info_width)
            
            # 重新绘制分时图
            if hasattr(self, 'current_stock') and self.current_stock and hasattr(self, 'chart_canvas'):
                self.draw_chart(self.current_stock)
                
        except Exception as e:
            print(f"更新布局比例失败: {e}")
    

    
    def show_settings(self):
        """显示设置窗口"""
        if self.settings_window:
            # 如果设置窗口已存在，激活并置顶
            self.settings_window.window.lift()
            self.settings_window.window.attributes('-topmost', True)
            self.settings_window.window.after(100, lambda: self.settings_window.window.attributes('-topmost', False))
        else:
            # 创建新的设置窗口
            self.settings_window = SettingsWindow(self.config_manager, self.stock_manager, self.root, self)
            # 绑定设置窗口关闭事件，清理引用
            self.settings_window.window.protocol("WM_DELETE_WINDOW", lambda: self.on_settings_window_closed())
    
    def toggle_chart(self):
        """切换分时图显示"""
        self.config_manager.config['show_chart'] = not self.config_manager.config.get('show_chart', True)
        self.recreate_ui()
        self.config_manager.save_config()
    
    def recreate_ui(self):
        """重新创建UI界面"""
        if self.root:
            # 保存当前位置
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            
            # 获取当前配置中的背景颜色
            appearance = self.config_manager.get_appearance_settings()
            bg_color = appearance['bg_color']
            
            # 更新主窗口背景颜色
            self.root.configure(bg=bg_color)
            
            # 获取当前所有子组件，排除Toplevel窗口（如设置窗口）
            children_to_destroy = []
            for widget in self.root.winfo_children():
                # 只销毁Frame类组件，不销毁Toplevel窗口
                if isinstance(widget, tk.Frame):
                    children_to_destroy.append(widget)
            
            # 销毁Frame组件
            for widget in children_to_destroy:
                widget.destroy()
            
            # 重新创建界面
            self.create_ui_components()
            
            # 重新添加拖拽功能和右键菜单
            self.make_draggable(self.root)
            self.create_context_menu()
            
            # 恢复位置
            self.root.geometry(f"+{current_x}+{current_y}")
            
            # 立即更新股票显示，确保新UI显示最新数据
            if hasattr(self, 'current_stock') and self.current_stock:
                self._update_ui_with_stock_data(self.current_stock)
    
    def bind_mouse_events(self, widget):
        """为组件绑定鼠标悬停事件"""
        # 只需要为根组件绑定事件，因为事件会冒泡
        widget.bind('<Enter>', self.on_mouse_enter)
        widget.bind('<Leave>', self.on_mouse_leave)
    
    def on_mouse_enter(self, event):
        """鼠标进入时显示盘口信息"""
        if self.current_stock:
            self.show_pankou_info()
    
    def on_mouse_leave(self, event):
        """鼠标离开时隐藏盘口信息"""
        self.hide_pankou_info()
    
    def show_pankou_info(self):
        """显示盘口信息窗口"""
        if not self.current_stock:
            return
        
        # 获取主界面的透明度，盘口UI透明度为主界面的两倍
        appearance = self.config_manager.get_appearance_settings()
        main_alpha = appearance.get('alpha', 1.0)  # 默认1.0（不透明）
        pankou_alpha = min(main_alpha * 2, 1.0)  # 最多不超过1.0
        
        # 设置窗口样式
        bg_color = self.config_manager.get_appearance_settings()['bg_color']
        
        if not self.pankou_window:
            # 创建新的盘口信息窗口 - 无边框，根据数据弹性宽度
            self.pankou_window = tk.Toplevel(self.root)
            self.pankou_window.title(f"{self.current_stock['name']} 盘口")
            
            # 设置无边框样式
            self.pankou_window.overrideredirect(True)
            
            # 设置窗口属性
            self.pankou_window.resizable(False, False)
            self.pankou_window.attributes('-topmost', True)
            self.pankou_window.attributes('-alpha', pankou_alpha)
            self.pankou_window.configure(bg=bg_color)
            
            # 创建盘口信息框架 - 减少内边距
            self.pankou_frame = tk.Frame(self.pankou_window, bg=bg_color)
            self.pankou_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
            
            # 初始化标签字典
            self.pankou_labels = {
                'sell': [],
                'buy': []
            }
            
            # 创建卖盘标签
            for i in range(5):
                price_label = tk.Label(self.pankou_frame, bg=bg_color, fg="#00ff00", font=("Microsoft YaHei", 6),
                                     borderwidth=0, highlightthickness=0, padx=0, pady=0, height=1)
                price_label.grid(row=i, column=0, sticky=tk.E+tk.N+tk.S, padx=1, pady=0)
                
                volume_label = tk.Label(self.pankou_frame, bg=bg_color, fg="#00ff00", font=("Microsoft YaHei", 6),
                                     borderwidth=0, highlightthickness=0, padx=0, pady=0, height=1)
                volume_label.grid(row=i, column=1, sticky=tk.W+tk.N+tk.S, padx=3, pady=0)
                
                self.pankou_labels['sell'].append((price_label, volume_label))
            
            # 分隔线 - 更细的分隔线，更小的间距
            tk.Frame(self.pankou_frame, height=1, bg="#cccccc", borderwidth=0, highlightthickness=0).grid(row=5, column=0, columnspan=2, pady=0, sticky=tk.EW)
            
            # 创建买盘标签
            for i in range(5):
                price_label = tk.Label(self.pankou_frame, bg=bg_color, fg="#ff6b6b", font=("Microsoft YaHei", 6),
                                     borderwidth=0, highlightthickness=0, padx=0, pady=0, height=1)
                price_label.grid(row=i+6, column=0, sticky=tk.E+tk.N+tk.S, padx=1, pady=0)
                
                volume_label = tk.Label(self.pankou_frame, bg=bg_color, fg="#ff6b6b", font=("Microsoft YaHei", 6),
                                     borderwidth=0, highlightthickness=0, padx=0, pady=0, height=1)
                volume_label.grid(row=i+6, column=1, sticky=tk.W+tk.N+tk.S, padx=3, pady=0)
                
                self.pankou_labels['buy'].append((price_label, volume_label))
        else:
            # 更新窗口属性
            self.pankou_window.title(f"{self.current_stock['name']} 盘口")
            self.pankou_window.attributes('-alpha', pankou_alpha)
            self.pankou_window.configure(bg=bg_color)
            self.pankou_frame.configure(bg=bg_color)
        
        # 获取盘口数据，如果没有则使用空数据
        pankou_data = self.current_stock.get('pankou', {})
        sell_levels = pankou_data.get('sell', [])
        buy_levels = pankou_data.get('buy', [])
        
        # 确保有5个卖盘和买盘数据项
        while len(sell_levels) < 5:
            sell_levels.append({'price': 0, 'volume': 0})
        while len(buy_levels) < 5:
            buy_levels.append({'price': 0, 'volume': 0})
        
        # 更新卖盘标签
        for i, (price_label, volume_label) in enumerate(self.pankou_labels['sell']):
            if i < len(sell_levels):
                sell = sell_levels[-(i+1)]  # 从卖5到卖1显示
                if isinstance(sell, dict) and 'price' in sell and 'volume' in sell:
                    price = sell['price'] if sell['price'] > 0 else '--'
                    volume = sell['volume'] if sell['volume'] > 0 else '--'
                    price_label.config(text=f"{price:.2f}" if isinstance(price, (int, float)) else price, bg=bg_color, fg="#00ff00")
                    volume_label.config(text=f"{volume}", bg=bg_color, fg="#00ff00")
        
        # 更新买盘标签
        for i, (price_label, volume_label) in enumerate(self.pankou_labels['buy']):
            if i < len(buy_levels):
                buy = buy_levels[i]  # 从买1到买5显示
                if isinstance(buy, dict) and 'price' in buy and 'volume' in buy:
                    price = buy['price'] if buy['price'] > 0 else '--'
                    volume = buy['volume'] if buy['volume'] > 0 else '--'
                    price_label.config(text=f"{price:.2f}" if isinstance(price, (int, float)) else price, bg=bg_color, fg="#ff6b6b")
                    volume_label.config(text=f"{volume}", bg=bg_color, fg="#ff6b6b")
        
        # 自动调整窗口大小 - 让Tkinter自动计算所需宽度
        # 更新所有组件的布局
        self.pankou_window.update_idletasks()
        
        # 获取窗口所需的实际宽度和高度
        window_width = self.pankou_frame.winfo_reqwidth() + 6  # 加上左右边距
        window_height = self.pankou_frame.winfo_reqheight() + 6  # 加上上下边距
        
        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算初始位置 - 主窗口右侧
        x = self.root.winfo_rootx() + self.root.winfo_width()
        y = self.root.winfo_rooty()
        
        # 检查并调整位置，确保窗口不超出屏幕
        # 如果右侧超出屏幕，调整到主窗口左侧
        if x + window_width > screen_width:
            x = self.root.winfo_rootx() - window_width
        
        # 如果左侧超出屏幕，调整到屏幕左侧
        if x < 0:
            x = 0
        
        # 如果底部超出屏幕，调整到屏幕底部
        if y + window_height > screen_height:
            y = screen_height - window_height
        
        # 如果顶部超出屏幕，调整到屏幕顶部
        if y < 0:
            y = 0
        
        # 设置最终窗口位置和大小
        self.pankou_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 显示窗口
        self.pankou_window.deiconify()
    
    def hide_pankou_info(self):
        """隐藏盘口信息窗口"""
        if self.pankou_window:
            # 只隐藏窗口，不销毁，提高性能
            self.pankou_window.withdraw()
    
    def close_app(self):
        """关闭应用"""
        self.hide_pankou_info()
        self.root.quit()
    
    def on_settings_window_closed(self):
        """设置窗口关闭时的处理"""
        if self.settings_window:
            # 调用设置窗口的关闭处理方法
            self.settings_window.on_settings_close()
            # 清理引用
            self.settings_window = None