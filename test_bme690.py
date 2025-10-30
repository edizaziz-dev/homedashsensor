#!/usr/bin/env python3
"""
BME690 Environmental Sensor Test
Test script to verify BME690 functionality and readings.
"""

import time
import sys

try:
    import bme680
    print("✅ BME680/690 library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import BME680/690 library: {e}")
    sys.exit(1)

def test_bme690():
    """Test BME690 environmental sensor functionality."""
    print("🌡️  Testing BME690 Environmental Sensor...")
    
    try:
        # Initialize sensor at I2C address 0x76
        sensor = bme680.BME680(i2c_addr=0x76)
        print(f"📡 Sensor initialized at I2C address 0x76")
        
        # Configure sensor settings
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        
        # Enable gas measurements
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        sensor.set_gas_heater_temperature(320)  # 320°C
        sensor.set_gas_heater_duration(150)     # 150ms
        
        print("⚙️  Sensor configured:")
        print("   - Temperature: 8x oversampling")
        print("   - Pressure: 4x oversampling") 
        print("   - Humidity: 2x oversampling")
        print("   - IIR Filter: Size 3")
        print("   - Gas heater: 320°C for 150ms")
        
        # Give sensor time to stabilize
        print("⏳ Waiting for sensor to stabilize...")
        time.sleep(2.0)
        
        print("\n🌡️  Reading environmental data (Ctrl+C to stop):")
        print("Time\t\tTemp\t\tPressure\tHumidity\tGas Resistance\t\tAir Quality")
        print("-" * 95)
        
        for i in range(30):  # Read for 30 seconds
            try:
                # Get sensor readings
                if sensor.get_sensor_data():
                    temp = sensor.data.temperature
                    pressure = sensor.data.pressure
                    humidity = sensor.data.humidity
                    
                    gas_resistance = sensor.data.gas_resistance if sensor.data.heat_stable else 0
                    heat_stable = "🔥" if sensor.data.heat_stable else "❄️"
                    
                    # Calculate simple air quality score
                    if gas_resistance > 0:
                        if gas_resistance > 200000:
                            air_quality = "Excellent 🌟"
                        elif gas_resistance > 100000:
                            air_quality = "Good 😊"
                        elif gas_resistance > 50000:
                            air_quality = "Moderate 😐"
                        elif gas_resistance > 10000:
                            air_quality = "Poor 😞"
                        else:
                            air_quality = "Very Poor ⚠️"
                    else:
                        air_quality = "Stabilizing... ⏳"
                    
                    print(f"{i+1:2d}s\t\t{temp:6.1f}°C\t\t{pressure:8.1f}hPa\t{humidity:6.1f}%\t\t{gas_resistance:8.0f}Ω {heat_stable}\t{air_quality}")
                else:
                    print(f"{i+1:2d}s\t\tNo data available")
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ Error reading sensor: {e}")
                continue
        
        print("\n✅ BME690 test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ BME690 test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
        print("2. Check wiring: SDA, SCL, VCC (3.3V), GND")
        print("3. Verify I2C address: sudo i2cdetect -y 1")
        print("4. Check I2C address in code (currently 0x76)")
        return False

if __name__ == "__main__":
    try:
        success = test_bme690()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(0)