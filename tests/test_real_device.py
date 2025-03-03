import pytest
import os
import json
from solox.public.common import Devices, File, Method, Platform

def test_ios_device_detection():
    devices = Devices(platform=Platform.iOS)
    device_list = devices.getDeviceInfoByiOS()
    assert len(device_list) > 0, "No iOS devices found"
    
    # Test device details
    device_id = device_list[0]
    device_details = devices.getDdeviceDetail(device_id, Platform.iOS)
    assert device_details is not None
    assert isinstance(device_details, dict)
    assert 'name' in device_details
    assert 'version' in device_details
    assert 'model' in device_details
    assert 'brand' in device_details
    assert 'manufacturer' in device_details
    
    # Test device check
    devices.devicesCheck(Platform.iOS, device_id)
    
    # Test package names
    pkg_names = devices.getPkgnameByiOS(device_id)
    assert isinstance(pkg_names, list)
    
    # Test physical size
    screen_size = devices.getPhysicalSizeOfiOS(device_id)
    assert isinstance(screen_size, str)
    if screen_size:
        width, height = map(int, screen_size.split('x'))
        assert width > 0
        assert height > 0

def test_network_monitoring():
    file = File()
    
    # Test pre-network recording
    pre_result = file.record_net('pre', 1000, 2000)
    assert pre_result['send'] == 1000
    assert pre_result['recv'] == 2000
    
    # Test next-network recording
    next_result = file.record_net('next', 3000, 4000)
    assert next_result['send'] == 2000  # 3000 - 1000
    assert next_result['recv'] == 2000  # 4000 - 2000

def test_report_generation():
    file = File()
    scene = 'test_scene'
    
    # Create test data
    os.makedirs(os.path.join(file.report_dir, scene), exist_ok=True)
    
    # Test iOS report generation
    ios_summary = {
        'devices': 'iPhone 14',
        'app': 'test_app',
        'platform': Platform.iOS,
        'ctime': '2024-03-03-12-00-00',
        'cpu_app': '10%',
        'cpu_sys': '5%',
        'gpu': 30.5,
        'mem_total': '500MB',
        'fps': '60',
        'tem': 35,
        'current': 200,
        'voltage': 4000,
        'power': 800,
        'net_send': '1MB',
        'net_recv': '2MB',
        'cpu_charts': [],
        'mem_charts': [],
        'net_charts': [],
        'battery_charts': [],
        'fps_charts': [],
        'gpu_charts': []
    }
    
    try:
        report_path = file.make_ios_html(scene, ios_summary)
        assert os.path.exists(report_path)
    except Exception as e:
        pytest.fail(f"Failed to generate iOS report: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(os.path.join(file.report_dir, scene)):
            import shutil
            shutil.rmtree(os.path.join(file.report_dir, scene))

def test_ios_error_handling():
    devices = Devices(platform=Platform.iOS)
    
    # Test invalid device ID
    with pytest.raises(Exception):
        devices.getDdeviceDetail('invalid_id', Platform.iOS)
    
    # Test unsupported platform
    with pytest.raises(ValueError, match='Unsupported platform'):
        devices.getDdeviceDetail('any_id', 'Windows')
    
    # Test invalid package name
    with pytest.raises(Exception):
        devices.devicesCheck(Platform.iOS, devices.getDeviceInfoByiOS()[0], 'invalid.package')
        
    # Test physical size with invalid device
    assert devices.getPhysicalSizeOfiOS('invalid_id') == ''
    
    # Test package names with invalid device
    assert devices.getPkgnameByiOS('invalid_id') == [] 