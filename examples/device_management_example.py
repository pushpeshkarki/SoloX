#!/usr/bin/env python3
"""
Example demonstrating the enhanced device management features in SoloX
"""

import time
from solox.device_management.device_manager import DeviceManager
from solox.device_management.device_pool import DeviceType

def main():
    # Initialize the device manager
    manager = DeviceManager()
    
    try:
        # Start device monitoring
        print("Starting device monitoring...")
        manager.start()
        
        # Scan for connected devices
        print("\nScanning for devices...")
        devices = manager.scan_devices()
        
        if not devices:
            print("No devices found. Please connect a device and try again.")
            return
        
        print("\nFound devices:")
        for device in devices:
            print(f"\nDevice ID: {device.id}")
            print(f"Type: {device.type.value}")
            print(f"Name: {device.name}")
            print(f"Version: {device.version}")
            print(f"Status: {device.status}")
            
            # Check device compatibility
            is_supported, features = manager.get_device_compatibility(device.id)
            print(f"\nDevice supported: {is_supported}")
            
            if is_supported:
                print("\nSupported features:")
                for feature, supported in features.items():
                    print(f"- {feature}: {'Yes' if supported else 'No'}")
        
        # Monitor devices for a while
        print("\nMonitoring devices for 30 seconds...")
        start_time = time.time()
        while time.time() - start_time < 30:
            connected_devices = manager.device_pool.get_connected_devices()
            print(f"\rConnected devices: {len(connected_devices)}", end="")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping device monitoring...")
    finally:
        manager.stop()
        print("Device monitoring stopped.")

if __name__ == "__main__":
    main() 