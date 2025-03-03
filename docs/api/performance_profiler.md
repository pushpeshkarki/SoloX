# PerformanceProfiler API Reference

## Overview

The `PerformanceProfiler` class provides comprehensive performance monitoring and analysis capabilities for mobile devices. It collects real-time metrics, maintains historical data, and supports long-term performance tracking.

## Class Definition

```python
@dataclass
class PerformanceMetrics:
    """Performance metrics for a device."""
    device_id: str
    response_time: float
    throughput: float
    error_rate: float
    timestamp: float

class PerformanceProfiler:
    def __init__(self, device_pool: DevicePool):
        """
        Initialize the performance profiler.
        
        Args:
            device_pool (DevicePool): The device pool to profile
        """
        
    async def start_profiling(
        self, 
        device_id: str, 
        duration: int = 60
    ) -> List[PerformanceMetrics]:
        """
        Profile device performance for a specified duration.
        
        Args:
            device_id (str): The ID of the device to profile
            duration (int): Duration in seconds to profile
            
        Returns:
            List[PerformanceMetrics]: List of collected metrics
            
        Raises:
            DeviceError: If the device is not found
        """
```

## Usage Examples

### Basic Profiling

```python
# Initialize
profiler = PerformanceProfiler(device_pool)

# Start profiling
metrics = await profiler.start_profiling("device1", duration=60)
for m in metrics:
    print(f"Response Time: {m.response_time}s")
    print(f"Throughput: {m.throughput} ops/s")
    print(f"Error Rate: {m.error_rate}%")
```

### Continuous Monitoring

```python
async def monitor_performance(device_id: str):
    while True:
        metrics = await profiler._collect_metrics(device_id)
        if metrics.error_rate > 0.01:  # 1% error rate threshold
            logger.warning(f"High error rate on {device_id}: {metrics.error_rate}%")
        if metrics.response_time > 1.0:  # 1 second response time threshold
            logger.warning(f"Slow response on {device_id}: {metrics.response_time}s")
        await asyncio.sleep(60)
```

### Performance Analysis

```python
def analyze_performance(device_id: str) -> Dict[str, float]:
    history = profiler.metrics_history[device_id]
    return {
        "avg_response_time": sum(m.response_time for m in history) / len(history),
        "avg_throughput": sum(m.throughput for m in history) / len(history),
        "error_rate_trend": [m.error_rate for m in history],
        "peak_throughput": max(m.throughput for m in history)
    }
```

## Implementation Details

### Metrics Collection

The profiler collects the following metrics:
- Response Time: Time taken for device to respond to requests
- Throughput: Operations per second
- Error Rate: Percentage of failed operations
- Timestamp: When metrics were collected

### History Management

```python
def _update_metrics_history(self, device_id: str, metrics: PerformanceMetrics):
    """Update metrics history for a device."""
    if device_id not in self.metrics_history:
        self.metrics_history[device_id] = []
    self.metrics_history[device_id].append(metrics)
    # Keep last 1000 records
    self.metrics_history[device_id] = self.metrics_history[device_id][-1000:]
```

### Error Handling

```python
try:
    metrics = await profiler._collect_metrics(device_id)
except DeviceError as e:
    logger.error(f"Device not found: {e}")
    metrics = PerformanceMetrics(
        device_id=device_id,
        response_time=0.0,
        throughput=0.0,
        error_rate=1.0,
        timestamp=time.time()
    )
```

## Best Practices

1. Regular Profiling
   ```python
   async def schedule_profiling(device_id: str):
       # Profile every hour
       while True:
           await profiler.start_profiling(device_id, duration=300)
           await asyncio.sleep(3600)
   ```

2. Performance Alerts
   ```python
   def check_performance_thresholds(metrics: PerformanceMetrics):
       if metrics.response_time > 2.0:
           alert("High Latency", f"Device {metrics.device_id}")
       if metrics.error_rate > 0.05:
           alert("High Error Rate", f"Device {metrics.device_id}")
   ```

3. Data Analysis
   ```python
   def generate_performance_report(device_id: str):
       history = profiler.metrics_history[device_id]
       return {
           "daily_avg": calculate_daily_averages(history),
           "peak_times": find_peak_usage_times(history),
           "error_patterns": analyze_error_patterns(history)
       }
   ```

## Advanced Use Cases

### Load Testing

```python
async def load_test(device_id: str, duration: int = 300):
    """Run a load test on a device."""
    baseline = await profiler._collect_metrics(device_id)
    
    # Start load generation
    load_task = asyncio.create_task(generate_load(device_id))
    
    # Collect metrics during load
    metrics = await profiler.start_profiling(device_id, duration)
    
    # Stop load
    load_task.cancel()
    
    return {
        "baseline": baseline,
        "under_load": metrics,
        "degradation": calculate_degradation(baseline, metrics)
    }
```

### Performance Comparison

```python
async def compare_devices(device_ids: List[str]) -> Dict[str, Dict]:
    """Compare performance across multiple devices."""
    results = {}
    for device_id in device_ids:
        metrics = await profiler._collect_metrics(device_id)
        results[device_id] = {
            "response_time": metrics.response_time,
            "throughput": metrics.throughput,
            "error_rate": metrics.error_rate
        }
    return results
```

### Trend Analysis

```python
def analyze_trends(device_id: str, window: int = 24) -> Dict:
    """Analyze performance trends over time."""
    history = profiler.metrics_history[device_id]
    return {
        "response_time_trend": calculate_moving_average(
            [m.response_time for m in history], 
            window
        ),
        "throughput_trend": calculate_moving_average(
            [m.throughput for m in history],
            window
        )
    }
```

## Performance Considerations

1. Data Collection
   - Minimize impact on device performance
   - Use appropriate sampling intervals
   - Consider data storage requirements

2. Analysis Overhead
   - Process metrics asynchronously
   - Cache frequently accessed calculations
   - Implement efficient data structures

3. Resource Management
   - Clean up old metrics regularly
   - Implement data retention policies
   - Monitor profiler resource usage

## Integration Examples

### With Health Monitoring

```python
class DeviceMonitor:
    def __init__(self, device_pool: DevicePool):
        self.health_monitor = HealthMonitor(device_pool)
        self.profiler = PerformanceProfiler(device_pool)
        
    async def monitor_device(self, device_id: str):
        while True:
            health = await self.health_monitor.check_device_health(device_id)
            metrics = await self.profiler._collect_metrics(device_id)
            
            if health.status != "healthy" or metrics.error_rate > 0.01:
                await self.handle_issues(device_id, health, metrics)
            
            await asyncio.sleep(60)
```

### With Reporting System

```python
class PerformanceReporter:
    def __init__(self, profiler: PerformanceProfiler):
        self.profiler = profiler
        
    async def generate_daily_report(self, device_id: str):
        metrics = self.profiler.metrics_history[device_id]
        report = {
            "summary": calculate_summary_statistics(metrics),
            "charts": generate_performance_charts(metrics),
            "recommendations": generate_recommendations(metrics)
        }
        await self.send_report(report)
``` 