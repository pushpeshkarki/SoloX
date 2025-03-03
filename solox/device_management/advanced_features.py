"""
Advanced device management features for SoloX.

This module provides enhanced capabilities for managing multiple devices:
- Batch operations across multiple devices
- Health monitoring and diagnostics
- Automatic recovery mechanisms
- Performance profiling
- Custom device profiles
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

from .device_pool import DevicePool
from .exceptions import DeviceError, OperationError

logger = logging.getLogger(__name__)

@dataclass
class DeviceHealth:
    """Device health metrics and status."""
    device_id: str
    cpu_usage: float
    memory_usage: float
    battery_level: Optional[float]
    temperature: Optional[float]
    connection_strength: float
    last_error: Optional[str] = None
    status: str = "healthy"

@dataclass
class PerformanceMetrics:
    """Performance metrics for a device."""
    device_id: str
    response_time: float
    throughput: float
    error_rate: float
    timestamp: float

@dataclass
class DeviceProfile:
    """Custom device configuration profile."""
    name: str
    settings: Dict[str, Union[str, int, float, bool]]
    compatibility: List[str]
    performance_targets: Dict[str, float]

class BatchOperationManager:
    """Manages batch operations across multiple devices."""
    
    def __init__(self, device_pool: DevicePool):
        self.device_pool = device_pool
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def execute_batch(self, operation: str, params: Dict, devices: Optional[List[str]] = None) -> Dict[str, any]:
        """Execute an operation across multiple devices in parallel."""
        if devices is None:
            devices = self.device_pool.list_devices()
        
        results = {}
        futures = []
        
        for device_id in devices:
            future = self.executor.submit(
                self._execute_single_operation,
                device_id,
                operation,
                params
            )
            futures.append((device_id, future))
        
        for device_id, future in futures:
            try:
                results[device_id] = future.result()
            except Exception as e:
                logger.error(f"Operation failed for device {device_id}: {str(e)}")
                results[device_id] = {"status": "error", "error": str(e)}
        
        return results
    
    def _execute_single_operation(self, device_id: str, operation: str, params: Dict) -> Dict:
        """Execute operation on a single device."""
        device = self.device_pool.get_device(device_id)
        if not device:
            raise DeviceError(f"Device {device_id} not found")
        
        try:
            result = getattr(device, operation)(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            raise OperationError(f"Operation {operation} failed: {str(e)}")

class HealthMonitor:
    """Monitors and manages device health."""
    
    def __init__(self, device_pool: DevicePool):
        self.device_pool = device_pool
        self.health_history: Dict[str, List[DeviceHealth]] = {}
        self.alert_thresholds = {
            "cpu_usage": 90.0,
            "memory_usage": 90.0,
            "battery_level": 15.0,
            "temperature": 45.0,
            "connection_strength": 30.0
        }
    
    async def check_device_health(self, device_id: str) -> DeviceHealth:
        """Check health metrics for a specific device."""
        device = self.device_pool.get_device(device_id)
        if not device:
            raise DeviceError(f"Device {device_id} not found")
        
        try:
            metrics = await device.get_metrics()
            health = DeviceHealth(
                device_id=device_id,
                cpu_usage=metrics["cpu_usage"],
                memory_usage=metrics["memory_usage"],
                battery_level=metrics.get("battery_level"),
                temperature=metrics.get("temperature"),
                connection_strength=metrics["connection_strength"]
            )
            
            # Update status based on thresholds
            if any(
                getattr(health, metric) > threshold
                for metric, threshold in self.alert_thresholds.items()
                if getattr(health, metric) is not None
            ):
                health.status = "warning"
            
            self._update_health_history(device_id, health)
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for device {device_id}: {str(e)}")
            return DeviceHealth(
                device_id=device_id,
                cpu_usage=0.0,
                memory_usage=0.0,
                battery_level=None,
                temperature=None,
                connection_strength=0.0,
                last_error=str(e),
                status="error"
            )
    
    def _update_health_history(self, device_id: str, health: DeviceHealth):
        """Update health history for a device."""
        if device_id not in self.health_history:
            self.health_history[device_id] = []
        self.health_history[device_id].append(health)
        # Keep last 100 records
        self.health_history[device_id] = self.health_history[device_id][-100:]

class AutoRecovery:
    """Handles automatic device recovery."""
    
    def __init__(self, device_pool: DevicePool, health_monitor: HealthMonitor):
        self.device_pool = device_pool
        self.health_monitor = health_monitor
        self.recovery_attempts: Dict[str, int] = {}
        self.max_attempts = 3
    
    async def check_and_recover(self, device_id: str) -> bool:
        """Check device health and attempt recovery if needed."""
        health = await self.health_monitor.check_device_health(device_id)
        
        if health.status == "healthy":
            self.recovery_attempts[device_id] = 0
            return True
        
        if self.recovery_attempts.get(device_id, 0) >= self.max_attempts:
            logger.error(f"Max recovery attempts reached for device {device_id}")
            return False
        
        try:
            await self._attempt_recovery(device_id, health)
            self.recovery_attempts[device_id] = self.recovery_attempts.get(device_id, 0) + 1
            return True
        except Exception as e:
            logger.error(f"Recovery failed for device {device_id}: {str(e)}")
            return False
    
    async def _attempt_recovery(self, device_id: str, health: DeviceHealth):
        """Attempt to recover a device based on its health status."""
        device = self.device_pool.get_device(device_id)
        if not device:
            raise DeviceError(f"Device {device_id} not found")
        
        if health.cpu_usage > 90 or health.memory_usage > 90:
            await device.restart_apps()
        
        if health.connection_strength < 30:
            await device.reconnect()
        
        if health.status == "error":
            await device.reboot()

class PerformanceProfiler:
    """Profiles device performance."""
    
    def __init__(self, device_pool: DevicePool):
        self.device_pool = device_pool
        self.metrics_history: Dict[str, List[PerformanceMetrics]] = {}
    
    async def start_profiling(self, device_id: str, duration: int = 60) -> List[PerformanceMetrics]:
        """Profile device performance for a specified duration."""
        device = self.device_pool.get_device(device_id)
        if not device:
            raise DeviceError(f"Device {device_id} not found")
        
        metrics_list = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            metrics = await self._collect_metrics(device_id)
            metrics_list.append(metrics)
            self._update_metrics_history(device_id, metrics)
            await asyncio.sleep(1)
        
        return metrics_list
    
    async def _collect_metrics(self, device_id: str) -> PerformanceMetrics:
        """Collect performance metrics for a device."""
        device = self.device_pool.get_device(device_id)
        start_time = time.time()
        
        try:
            response = await device.ping()
            response_time = time.time() - start_time
            
            metrics = await device.get_metrics()
            return PerformanceMetrics(
                device_id=device_id,
                response_time=response_time,
                throughput=metrics["throughput"],
                error_rate=metrics["error_rate"],
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Failed to collect metrics for device {device_id}: {str(e)}")
            return PerformanceMetrics(
                device_id=device_id,
                response_time=0.0,
                throughput=0.0,
                error_rate=1.0,
                timestamp=time.time()
            )
    
    def _update_metrics_history(self, device_id: str, metrics: PerformanceMetrics):
        """Update metrics history for a device."""
        if device_id not in self.metrics_history:
            self.metrics_history[device_id] = []
        self.metrics_history[device_id].append(metrics)
        # Keep last 1000 records
        self.metrics_history[device_id] = self.metrics_history[device_id][-1000:]

class ProfileManager:
    """Manages custom device profiles."""
    
    def __init__(self):
        self.profiles: Dict[str, DeviceProfile] = {}
    
    def create_profile(self, name: str, settings: Dict, compatibility: List[str], 
                      performance_targets: Dict[str, float]) -> DeviceProfile:
        """Create a new device profile."""
        profile = DeviceProfile(
            name=name,
            settings=settings,
            compatibility=compatibility,
            performance_targets=performance_targets
        )
        self.profiles[name] = profile
        return profile
    
    def apply_profile(self, device_id: str, profile_name: str, device_pool: DevicePool) -> bool:
        """Apply a profile to a device."""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile {profile_name} not found")
        
        device = device_pool.get_device(device_id)
        if not device:
            raise DeviceError(f"Device {device_id} not found")
        
        profile = self.profiles[profile_name]
        
        # Check compatibility
        if device.model not in profile.compatibility:
            raise ValueError(f"Profile {profile_name} is not compatible with device {device_id}")
        
        try:
            for setting, value in profile.settings.items():
                setattr(device, setting, value)
            return True
        except Exception as e:
            logger.error(f"Failed to apply profile {profile_name} to device {device_id}: {str(e)}")
            return False 