#!/usr/bin/env python3
"""
Device Configuration Status Check
Displays all configured devices and their current settings from proximity_config.ini
"""

import sys
import configparser
from pathlib import Path

def print_section(config, section_name, title):
    """Print a configuration section nicely formatted."""
    print(f"\n📋 {title}")
    print("=" * 50)
    
    if section_name not in config:
        print(f"❌ Section [{section_name}] not found in config")
        return
    
    section = config[section_name]
    for key, value in section.items():
        # Format key nicely
        display_key = key.replace('_', ' ').title()
        
        # Add units/context where appropriate
        if 'mm' in key:
            print(f"  📏 {display_key}: {value}mm ({float(value)/10:.1f}cm)")
        elif 'duration' in key:
            print(f"  ⏱️  {display_key}: {value}s")
        elif 'frequency' in key or 'hz' in key:
            print(f"  📡 {display_key}: {value} Hz")
        elif 'address' in key:
            addr_val = value if value.startswith('0x') else f"0x{int(value):02X}"
            print(f"  📍 {display_key}: {addr_val}")
        elif 'enabled' in key:
            status = "✅ Enabled" if value.lower() == 'true' else "❌ Disabled"
            print(f"  🔧 {display_key}: {status}")
        elif 'threshold' in key:
            print(f"  🎯 {display_key}: {value}")
        elif 'brightness' in key and 'path' not in key:
            print(f"  💡 {display_key}: {value}")
        elif 'pin' in key:
            print(f"  📌 {display_key}: GPIO {value}")
        else:
            print(f"  ⚙️  {display_key}: {value}")

def main():
    """Main configuration display function."""
    print("🏠 HomeDashSensor Device Configuration")
    print("🔧 Loading configuration from proximity_config.ini")
    
    config_file = Path("proximity_config.ini")
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Display all device sections
    print_section(config, 'VL53L5CX', 'VL53L5CX 8x8 ToF Sensor')
    print_section(config, 'LightSensor', 'LTR-559 Light Sensor')
    print_section(config, 'BME690', 'BME690 Environmental Sensor')
    print_section(config, 'Display', 'Display Controller')
    print_section(config, 'Detection', 'Proximity Detection')
    print_section(config, 'System', 'System Configuration')
    
    print(f"\n✅ Configuration loaded successfully!")
    print(f"📁 File location: {config_file.absolute()}")
    
    # Show I2C device summary
    print("\n🔌 I2C Device Summary")
    print("=" * 30)
    
    if 'VL53L5CX' in config:
        vl_addr = config.get('VL53L5CX', 'i2c_address', fallback='0x29')
        vl_enabled = config.getboolean('VL53L5CX', 'enabled', fallback=True)
        status = "✅" if vl_enabled else "❌"
        print(f"  {status} VL53L5CX ToF:    {vl_addr}")
    
    if 'LightSensor' in config:
        lt_addr = config.get('LightSensor', 'i2c_address', fallback='0x23')
        lt_enabled = config.getboolean('LightSensor', 'enabled', fallback=True)
        status = "✅" if lt_enabled else "❌"
        print(f"  {status} LTR-559 Light:  {lt_addr}")
    
    if 'BME690' in config:
        bme_addr = config.get('BME690', 'i2c_address', fallback='0x76')
        bme_enabled = config.getboolean('BME690', 'enabled', fallback=True)
        status = "✅" if bme_enabled else "❌"
        print(f"  {status} BME690 Environment: {bme_addr}")
    
    print(f"\n💡 Use 'sudo i2cdetect -y 1' to verify connected devices")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)