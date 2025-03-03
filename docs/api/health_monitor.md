# HealthMonitor API Reference

## Overview

The `HealthMonitor` class provides real-time health monitoring for mobile devices. It tracks various metrics, maintains historical data, and provides alerts when thresholds are exceeded.

## Class Definition

```python
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

class HealthMonitor:
    def __init__(self, device_pool: DevicePool):
        """
        Initialize the health monitor.
        
        Args:
            device_pool (DevicePool): The device pool to monitor
        """
        
    async def check_device_health(self, device_id: str) -> DeviceHealth:
        """
        Check health metrics for a specific device.
        
        Args:
            device_id (str): The ID of the device to check
            
        Returns:
            DeviceHealth: Current health status and metrics
            
        Raises:
            DeviceError: If the device is not found
        """
```

## Usage Examples

### Basic Health Check

```python
# Initialize
monitor = HealthMonitor(device_pool)

# Check device health
health = await monitor.check_device_health("device1")
print(f"Status: {health.status}")
print(f"CPU Usage: {health.cpu_usage}%")
print(f"Memory Usage: {health.memory_usage}%")
```

### Alert Handling

```python
# Check for warnings
health = await monitor.check_device_health("device1")
if health.status == "warning":
    if health.cpu_usage > 90:
        logger.warning(f"High CPU usage on device {health.device_id}: {health.cpu_usage}%")
    if health.memory_usage > 90:
        logger.warning(f"High memory usage on device {health.device_id}: {health.memory_usage}%")
```

### Historical Data

```python
# Access health history
device_history = monitor.health_history["device1"]
recent_health = device_history[-1]  # Most recent check
avg_cpu = sum(h.cpu_usage for h in device_history) / len(device_history)
```

## Alert Thresholds

The monitor uses the following default thresholds:

```python
alert_thresholds = {
    "cpu_usage": 90.0,      # Percentage
    "memory_usage": 90.0,   # Percentage
    "battery_level": 15.0,  # Percentage
    "temperature": 45.0,    # Celsius
    "connection_strength": 30.0  # Percentage
}
```

### Customizing Thresholds

```python
# Create monitor with custom thresholds
monitor = HealthMonitor(device_pool)
monitor.alert_thresholds.update({
    "cpu_usage": 80.0,  # More conservative CPU threshold
    "memory_usage": 85.0  # More conservative memory threshold
})
```

## Implementation Details

### Health Status Calculation

The health status is determined based on thresholds:
- "healthy": All metrics within normal ranges
- "warning": Any metric exceeds its threshold
- "error": Device communication error or critical issue

### History Management

- Maintains last 100 health records per device
- Automatically prunes older records
- Thread-safe implementation

### Error Handling

```python
try:
    health = await monitor.check_device_health("device1")
except DeviceError as e:
    logger.error(f"Device not found: {e}")
except Exception as e:
    logger.error(f"Health check failed: {e}")
```

## Best Practices

1. Regular Monitoring
   ```python
   async def monitor_device(device_id: str):
       while True:
           health = await monitor.check_device_health(device_id)
           if health.status != "healthy":
               await handle_unhealthy_device(device_id, health)
           await asyncio.sleep(60)  # Check every minute
   ```

2. Alert Handling
   ```python
   def handle_health_alert(health: DeviceHealth):
       if health.cpu_usage > 90:
           notify_admin("High CPU Usage", f"Device {health.device_id}")
       if health.battery_level and health.battery_level < 15:
           notify_admin("Low Battery", f"Device {health.device_id}")
   ```

3. Historical Analysis
   ```python
   def analyze_device_health(device_id: str):
       history = monitor.health_history[device_id]
       cpu_trend = [h.cpu_usage for h in history]
       mem_trend = [h.memory_usage for h in history]
       return {
           "avg_cpu": sum(cpu_trend) / len(cpu_trend),
           "avg_memory": sum(mem_trend) / len(mem_trend),
           "warnings": sum(1 for h in history if h.status == "warning")
       }
   ```

## Common Issues

1. Missing Metrics
   ```python
   # Handle optional metrics
   if health.battery_level is not None:
       check_battery(health.battery_level)
   if health.temperature is not None:
       check_temperature(health.temperature)
   ```

2. Connection Issues
   ```python
   # Handle connection problems
   if health.connection_strength < 30:
       await reconnect_device(health.device_id)
   ```

3. Resource Leaks
   ```python
   # Clean up old history
   def cleanup_history():
       for device_id in monitor.health_history:
           monitor.health_history[device_id] = monitor.health_history[device_id][-100:]
   ```

## Performance Considerations

1. Monitoring Frequency
   - Balance between accuracy and resource usage
   - Consider device capabilities
   - Adjust based on device state

2. History Size
   - Default 100 records per device
   - Memory usage grows with device count
   - Consider cleanup strategies

3. Metric Collection
   - Asynchronous collection
   - Timeout handling
   - Batch collection for multiple devices 