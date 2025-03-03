# Getting Started with SoloX Advanced Device Management

## Overview

SoloX provides a comprehensive suite of advanced device management features that enable you to efficiently manage, monitor, and optimize multiple mobile devices. This guide will help you get started with the key features:

- Batch Operations
- Health Monitoring
- Automatic Recovery
- Performance Profiling
- Profile Management

## Installation

```bash
pip install solox
```

## Quick Start

Here's a simple example that demonstrates the basic usage of all major features:

```python
from solox import (
    DevicePool,
    BatchOperationManager,
    HealthMonitor,
    AutoRecovery,
    PerformanceProfiler,
    ProfileManager
)

async def main():
    # Initialize device pool
    device_pool = DevicePool()
    await device_pool.initialize()
    
    # Set up managers
    batch_manager = BatchOperationManager(device_pool)
    health_monitor = HealthMonitor(device_pool)
    auto_recovery = AutoRecovery(device_pool)
    performance_profiler = PerformanceProfiler(device_pool)
    profile_manager = ProfileManager()
    
    # Create and apply a device profile
    high_performance = profile_manager.create_profile(
        name="high_performance",
        settings={
            "performance_mode": True,
            "cpu_governor": "performance"
        },
        compatibility=[".*"],  # All devices
        performance_targets={
            "response_time": 0.1
        }
    )
    
    # Start monitoring devices
    devices = await device_pool.get_all_devices()
    for device in devices:
        # Apply profile
        await profile_manager.apply_profile(
            device.id,
            "high_performance",
            device_pool
        )
        
        # Start health monitoring
        health_monitor.start_monitoring(device.id)
        
        # Enable automatic recovery
        auto_recovery.enable(device.id)
        
        # Start performance profiling
        await performance_profiler.start_profiling(device.id)
    
    # Execute batch operation
    results = await batch_manager.execute_batch(
        operation="launch_app",
        params={"app_id": "com.example.app"},
        devices=devices
    )
    
    print("Batch operation results:", results)

if __name__ == "__main__":
    asyncio.run(main())
```

## Feature Guides

### 1. Batch Operations

Batch operations allow you to execute the same operation across multiple devices simultaneously:

```python
# Execute an operation on all devices
results = await batch_manager.execute_batch(
    operation="install_app",
    params={"app_path": "path/to/app.apk"},
    devices=devices
)

# Execute on specific devices
results = await batch_manager.execute_batch(
    operation="clear_cache",
    params={},
    devices=[device1, device2]
)
```

### 2. Health Monitoring

Monitor device health metrics and receive alerts:

```python
# Start monitoring with custom thresholds
health_monitor.start_monitoring(
    device_id,
    thresholds={
        "cpu_usage": 80,
        "memory_usage": 85,
        "battery_level": 20
    }
)

# Register alert handler
health_monitor.on_alert(device_id, async def handle_alert(alert):
    print(f"Health alert for {device_id}: {alert.message}")
)
```

### 3. Automatic Recovery

Enable automatic recovery for devices:

```python
# Enable with custom recovery steps
auto_recovery.enable(
    device_id,
    recovery_steps=[
        "restart_app",
        "clear_cache",
        "reboot_device"
    ]
)

# Register recovery event handler
auto_recovery.on_recovery(device_id, async def handle_recovery(event):
    print(f"Recovery event for {device_id}: {event.step}")
)
```

### 4. Performance Profiling

Profile device performance:

```python
# Start profiling with custom metrics
await performance_profiler.start_profiling(
    device_id,
    metrics=[
        "response_time",
        "throughput",
        "error_rate"
    ]
)

# Get performance report
report = await performance_profiler.get_report(device_id)
print("Performance report:", report)
```

### 5. Profile Management

Create and manage device profiles:

```python
# Create a profile
test_profile = profile_manager.create_profile(
    name="test_profile",
    settings={
        "performance_mode": True,
        "background_apps": "minimal"
    },
    compatibility=["iPhone.*", "Pixel.*"],
    performance_targets={
        "response_time": 0.2
    }
)

# Apply profile
await profile_manager.apply_profile(
    device_id,
    "test_profile",
    device_pool
)
```

## Best Practices

1. Resource Management
   ```python
   # Use context managers for cleanup
   async with DevicePool() as pool:
       async with BatchOperationManager(pool) as batch_manager:
           await batch_manager.execute_batch(...)
   ```

2. Error Handling
   ```python
   try:
       await batch_manager.execute_batch(...)
   except BatchOperationError as e:
       logger.error(f"Batch operation failed: {e}")
       # Handle failed operations
   ```

3. Monitoring Configuration
   ```python
   # Configure monitoring intervals
   health_monitor.configure(
       check_interval=30,  # seconds
       history_size=100    # entries
   )
   ```

4. Profile Organization
   ```python
   # Group profiles by purpose
   profiles = {
       "testing": [
           profile_manager.create_profile(...),
           profile_manager.create_profile(...)
       ],
       "production": [
           profile_manager.create_profile(...),
           profile_manager.create_profile(...)
       ]
   }
   ```

## Common Issues and Solutions

### 1. Device Connection Issues

```python
# Implement retry logic
async def connect_with_retry(device_id, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            await device_pool.connect(device_id)
            return True
        except ConnectionError:
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
    return False
```

### 2. Performance Monitoring

```python
# Handle missing metrics gracefully
async def get_safe_metrics(device_id):
    try:
        return await performance_profiler.get_metrics(device_id)
    except MetricNotAvailable as e:
        logger.warning(f"Metric not available: {e}")
        return {}
```

### 3. Profile Compatibility

```python
# Validate profile before applying
def validate_profile(profile, device):
    if not profile_manager.check_compatibility(profile, device):
        raise ValueError(f"Profile {profile.name} not compatible with {device.model}")
```

## Integration Examples

### 1. Automated Testing

```python
async def run_performance_test(device_id):
    # Apply test profile
    await profile_manager.apply_profile(device_id, "test_profile", device_pool)
    
    # Start profiling
    await performance_profiler.start_profiling(device_id)
    
    # Run test operations
    await batch_manager.execute_batch(
        operation="run_test_suite",
        params={"suite": "performance"},
        devices=[device_id]
    )
    
    # Get results
    return await performance_profiler.get_report(device_id)
```

### 2. Health-Based Recovery

```python
async def monitor_and_recover():
    health_monitor.on_alert("*", async def handle_alert(alert):
        if alert.severity == "critical":
            await auto_recovery.recover(alert.device_id)
    )
```

### 3. Profile Optimization

```python
async def optimize_profiles():
    for device in devices:
        metrics = await performance_profiler.get_metrics(device.id)
        if metrics["response_time"] > 0.5:
            await profile_manager.apply_profile(
                device.id,
                "high_performance",
                device_pool
            )
```

## Next Steps

1. Explore the [API Documentation](api/) for detailed information about each component
2. Check out the [Examples](examples/) directory for more usage scenarios
3. Join our [Community](https://github.com/solox/community) for support and discussions
4. Read our [Contributing Guide](CONTRIBUTING.md) to get involved in development

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/solox/issues)
- Documentation: [Full documentation](https://solox.readthedocs.io)
- Discord: [Join our community](https://discord.gg/solox) 