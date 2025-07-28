"""
API Module - AgentOS Enterprise
Organización modular de endpoints y rutas
"""

from .v1 import register_v1_endpoints
from .v2 import register_v2_endpoints

__all__ = ["register_v1_endpoints", "register_v2_endpoints"] 