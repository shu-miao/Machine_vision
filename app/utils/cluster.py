# 集群协调
import socket
from typing import Optional

class NodeRegistry:
    _instance = None
    
    def __init__(self):
        self.nodes = set()
        self.current_node = socket.gethostname()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_node(self, node_id: str):
        """节点注册 (示例: 实际使用Redis实现)"""
        self.nodes.add(node_id)