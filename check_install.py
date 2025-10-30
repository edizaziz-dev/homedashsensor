#!/usr/bin/env python3
"""
Quick test to verify VL53L5CX library is installed correctly.
"""

try:
    import vl53l5cx_ctypes as vl53l5cx
    print(f"✅ VL53L5CX library installed successfully!")
    print(f"📦 Version: {vl53l5cx.__version__}")
    print(f"🏠 Default I2C address: 0x{vl53l5cx.DEFAULT_I2C_ADDRESS:02x}")
    print(f"🎯 Available resolutions: 4x4 ({vl53l5cx.RESOLUTION_4X4}), 8x8 ({vl53l5cx.RESOLUTION_8X8})")
    print("\n🔧 Next steps:")
    print("1. Enable I2C: sudo raspi-config")
    print("2. Connect your VL53L5CX sensor")
    print("3. Run: python test_vl53l5cx.py")
except ImportError as e:
    print(f"❌ VL53L5CX library not found: {e}")
    print("📦 Install with: pip install vl53l5cx-ctypes")
except Exception as e:
    print(f"❌ Unexpected error: {e}")