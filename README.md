# StockBar - 股票工具栏

一个基于Python和Tkinter开发的Windows股票工具栏应用，支持实时显示股票价格、分时图、盘口信息等功能。

## 功能特性

- 📈 实时显示股票价格和涨跌幅
- 📊 支持分时图显示，可切换显示/隐藏
- 🔄 自动更新股票数据（默认3秒）
- 🎨 支持自定义外观（透明度、背景颜色等）
- 📱 支持鼠标悬停显示盘口信息
- ⚙️ 丰富的设置选项
- 📱 支持多股票切换
- 🔍 自动根据股票类型调整最大涨跌幅

## 技术栈

- Python 3.7+
- Tkinter（GUI框架）
- Requests（网络请求）
- JSON（数据存储）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

```bash
python main.py
```

## 构建可执行文件

```bash
pyinstaller StockBar.spec
```

## 配置说明

应用首次运行会生成 `stock_config.json` 配置文件，包含以下主要配置项：

- `stocks`: 股票代码列表
- `window_width`: 窗口宽度
- `window_height`: 窗口高度
- `bg_opacity`: 背景透明度
- `bg_color`: 背景颜色
- `show_chart`: 是否显示分时图
- `chart_fixed_percentage`: 是否使用固定百分比
- `always_on_top`: 是否始终置顶

## 使用说明

1. **添加股票**：在设置界面的股票列表中添加股票代码
2. **切换股票**：使用鼠标滚轮或点击切换不同股票
3. **显示/隐藏分时图**：在设置界面勾选/取消勾选"显示分时图"
4. **调整外观**：在设置界面调整透明度、背景颜色等
5. **查看盘口信息**：将鼠标悬停在股票信息上

## 项目结构

```
stockbar/
├── app/                    # 主应用代码
│   ├── __init__.py         # 包初始化
│   ├── config.py           # 配置管理
│   ├── core.py             # 核心逻辑
│   ├── settings.py         # 设置界面
│   ├── stock.py            # 股票数据获取
│   ├── ui.py               # UI界面
│   └── utils.py            # 工具函数
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
├── setup.py                # 安装配置
├── StockBar.spec           # PyInstaller配置
└── stock_config.json       # 配置文件
```

## 开发说明

### 语法检查

```bash
python check_syntax.py
```

### 代码规范

- 遵循PEP8规范
- 使用类型注解
- 保持代码简洁清晰

## 注意事项

1. 本应用使用东方财富API获取股票数据，仅供学习和参考
2. 请勿用于商业用途
3. 股票数据可能存在延迟，请以实际交易数据为准
4. 建议定期更新应用以获取最新功能和修复

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 支持实时股票价格显示
- 支持分时图显示
- 支持盘口信息显示
- 支持自定义外观设置
- 支持多股票切换

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，欢迎通过GitHub Issues反馈。