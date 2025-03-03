"""
Example script demonstrating advanced device management features in SoloX.

This script shows how to:
1. Set up batch operations for multiple devices
2. Monitor device health and handle alerts
3. Enable automatic recovery for problematic devices
4. Profile device performance
5. Create and apply custom device profiles
"""

import asyncio
import logging
from typing import List

from solox.device_management.device_pool import DevicePool
from solox.device_management.advanced_features import (
    BatchOperationManager,
    HealthMonitor,
    AutoRecovery,
    PerformanceProfiler,
    ProfileManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def monitor_devices(device_ids: List[str], duration: int = 300):
    """Monitor multiple devices for a specified duration."""
    # Initialize device pool
    device_pool = DevicePool()
    
    # Initialize advanced features
    batch_manager = BatchOperationManager(device_pool)
    health_monitor = HealthMonitor(device_pool)
    auto_recovery = AutoRecovery(device_pool, health_monitor)
    performance_profiler = PerformanceProfiler(device_pool)
    profile_manager = ProfileManager()
    
    # Create device profiles
    high_performance_profile = profile_manager.create_profile(
        name="high_performance",
        settings={
            "performance_mode": True,
            "cpu_governor": "performance",
            "keep_alive": True
        },
        compatibility=["iPhone.*", "Pixel.*"],
        performance_targets={
            "response_time": 0.1,
            "throughput": 1000,
            "error_rate": 0.001
        }
    )
    
    try:
        # Apply profiles to devices
        for device_id in device_ids:
            try:
                profile_manager.apply_profile(device_id, "high_performance", device_pool)
                logger.info(f"Applied high performance profile to device {device_id}")
            except Exception as e:
                logger.error(f"Failed to apply profile to device {device_id}: {e}")
        
        # Start monitoring loop
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration:
            # Execute batch operation
            result = await batch_manager.execute_batch(
                "check_status",
                {"detailed": True},
                device_ids
            )
            logger.info(f"Batch status check results: {result}")
            
            # Check health and attempt recovery if needed
            for device_id in device_ids:
                health = await health_monitor.check_device_health(device_id)
                logger.info(f"Device {device_id} health: {health}")
                
                if health.status != "healthy":
                    logger.warning(f"Unhealthy device detected: {device_id}")
                    recovery_success = await auto_recovery.check_and_recover(device_id)
                    if recovery_success:
                        logger.info(f"Successfully recovered device {device_id}")
                    else:
                        logger.error(f"Failed to recover device {device_id}")
            
            # Collect performance metrics
            for device_id in device_ids:
                try:
                    metrics = await performance_profiler._collect_metrics(device_id)
                    logger.info(f"Device {device_id} metrics: {metrics}")
                except Exception as e:
                    logger.error(f"Failed to collect metrics for device {device_id}: {e}")
            
            # Wait before next iteration
            await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error during monitoring: {e}")
    finally:
        # Clean up
        batch_manager.executor.shutdown()

async def main():
    """Main function demonstrating advanced device management."""
    # Example device IDs (replace with actual device IDs)
    device_ids = ["device1", "device2", "device3"]
    
    logger.info("Starting advanced device management demo")
    logger.info(f"Monitoring devices: {device_ids}")
    
    try:
        # Monitor devices for 5 minutes
        await monitor_devices(device_ids, duration=300)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 