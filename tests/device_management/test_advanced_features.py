"""Tests for advanced device management features."""

import pytest
import asyncio
from unittest.mock import Mock, patch

from solox.device_management.advanced_features import (
    BatchOperationManager,
    HealthMonitor,
    AutoRecovery,
    PerformanceProfiler,
    ProfileManager,
    DeviceHealth,
    PerformanceMetrics,
    DeviceProfile
)
from solox.device_management.device_pool import DevicePool
from solox.device_management.exceptions import DeviceError, OperationError

@pytest.fixture
def device_pool():
    """Create a mock device pool."""
    pool = Mock(spec=DevicePool)
    device = Mock()
    device.model = "test_model"
    device.get_metrics.return_value = {
        "cpu_usage": 50.0,
        "memory_usage": 60.0,
        "battery_level": 80.0,
        "temperature": 35.0,
        "connection_strength": 90.0,
        "throughput": 100.0,
        "error_rate": 0.01
    }
    pool.get_device.return_value = device
    pool.list_devices.return_value = ["device1", "device2"]
    return pool

@pytest.mark.asyncio
async def test_batch_operations(device_pool):
    """Test batch operations across multiple devices."""
    manager = BatchOperationManager(device_pool)
    
    # Test successful batch operation
    result = await manager.execute_batch("test_operation", {"param": "value"})
    assert len(result) == 2
    assert all(r["status"] == "success" for r in result.values())
    
    # Test operation failure
    device_pool.get_device.return_value.test_operation.side_effect = Exception("Test error")
    result = await manager.execute_batch("test_operation", {"param": "value"})
    assert all(r["status"] == "error" for r in result.values())

@pytest.mark.asyncio
async def test_health_monitoring(device_pool):
    """Test device health monitoring."""
    monitor = HealthMonitor(device_pool)
    
    # Test normal health check
    health = await monitor.check_device_health("device1")
    assert health.status == "healthy"
    assert health.cpu_usage == 50.0
    assert health.memory_usage == 60.0
    
    # Test warning threshold
    device_pool.get_device.return_value.get_metrics.return_value["cpu_usage"] = 95.0
    health = await monitor.check_device_health("device1")
    assert health.status == "warning"
    
    # Test error handling
    device_pool.get_device.return_value.get_metrics.side_effect = Exception("Test error")
    health = await monitor.check_device_health("device1")
    assert health.status == "error"
    assert health.last_error is not None

@pytest.mark.asyncio
async def test_auto_recovery(device_pool):
    """Test automatic device recovery."""
    monitor = HealthMonitor(device_pool)
    recovery = AutoRecovery(device_pool, monitor)
    
    # Test successful recovery
    assert await recovery.check_and_recover("device1")
    
    # Test recovery with high resource usage
    device_pool.get_device.return_value.get_metrics.return_value["cpu_usage"] = 95.0
    assert await recovery.check_and_recover("device1")
    device_pool.get_device.return_value.restart_apps.assert_called_once()
    
    # Test max recovery attempts
    for _ in range(4):
        await recovery.check_and_recover("device1")
    assert recovery.recovery_attempts["device1"] >= recovery.max_attempts

@pytest.mark.asyncio
async def test_performance_profiling(device_pool):
    """Test device performance profiling."""
    profiler = PerformanceProfiler(device_pool)
    
    # Test metrics collection
    metrics = await profiler._collect_metrics("device1")
    assert isinstance(metrics, PerformanceMetrics)
    assert metrics.device_id == "device1"
    assert metrics.error_rate == 0.01
    
    # Test error handling
    device_pool.get_device.return_value.get_metrics.side_effect = Exception("Test error")
    metrics = await profiler._collect_metrics("device1")
    assert metrics.error_rate == 1.0

def test_profile_management(device_pool):
    """Test device profile management."""
    manager = ProfileManager()
    
    # Test profile creation
    profile = manager.create_profile(
        name="test_profile",
        settings={"setting1": "value1"},
        compatibility=["test_model"],
        performance_targets={"response_time": 0.1}
    )
    assert isinstance(profile, DeviceProfile)
    assert profile.name == "test_profile"
    
    # Test profile application
    assert manager.apply_profile("device1", "test_profile", device_pool)
    
    # Test incompatible profile
    profile.compatibility = ["other_model"]
    with pytest.raises(ValueError):
        manager.apply_profile("device1", "test_profile", device_pool)
    
    # Test non-existent profile
    with pytest.raises(ValueError):
        manager.apply_profile("device1", "non_existent", device_pool)

@pytest.mark.asyncio
async def test_health_history(device_pool):
    """Test health history tracking."""
    monitor = HealthMonitor(device_pool)
    
    # Record multiple health checks
    for _ in range(5):
        await monitor.check_device_health("device1")
    
    assert len(monitor.health_history["device1"]) == 5
    
    # Test history limit
    for _ in range(200):
        await monitor.check_device_health("device1")
    
    assert len(monitor.health_history["device1"]) == 100

@pytest.mark.asyncio
async def test_metrics_history(device_pool):
    """Test metrics history tracking."""
    profiler = PerformanceProfiler(device_pool)
    
    # Record multiple metrics
    for _ in range(5):
        metrics = await profiler._collect_metrics("device1")
        profiler._update_metrics_history("device1", metrics)
    
    assert len(profiler.metrics_history["device1"]) == 5
    
    # Test history limit
    for _ in range(2000):
        metrics = await profiler._collect_metrics("device1")
        profiler._update_metrics_history("device1", metrics)
    
    assert len(profiler.metrics_history["device1"]) == 1000 