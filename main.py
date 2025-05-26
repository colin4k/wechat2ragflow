import sys
import json
import os
import pyperclip
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import threading

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "api_key": "",
            "knowledge_base_id": "",
            "api_url": "http://localhost:8000",
            "hotkey": "<ctrl>+<alt>+v"
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

class HotkeyThread(threading.Thread):
    def __init__(self, hotkey, callback):
        super().__init__()
        self.hotkey = hotkey
        self.callback = callback
        self.running = True
        self.listener = None
        self.daemon = True

    def on_activate(self):
        self.callback()

    def run(self):
        try:
            hotkey_parts = self.hotkey.replace("ctrl", "<ctrl>").replace("alt", "<alt>").replace("shift", "<shift>").split("+")
            hotkey_parts = [part.strip() for part in hotkey_parts]
            
            with keyboard.GlobalHotKeys({
                "+".join(hotkey_parts): self.on_activate
            }) as self.listener:
                self.listener.join()
        except Exception as e:
            print(f"Hotkey error: {str(e)}")

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()

class MainWindow:
    def __init__(self):
        self.config = Config()
        self.root = tk.Tk()
        self.root.title("微信聊天导入 RAGFlow")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.setup_hotkey()
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建系统托盘图标
        self.setup_tray()

    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # API Key
        ttk.Label(main_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=self.config.config["api_key"])
        ttk.Entry(main_frame, textvariable=self.api_key_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Knowledge Base ID
        ttk.Label(main_frame, text="知识库 ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.kb_var = tk.StringVar(value=self.config.config["knowledge_base_id"])
        ttk.Entry(main_frame, textvariable=self.kb_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)

        # API URL
        ttk.Label(main_frame, text="API URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.config.config["api_url"])
        ttk.Entry(main_frame, textvariable=self.url_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Hotkey
        ttk.Label(main_frame, text="快捷键:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.hotkey_var = tk.StringVar(value=self.config.config["hotkey"])
        ttk.Entry(main_frame, textvariable=self.hotkey_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Save Button
        ttk.Button(main_frame, text="保存配置", command=self.save_config).grid(row=4, column=0, columnspan=2, pady=20)

    def setup_tray(self):
        # 在 macOS 上，我们可以使用 Dock 图标
        self.root.iconify = self.hide_window
        self.root.deiconify = self.show_window

    def setup_hotkey(self):
        self.hotkey_thread = HotkeyThread(self.config.config["hotkey"], self.process_clipboard)
        self.hotkey_thread.start()

    def save_config(self):
        self.config.config["api_key"] = self.api_key_var.get()
        self.config.config["knowledge_base_id"] = self.kb_var.get()
        self.config.config["api_url"] = self.url_var.get()
        self.config.config["hotkey"] = self.hotkey_var.get()
        self.config.save_config()
        
        # 重新设置快捷键
        self.hotkey_thread.stop()
        self.setup_hotkey()
        
        messagebox.showinfo("成功", "配置已保存")

    def process_clipboard(self):
        try:
            text = pyperclip.paste()
            if not text:
                return

            headers = {
                "Authorization": f"Bearer {self.config.config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "knowledge_base_id": self.config.config["knowledge_base_id"],
                "content": text
            }

            response = requests.post(
                f"{self.config.config['api_url']}/api/v1/documents",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                messagebox.showinfo("成功", "文本已成功导入到知识库")
            else:
                messagebox.showerror("错误", f"导入失败: {response.text}")

        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()

    def on_closing(self):
        self.hide_window()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()
