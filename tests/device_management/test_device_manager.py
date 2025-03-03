"""
Unit tests for the DeviceManager class
"""

import unittest
from unittest.mock import Mock, patch
from solox.device_management.device_manager import DeviceManager, VersionSupport
from solox.device_management.device_pool import DeviceType, DeviceInfo

class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.manager = DeviceManager()
        
        # Sample device data
        self.android_device = DeviceInfo(
            id='android123',
            type=DeviceType.ANDROID,
            name='Test Android',
            version='12.0',
            status='connected'
        )
        
        self.ios_device = DeviceInfo(
            id='ios456',
            type=DeviceType.IOS,
            name='Test iPhone',
            version='15.0',
            status='connected'
        )
        
        self.old_android = DeviceInfo(
            id='old_android',
            type=DeviceType.ANDROID,
            name='Old Android',
            version='4.0',
            status='connected'
        )
        
        self.old_ios = DeviceInfo(
            id='old_ios',
            type=DeviceType.IOS,
            name='Old iPhone',
            version='10.0',
            status='connected'
        )

    def tearDown(self):
        """Clean up after each test method"""
        self.manager.stop()

    @patch('adbutils.adb.device_list')
    @patch('tidevice.Usbmux.devices')
    @patch('tidevice.Device')
    def test_scan_devices(self, mock_tidevice, mock_ios_devices, mock_android_devices):
        """Test scanning for connected devices"""
        # Mock Android device
        mock_android = Mock()
        mock_android.serial = self.android_device.id
        mock_android.get_properties.return_value = {
            'ro.product.model': self.android_device.name,
            'ro.build.version.release': self.android_device.version
        }
        mock_android_devices.return_value = [mock_android]
        
        # Mock iOS device
        mock_ios = Mock()
        mock_ios.udid = self.ios_device.id
        mock_ios_devices.return_value = [mock_ios]
        
        # Mock tidevice.Device
        mock_device_instance = Mock()
        mock_device_instance.device_info.return_value = {
            'DeviceName': self.ios_device.name,
            'ProductVersion': self.ios_device.version
        }
        mock_tidevice.return_value = mock_device_instance
        
        # Scan devices
        devices = self.manager.scan_devices()
        
        # Verify results
        self.assertEqual(len(devices), 2)
        device_ids = {d.id for d in devices}
        self.assertEqual(device_ids, {self.android_device.id, self.ios_device.id})

    def test_version_support(self):
        """Test version support checking"""
        # Test supported versions
        self.assertTrue(self.manager.is_version_supported(self.android_device))
        self.assertTrue(self.manager.is_version_supported(self.ios_device))
        
        # Test unsupported versions
        self.assertFalse(self.manager.is_version_supported(self.old_android))
        self.assertFalse(self.manager.is_version_supported(self.old_ios))

    def test_feature_support(self):
        """Test feature support checking"""
        # Test Android features
        android_features = self.manager.get_supported_features(self.android_device)
        self.assertTrue(all(android_features.values()))  # All features should be supported
        
        # Test iOS features
        ios_features = self.manager.get_supported_features(self.ios_device)
        self.assertTrue(all(ios_features.values()))  # All features should be supported
        
        # Test old Android features
        old_android_features = self.manager.get_supported_features(self.old_android)
        self.assertFalse(any(old_android_features.values()))  # No features should be supported
        
        # Test old iOS features
        old_ios_features = self.manager.get_supported_features(self.old_ios)
        self.assertFalse(any(old_ios_features.values()))  # No features should be supported

    def test_device_compatibility(self):
        """Test device compatibility checking"""
        # Add devices to pool
        self.manager.device_pool.add_device(
            id=self.android_device.id,
            type=self.android_device.type,
            name=self.android_device.name,
            version=self.android_device.version
        )
        
        self.manager.device_pool.add_device(
            id=self.old_android.id,
            type=self.old_android.type,
            name=self.old_android.name,
            version=self.old_android.version
        )
        
        # Test supported device
        is_supported, features = self.manager.get_device_compatibility(self.android_device.id)
        self.assertTrue(is_supported)
        self.assertTrue(all(features.values()))
        
        # Test unsupported device
        is_supported, features = self.manager.get_device_compatibility(self.old_android.id)
        self.assertFalse(is_supported)
        self.assertEqual(len(features), 0)
        
        # Test non-existent device
        is_supported, features = self.manager.get_device_compatibility('nonexistent')
        self.assertFalse(is_supported)
        self.assertEqual(len(features), 0)

    @patch('adbutils.adb.device_list')
    def test_wait_for_device(self, mock_android_devices):
        """Test waiting for device availability"""
        # Add device to pool
        self.manager.device_pool.add_device(
            id=self.android_device.id,
            type=self.android_device.type,
            name=self.android_device.name,
            version=self.android_device.version
        )
        
        # Mock Android device
        mock_android = Mock()
        mock_android.serial = self.android_device.id
        mock_android_devices.return_value = [mock_android]
        
        # Test waiting for device
        device = self.manager.wait_for_device(self.android_device.id, timeout=1)
        self.assertIsNotNone(device)
        self.assertEqual(device.id, self.android_device.id)
        
        # Test waiting for non-existent device
        device = self.manager.wait_for_device('nonexistent', timeout=1)
        self.assertIsNone(device)

if __name__ == '__main__':
    unittest.main() 