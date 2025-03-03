"""
Unit tests for the DevicePool class
"""

import time
import unittest
from unittest.mock import Mock, patch
from solox.device_management.device_pool import DevicePool, DeviceType, DeviceInfo

class TestDevicePool(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.pool = DevicePool(max_reconnect_attempts=2, reconnect_interval=1)
        
        # Sample device data
        self.android_device = {
            'id': 'android123',
            'type': DeviceType.ANDROID,
            'name': 'Test Android',
            'version': '12.0'
        }
        
        self.ios_device = {
            'id': 'ios456',
            'type': DeviceType.IOS,
            'name': 'Test iPhone',
            'version': '15.0'
        }

    def tearDown(self):
        """Clean up after each test method"""
        self.pool.stop_monitoring()

    def test_add_device(self):
        """Test adding devices to the pool"""
        # Test adding Android device
        self.assertTrue(self.pool.add_device(**self.android_device))
        device = self.pool.get_device_info(self.android_device['id'])
        self.assertIsNotNone(device)
        self.assertEqual(device.type, DeviceType.ANDROID)
        
        # Test adding iOS device
        self.assertTrue(self.pool.add_device(**self.ios_device))
        device = self.pool.get_device_info(self.ios_device['id'])
        self.assertIsNotNone(device)
        self.assertEqual(device.type, DeviceType.IOS)
        
        # Test adding duplicate device
        self.assertFalse(self.pool.add_device(**self.android_device))

    def test_remove_device(self):
        """Test removing devices from the pool"""
        self.pool.add_device(**self.android_device)
        
        # Test removing existing device
        self.assertTrue(self.pool.remove_device(self.android_device['id']))
        self.assertIsNone(self.pool.get_device_info(self.android_device['id']))
        
        # Test removing non-existent device
        self.assertFalse(self.pool.remove_device('nonexistent'))

    def test_get_device_info(self):
        """Test retrieving device information"""
        self.pool.add_device(**self.android_device)
        
        # Test getting existing device
        device = self.pool.get_device_info(self.android_device['id'])
        self.assertIsNotNone(device)
        self.assertEqual(device.name, self.android_device['name'])
        
        # Test getting non-existent device
        self.assertIsNone(self.pool.get_device_info('nonexistent'))

    def test_get_all_devices(self):
        """Test retrieving all devices"""
        self.pool.add_device(**self.android_device)
        self.pool.add_device(**self.ios_device)
        
        devices = self.pool.get_all_devices()
        self.assertEqual(len(devices), 2)
        device_ids = {d.id for d in devices}
        self.assertEqual(device_ids, {self.android_device['id'], self.ios_device['id']})

    @patch('adbutils.adb.device_list')
    @patch('tidevice.Usbmux.devices')
    def test_device_monitoring(self, mock_ios_devices, mock_android_devices):
        """Test device connection monitoring"""
        # Mock Android device
        mock_android = Mock()
        mock_android.serial = self.android_device['id']
        mock_android_devices.return_value = [mock_android]
        
        # Mock iOS device
        mock_ios = Mock()
        mock_ios.udid = self.ios_device['id']
        mock_ios_devices.return_value = [mock_ios]
        
        # Add devices and start monitoring
        self.pool.add_device(**self.android_device)
        self.pool.add_device(**self.ios_device)
        self.pool.start_monitoring()
        
        # Wait for status update
        time.sleep(2)
        
        # Check device statuses
        android_device = self.pool.get_device_info(self.android_device['id'])
        ios_device = self.pool.get_device_info(self.ios_device['id'])
        
        self.assertEqual(android_device.status, "connected")
        self.assertEqual(ios_device.status, "connected")
        
        # Simulate device disconnection
        mock_android_devices.return_value = []
        mock_ios_devices.return_value = []
        
        # Wait for status update
        time.sleep(2)
        
        # Check updated statuses
        android_device = self.pool.get_device_info(self.android_device['id'])
        ios_device = self.pool.get_device_info(self.ios_device['id'])
        
        self.assertEqual(android_device.status, "disconnected")
        self.assertEqual(ios_device.status, "disconnected")

    def test_wait_for_device(self):
        """Test waiting for device availability"""
        self.pool.add_device(**self.android_device)
        
        # Test with short timeout
        result = self.pool.wait_for_device(self.android_device['id'], timeout=1)
        self.assertFalse(result)  # Should fail as device is not connected
        
        # Simulate device connection
        device = self.pool.get_device_info(self.android_device['id'])
        device.status = "connected"
        
        # Test with connected device
        result = self.pool.wait_for_device(self.android_device['id'], timeout=1)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 