"""
虚拟机管理器
提供虚拟机的启动、关闭、状态查询等功能
"""

from typing import List, Dict, Optional, Any
from vmware_client import VMwareAPIClient


class VMManager:
    """虚拟机管理器类"""
    
    def __init__(self, client: VMwareAPIClient):
        """
        初始化虚拟机管理器
        
        Args:
            client: VMware API 客户端实例
        """
        self.client = client
    
    def list_vms(self) -> List[Dict[str, Any]]:
        """
        获取所有虚拟机列表
        
        Returns:
            虚拟机列表
        """
        try:
            response = self.client.get('vms')
            return response if isinstance(response, list) else []
        except Exception as e:
            raise Exception(f"获取虚拟机列表失败: {str(e)}")
    
    def get_vm_info(self, vm_id: str) -> Dict[str, Any]:
        """
        获取虚拟机详细信息
        
        Args:
            vm_id: 虚拟机 ID
            
        Returns:
            虚拟机信息字典
        """
        try:
            return self.client.get(f'vms/{vm_id}')
        except Exception as e:
            raise Exception(f"获取虚拟机信息失败: {str(e)}")
    
    def get_vm_power_state(self, vm_id: str) -> str:
        """
        获取虚拟机电源状态
        
        Args:
            vm_id: 虚拟机 ID
            
        Returns:
            电源状态 (poweredOn, poweredOff, suspended)
        """
        try:
            response = self.client.get(f'vms/{vm_id}/power')
            return response.get('power_state', 'unknown')
        except Exception as e:
            raise Exception(f"获取虚拟机电源状态失败: {str(e)}")
    
    def power_on(self, vm_id: str) -> bool:
        """
        启动虚拟机

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'on')
            return True
        except Exception as e:
            raise Exception(f"启动虚拟机失败: {str(e)}")

    def power_off(self, vm_id: str) -> bool:
        """
        关闭虚拟机

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'off')
            return True
        except Exception as e:
            raise Exception(f"关闭虚拟机失败: {str(e)}")

    def shutdown(self, vm_id: str) -> bool:
        """
        优雅关闭虚拟机（需要 VMware Tools）

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'shutdown')
            return True
        except Exception as e:
            raise Exception(f"优雅关闭虚拟机失败: {str(e)}")

    def suspend(self, vm_id: str) -> bool:
        """
        挂起虚拟机

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'suspend')
            return True
        except Exception as e:
            raise Exception(f"挂起虚拟机失败: {str(e)}")

    def pause(self, vm_id: str) -> bool:
        """
        暂停虚拟机

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'pause')
            return True
        except Exception as e:
            raise Exception(f"暂停虚拟机失败: {str(e)}")

    def unpause(self, vm_id: str) -> bool:
        """
        恢复暂停的虚拟机

        Args:
            vm_id: 虚拟机 ID

        Returns:
            操作是否成功
        """
        try:
            self.client.put(f'vms/{vm_id}/power', 'unpause')
            return True
        except Exception as e:
            raise Exception(f"恢复虚拟机失败: {str(e)}")

