#!/usr/bin/env python3
"""
VL53L5CX ToF Sensor Test Program
Simple test to verify the VL53L5CX 8x8 ToF array sensor is working.

Hardware connections:
- VCC to 3.3V or 5V
- GND to GND  
- SDA to GPIO 2 (pin 3)
- SCL to GPIO 3 (pin 5)

I2C address: 0x29
"""

import time
import sys
import vl53l5cx_ctypes as vl53l5cx
from vl53l5cx_ctypes import STATUS_RANGE_VALID, STATUS_RANGE_VALID_LARGE_PULSE

def print_8x8_grid(distances):
    """Print the 8x8 distance array in a readable format."""
    print("\n8x8 Distance Grid (mm):")
    print("+" + "-" * 50 + "+")
    
    for row in range(8):
        line = "|"
        for col in range(8):
            # VL53L5CX returns data in a 64-element array
            # Convert row,col to linear index
            idx = row * 8 + col
            try:
                # Access the distance value directly
                dist = distances[idx] if idx < len(distances) else 0
                line += f"{dist:5d} "
            except (IndexError, TypeError):
                line += "  --- "
        line += "|"
        print(line)
    
    print("+" + "-" * 50 + "+")

def main():
    print("🎯 VL53L5CX 8x8 ToF Sensor Test")
    print("=" * 40)
    
    try:
        # Initialize the sensor
        print("🔄 Initializing VL53L5CX sensor...")
        sensor = vl53l5cx.VL53L5CX()
        
        # Check if sensor is connected
        if sensor.is_alive():
            print("✅ Sensor detected and responsive!")
        else:
            print("❌ Sensor not detected. Check connections!")
            return False
            
        # Initialize and start ranging
        print("🚀 Starting sensor initialization...")
        # Sensor is already initialized in constructor
        
        # Configure for 8x8 mode (default)
        sensor.set_resolution(8*8)
        
        # Set ranging frequency (1-60 Hz for 4x4, 1-15Hz for 8x8)
        sensor.set_ranging_frequency_hz(10)  # Start with 10Hz
        
        # Start ranging
        sensor.start_ranging()
        print("📡 Ranging started!")
        
        print("\nPress Ctrl+C to stop...\n")
        
        frame_count = 0
        while True:
            # Check if new data is ready
            if sensor.data_ready():
                # Get the ranging data
                ranging_data = sensor.get_data()
                
                frame_count += 1
                print(f"\n📊 Frame #{frame_count}")
                
                # Extract distance data and convert to Python list
                # The distance_mm is a nested array structure [targets][zones]
                distances = list(ranging_data.distance_mm[0])  # Get the first target's data
                
                # Print the 8x8 grid
                print_8x8_grid(distances)
                
                # Show some statistics
                valid_distances = [d for d in distances if d > 0 and d < 4000]
                if valid_distances:
                    min_dist = min(valid_distances)
                    max_dist = max(valid_distances)
                    avg_dist = sum(valid_distances) / len(valid_distances)
                    
                    print(f"\n📈 Stats: Min={min_dist}mm, Max={max_dist}mm, Avg={avg_dist:.1f}mm")
                    print(f"🎯 Valid readings: {len(valid_distances)}/64")
                else:
                    print("\n⚠️  No valid distance readings")
                
                print("-" * 60)
            
            time.sleep(0.1)  # Small delay to prevent overwhelming output
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except ImportError:
        print("❌ VL53L5CX library not installed!")
        print("📦 Install with: pip install vl53l5cx-ctypes")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        try:
            sensor.stop_ranging()
            print("🛑 Sensor stopped")
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)