# AutoRecovery API Reference

## Overview

The `AutoRecovery` class provides automated recovery mechanisms for devices experiencing issues. It works in conjunction with the `HealthMonitor` to detect and resolve device problems automatically.

## Class Definition

```python
class AutoRecovery:
    def __init__(self, device_pool: DevicePool, health_monitor: HealthMonitor):
        """
        Initialize the auto recovery system.
        
        Args:
            device_pool (DevicePool): The device pool to manage
            health_monitor (HealthMonitor): The health monitor to use for detection
        """
        
    async def check_and_recover(self, device_id: str) -> bool:
        """
        Check device health and attempt recovery if needed.
        
        Args:
            device_id (str): The ID of the device to check and recover
            
        Returns:
            bool: True if recovery was successful or not needed, False if recovery failed
            
        Raises:
            DeviceError: If the device is not found
        """
```

## Usage Examples

### Basic Recovery

```python
# Initialize
recovery = AutoRecovery(device_pool, health_monitor)

# Check and recover if needed
success = await recovery.check_and_recover("device1")
if not success:
    logger.error("Recovery failed for device1")
```

### Recovery with Monitoring

```python
async def monitor_and_recover(device_id: str):
    while True:
        try:
            success = await recovery.check_and_recover(device_id)
            if not success:
                notify_admin(f"Recovery failed for device {device_id}")
        except Exception as e:
            logger.error(f"Recovery error: {e}")
        await asyncio.sleep(300)  # Check every 5 minutes
```

### Multiple Device Recovery

```python
async def recover_all_devices(device_ids: List[str]):
    results = {}
    for device_id in device_ids:
        results[device_id] = await recovery.check_and_recover(device_id)
    return results
```

## Recovery Steps

The system implements a progressive recovery strategy:

1. High Resource Usage (CPU/Memory > 90%)
   ```python
   if health.cpu_usage > 90 or health.memory_usage > 90:
       await device.restart_apps()
   ```

2. Poor Connection (strength < 30%)
   ```python
   if health.connection_strength < 30:
       await device.reconnect()
   ```

3. Critical Error
   ```python
   if health.status == "error":
       await device.reboot()
   ```

## Implementation Details

### Recovery Attempt Tracking

- Maximum attempts: 3 (configurable)
- Attempts reset on successful recovery
- Per-device attempt counting

### Recovery Flow

1. Check device health
2. Determine recovery action
3. Execute recovery
4. Verify recovery success
5. Update attempt counter

### Error Handling

```python
try:
    await recovery._attempt_recovery(device_id, health)
except DeviceError as e:
    logger.error(f"Device not found: {e}")
except Exception as e:
    logger.error(f"Recovery failed: {e}")
```

## Best Practices

1. Progressive Recovery
   ```python
   async def custom_recovery(device_id: str):
       # Try least intrusive methods first
       if await soft_reset(device_id):
           return True
       if await restart_apps(device_id):
           return True
       # Last resort
       return await hard_reset(device_id)
   ```

2. Recovery Monitoring
   ```python
   async def monitor_recovery(device_id: str):
       initial_health = await health_monitor.check_device_health(device_id)
       await recovery.check_and_recover(device_id)
       final_health = await health_monitor.check_device_health(device_id)
       return final_health.status == "healthy"
   ```

3. Attempt Management
   ```python
   def should_attempt_recovery(device_id: str) -> bool:
       attempts = recovery.recovery_attempts.get(device_id, 0)
       return attempts < recovery.max_attempts
   ```

## Common Issues

1. Recovery Loop
   ```python
   # Prevent continuous recovery attempts
   if recovery.recovery_attempts.get(device_id, 0) >= recovery.max_attempts:
       notify_admin(f"Device {device_id} needs manual intervention")
       return False
   ```

2. Failed Recovery Verification
   ```python
   async def verify_recovery(device_id: str) -> bool:
       # Wait for device to stabilize
       await asyncio.sleep(10)
       health = await health_monitor.check_device_health(device_id)
       return health.status == "healthy"
   ```

3. Resource Cleanup
   ```python
   async def cleanup_after_recovery(device_id: str):
       # Reset attempt counter
       recovery.recovery_attempts[device_id] = 0
       # Clear error states
       await device.clear_error_state()
   ```

## Performance Considerations

1. Recovery Timing
   - Allow sufficient time between attempts
   - Consider device reboot time
   - Implement progressive delays

2. Resource Impact
   - Monitor system resources during recovery
   - Consider impact on other devices
   - Implement recovery queuing

3. Network Usage
   - Handle offline recovery scenarios
   - Implement timeout mechanisms
   - Consider bandwidth usage

## Integration Examples

### With Health Monitoring

```python
class DeviceManager:
    def __init__(self):
        self.device_pool = DevicePool()
        self.health_monitor = HealthMonitor(self.device_pool)
        self.recovery = AutoRecovery(self.device_pool, self.health_monitor)
        
    async def manage_device(self, device_id: str):
        while True:
            health = await self.health_monitor.check_device_health(device_id)
            if health.status != "healthy":
                await self.recovery.check_and_recover(device_id)
            await asyncio.sleep(60)
```

### With Notification System

```python
class RecoveryNotifier:
    def __init__(self, recovery: AutoRecovery):
        self.recovery = recovery
        
    async def monitor_recoveries(self):
        while True:
            for device_id, attempts in self.recovery.recovery_attempts.items():
                if attempts >= self.recovery.max_attempts:
                    await self.notify_failed_recovery(device_id)
            await asyncio.sleep(300)
```

### With Custom Recovery Steps

```python
class CustomRecovery(AutoRecovery):
    async def _attempt_recovery(self, device_id: str, health: DeviceHealth):
        if health.status == "warning":
            await self.custom_warning_recovery(device_id)
        elif health.status == "error":
            await self.custom_error_recovery(device_id)
``` 