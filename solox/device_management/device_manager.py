"""
Device manager module for handling device version compatibility and feature support
"""

import re
from typing import Dict, List, Optional, Tuple
from packaging import version
import tidevice
from adbutils import adb
from .device_pool import DevicePool, DeviceType, DeviceInfo

class VersionSupport:
    """Defines version support for different features"""
    
    # Minimum supported versions
    MIN_ANDROID_VERSION = "4.4"
    MIN_IOS_VERSION = "11.0"
    
    # Latest tested versions
    LATEST_ANDROID_VERSION = "14.0"
    LATEST_IOS_VERSION = "17.0"
    
    # Feature support matrix
    FEATURE_SUPPORT = {
        "android": {
            "performance_metrics": "5.0",
            "gpu_monitoring": "6.0",
            "network_monitoring": "5.0",
            "battery_stats": "5.0",
            "screen_recording": "10.0",
        },
        "ios": {
            "performance_metrics": "11.0",
            "gpu_monitoring": "12.0",
            "network_monitoring": "11.0",
            "battery_stats": "11.0",
            "screen_recording": "11.0",
        }
    }

class DeviceManager:
    """Manages device compatibility and feature support"""
    
    def __init__(self):
        self.device_pool = DevicePool()
        self.logger = self.device_pool.logger

    def start(self):
        """Start device monitoring"""
        self.device_pool.start_monitoring()

    def stop(self):
        """Stop device monitoring"""
        self.device_pool.stop_monitoring()

    def scan_devices(self) -> List[DeviceInfo]:
        """Scan and register all connected devices"""
        # Scan Android devices
        for device in adb.device_list():
            try:
                # Get Android device information
                props = device.get_properties()
                device_id = device.serial
                name = props.get('ro.product.model', 'Unknown Android Device')
                android_version = props.get('ro.build.version.release', '0.0')
                
                self.device_pool.add_device(
                    device_id=device_id,
                    device_type=DeviceType.ANDROID,
                    name=name,
                    version=android_version
                )
            except Exception as e:
                self.logger.error(f"Error scanning Android device {device.serial}: {e}")

        # Scan iOS devices
        try:
            for device in tidevice.Usbmux().devices():
                try:
                    # Get iOS device information
                    d = tidevice.Device(device.udid)
                    device_info = d.device_info()
                    
                    self.device_pool.add_device(
                        device_id=device.udid,
                        device_type=DeviceType.IOS,
                        name=device_info.get('DeviceName', 'Unknown iOS Device'),
                        version=device_info.get('ProductVersion', '0.0')
                    )
                except Exception as e:
                    self.logger.error(f"Error scanning iOS device {device.udid}: {e}")
        except Exception as e:
            self.logger.error(f"Error accessing iOS devices: {e}")

        return self.device_pool.get_all_devices()

    def is_version_supported(self, device_info: DeviceInfo) -> bool:
        """Check if device version is supported"""
        try:
            device_version = version.parse(device_info.version)
            
            if device_info.type == DeviceType.ANDROID:
                min_version = version.parse(VersionSupport.MIN_ANDROID_VERSION)
                max_version = version.parse(VersionSupport.LATEST_ANDROID_VERSION)
            else:
                min_version = version.parse(VersionSupport.MIN_IOS_VERSION)
                max_version = version.parse(VersionSupport.LATEST_IOS_VERSION)
            
            return min_version <= device_version <= max_version
        except Exception as e:
            self.logger.error(f"Error checking version support for device {device_info.id}: {e}")
            return False

    def get_supported_features(self, device_info: DeviceInfo) -> Dict[str, bool]:
        """Get list of supported features for a device"""
        features = {}
        try:
            device_version = version.parse(device_info.version)
            platform = "android" if device_info.type == DeviceType.ANDROID else "ios"
            
            for feature, min_version in VersionSupport.FEATURE_SUPPORT[platform].items():
                features[feature] = device_version >= version.parse(min_version)
                
        except Exception as e:
            self.logger.error(f"Error checking feature support for device {device_info.id}: {e}")
            # Set all features to False if there's an error
            for feature in VersionSupport.FEATURE_SUPPORT[platform]:
                features[feature] = False
                
        return features

    def get_device_compatibility(self, device_id: str) -> Tuple[bool, Dict[str, bool]]:
        """Get device compatibility and feature support"""
        device_info = self.device_pool.get_device_info(device_id)
        if not device_info:
            return False, {}
            
        is_supported = self.is_version_supported(device_info)
        features = self.get_supported_features(device_info) if is_supported else {}
        
        return is_supported, features

    def wait_for_device(self, device_id: str, timeout: int = 30) -> Optional[DeviceInfo]:
        """Wait for a specific device to become available"""
        if self.device_pool.wait_for_device(device_id, timeout):
            return self.device_pool.get_device_info(device_id)
        return None 