# ProfileManager API Reference

## Overview

The `ProfileManager` class provides functionality for creating, managing, and applying device configuration profiles. It supports customizable settings, compatibility checks, and performance targets.

## Class Definition

```python
@dataclass
class DeviceProfile:
    """Custom device configuration profile."""
    name: str
    settings: Dict[str, Union[str, int, float, bool]]
    compatibility: List[str]
    performance_targets: Dict[str, float]

class ProfileManager:
    def __init__(self):
        """Initialize the profile manager."""
        
    def create_profile(
        self,
        name: str,
        settings: Dict,
        compatibility: List[str],
        performance_targets: Dict[str, float]
    ) -> DeviceProfile:
        """
        Create a new device profile.
        
        Args:
            name (str): Profile name
            settings (Dict): Device settings
            compatibility (List[str]): Compatible device models
            performance_targets (Dict[str, float]): Target performance metrics
            
        Returns:
            DeviceProfile: The created profile
        """
        
    def apply_profile(
        self,
        device_id: str,
        profile_name: str,
        device_pool: DevicePool
    ) -> bool:
        """
        Apply a profile to a device.
        
        Args:
            device_id (str): Target device ID
            profile_name (str): Name of profile to apply
            device_pool (DevicePool): Device pool instance
            
        Returns:
            bool: True if profile was applied successfully
            
        Raises:
            ValueError: If profile not found or incompatible
            DeviceError: If device not found
        """
```

## Usage Examples

### Creating Profiles

```python
# Initialize
profile_manager = ProfileManager()

# Create a high-performance profile
high_performance = profile_manager.create_profile(
    name="high_performance",
    settings={
        "performance_mode": True,
        "cpu_governor": "performance",
        "keep_alive": True,
        "background_apps": "minimal",
        "display_quality": "high"
    },
    compatibility=["iPhone.*", "Pixel.*", "Galaxy S.*"],
    performance_targets={
        "response_time": 0.1,
        "throughput": 1000,
        "error_rate": 0.001
    }
)

# Create a battery-saving profile
battery_saver = profile_manager.create_profile(
    name="battery_saver",
    settings={
        "performance_mode": False,
        "cpu_governor": "powersave",
        "keep_alive": False,
        "background_apps": "none",
        "display_quality": "low"
    },
    compatibility=[".*"],  # Compatible with all devices
    performance_targets={
        "response_time": 0.5,
        "battery_drain": 0.1
    }
)
```

### Applying Profiles

```python
# Apply profile to specific device
try:
    success = profile_manager.apply_profile(
        device_id="device1",
        profile_name="high_performance",
        device_pool=device_pool
    )
    if success:
        logger.info("Profile applied successfully")
except ValueError as e:
    logger.error(f"Profile error: {e}")
except DeviceError as e:
    logger.error(f"Device error: {e}")
```

### Profile Management

```python
class ProfileCoordinator:
    def __init__(self, profile_manager: ProfileManager, device_pool: DevicePool):
        self.profile_manager = profile_manager
        self.device_pool = device_pool
        self.device_profiles = {}
    
    async def optimize_device_profile(self, device_id: str):
        """Choose and apply the best profile based on device state."""
        device = self.device_pool.get_device(device_id)
        battery_level = await device.get_battery_level()
        
        if battery_level < 20:
            profile_name = "battery_saver"
        else:
            profile_name = "high_performance"
        
        return await self.profile_manager.apply_profile(
            device_id, profile_name, self.device_pool
        )
```

## Implementation Details

### Profile Storage

Profiles are stored in memory with the following structure:
```python
self.profiles: Dict[str, DeviceProfile] = {
    "profile_name": DeviceProfile(
        name="profile_name",
        settings={...},
        compatibility=[...],
        performance_targets={...}
    )
}
```

### Compatibility Checking

```python
import re

def check_compatibility(device_model: str, compatibility: List[str]) -> bool:
    """Check if device is compatible with profile."""
    return any(
        re.match(pattern, device_model)
        for pattern in compatibility
    )
```

### Settings Application

```python
def apply_settings(device, settings: Dict) -> bool:
    """Apply settings to device."""
    try:
        for setting, value in settings.items():
            setattr(device, setting, value)
        return True
    except Exception as e:
        logger.error(f"Failed to apply settings: {e}")
        return False
```

## Best Practices

1. Profile Design
   ```python
   # Good - Clear, specific settings
   good_profile = {
       "name": "test_profile",
       "settings": {
           "cpu_governor": "performance",
           "background_apps": "minimal"
       }
   }
   
   # Bad - Ambiguous settings
   bad_profile = {
       "name": "test",
       "settings": {
           "mode": "fast",
           "apps": "some"
       }
   }
   ```

2. Compatibility Management
   ```python
   # Use specific patterns
   compatibility = [
       "iPhone1[0-4].*",  # iPhone 10-14
       "Pixel[6-7].*",    # Pixel 6-7
       "Galaxy S2[0-3].*" # Galaxy S20-23
   ]
   ```

3. Error Handling
   ```python
   try:
       profile_manager.apply_profile(device_id, profile_name, device_pool)
   except ValueError as e:
       logger.error(f"Invalid profile configuration: {e}")
   except DeviceError as e:
       logger.error(f"Device error: {e}")
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
   ```

## Advanced Use Cases

### Dynamic Profile Generation

```python
class DynamicProfileGenerator:
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
    
    def generate_profile(self, device_metrics: Dict) -> DeviceProfile:
        """Generate profile based on device metrics."""
        if device_metrics["cpu_capacity"] > 8:
            return self._create_high_performance_profile()
        else:
            return self._create_balanced_profile()
```

### Profile Templates

```python
class ProfileTemplate:
    @staticmethod
    def create_test_profile(name: str, device_model: str) -> DeviceProfile:
        """Create a profile for testing purposes."""
        return DeviceProfile(
            name=f"test_{name}",
            settings={
                "performance_mode": True,
                "logging_level": "debug"
            },
            compatibility=[device_model],
            performance_targets={
                "response_time": 0.1
            }
        )
```

### Profile Migration

```python
class ProfileMigrator:
    @staticmethod
    def migrate_legacy_profile(old_profile: Dict) -> DeviceProfile:
        """Migrate old profile format to new format."""
        return DeviceProfile(
            name=old_profile["name"],
            settings=convert_legacy_settings(old_profile["config"]),
            compatibility=generate_compatibility(old_profile["devices"]),
            performance_targets=extract_targets(old_profile["metrics"])
        )
```

## Performance Considerations

1. Profile Application
   - Validate settings before applying
   - Implement rollback mechanism
   - Cache frequently used profiles

2. Compatibility Checks
   - Use efficient regex patterns
   - Cache compatibility results
   - Implement pattern optimization

3. Profile Storage
   - Implement profile versioning
   - Consider persistent storage
   - Implement profile cleanup

## Integration Examples

### With Health Monitoring

```python
class HealthAwareProfileManager:
    def __init__(self, profile_manager: ProfileManager, health_monitor: HealthMonitor):
        self.profile_manager = profile_manager
        self.health_monitor = health_monitor
    
    async def adjust_profile(self, device_id: str):
        """Adjust profile based on device health."""
        health = await self.health_monitor.check_device_health(device_id)
        if health.status == "warning":
            await self.profile_manager.apply_profile(
                device_id, "conservative", device_pool
            )
```

### With Performance Monitoring

```python
class PerformanceOptimizer:
    def __init__(self, profile_manager: ProfileManager, profiler: PerformanceProfiler):
        self.profile_manager = profile_manager
        self.profiler = profiler
    
    async def optimize_profile(self, device_id: str):
        """Optimize profile based on performance metrics."""
        metrics = await self.profiler._collect_metrics(device_id)
        if metrics.response_time > 1.0:
            await self.profile_manager.apply_profile(
                device_id, "high_performance", device_pool
            )
``` 