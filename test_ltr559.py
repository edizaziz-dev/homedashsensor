#!/usr/bin/env python3
"""
LTR-559 Light Sensor Test
Simple test script to verify LTR-559 functionality and I2C communication.
"""

import time
import sys

try:
    import ltr559
    print("✅ LTR-559 library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LTR-559 library: {e}")
    sys.exit(1)

def test_ltr559():
    """Test LTR-559 light sensor functionality."""
    print("🔍 Testing LTR-559 Light Sensor...")
    
    try:
        # Initialize sensor with default settings
        sensor = ltr559.LTR559()  # Uses default I2C bus and address
        print(f"📡 Sensor initialized with default settings")
        
        # Configure sensor
        sensor.set_light_options(
            active=True,
            gain=1,  # 1x gain
            integration_time=100  # 100ms integration time
        )
        print("⚙️  Sensor configured: gain=1x, integration=100ms")
        
        # Give sensor time to stabilize
        print("⏳ Waiting for sensor to stabilize...")
        time.sleep(1.0)
        
        print("\n🌞 Reading light levels (Ctrl+C to stop):")
        print("Time\t\tLux\t\tBrightness Level")
        print("-" * 50)
        
        for i in range(30):  # Read for 30 seconds
            try:
                # Read light level
                lux = sensor.get_lux()
                
                # Determine brightness level
                if lux < 10:
                    level = "Very Dark"
                elif lux < 50:
                    level = "Dark"
                elif lux < 200:
                    level = "Dim"
                elif lux < 500:
                    level = "Normal"
                elif lux < 1000:
                    level = "Bright"
                else:
                    level = "Very Bright"
                
                print(f"{i+1:2d}s\t\t{lux:8.2f}\t{level}")
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ Error reading sensor: {e}")
                continue
        
        print("\n✅ LTR-559 test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ LTR-559 test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
        print("2. Check wiring: SDA, SCL, VCC (3.3V), GND")
        print("3. Verify I2C address: sudo i2cdetect -y 1")
        print("4. Check I2C address in code (currently 0x23)")
        return False

if __name__ == "__main__":
    try:
        success = test_ltr559()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(0)