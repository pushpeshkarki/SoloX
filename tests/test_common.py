import pytest
import os
import json
from solox.public.common import Devices, File, Method, Platform
from unittest.mock import patch

def test_devices_check():
    devices = Devices()
    
    # Test Android platform
    with pytest.raises(Exception, match='no devices found'):
        devices.devicesCheck(Platform.Android)
        
    # Test iOS platform
    with pytest.raises(Exception, match='no devices found'):
        devices.devicesCheck(Platform.iOS)
        
    # Test unsupported platform
    with pytest.raises(ValueError, match='Unsupported platform'):
        devices.devicesCheck('Windows')

def test_get_device_detail():
    devices = Devices()
    
    # Test Android platform
    with pytest.raises(Exception):
        devices.getDdeviceDetail('invalid_id', Platform.Android)
    
    # Test iOS platform
    with patch('solox.public.common.Device') as mock_device:
        mock_device.return_value.device_info = None
        with pytest.raises(Exception):
            devices.getDdeviceDetail('invalid_id', Platform.iOS)
    
    # Test unsupported platform
    with pytest.raises(ValueError, match='Unsupported platform'):
        devices.getDdeviceDetail('invalid_id', 'Windows')

def test_record_net():
    file = File()
    
    # Test 'pre' type
    result = file.record_net('pre', 100, 200)
    assert isinstance(result, dict)
    assert result['send'] == 100
    assert result['recv'] == 200
    
    # Test 'next' type
    result = file.record_net('next', 300, 400)
    assert isinstance(result, dict)
    assert result['send'] == 200  # 300 - 100
    assert result['recv'] == 200  # 400 - 200
    
    # Test invalid type
    with pytest.raises(ValueError, match='Unsupported network record type'):
        file.record_net('invalid', 100, 200)

def test_request():
    class MockRequest:
        def __init__(self, method, data):
            self.method = method
            self.form = data if method == 'POST' else {}
            self.args = data if method == 'GET' else {}
    
    # Test POST request
    post_request = MockRequest('POST', {'test': 'value'})
    assert Method._request(post_request, 'test') == 'value'
    
    # Test GET request
    get_request = MockRequest('GET', {'test': 'value'})
    assert Method._request(get_request, 'test') == 'value'
    
    # Test unsupported method
    with pytest.raises(ValueError, match='Unsupported HTTP method'):
        Method._request(MockRequest('PUT', {}), 'test') 