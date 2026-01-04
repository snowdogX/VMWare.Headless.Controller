"""
配置文件加载器
用于加载和解析 YAML 配置文件
"""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = None
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请复制 config.example.yaml 为 config.yaml 并填入你的配置"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            return self.config
        except yaml.YAMLError as e:
            raise Exception(f"配置文件解析失败: {str(e)}")
        except Exception as e:
            raise Exception(f"读取配置文件失败: {str(e)}")
    
    def get_vmware_config(self) -> Dict[str, Any]:
        """
        获取 VMware 配置
        
        Returns:
            VMware 配置字典
        """
        if self.config is None:
            self.load()
        
        if 'vmware' not in self.config:
            raise Exception("配置文件中缺少 'vmware' 配置项")
        
        return self.config['vmware']
    
    def validate(self) -> bool:
        """
        验证配置文件
        
        Returns:
            配置是否有效
        """
        try:
            vmware_config = self.get_vmware_config()
            
            required_fields = ['host', 'port', 'username', 'password']
            for field in required_fields:
                if field not in vmware_config:
                    raise Exception(f"配置文件中缺少必需字段: {field}")
            
            return True
        except Exception as e:
            raise Exception(f"配置验证失败: {str(e)}")

