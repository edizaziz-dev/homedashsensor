#!/usr/bin/env python3
"""
Simple debug version to understand the VL53L5CX data format
"""

import time
import vl53l5cx_ctypes as vl53l5cx

print("🔍 VL53L5CX Debug Test")
print("=" * 30)

try:
    # Initialize the sensor
    sensor = vl53l5cx.VL53L5CX()
    print("✅ Sensor initialized")
    
    # Configure for 8x8 mode
    sensor.set_resolution(8*8)
    sensor.set_ranging_frequency_hz(5)  # Slow for debugging
    
    # Start ranging
    sensor.start_ranging()
    print("📡 Ranging started")
    
    frame_count = 0
    while frame_count < 3:  # Just 3 frames for debugging
        if sensor.data_ready():
            data = sensor.get_data()
            frame_count += 1
            
            print(f"\n📊 Frame #{frame_count}")
            print(f"🔍 Data type: {type(data.distance_mm)}")
            print(f"📏 Data length: {len(data.distance_mm) if hasattr(data.distance_mm, '__len__') else 'N/A'}")
            
            # Try different ways to access the data
            try:
                # Method 1: Access the first array in the nested structure
                distance_array = data.distance_mm[0]  # Get the first (and only) array
                distances = list(distance_array)
                print(f"✅ Nested array access successful, length: {len(distances)}")
                print(f"🎯 First 8 values: {distances[:8]}")
                
                # Test some values
                valid_count = sum(1 for d in distances if d > 0 and d < 4000)
                print(f"🎯 Valid readings: {valid_count}/64")
                
            except Exception as e:
                print(f"❌ Nested array access failed: {e}")
                
            # Try accessing individual elements from the nested array
            try:
                distance_array = data.distance_mm[0]
                print(f"🔍 Element [0]: {distance_array[0]}")
                print(f"🔍 Element [1]: {distance_array[1]}")
                print(f"🔍 Element [63]: {distance_array[63]}")
            except Exception as e:
                print(f"❌ Individual element access failed: {e}")
                
        time.sleep(0.5)
    
    sensor.stop_ranging()
    print("\n✅ Debug test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()