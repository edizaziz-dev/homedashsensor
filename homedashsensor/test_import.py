#!/usr/bin/env python3
"""
Simple test script to verify LD2450 import and basic functionality
"""

try:
    from ld2450_protocol import LD2450
    print("✅ Successfully imported LD2450 class")
    
    # Test creating an instance
    sensor = LD2450()
    print("✅ Successfully created LD2450 instance")
    
    # Show the available methods
    print("\n📋 Available methods:")
    methods = [method for method in dir(sensor) if not method.startswith('_')]
    for method in methods:
        print(f"  - {method}")
    
    print("\n🔧 To use with your actual sensor:")
    print("  1. Connect your LD2450 sensor to a USB-to-TTL adapter")
    print("  2. Connect the adapter to your Raspberry Pi")
    print("  3. Find the correct port with: dmesg | grep tty")
    print("  4. Update the port in main.py (usually /dev/ttyUSB0)")
    print("  5. Run: python main.py")
    
except ImportError as e:
    print(f"❌ Failed to import LD2450: {e}")
except Exception as e:
    print(f"❌ Error: {e}")