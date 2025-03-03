# BatchOperationManager API Reference

## Overview

The `BatchOperationManager` class provides functionality for executing operations across multiple devices in parallel. It handles error management and result aggregation automatically.

## Class Definition

```python
class BatchOperationManager:
    def __init__(self, device_pool: DevicePool):
        """
        Initialize the batch operation manager.
        
        Args:
            device_pool (DevicePool): The device pool to manage operations for
        """
        
    async def execute_batch(
        self, 
        operation: str, 
        params: Dict, 
        devices: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Execute an operation across multiple devices in parallel.
        
        Args:
            operation (str): The name of the operation to execute
            params (Dict): Parameters for the operation
            devices (Optional[List[str]]): List of device IDs. If None, uses all devices
            
        Returns:
            Dict[str, any]: Results for each device
            {
                "device_id": {
                    "status": "success"|"error",
                    "result": any,
                    "error": str  # Only present if status is "error"
                }
            }
            
        Raises:
            DeviceError: If a device is not found
            OperationError: If the operation fails
        """
```

## Usage Examples

### Basic Usage

```python
# Initialize
device_pool = DevicePool()
batch_manager = BatchOperationManager(device_pool)

# Execute on all devices
result = await batch_manager.execute_batch(
    operation="install_app",
    params={"app_path": "app.apk"}
)
```

### Specific Devices

```python
# Execute on specific devices
result = await batch_manager.execute_batch(
    operation="run_test",
    params={"test_name": "performance_test"},
    devices=["device1", "device2"]
)
```

### Error Handling

```python
try:
    result = await batch_manager.execute_batch(
        operation="complex_operation",
        params={"param1": "value1"}
    )
    
    for device_id, device_result in result.items():
        if device_result["status"] == "error":
            logger.error(f"Operation failed on {device_id}: {device_result['error']}")
        else:
            logger.info(f"Operation succeeded on {device_id}: {device_result['result']}")
except Exception as e:
    logger.error(f"Batch operation failed: {e}")
```

## Implementation Details

### Thread Pool

The manager uses a `ThreadPoolExecutor` with a maximum of 10 workers to execute operations in parallel:

```python
self.executor = ThreadPoolExecutor(max_workers=10)
```

### Operation Execution

Operations are executed using Python's `getattr` to dynamically call device methods:

```python
result = getattr(device, operation)(**params)
```

### Error Management

Errors are caught and logged at multiple levels:
1. Individual operation level
2. Device level
3. Batch level

## Best Practices

1. Resource Management
   ```python
   try:
       batch_manager = BatchOperationManager(device_pool)
       # ... use batch manager
   finally:
       batch_manager.executor.shutdown()
   ```

2. Operation Parameters
   ```python
   # Good - clear parameter structure
   params = {
       "app_path": "path/to/app.apk",
       "force_install": True
   }
   
   # Bad - unclear parameter structure
   params = {
       "path": "path/to/app.apk",
       "f": True
   }
   ```

3. Error Handling
   ```python
   result = await batch_manager.execute_batch(...)
   failed_devices = [
       device_id for device_id, r in result.items()
       if r["status"] == "error"
   ]
   if failed_devices:
       logger.error(f"Operation failed on devices: {failed_devices}")
   ```

## Common Issues

1. Device Not Found
   ```python
   # Handle missing devices
   if not device_pool.get_device(device_id):
       logger.error(f"Device {device_id} not found")
   ```

2. Operation Not Supported
   ```python
   # Check operation support
   if not hasattr(device, operation):
       logger.error(f"Operation {operation} not supported")
   ```

3. Parameter Validation
   ```python
   # Validate parameters before execution
   required_params = {"app_path", "force_install"}
   if not all(param in params for param in required_params):
       raise ValueError("Missing required parameters")
   ```

## Performance Considerations

1. Batch Size
   - Consider memory usage when executing on many devices
   - Default thread pool size is 10
   - Adjust based on system capabilities

2. Operation Timeout
   - No built-in timeout mechanism
   - Implement at operation level if needed
   - Consider using `asyncio.wait_for`

3. Resource Usage
   - Thread pool resources
   - Network bandwidth for remote devices
   - System memory for large operations 