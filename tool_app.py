import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
import sys
import winreg

class FloatingTodoApp:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("悬浮待办事项")
        
        # 设置窗口属性
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', False)
        
        # 设置窗口大小和位置
        self.root.geometry("350x500+100+100")
        self.root.minsize(300, 400)
        
        # 设置颜色主题
        self.bg_color = "#1A1A1A"
        self.text_color = "#E8E8E8"
        self.accent_color = "#7e8dff"
        self.completed_color = "#888888"
        self.entry_bg = "#2A2A2A"
        self.hover_color = "#3A3A3A"
        
        # 配置窗口背景
        self.root.configure(bg=self.bg_color)
        
        # 设置自定义图标
        self.set_custom_icon()
        
        # 存储待办事项
        self.todos = []
        
        # 字体大小设置
        self.font_size = 11  # 默认字体大小
        self.min_font_size = 8  # 最小字体大小
        self.max_font_size = 20  # 最大字体大小
        
        # 创建UI
        self.create_widgets()
        
        # 加载保存的待办事项
        self.load_todos()
        
        # 绑定事件
        self.bind_events()
    
    def set_custom_icon(self):
        """设置自定义图标"""
        try:
            if os.path.exists("todo_icon.ico"):
                self.root.iconbitmap("todo_icon.ico")
                print("图标设置成功")
            elif os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
                print("图标设置成功")
            else:
                print("未找到图标文件")
        except Exception as e:
            print(f"设置图标失败: {e}")
    
    def create_widgets(self):
        # 主容器
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 输入区域
        self.input_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 输入框
        self.entry = tk.Entry(self.input_frame, 
                            bg=self.entry_bg, 
                            fg=self.text_color,
                            insertbackground=self.text_color,
                            relief='flat',
                            font=('Segoe UI', 12),
                            bd=0)
        self.entry.pack(fill=tk.X, ipady=8)
        self.entry.insert(0, "输入待办事项，按回车添加")
        self.entry.bind('<FocusIn>', self.clear_placeholder)
        self.entry.bind('<FocusOut>', self.restore_placeholder)
        
        # 分隔线
        self.separator = tk.Frame(self.main_frame, bg="#333333", height=1)
        self.separator.pack(fill=tk.X, padx=20, pady=10)
        
        # 待办事项列表容器
        self.list_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 先创建列表框
        self.todo_list = tk.Listbox(self.list_frame, 
                                yscrollcommand=self.on_scroll_change,
                                selectmode=tk.SINGLE, 
                                bg=self.bg_color,
                                fg=self.text_color,
                                bd=0,
                                highlightthickness=0,
                                font=('Segoe UI', self.font_size),
                                activestyle='none')
        self.todo_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 然后创建滚动条
        self.scrollbar = tk.Scrollbar(self.list_frame, 
                                    orient="vertical", 
                                    command=self.todo_list.yview,
                                    bg=self.bg_color,
                                    troughcolor=self.bg_color,
                                    activebackground="#7e8dff",
                                    width=12)
        
        # 创建右键菜单
        self.create_context_menu()
        
        # 窗口调整大小的控制点
        self.create_resize_control()
    
    def create_context_menu(self):
        """创建右键上下文菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.entry_bg, fg=self.text_color)
        self.context_menu.add_command(label="删除", command=self.delete_selected_todo)
    
    def create_resize_control(self):
        # 右下角调整大小的控制点
        self.resize_control = tk.Frame(self.root, bg=self.accent_color, width=12, height=12)
        self.resize_control.place(relx=1.0, rely=1.0, anchor='se')
        self.resize_control.bind("<ButtonPress-1>", self.start_resize)
        self.resize_control.bind("<B1-Motion>", self.do_resize)
        
    def start_resize(self, event):
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.initial_width = self.root.winfo_width()
        self.initial_height = self.root.winfo_height()
        
    def do_resize(self, event):
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        
        new_width = max(self.root.minsize()[0], self.initial_width + dx)
        new_height = max(self.root.minsize()[1], self.initial_height + dy)
        
        self.root.geometry(f"{new_width}x{new_height}")
        
    def clear_placeholder(self, event):
        if self.entry.get() == "输入待办事项，按回车添加":
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.text_color)
            
    def restore_placeholder(self, event):
        if not self.entry.get().strip():
            self.entry.insert(0, "输入待办事项，按回车添加")
            self.entry.configure(fg="#666666") 
    
    def bind_events(self):
        # 绑定回车键添加待办事项
        self.entry.bind("<Return>", lambda event: self.add_todo())
        
        # 绑定列表框点击事件
        self.todo_list.bind("<Button-1>", self.on_list_click)
        
        # 绑定列表框右键点击事件
        self.todo_list.bind("<Button-3>", self.show_context_menu)
        
        # 绑定字体缩放快捷键
        self.root.bind("<Control-plus>", self.increase_font_size)
        self.root.bind("<Control-equal>", self.increase_font_size)  # 某些键盘布局需要
        self.root.bind("<Control-minus>", self.decrease_font_size)
    
    def on_scroll_change(self, first, last):
        """当滚动位置改变时调用，用于控制滚动条的显示/隐藏"""
        self.scrollbar.set(first, last)
        
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_list_click(self, event):
        # 获取点击的项索引
        index = self.todo_list.nearest(event.y)
        if index >= 0:
            self.toggle_todo(index)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击的项索引
        index = self.todo_list.nearest(event.y)
        if index >= 0 and index < len(self.todos):
            # 选中该项
            self.todo_list.selection_clear(0, tk.END)
            self.todo_list.selection_set(index)
            
            # 显示右键菜单
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def delete_selected_todo(self):
        """删除选中的待办事项"""
        selected_indices = self.todo_list.curselection()
        if selected_indices:
            index = selected_indices[0]
            if 0 <= index < len(self.todos):
                # 从列表中删除
                del self.todos[index]
                # 更新显示
                self.update_todo_list()
                # 保存更改
                self.save_todos()
            
    def increase_font_size(self, event=None):
        """增大字体大小"""
        if self.font_size < self.max_font_size:
            self.font_size += 1
            self.todo_list.configure(font=('Segoe UI', self.font_size))
    
    def decrease_font_size(self, event=None):
        """减小字体大小"""
        if self.font_size > self.min_font_size:
            self.font_size -= 1
            self.todo_list.configure(font=('Segoe UI', self.font_size))
        
    def add_todo(self):
        todo_text = self.entry.get().strip()
        if todo_text and todo_text != "输入待办事项，按回车添加":
            self.todos.append({"text": todo_text, "completed": False})
            self.update_todo_list()
            self.entry.delete(0, tk.END)
            self.save_todos()
            
    def update_todo_list(self):
        # 清空列表框
        self.todo_list.delete(0, tk.END)
        
        # 重新添加所有待办事项
        for todo in self.todos:
            if todo["completed"]:
                # 已完成的事项：灰色文字，前面加对勾
                display_text = "✓ " + todo["text"]
                self.todo_list.insert(tk.END, display_text)
                self.todo_list.itemconfig(tk.END, {'fg': self.completed_color})
            else:
                # 未完成的事项：白色文字，前面加圆圈
                display_text = "○ " + todo["text"]
                self.todo_list.insert(tk.END, display_text)
                self.todo_list.itemconfig(tk.END, {'fg': self.text_color})
            
    def toggle_todo(self, index):
        if 0 <= index < len(self.todos):
            self.todos[index]["completed"] = not self.todos[index]["completed"]
            self.update_todo_list()
            self.save_todos()
            
    def save_todos(self):
        try:
            with open("todos.json", "w", encoding="utf-8") as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存待办事项时出错: {e}")
            
    def load_todos(self):
        try:
            if os.path.exists("todos.json"):
                with open("todos.json", "r", encoding="utf-8") as f:
                    self.todos = json.load(f)
                self.update_todo_list()
        except Exception as e:
            print(f"加载待办事项时出错: {e}")
    
    def setup_autostart(self):
        """设置开机自启动"""
        try:
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = os.path.abspath(__file__)
                app_path = f'pythonw.exe "{app_path}"'
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "FloatingTodoApp", 0, winreg.REG_SZ, app_path)
                
            print("开机自启动设置成功")
            
        except Exception as e:
            print(f"设置开机自启动失败: {e}") 

    def run(self):
        # 设置开机启动
        self.setup_autostart()
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingTodoApp()
    app.run()