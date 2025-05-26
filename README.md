# 微信聊天导入 RAGFlow

这是一个用于将微信聊天内容快速导入到 RAGFlow 知识库的工具。

## 功能特点

- 支持全局快捷键（默认 Ctrl+Alt+V）快速导入选中的聊天内容
- 图形界面配置 API 密钥、知识库 ID 等信息
- 系统托盘运行，最小化到后台
- 配置文件自动保存

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 在配置界面中填写：
   - API Key：RAGFlow 的 API 密钥
   - 知识库 ID：目标知识库的 ID
   - API URL：RAGFlow 服务器地址（默认为 http://localhost:8000）
   - 快捷键：自定义快捷键组合（默认为 ctrl+alt+v）

3. 点击"保存配置"按钮保存设置

4. 在微信中选中要导入的聊天内容，按下配置的快捷键即可将内容导入到指定的知识库中

## 注意事项

- 程序会在后台运行，可以通过系统托盘图标控制显示/隐藏
- 配置文件保存在程序目录下的 config.json 文件中
- 确保 RAGFlow 服务器正常运行且可访问
