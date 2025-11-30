#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据管理模块
"""

import logging
import requests
import json
import threading
import time
from queue import Queue

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class StockDataManager:
    """股票数据管理器
    
    负责股票数据的获取、解析和更新，支持异步获取数据和回调通知。
    使用队列和工作线程实现异步数据获取，避免阻塞主线程。
    """
    
    def __init__(self):
        """初始化股票数据管理器"""
        self.stocks = []  # 股票列表
        self.current_stock_index = 0  # 当前显示的股票索引
        self.is_fetching = False  # 是否正在获取数据
        self.fetch_queue = Queue()  # 数据获取队列
        self.update_callback = None  # UI更新回调函数
        self.start_fetch_worker()  # 启动数据获取工作线程
    
    def get_current_stock(self):
        """获取当前显示的股票"""
        if not self.stocks:
            return None
        
        stock = self.stocks[self.current_stock_index % len(self.stocks)]
        self.current_stock_index += 1
        return stock
    
    def set_update_callback(self, callback):
        """设置UI更新回调函数"""
        self.update_callback = callback
    
    def start_fetch_worker(self):
        """启动数据获取工作线程"""
        def worker():
            while True:
                try:
                    # 从队列中获取股票和回调
                    stock, callback = self.fetch_queue.get(timeout=1)
                    
                    # 在后台线程中获取数据
                    self.fetch_stock_data_sync(stock)
                    
                    # 通过回调通知主线程更新UI
                    if callback:
                        callback(stock)
                    
                    self.fetch_queue.task_done()
                    
                except:
                    # 队列为空或超时，继续等待
                    continue
        
        # 启动工作线程
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def fetch_stock_data_async(self, stock, callback=None):
        """异步获取股票数据"""
        # 将股票和回调函数放入队列
        self.fetch_queue.put((stock, callback or self.update_callback))
    
    def fetch_stock_data(self, stock):
        """保持向后兼容的同步方法"""
        self.fetch_stock_data_async(stock)
    
    def fetch_stock_data_sync(self, stock):
        """同步获取股票数据（在后台线程中运行）"""
        try:
            url = f"https://api.duishu.com/hangqing/stock/fenshi?time_type=F&code={stock['symbol']}&get_zhutu=1&get_pankou=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.duishu.com/',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_text = response.text
                
                if '\\u' in response_text:
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError:
                        decoded_text = response_text.encode().decode('unicode_escape')
                        data = json.loads(decoded_text)
                else:
                    data = response.json()
                
                if data.get('code') == 10000 and 'data' in data:
                    stock_data = data['data']
                    logger.debug(f"API返回的股票数据: {stock_data.keys()}")
                    if 'pankou' in stock_data:
                        logger.debug(f"API返回的盘口数据: {stock_data['pankou']}")
                    
                    # 解析股票数据
                    success = self.parse_stock_data(stock, stock_data)
                    if not success:
                        self.parse_stock_data_fallback(stock, stock_data)
                    
                    # 获取股票名称
                    if not stock.get('name') or stock['name'].startswith('股票'):
                        self.fetch_stock_name(stock)
                else:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"股票 {stock['symbol']} API返回错误: {error_msg}")
                    
                    if 'code' in error_msg.lower() or '不存在' in error_msg:
                        self.try_fix_stock_code(stock)
            else:
                logger.error(f"股票 {stock['symbol']} HTTP请求失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"股票 {stock['symbol']} 请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"股票 {stock['symbol']} 网络请求失败: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"股票 {stock['symbol']} 数据解析失败: {e}")
        except Exception as e:
            logger.error(f"股票 {stock['symbol']} 获取数据失败: {e}")
    
    def parse_stock_data(self, stock, stock_data):
        """解析股票数据"""
        try:
            # 解析股票名称
            self.parse_stock_name(stock, stock_data)
            
            # 提取分时数据
            self.extract_chart_data(stock, stock_data)
            
            # 解析盘口数据 - 无论价格解析是否成功，都要解析盘口数据
            self.parse_pankou_data(stock, stock_data)
            
            # 解析当前价格
            return self.parse_current_price(stock, stock_data)
            
        except Exception as e:
            logger.error(f"解析股票数据时出错: {e}")
            return False
    
    def parse_stock_name(self, stock, stock_data):
        """解析股票名称"""
        # 获取股票名称
        stock_name = None
        if 'name' in stock_data:
            stock_name = stock_data['name']
        elif 'stock_name' in stock_data:
            stock_name = stock_data['stock_name']
        elif 'title' in stock_data:
            stock_name = stock_data['title']
        elif 'display_name' in stock_data:
            stock_name = stock_data['display_name']
        
        if stock_name:
            stock['name'] = stock_name
            logger.info(f"获取到股票名称: {stock['symbol']} -> {stock_name}")
    
    def parse_pankou_data(self, stock, stock_data):
        """解析盘口数据"""
        if 'pankou' in stock_data and stock_data['pankou']:
            pankou = stock_data['pankou']
            logger.debug(f"获取到盘口数据: {pankou}")
            
            # 解析5档盘口数据
            stock['pankou'] = {}
            
            # 买盘数据（5档）- API返回格式：b1_p, b1_v, b2_p, b2_v...
            buy_levels = []
            for i in range(1, 6):
                buy_price_key = f'b{i}_p'
                buy_volume_key = f'b{i}_v'
                
                if buy_price_key in pankou and buy_volume_key in pankou:
                    buy_levels.append({
                        'price': pankou[buy_price_key],
                        'volume': pankou[buy_volume_key]
                    })
                    logger.debug(f"解析买{i}数据: 价格={pankou[buy_price_key]}, 成交量={pankou[buy_volume_key]}")
            stock['pankou']['buy'] = buy_levels
            logger.debug(f"解析完成买盘数据: {buy_levels}")
            
            # 卖盘数据（5档）- API返回格式：a1_p, a1_v, a2_p, a2_v...
            sell_levels = []
            for i in range(1, 6):
                sell_price_key = f'a{i}_p'
                sell_volume_key = f'a{i}_v'
                
                if sell_price_key in pankou and sell_volume_key in pankou:
                    sell_levels.append({
                        'price': pankou[sell_price_key],
                        'volume': pankou[sell_volume_key]
                    })
                    logger.debug(f"解析卖{i}数据: 价格={pankou[sell_price_key]}, 成交量={pankou[sell_volume_key]}")
            stock['pankou']['sell'] = sell_levels
            logger.debug(f"解析完成卖盘数据: {sell_levels}")
    
    def parse_current_price(self, stock, stock_data):
        """解析当前价格"""
        # 从分时数据获取最新价格
        if 'zhutu' in stock_data:
            zhutu = stock_data['zhutu']
            pre_close = zhutu.get('pre_close')
            
            # 保存昨日收盘价到股票对象
            if pre_close and pre_close > 0:
                stock['yesterday_close'] = pre_close
            
            if 'left_line_list' in zhutu and zhutu['left_line_list']:
                left_line_list = zhutu['left_line_list']
                
                for line in left_line_list:
                    if 'data' in line and line['data']:
                        price_data = line['data']
                        
                        current_price = None
                        for price in reversed(price_data):
                            if price and isinstance(price, (int, float)) and price > 0:
                                current_price = price
                                break
                        
                        if current_price and pre_close and pre_close > 0:
                            change_percent = ((current_price - pre_close) / pre_close) * 100
                            stock['price'] = f"{current_price:.2f}"
                            stock['change'] = f"{change_percent:+.2f}%"
                            
                            stock_name_display = stock.get('name', 'Unknown')
                            logger.info(f"股票 {stock['symbol']} ({stock_name_display}) 价格更新: {current_price:.2f} {change_percent:+.2f}%")
                            return True
                        elif current_price:
                            stock['price'] = f"{current_price:.2f}"
                            stock['change'] = "+0.00%"
                            
                            stock_name_display = stock.get('name', 'Unknown')
                            logger.info(f"股票 {stock['symbol']} ({stock_name_display}) 价格更新: {current_price:.2f} (无涨跌幅)")
                            return True
        
        # 备用方法 - 从stock_data直接获取价格
        for price_key in ['current_price', 'current', 'last_price', 'price']:
            if price_key in stock_data:
                current_price = stock_data[price_key]
                if isinstance(current_price, (int, float)) and current_price > 0:
                    pre_close = stock_data.get('pre_close', current_price)
                    
                    if pre_close and pre_close > 0:
                        change_percent = ((current_price - pre_close) / pre_close) * 100
                        stock['price'] = f"{current_price:.2f}"
                        stock['change'] = f"{change_percent:+.2f}%"
                    else:
                        stock['price'] = f"{current_price:.2f}"
                        stock['change'] = "+0.00%"
                    
                    stock_name_display = stock.get('name', 'Unknown')
                    logger.info(f"股票 {stock['symbol']} ({stock_name_display}) 从{price_key}更新价格: {stock['price']} {stock['change']}")
                    return True
        
        # 从盘口获取当前价格
        if 'pankou' in stock_data and stock_data['pankou']:
            pankou = stock_data['pankou']
            for price_key in ['current_price', 'current', 'last_price', 'price']:
                if price_key in pankou:
                    current_price = pankou[price_key]
                    if isinstance(current_price, (int, float)) and current_price > 0:
                        pre_close = pankou.get('pre_close', current_price)
                        
                        if pre_close and pre_close > 0:
                            change_percent = ((current_price - pre_close) / pre_close) * 100
                            stock['price'] = f"{current_price:.2f}"
                            stock['change'] = f"{change_percent:+.2f}%"
                        else:
                            stock['price'] = f"{current_price:.2f}"
                            stock['change'] = "+0.00%"
                        
                        stock_name_display = stock.get('name', 'Unknown')
                        logger.info(f"股票 {stock['symbol']} ({stock_name_display}) 从盘口{price_key}更新价格: {stock['price']} {stock['change']}")
                        return True
        
        logger.warning(f"股票 {stock['symbol']} 无法解析价格数据")
        return False
    
    def extract_chart_data(self, stock, stock_data):
        """提取分时数据"""
        try:
            chart_data = []
            
            if 't' in stock_data and 'zhutu' in stock_data:
                timestamps = stock_data['t']
                zhutu = stock_data['zhutu']
                
                price_series = None
                if 'left_line_list' in zhutu and zhutu['left_line_list']:
                    for line in zhutu['left_line_list']:
                        if 'data' in line and line['data']:
                            price_series = line['data']
                            break
                
                if price_series and timestamps:
                    min_len = min(len(price_series), len(timestamps))
                    for i in range(min_len):
                        if price_series[i] and timestamps[i]:
                            chart_data.append({
                                'time': timestamps[i],
                                'price': price_series[i]
                            })
            
            stock['chart_data'] = chart_data
            
            if chart_data:
                logger.info(f"股票 {stock['symbol']} 提取到 {len(chart_data)} 个分时数据点")
            
        except Exception as e:
            logger.error(f"提取分时数据失败: {e}")
            stock['chart_data'] = []
    
    def parse_stock_data_fallback(self, stock, stock_data):
        """备用解析方法"""
        try:
            if 'zhutu' in stock_data:
                zhutu = stock_data['zhutu']
                
                for key in ['left_line_list', 'right_line_list']:
                    if key in zhutu:
                        lines = zhutu[key]
                        for line in lines:
                            if 'data' in line and line['data']:
                                data = line['data']
                                if data and len(data) > 0:
                                    for value in reversed(data):
                                        if value and isinstance(value, (int, float)) and value > 0:
                                            stock['price'] = f"{value:.2f}"
                                            stock['change'] = "+0.00%"
                                            logger.info(f"股票 {stock['symbol']} 使用备用方法获取价格: {value:.2f}")
                                            return True
            return False
            
        except Exception as e:
            logger.error(f"备用解析方法失败: {e}")
            return False
    
    def fetch_stock_name(self, stock):
        """获取股票名称"""
        try:
            # 检查是否已经尝试获取过股票名称，避免重复调用
            if stock.get('_name_fetched', False):
                return False
            
            symbol = stock['symbol']
            
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('6'):
                    full_symbol = f"sh{symbol}"
                elif symbol.startswith(('0', '3')):
                    full_symbol = f"sz{symbol}"
                else:
                    full_symbol = symbol
            else:
                full_symbol = symbol
            
            # 新浪财经API
            url = f"https://hq.sinajs.cn/list={full_symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn/',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                if f'var hq_str_{full_symbol}=' in content:
                    start = content.find('"') + 1
                    end = content.rfind('"')
                    if start > 0 and end > start:
                        stock_info = content[start:end]
                        parts = stock_info.split(',')
                        
                        if len(parts) > 0 and parts[0]:
                            stock_name = parts[0].strip()
                            if stock_name and not stock_name.startswith('股票'):
                                stock['name'] = stock_name
                                stock['_name_fetched'] = True  # 标记为已获取
                                logger.info(f"获取到股票名称: {stock['symbol']} -> {stock_name}")
                                return True
            
            # 东方财富API
            result = self.fetch_stock_name_eastmoney(stock)
            if result:
                stock['_name_fetched'] = True  # 标记为已获取
            return result
            
        except Exception as e:
            logger.error(f"获取股票名称失败: {e}")
            stock['_name_fetched'] = True  # 即使失败也标记为已尝试
            return False
    
    def fetch_stock_name_eastmoney(self, stock):
        """从东方财富获取股票名称"""
        try:
            symbol = stock['symbol']
            
            if symbol.startswith('6'):
                market = '1'
                code = symbol
            elif symbol.startswith(('0', '3')):
                market = '0'
                code = symbol
            else:
                return False
            
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{code}&fields=f58,f59"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com/',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('f58'):
                    stock_name = data['data']['f58']
                    if stock_name:
                        stock['name'] = stock_name
                        logger.info(f"从东方财富获取到股票名称: {stock['symbol']} -> {stock_name}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"从东方财富获取股票名称失败: {e}")
            return False
    
    def search_stock_by_name(self, stock_name):
        """根据股票名称搜索股票代码"""
        try:
            if not stock_name or not isinstance(stock_name, str):
                return None
            
            # 使用新浪财经的股票搜索API
            url = f"https://suggest3.sinajs.cn/suggest/type=11&key={stock_name}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn/',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                # 解析返回数据，格式：var suggestdata = [["股票名称","股票代码","..."],...]
                start = content.find('[[')
                end = content.rfind(']]')
                if start > 0 and end > start:
                    data_str = content[start:end+2]
                    stock_list = json.loads(data_str)
                    
                    if stock_list and isinstance(stock_list, list):
                        for stock_info in stock_list:
                            if isinstance(stock_info, list) and len(stock_info) >= 2:
                                name = stock_info[0]
                                code = stock_info[1]
                                # 只返回A股股票代码（6位数字）
                                if code.isdigit() and len(code) == 6:
                                    logger.info(f"根据股票名称 '{stock_name}' 搜索到: {name} ({code})")
                                    return code
            
            # 东方财富搜索API
            return self.search_stock_by_name_eastmoney(stock_name)
            
        except Exception as e:
            logger.error(f"搜索股票名称失败: {e}")
            return None
    
    def try_fix_stock_code(self, stock):
        """尝试修复无效的股票代码"""
        try:
            logger.info(f"尝试修复股票代码: {stock['symbol']}")
            # 这里可以添加修复逻辑，比如检查股票代码格式、尝试搜索正确代码等
            # 目前只是记录日志
            return False
        except Exception as e:
            logger.error(f"修复股票代码失败: {e}")
            return False
    
    def search_stock_by_name_eastmoney(self, stock_name):
        """从东方财富搜索股票代码"""
        try:
            if not stock_name:
                return None
            
            # 使用正确的东方财富搜索API
            url = f"https://searchapi.eastmoney.com/api/suggest/get?input={stock_name}&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=10"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com/',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('QuotationCodeTable') and data['QuotationCodeTable'].get('Data'):
                    stock_list = data['QuotationCodeTable']['Data']
                    for stock_info in stock_list:
                        code = stock_info.get('Code')
                        name = stock_info.get('Name')
                        # 确保是A股股票（6位数字代码）
                        if code and name and isinstance(code, str) and code.isdigit() and len(code) == 6:
                            logger.info(f"从东方财富搜索到股票: {name} ({code})")
                            return code
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"从东方财富搜索股票名称网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"从东方财富搜索股票名称数据解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"从东方财富搜索股票名称失败: {e}")
            return None