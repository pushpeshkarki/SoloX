"""
Integration tests for device management features
"""

import pytest
import time
from solox.device_management import DeviceManager, DeviceType, DeviceInfo
from solox.public.apm import AppPerformanceMonitor

class TestDeviceManagementIntegration:
    @pytest.fixture(autouse=True)
    def setup_manager(self):
        """Setup and teardown the device manager"""
        self.manager = DeviceManager()
        self.manager.start()
        yield
        self.manager.stop()

    def test_device_discovery_and_monitoring(self):
        """Test complete device discovery and monitoring flow"""
        # Scan for devices
        devices = self.manager.scan_devices()
        
        if not devices:
            pytest.skip("No physical devices connected for testing")
        
        for device in devices:
            # Check device information
            assert device.id is not None
            assert device.type in [DeviceType.ANDROID, DeviceType.IOS]
            assert device.version is not None
            
            # Check device compatibility
            is_supported, features = self.manager.get_device_compatibility(device.id)
            assert isinstance(is_supported, bool)
            assert isinstance(features, dict)
            
            # Monitor device for a short period
            start_time = time.time()
            while time.time() - start_time < 5:
                device_info = self.manager.device_pool.get_device_info(device.id)
                assert device_info is not None
                time.sleep(1)

    def test_performance_monitoring_integration(self):
        """Test integration with performance monitoring"""
        devices = self.manager.scan_devices()
        
        if not devices:
            pytest.skip("No physical devices connected for testing")
        
        for device in devices:
            if not self.manager.is_version_supported(device):
                continue
                
            # Initialize performance monitor based on device type
            if device.type == DeviceType.ANDROID:
                monitor = AppPerformanceMonitor(
                    pkgName='com.android.settings',
                    platform='Android',
                    deviceId=device.id,
                    surfaceview=True,
                    noLog=True
                )
            else:  # iOS
                monitor = AppPerformanceMonitor(
                    pkgName='com.apple.Preferences',
                    platform='iOS',
                    deviceId=device.id,
                    noLog=True
                )
            
            try:
                # Test basic metrics collection
                cpu = monitor.collectCpu()
                assert isinstance(cpu, (int, float))
                
                memory = monitor.collectMemory()
                assert isinstance(memory, (int, float))
                
                fps = monitor.collectFps()
                assert isinstance(fps, (int, float))
            except Exception as e:
                pytest.fail(f"Performance monitoring failed for device {device.id}: {str(e)}")

    def test_device_reconnection(self):
        """Test device reconnection handling"""
        devices = self.manager.scan_devices()
        
        if not devices:
            pytest.skip("No physical devices connected for testing")
        
        for device in devices:
            # Simulate device disconnection
            self.manager.device_pool._handle_disconnected_device(device.id, time.time())
            
            # Wait for reconnection attempt
            time.sleep(2)
            
            # Check if device was reconnected
            device_info = self.manager.device_pool.get_device_info(device.id)
            assert device_info is not None
            
            # Check reconnection attempts were recorded
            assert device_info.reconnect_attempts > 0

    def test_feature_compatibility(self):
        """Test feature compatibility across different device versions"""
        devices = self.manager.scan_devices()
        
        if not devices:
            pytest.skip("No physical devices connected for testing")
        
        for device in devices:
            is_supported, features = self.manager.get_device_compatibility(device.id)
            
            if is_supported:
                # Check all expected features are present
                expected_features = [
                    'performance_metrics',
                    'gpu_monitoring',
                    'network_monitoring',
                    'battery_stats',
                    'screen_recording'
                ]
                
                for feature in expected_features:
                    assert feature in features
                    assert isinstance(features[feature], bool)
                
                # Verify feature support matches version requirements
                if device.type == DeviceType.ANDROID:
                    if float(device.version.split('.')[0]) >= 6.0:
                        assert features['gpu_monitoring']
                    if float(device.version.split('.')[0]) >= 10.0:
                        assert features['screen_recording']
                else:  # iOS
                    if float(device.version.split('.')[0]) >= 12.0:
                        assert features['gpu_monitoring'] 