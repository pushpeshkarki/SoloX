"""
SoloX Device Management Package

This package provides enhanced device management features including:
- Device pooling and automatic reconnection
- Support for newer iOS and Android versions
- Feature compatibility checking
- Robust error handling
"""

from .device_pool import DevicePool, DeviceType, DeviceInfo
from .device_manager import DeviceManager, VersionSupport

__all__ = [
    'DevicePool',
    'DeviceType',
    'DeviceInfo',
    'DeviceManager',
    'VersionSupport'
] 