import sys
import json
import os
import pyperclip
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import threading
import time
import subprocess

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "api_key": "",
            "knowledge_base_id": "",
            "document_id": "",
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
        print(f"初始化热键线程，热键设置为: {hotkey}")  # 调试信息

    def on_activate(self):
        print("热键被触发")  # 调试信息
        self.callback()

    def run(self):
        try:
            # 转换热键格式
            hotkey_parts = []
            for part in self.hotkey.split('+'):
                part = part.strip().lower()
                if part.startswith('<') and part.endswith('>'):
                    part = part[1:-1]
                if part in ['ctrl', 'alt', 'shift', 'cmd']:
                    hotkey_parts.append(f"<{part}>")
                else:
                    # 对于普通按键，直接使用字符
                    hotkey_parts.append(part)
            
            hotkey_str = '+'.join(hotkey_parts)
            print(f"转换后的热键格式: {hotkey_str}")  # 调试信息
            
            with keyboard.GlobalHotKeys({
                hotkey_str: self.on_activate
            }) as self.listener:
                print("热键监听器已启动")  # 调试信息
                self.listener.join()
        except Exception as e:
            print(f"热键监听器错误: {str(e)}")  # 调试信息
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈

    def stop(self):
        print("停止热键监听器")  # 调试信息
        self.running = False
        if self.listener:
            self.listener.stop()

class HotkeyEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.current_keys = set()
        
        # 设置只读
        self.configure(state='readonly')
        
        # 提示文本
        self.placeholder = "点击此处并按下快捷键组合"
        self.insert(0, self.placeholder)
        self.configure(foreground='gray')
        
        # 绑定点击事件
        self.bind('<Button-1>', self.on_click)
        self.bind('<FocusOut>', self.on_focus_out)

    def on_click(self, event):
        # 清除当前内容
        self.configure(state='normal')  # 临时允许编辑
        self.delete(0, tk.END)
        self.configure(foreground='black')
        self.current_keys.clear()  # 清空当前按键集合
        self.configure(state='readonly')  # 恢复只读状态
        
        # 绑定所有键盘事件
        self.master.bind_all('<Key>', self.on_key)
        print("开始监听键盘事件")  # 调试信息

    def on_focus_out(self, event):
        # 解绑所有键盘事件
        self.master.unbind_all('<Key>')
        print("停止监听键盘事件")  # 调试信息
        
        if not self.get() or self.get() == self.placeholder:
            self.configure(state='normal')  # 临时允许编辑
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.configure(foreground='gray')
            self.configure(state='readonly')  # 恢复只读状态

    def on_key(self, event):
        print(f"按键事件: {event.keysym}")  # 调试信息
        
        # 处理修饰键
        if event.keysym in ('Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R'):
            if event.keysym not in self.current_keys:
                self.current_keys.add(event.keysym)
                self.update_hotkey_display()
            return
            
        # 处理 Escape 键
        if event.keysym == 'Escape':
            self.master.unbind_all('<Key>')
            self.current_keys.clear()
            self.configure(state='normal')  # 临时允许编辑
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.configure(foreground='gray')
            self.configure(state='readonly')  # 恢复只读状态
            return
            
        # 更新当前按键集合
        if event.keysym not in self.current_keys:
            self.current_keys.add(event.keysym)
            self.update_hotkey_display()

    def update_hotkey_display(self):
        if not self.current_keys:
            self.configure(state='normal')  # 临时允许编辑
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.configure(foreground='gray')
            self.configure(state='readonly')  # 恢复只读状态
            return

        # 转换按键为显示格式
        display_keys = []
        for key in sorted(self.current_keys):
            if key.lower() in ('control_l', 'control_r'):
                display_keys.append('Ctrl')
            elif key.lower() in ('alt_l', 'alt_r'):
                display_keys.append('Alt')
            elif key.lower() in ('shift_l', 'shift_r'):
                display_keys.append('Shift')
            elif key.lower() in ('meta_l', 'meta_r'):
                display_keys.append('Cmd')
            else:
                display_keys.append(key.capitalize())

        # 更新显示
        self.configure(state='normal')  # 临时允许编辑
        self.delete(0, tk.END)
        hotkey_text = '+'.join(display_keys)
        self.insert(0, hotkey_text)
        self.configure(foreground='black')
        self.configure(state='readonly')  # 恢复只读状态
        print(f"当前按键: {hotkey_text}")  # 调试信息

    def get_hotkey(self):
        """获取标准格式的热键字符串"""
        if not self.current_keys:
            return ""
            
        hotkey_parts = []
        for key in sorted(self.current_keys):
            if key.lower() in ('control_l', 'control_r'):
                hotkey_parts.append('ctrl')
            elif key.lower() in ('alt_l', 'alt_r'):
                hotkey_parts.append('alt')
            elif key.lower() in ('shift_l', 'shift_r'):
                hotkey_parts.append('shift')
            elif key.lower() in ('meta_l', 'meta_r'):
                hotkey_parts.append('cmd')
            else:
                hotkey_parts.append(key.lower())
        
        return '+'.join(hotkey_parts)

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

        # Document ID
        ttk.Label(main_frame, text="文档 ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.doc_var = tk.StringVar(value=self.config.config["document_id"])
        ttk.Entry(main_frame, textvariable=self.doc_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)

        # API URL
        ttk.Label(main_frame, text="API URL:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.config.config["api_url"])
        ttk.Entry(main_frame, textvariable=self.url_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Hotkey
        ttk.Label(main_frame, text="快捷键:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.hotkey_entry = HotkeyEntry(main_frame, width=40)
        self.hotkey_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 设置初始值
        if self.config.config["hotkey"]:
            # 将 pynput 格式的热键转换为显示格式
            hotkey = self.config.config["hotkey"]
            hotkey = hotkey.replace("<", "").replace(">", "")
            hotkey = hotkey.replace("ctrl", "Ctrl").replace("alt", "Alt").replace("shift", "Shift").replace("cmd", "Cmd")
            
            # 更新显示
            self.hotkey_entry.configure(state='normal')
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, hotkey)
            self.hotkey_entry.configure(foreground='black')
            self.hotkey_entry.configure(state='readonly')
            
            # 更新当前按键集合
            self.hotkey_entry.current_keys.clear()
            for key in hotkey.split('+'):
                if key.lower() == 'ctrl':
                    self.hotkey_entry.current_keys.add('Control_L')
                elif key.lower() == 'alt':
                    self.hotkey_entry.current_keys.add('Alt_L')
                elif key.lower() == 'shift':
                    self.hotkey_entry.current_keys.add('Shift_L')
                elif key.lower() == 'cmd':
                    self.hotkey_entry.current_keys.add('Meta_L')
                else:
                    self.hotkey_entry.current_keys.add(key.upper())

        # Save Button
        ttk.Button(main_frame, text="保存配置", command=self.save_config).grid(row=5, column=0, columnspan=2, pady=20)

    def setup_tray(self):
        # 在 macOS 上，我们可以使用 Dock 图标
        self.root.iconify = self.hide_window
        self.root.deiconify = self.show_window

    def setup_hotkey(self):
        print(f"设置热键: {self.config.config['hotkey']}")  # 调试信息
        if hasattr(self, 'hotkey_thread'):
            self.hotkey_thread.stop()
        self.hotkey_thread = HotkeyThread(self.config.config["hotkey"], self.process_clipboard)
        self.hotkey_thread.start()

    def save_config(self):
        self.config.config["api_key"] = self.api_key_var.get()
        self.config.config["knowledge_base_id"] = self.kb_var.get()
        self.config.config["document_id"] = self.doc_var.get()
        self.config.config["api_url"] = self.url_var.get()
        
        # 获取新的快捷键
        new_hotkey = self.hotkey_entry.get_hotkey()
        if new_hotkey:
            # 转换热键格式
            hotkey_parts = []
            for part in new_hotkey.split('+'):
                part = part.strip().lower()
                if part in ['ctrl', 'alt', 'shift', 'cmd']:
                    hotkey_parts.append(f"<{part}>")
                else:
                    hotkey_parts.append(part)
            
            self.config.config["hotkey"] = '+'.join(hotkey_parts)
        
        self.config.save_config()
        messagebox.showinfo("成功", "配置已保存，重启程序后快捷键生效")

    def get_selected_text(self):
        """获取选中的文本"""
        if sys.platform == 'darwin':  # macOS
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell process frontAppName
                    keystroke "c" using command down
                    delay 0.1
                end tell
            end tell
            return the clipboard
            '''
            try:
                proc = subprocess.run(['osascript', '-e', script], 
                                    capture_output=True, text=True)
                if proc.returncode == 0:
                    return proc.stdout.strip()
                else:
                    print(f"AppleScript 执行失败: {proc.stderr}")
                    return ""
            except Exception as e:
                print(f"执行 AppleScript 时出错: {str(e)}")
                return ""
        else:  # Windows/Linux
            try:
                # 使用 pynput 模拟复制操作
                c = keyboard.Controller()
                if sys.platform == 'win32':  # Windows
                    c.press(keyboard.Key.ctrl)
                    c.press('c')
                    c.release('c')
                    c.release(keyboard.Key.ctrl)
                else:  # Linux
                    c.press(keyboard.Key.ctrl)
                    c.press('c')
                    c.release('c')
                    c.release(keyboard.Key.ctrl)
                
                # 等待复制完成
                time.sleep(0.1)
                
                # 获取剪贴板内容
                return pyperclip.paste()
            except Exception as e:
                print(f"使用 pynput 获取文本时出错: {str(e)}")
                return ""

    def process_clipboard(self):
        try:
            print("开始处理选中文本")  # 调试信息
            
            # 保存当前剪贴板内容
            old_clipboard = pyperclip.paste()
            print(f"保存的原始剪贴板内容: {old_clipboard}")  # 调试信息
            
            # 获取选中的文本
            text = self.get_selected_text()
            print(f"获取到的文本: {text}")  # 调试信息
            
            # 恢复原来的剪贴板内容
            pyperclip.copy(old_clipboard)
            print(f"已恢复原始剪贴板内容")  # 调试信息
            
            if not text:
                print("未获取到文本")  # 调试信息
                messagebox.showerror("错误", "未能获取到选中的文本")
                return

            headers = {
                "Authorization": f"Bearer {self.config.config['api_key']}",
                "Content-Type": "application/json"
            }
            print(f"API Key: {self.config.config['api_key']}")  # 调试信息
            print(f"知识库 ID: {self.config.config['knowledge_base_id']}")  # 调试信息
            print(f"文档 ID: {self.config.config['document_id']}")  # 调试信息
            print(f"API URL: {self.config.config['api_url']}")  # 调试信息

            # 构建请求数据
            data = {
                "content": text
            }

            api_url = f"{self.config.config['api_url']}/api/v1/datasets/{self.config.config['knowledge_base_id']}/documents/{self.config.config['document_id']}/chunks"
            print(f"发送请求到: {api_url}")  # 调试信息
            print(f"请求数据: {data}")  # 调试信息

            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=10  # 添加超时设置
                )
                
                print(f"API 响应状态码: {response.status_code}")  # 调试信息
                print(f"API 响应内容: {response.text}")  # 调试信息
                print(f"API 响应头: {response.headers}")  # 调试信息

                if response.status_code == 200:
                    messagebox.showinfo("成功", "文本已成功导入到知识库")
                else:
                    error_msg = f"导入失败: HTTP {response.status_code}"
                    if response.text:
                        try:
                            error_json = response.json()
                            if 'message' in error_json:
                                error_msg += f"\n{error_json['message']}"
                        except:
                            error_msg += f"\n{response.text}"
                    messagebox.showerror("错误", error_msg)
            except requests.exceptions.Timeout:
                messagebox.showerror("错误", "请求超时，请检查网络连接和服务器状态")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("错误", "连接错误，请检查网络连接和服务器地址")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("错误", f"请求错误: {str(e)}")

        except Exception as e:
            print(f"发生错误: {str(e)}")  # 调试信息
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
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
