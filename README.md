# 微信聊天导入 RAGFlow

这是一个用于将微信聊天内容快速导入到 RAGFlow 知识库的工具。通过全局快捷键，可以方便地将选中的文本导入到指定的知识库中。

## 功能特点

- 支持全局快捷键（默认 Ctrl+Alt+V）
- 跨平台支持（Windows、macOS、Linux）
- 自动保存和恢复剪贴板内容
- 图形界面配置
- 系统托盘运行

## 系统要求

- Python 3.6 或更高版本
- 操作系统：Windows、macOS 或 Linux

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 在配置界面中设置：
   - API Key：RAGFlow 的 API 密钥
   - 知识库 ID：目标知识库的 ID
   - 文档 ID：目标文档的 ID
   - API URL：RAGFlow 的 API 地址
   - 快捷键：自定义快捷键组合

3. 点击"保存配置"按钮保存设置

4. 在微信中选择要导入的文本，按下快捷键（默认 Ctrl+Alt+V）即可将文本导入到知识库

## 注意事项

### macOS 用户
- 首次运行时需要在系统偏好设置中授予辅助功能权限
- 程序使用 AppleScript 获取选中的文本，确保微信在前台运行

### Windows/Linux 用户
- 程序使用 pynput 模拟复制操作，确保微信在前台运行
- 如果快捷键不生效，请检查是否有其他程序占用了相同的快捷键

## 常见问题

1. 快捷键不生效
   - 检查是否有其他程序占用了相同的快捷键
   - 确保程序有足够的系统权限
   - 在 macOS 上，确保已授予辅助功能权限

2. 无法获取选中的文本
   - 确保微信在前台运行
   - 确保已正确选中文本
   - 检查系统权限设置

3. API 调用失败
   - 检查 API Key 是否正确
   - 检查知识库 ID 和文档 ID 是否正确
   - 检查 API URL 是否可访问
   - 检查网络连接

## 开发说明

### 文本获取方式
- macOS：使用 AppleScript 获取选中的文本
- Windows/Linux：使用 pynput 模拟复制操作

### 配置文件
配置文件 `config.json` 包含以下字段：
- api_key：RAGFlow 的 API 密钥
- knowledge_base_id：知识库 ID
- document_id：文档 ID
- api_url：API 地址
- hotkey：快捷键设置

## 许可证

MIT License
