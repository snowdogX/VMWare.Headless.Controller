"""
VMware REST API 客户端
用于与 VMware Workstation/Player REST API 进行交互
"""

import requests
import json
import urllib3
from typing import Dict, List, Optional, Any, Union


class VMwareAPIClient:
    """VMware REST API 客户端类"""
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 verify_ssl: bool = False, timeout: int = 30):
        """
        初始化 VMware API 客户端
        
        Args:
            host: VMware REST API 主机地址
            port: VMware REST API 端口
            username: 用户名
            password: 密码
            verify_ssl: 是否验证 SSL 证书
            timeout: 请求超时时间（秒）
        """
        self.base_url = f"http://{host}:{port}/api"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()
        
        # 禁用 SSL 警告
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 设置认证
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
            'Accept': 'application/vnd.vmware.vmw.rest-v1+json'
        })
    
    def _request(self, method: str, endpoint: str, data: Optional[Union[Dict, str]] = None) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点
            data: 请求数据（可以是字典或字符串）

        Returns:
            响应数据字典
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            # 根据数据类型选择合适的参数
            if isinstance(data, str):
                # 对于字符串数据，使用 data 参数发送纯文本
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
            else:
                # 对于字典数据，使用 json 参数
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )

            # 检查响应状态
            response.raise_for_status()

            # 返回 JSON 响应
            if response.text:
                return response.json()
            return {}

        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """发送 GET 请求"""
        return self._request('GET', endpoint)
    
    def post(self, endpoint: str, data: Optional[Union[Dict, str]] = None) -> Dict[str, Any]:
        """发送 POST 请求"""
        return self._request('POST', endpoint, data)

    def put(self, endpoint: str, data: Optional[Union[Dict, str]] = None) -> Dict[str, Any]:
        """发送 PUT 请求"""
        return self._request('PUT', endpoint, data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """发送 DELETE 请求"""
        return self._request('DELETE', endpoint)
    
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            连接是否成功
        """
        try:
            # 尝试获取虚拟机列表来测试连接
            self.get('vms')
            return True
        except Exception:
            return False

