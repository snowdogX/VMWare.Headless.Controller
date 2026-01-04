#!/usr/bin/env python3
"""
VMware 无界面虚拟机管理器
主程序入口
"""

import sys
import argparse
from colorama import init, Fore, Style
from tabulate import tabulate
from config_loader import ConfigLoader
from vmware_client import VMwareAPIClient
from vm_manager import VMManager


# 初始化 colorama
init(autoreset=True)


def print_success(message: str):
    """打印成功消息"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """打印错误消息"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """打印信息消息"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """打印警告消息"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def list_vms(vm_manager: VMManager):
    """列出所有虚拟机"""
    try:
        vms = vm_manager.list_vms()
        
        if not vms:
            print_warning("没有找到虚拟机")
            return
        
        # 准备表格数据
        table_data = []
        for vm in vms:
            vm_id = vm.get('id', 'N/A')
            vm_path = vm.get('path', 'N/A')
            
            # 获取电源状态
            try:
                power_state = vm_manager.get_vm_power_state(vm_id)
                # 根据状态添加颜色
                if power_state == 'poweredOn':
                    power_state = f"{Fore.GREEN}运行中{Style.RESET_ALL}"
                elif power_state == 'poweredOff':
                    power_state = f"{Fore.RED}已关闭{Style.RESET_ALL}"
                elif power_state == 'suspended':
                    power_state = f"{Fore.YELLOW}已挂起{Style.RESET_ALL}"
                else:
                    power_state = f"{Fore.CYAN}{power_state}{Style.RESET_ALL}"
            except:
                power_state = f"{Fore.CYAN}未知{Style.RESET_ALL}"
            
            table_data.append([vm_id, vm_path, power_state])
        
        # 打印表格
        headers = ["虚拟机 ID", "路径", "状态"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        print_error(f"列出虚拟机失败: {str(e)}")
        sys.exit(1)


def get_vm_status(vm_manager: VMManager, vm_id: str):
    """获取虚拟机状态"""
    try:
        info = vm_manager.get_vm_info(vm_id)
        power_state = vm_manager.get_vm_power_state(vm_id)
        
        print_info(f"虚拟机 ID: {vm_id}")
        print_info(f"路径: {info.get('path', 'N/A')}")
        print_info(f"CPU 数量: {info.get('cpu', {}).get('processors', 'N/A')}")
        print_info(f"内存大小: {info.get('memory', 'N/A')} MB")
        print_info(f"电源状态: {power_state}")
        
    except Exception as e:
        print_error(f"获取虚拟机状态失败: {str(e)}")
        sys.exit(1)


def power_on_vm(vm_manager: VMManager, vm_id: str):
    """启动虚拟机"""
    try:
        print_info(f"正在启动虚拟机 {vm_id}...")
        vm_manager.power_on(vm_id)
        print_success(f"虚拟机 {vm_id} 已启动")
    except Exception as e:
        print_error(f"启动虚拟机失败: {str(e)}")
        sys.exit(1)


def power_off_vm(vm_manager: VMManager, vm_id: str):
    """关闭虚拟机"""
    try:
        print_info(f"正在关闭虚拟机 {vm_id}...")
        vm_manager.power_off(vm_id)
        print_success(f"虚拟机 {vm_id} 已关闭")
    except Exception as e:
        print_error(f"关闭虚拟机失败: {str(e)}")
        sys.exit(1)


def shutdown_vm(vm_manager: VMManager, vm_id: str):
    """优雅关闭虚拟机"""
    try:
        print_info(f"正在优雅关闭虚拟机 {vm_id}...")
        vm_manager.shutdown(vm_id)
        print_success(f"虚拟机 {vm_id} 正在关闭（需要 VMware Tools）")
    except Exception as e:
        print_error(f"优雅关闭虚拟机失败: {str(e)}")
        sys.exit(1)


def suspend_vm(vm_manager: VMManager, vm_id: str):
    """挂起虚拟机"""
    try:
        print_info(f"正在挂起虚拟机 {vm_id}...")
        vm_manager.suspend(vm_id)
        print_success(f"虚拟机 {vm_id} 已挂起")
    except Exception as e:
        print_error(f"挂起虚拟机失败: {str(e)}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='VMware 无界面虚拟机管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-c', '--config', default='config.yaml',
                        help='配置文件路径 (默认: config.yaml)')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # list 命令
    subparsers.add_parser('list', help='列出所有虚拟机')

    # status 命令
    status_parser = subparsers.add_parser('status', help='查看虚拟机状态')
    status_parser.add_argument('vm_id', help='虚拟机 ID')

    # start 命令
    start_parser = subparsers.add_parser('start', help='启动虚拟机')
    start_parser.add_argument('vm_id', help='虚拟机 ID')

    # stop 命令
    stop_parser = subparsers.add_parser('stop', help='强制关闭虚拟机')
    stop_parser.add_argument('vm_id', help='虚拟机 ID')

    # shutdown 命令
    shutdown_parser = subparsers.add_parser('shutdown', help='优雅关闭虚拟机（需要 VMware Tools）')
    shutdown_parser.add_argument('vm_id', help='虚拟机 ID')

    # suspend 命令
    suspend_parser = subparsers.add_parser('suspend', help='挂起虚拟机')
    suspend_parser.add_argument('vm_id', help='虚拟机 ID')

    # test 命令
    subparsers.add_parser('test', help='测试 API 连接')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 加载配置
    try:
        print_info("正在加载配置文件...")
        config_loader = ConfigLoader(args.config)
        config_loader.validate()
        vmware_config = config_loader.get_vmware_config()
        print_success("配置文件加载成功")
    except Exception as e:
        print_error(f"配置加载失败: {str(e)}")
        sys.exit(1)

    # 创建 API 客户端
    try:
        print_info("正在连接 VMware REST API...")
        client = VMwareAPIClient(
            host=vmware_config['host'],
            port=vmware_config['port'],
            username=vmware_config['username'],
            password=vmware_config['password'],
            verify_ssl=vmware_config.get('verify_ssl', False),
            timeout=vmware_config.get('timeout', 30)
        )
        print_success("API 连接成功")
    except Exception as e:
        print_error(f"API 连接失败: {str(e)}")
        sys.exit(1)

    # 创建虚拟机管理器
    vm_manager = VMManager(client)

    # 执行命令
    try:
        if args.command == 'list':
            list_vms(vm_manager)
        elif args.command == 'status':
            get_vm_status(vm_manager, args.vm_id)
        elif args.command == 'start':
            power_on_vm(vm_manager, args.vm_id)
        elif args.command == 'stop':
            power_off_vm(vm_manager, args.vm_id)
        elif args.command == 'shutdown':
            shutdown_vm(vm_manager, args.vm_id)
        elif args.command == 'suspend':
            suspend_vm(vm_manager, args.vm_id)
        elif args.command == 'test':
            if client.test_connection():
                print_success("API 连接测试成功")
            else:
                print_error("API 连接测试失败")
                sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"执行命令失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

