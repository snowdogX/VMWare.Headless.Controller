#!/usr/bin/env python3
"""
VMware 虚拟机管理器 - 图形界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import List, Dict, Any
from config_loader import ConfigLoader
from vmware_client import VMwareAPIClient
from vm_manager import VMManager


class VMwareGUI:
    """VMware 虚拟机管理器图形界面"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("VMware 虚拟机管理器")
        self.root.geometry("1000x600")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 初始化变量
        self.vm_manager = None
        self.client = None
        self.vms = []
        self.selected_vm_id = None
        self.auto_refresh = tk.BooleanVar(value=False)
        self.refresh_interval = 5  # 秒
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置并连接
        self.load_config_and_connect()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="🔄 刷新", command=self.refresh_vm_list).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(toolbar, text="自动刷新", variable=self.auto_refresh, 
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=2)
        
        # 连接状态标签
        self.status_label = ttk.Label(toolbar, text="状态: 未连接", foreground="red")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：虚拟机列表
        left_frame = ttk.LabelFrame(main_container, text="虚拟机列表", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("id", "name", "status", "cpu", "memory")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        
        # 设置列标题
        self.tree.heading("id", text="虚拟机 ID")
        self.tree.heading("name", text="名称")
        self.tree.heading("status", text="状态")
        self.tree.heading("cpu", text="CPU")
        self.tree.heading("memory", text="内存(MB)")
        
        # 设置列宽
        self.tree.column("id", width=100)
        self.tree.column("name", width=200)
        self.tree.column("status", width=80)
        self.tree.column("cpu", width=60)
        self.tree.column("memory", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_vm_select)
        
        # 右侧：控制面板
        right_frame = ttk.Frame(main_container, padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 虚拟机信息
        info_frame = ttk.LabelFrame(right_frame, text="虚拟机信息", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=35, height=10, 
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮
        control_frame = ttk.LabelFrame(right_frame, text="虚拟机控制", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        button_width = 20
        
        self.start_btn = ttk.Button(control_frame, text="▶ 启动", 
                                    command=self.start_vm, width=button_width)
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ 强制关闭", 
                                   command=self.stop_vm, width=button_width)
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        self.shutdown_btn = ttk.Button(control_frame, text="🔌 优雅关闭", 
                                       command=self.shutdown_vm, width=button_width)
        self.shutdown_btn.pack(fill=tk.X, pady=2)
        
        self.suspend_btn = ttk.Button(control_frame, text="⏸ 挂起", 
                                      command=self.suspend_vm, width=button_width)
        self.suspend_btn.pack(fill=tk.X, pady=2)
        
        # 初始禁用所有控制按钮
        self.disable_control_buttons()
        
        # 底部日志区域
        log_frame = ttk.LabelFrame(self.root, text="操作日志", padding="5")
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def log(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        self.log_text.configure(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        
        # 根据级别设置颜色标签
        if level == "ERROR":
            tag = "error"
        elif level == "SUCCESS":
            tag = "success"
        elif level == "WARNING":
            tag = "warning"
        else:
            tag = "info"
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", tag)

        # 配置标签颜色
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("timestamp", foreground="gray")

        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def load_config_and_connect(self):
        """加载配置并连接到 VMware API"""
        try:
            self.log("正在加载配置文件...")
            config_loader = ConfigLoader('config.yaml')
            config_loader.validate()
            vmware_config = config_loader.get_vmware_config()
            self.log("配置文件加载成功", "SUCCESS")

            self.log("正在连接 VMware REST API...")
            self.client = VMwareAPIClient(
                host=vmware_config['host'],
                port=vmware_config['port'],
                username=vmware_config['username'],
                password=vmware_config['password'],
                verify_ssl=vmware_config.get('verify_ssl', False),
                timeout=vmware_config.get('timeout', 30)
            )

            # 测试连接
            if self.client.test_connection():
                self.vm_manager = VMManager(self.client)
                self.status_label.config(text="状态: 已连接", foreground="green")
                self.log("API 连接成功", "SUCCESS")

                # 加载虚拟机列表
                self.refresh_vm_list()
            else:
                raise Exception("API 连接测试失败")

        except Exception as e:
            self.log(f"连接失败: {str(e)}", "ERROR")
            messagebox.showerror("连接错误", f"无法连接到 VMware API:\n{str(e)}")
            self.status_label.config(text="状态: 连接失败", foreground="red")

    def refresh_vm_list(self):
        """刷新虚拟机列表"""
        if not self.vm_manager:
            return

        try:
            self.log("正在刷新虚拟机列表...")

            # 清空现有列表
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 获取虚拟机列表
            self.vms = self.vm_manager.list_vms()

            # 填充列表
            for vm in self.vms:
                vm_id = vm.get('id', 'N/A')
                vm_path = vm.get('path', 'N/A')
                vm_name = vm_path.split('\\')[-1].replace('.vmx', '') if vm_path != 'N/A' else 'N/A'

                # 获取详细信息
                try:
                    info = self.vm_manager.get_vm_info(vm_id)
                    power_state = self.vm_manager.get_vm_power_state(vm_id)
                    cpu = info.get('cpu', {}).get('processors', 'N/A')
                    memory = info.get('memory', 'N/A')

                    # 状态映射
                    status_map = {
                        'poweredOn': '运行中',
                        'poweredOff': '已关闭',
                        'suspended': '已挂起'
                    }
                    status = status_map.get(power_state, power_state)

                except Exception:
                    cpu = 'N/A'
                    memory = 'N/A'
                    status = '未知'

                # 插入到树形视图
                item_id = self.tree.insert("", tk.END, values=(vm_id, vm_name, status, cpu, memory))

                # 根据状态设置颜色
                if status == '运行中':
                    self.tree.item(item_id, tags=('running',))
                elif status == '已关闭':
                    self.tree.item(item_id, tags=('stopped',))
                elif status == '已挂起':
                    self.tree.item(item_id, tags=('suspended',))

            # 配置标签颜色
            self.tree.tag_configure('running', foreground='green')
            self.tree.tag_configure('stopped', foreground='red')
            self.tree.tag_configure('suspended', foreground='orange')

            self.log(f"刷新完成，共 {len(self.vms)} 个虚拟机", "SUCCESS")

        except Exception as e:
            self.log(f"刷新失败: {str(e)}", "ERROR")
            messagebox.showerror("刷新错误", f"刷新虚拟机列表失败:\n{str(e)}")

    def on_vm_select(self, event):
        """虚拟机选择事件"""
        selection = self.tree.selection()
        if not selection:
            self.disable_control_buttons()
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        self.selected_vm_id = values[0]

        # 显示虚拟机详细信息
        self.show_vm_info(self.selected_vm_id)

        # 启用控制按钮
        self.enable_control_buttons()

    def show_vm_info(self, vm_id: str):
        """显示虚拟机详细信息"""
        try:
            info = self.vm_manager.get_vm_info(vm_id)
            power_state = self.vm_manager.get_vm_power_state(vm_id)

            # 格式化信息
            info_text = f"虚拟机 ID: {vm_id}\n\n"
            info_text += f"路径: {info.get('path', 'N/A')}\n\n"
            info_text += f"CPU 数量: {info.get('cpu', {}).get('processors', 'N/A')}\n"
            info_text += f"内存大小: {info.get('memory', 'N/A')} MB\n\n"
            info_text += f"电源状态: {power_state}\n"

            # 更新信息文本框
            self.info_text.configure(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.configure(state=tk.DISABLED)

        except Exception as e:
            self.log(f"获取虚拟机信息失败: {str(e)}", "ERROR")

    def enable_control_buttons(self):
        """启用控制按钮"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.shutdown_btn.config(state=tk.NORMAL)
        self.suspend_btn.config(state=tk.NORMAL)

    def disable_control_buttons(self):
        """禁用控制按钮"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.shutdown_btn.config(state=tk.DISABLED)
        self.suspend_btn.config(state=tk.DISABLED)

    def start_vm(self):
        """启动虚拟机"""
        if not self.selected_vm_id:
            return

        def task():
            try:
                self.log(f"正在启动虚拟机 {self.selected_vm_id}...")
                self.vm_manager.power_on(self.selected_vm_id)
                self.log(f"虚拟机 {self.selected_vm_id} 已启动", "SUCCESS")
                self.root.after(2000, self.refresh_vm_list)
            except Exception as e:
                self.log(f"启动虚拟机失败: {str(e)}", "ERROR")
                messagebox.showerror("操作失败", f"启动虚拟机失败:\n{str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def stop_vm(self):
        """强制关闭虚拟机"""
        if not self.selected_vm_id:
            return

        if not messagebox.askyesno("确认", "确定要强制关闭虚拟机吗？\n这可能导致数据丢失。"):
            return

        def task():
            try:
                self.log(f"正在关闭虚拟机 {self.selected_vm_id}...")
                self.vm_manager.power_off(self.selected_vm_id)
                self.log(f"虚拟机 {self.selected_vm_id} 已关闭", "SUCCESS")
                self.root.after(2000, self.refresh_vm_list)
            except Exception as e:
                self.log(f"关闭虚拟机失败: {str(e)}", "ERROR")
                messagebox.showerror("操作失败", f"关闭虚拟机失败:\n{str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def shutdown_vm(self):
        """优雅关闭虚拟机"""
        if not self.selected_vm_id:
            return

        def task():
            try:
                self.log(f"正在优雅关闭虚拟机 {self.selected_vm_id}...")
                self.vm_manager.shutdown(self.selected_vm_id)
                self.log(f"虚拟机 {self.selected_vm_id} 正在关闭（需要 VMware Tools）", "SUCCESS")
                self.root.after(2000, self.refresh_vm_list)
            except Exception as e:
                self.log(f"优雅关闭虚拟机失败: {str(e)}", "ERROR")
                messagebox.showerror("操作失败", f"优雅关闭虚拟机失败:\n{str(e)}\n\n请确保虚拟机已安装 VMware Tools。")

        threading.Thread(target=task, daemon=True).start()

    def suspend_vm(self):
        """挂起虚拟机"""
        if not self.selected_vm_id:
            return

        def task():
            try:
                self.log(f"正在挂起虚拟机 {self.selected_vm_id}...")
                self.vm_manager.suspend(self.selected_vm_id)
                self.log(f"虚拟机 {self.selected_vm_id} 已挂起", "SUCCESS")
                self.root.after(2000, self.refresh_vm_list)
            except Exception as e:
                self.log(f"挂起虚拟机失败: {str(e)}", "ERROR")
                messagebox.showerror("操作失败", f"挂起虚拟机失败:\n{str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def toggle_auto_refresh(self):
        """切换自动刷新"""
        if self.auto_refresh.get():
            self.log("已启用自动刷新", "SUCCESS")
            self.auto_refresh_task()
        else:
            self.log("已禁用自动刷新", "WARNING")

    def auto_refresh_task(self):
        """自动刷新任务"""
        if self.auto_refresh.get():
            self.refresh_vm_list()
            self.root.after(self.refresh_interval * 1000, self.auto_refresh_task)


def main():
    """主函数"""
    root = tk.Tk()
    app = VMwareGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

