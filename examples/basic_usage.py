#!/usr/bin/env python3
"""
Basic example of using SoloX for performance monitoring
"""

from solox.public.apm import AppPerformanceMonitor
from solox.public.common import Devices

def main():
    # Initialize device manager
    devices = Devices()
    
    # Example for Android device
    def monitor_android():
        device_id = 'YOUR_DEVICE_ID'  # Replace with actual device ID
        package_name = 'com.example.app'  # Replace with your app package name
        
        # Get process list for the app
        process_list = devices.getPid(deviceId=device_id, pkgName=package_name)
        print(f"Process list: {process_list}")
        
        # Initialize performance monitor
        apm = AppPerformanceMonitor(
            pkgName=package_name,
            platform='Android',
            deviceId=device_id,
            surfaceview=True,
            noLog=False,
            collect_all=True
        )
        
        # Collect and print metrics
        print(f"CPU Usage: {apm.collectCpu()}%")
        print(f"Memory Usage: {apm.collectMemory()} MB")
        print(f"FPS: {apm.collectFps()} Hz")
        print(f"Battery Info: {apm.collectBattery()}")
        
        # Generate HTML report
        apm.collectAll(report_path='performance_report.html')
    
    # Example for iOS device
    def monitor_ios():
        package_name = 'com.example.app'  # Replace with your app bundle ID
        
        # Initialize performance monitor for iOS
        apm = AppPerformanceMonitor(
            pkgName=package_name,
            platform='iOS',
            noLog=False,
            collect_all=True
        )
        
        # Collect and print metrics
        print(f"CPU Usage: {apm.collectCpu()}%")
        print(f"Memory Usage: {apm.collectMemory()} MB")
        print(f"FPS: {apm.collectFps()} Hz")
        
        # Generate HTML report
        apm.collectAll(report_path='ios_performance_report.html')

if __name__ == '__main__':
    main() 