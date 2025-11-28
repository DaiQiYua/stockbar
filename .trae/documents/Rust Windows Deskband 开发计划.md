# Rust Windows Deskband 开发计划

## 项目概述
使用 Rust 开发一个 Windows Deskband 程序，在任务栏上显示 CPU 和内存占用情况，支持 Windows 10 和 Windows 11。

## 技术栈
- **Rust**：主要开发语言
- **windows-rs**：微软官方 Windows API 绑定库
- **Win32 COM API**：实现 DeskBand 功能

## 实现步骤

### 1. 项目初始化
- 创建 Rust 库项目：`cargo new --lib rust_deskband`
- 配置 `Cargo.toml`，添加 `windows-rs` 依赖
- 配置编译目标为 Windows DLL

### 2. 定义 COM 接口
使用 `windows-rs` 库定义 DeskBand 所需的 COM 接口：
- `IDeskBand`：DeskBand 核心接口
- `IObjectWithSite`：站点管理接口
- `IPersistStream`：持久化接口
- `IDeskBand2`：扩展 DeskBand 接口（可选）
- `IDeskBandInfo`：DeskBand 信息接口（可选）

### 3. 实现 DeskBand 组件
创建 DeskBand 组件结构体，实现以下功能：
- COM 接口的查询和释放（`QueryInterface`、`AddRef`、`Release`）
- 站点管理（`SetSite`、`GetSite`）
- 窗口创建和消息处理
- 尺寸计算和位置调整

### 4. 实现 CPU 和内存占用获取
使用 Windows API 获取系统资源信息：
- `GetSystemTimes`：获取 CPU 时间
- `GlobalMemoryStatusEx`：获取内存使用情况
- 实现定时更新机制，每秒更新一次数据

### 5. 实现 UI 绘制
- 处理窗口绘制消息（`WM_PAINT`）
- 使用 GDI 或 Direct2D 绘制文本和图形
- 显示 CPU 和内存占用百分比

### 6. 实现 COM 注册和反注册
- 实现 `DllRegisterServer` 函数：注册 COM 组件和 DeskBand 类别
- 实现 `DllUnregisterServer` 函数：注销 COM 组件
- 配置注册表项，使资源管理器能够识别 DeskBand

### 7. 编译和测试
- 编译生成 DLL 文件
- 使用 `regsvr32` 注册 DLL
- 在任务栏上启用 DeskBand，测试功能

## 关键注意事项

1. **COM 接口安全**：确保正确实现 COM 引用计数
2. **线程安全**：处理好不同线程间的调用
3. **资源管理**：正确释放 Windows 资源
4. **兼容性**：确保代码在 Windows 10 和 Windows 11 上都能正常工作
5. **错误处理**：妥善处理 Windows API 调用可能返回的错误

## 预期成果
- 生成一个 Rust 编写的 Windows Deskband DLL
- 在任务栏上显示实时 CPU 和内存占用
- 支持 Windows 10 和 Windows 11 系统
- 提供注册和反注册脚本

## 后续优化方向
- 添加配置选项，允许用户自定义显示样式
- 支持更多系统指标（如磁盘使用率、网络流量等）
- 添加悬停提示，显示详细信息
- 支持主题适配，跟随系统深色/浅色模式