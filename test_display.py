#!/usr/bin/env python3
"""
Test Display Control - Simple test to verify brightness control works
"""

import asyncio
import sys
from pathlib import Path
from glob import glob

class DisplayController:
    """Simple display controller for testing."""
    
    def __init__(self):
        self.brightness_path = self._find_brightness_path()
        self.max_brightness = self._get_max_brightness()
        self.current_brightness = self._get_current_brightness()
        
        print(f"🖥️  Display controller initialized")
        print(f"📁 Brightness path: {self.brightness_path}")
        print(f"🔆 Max brightness: {self.max_brightness}")
        print(f"💡 Current brightness: {self.current_brightness}")
    
    def _find_brightness_path(self):
        """Find brightness control path."""
        patterns = [
            "/sys/class/backlight/*/brightness",
            "/sys/class/backlight/rpi_backlight/brightness",
            "/sys/class/backlight/11-0045/brightness",
            "/sys/class/backlight/10-0045/brightness"
        ]
        
        for pattern in patterns:
            paths = glob(pattern)
            if paths:
                return Path(paths[0])
        
        raise FileNotFoundError("❌ No brightness control found")
    
    def _get_max_brightness(self):
        """Get maximum brightness."""
        max_path = self.brightness_path.parent / "max_brightness"
        try:
            return int(max_path.read_text().strip())
        except:
            return 255
    
    def _get_current_brightness(self):
        """Get current brightness."""
        try:
            return int(self.brightness_path.read_text().strip())
        except:
            return 0
    
    def set_brightness(self, value):
        """Set brightness."""
        value = max(0, min(value, self.max_brightness))
        try:
            self.brightness_path.write_text(str(value))
            self.current_brightness = value
            print(f"✅ Brightness set to: {value}")
            return True
        except Exception as e:
            print(f"❌ Failed to set brightness: {e}")
            return False
    
    async def fade_to(self, target, duration=1.0, steps=20):
        """Fade to target brightness."""
        target = max(0, min(target, self.max_brightness))
        start = self.current_brightness
        
        if start == target:
            print(f"Already at target brightness: {target}")
            return
        
        print(f"🎭 Fading: {start} → {target} over {duration:.1f}s")
        
        step_delay = duration / steps
        step_size = (target - start) / steps
        
        for i in range(steps + 1):
            brightness = int(start + (step_size * i))
            self.set_brightness(brightness)
            
            if i < steps:
                await asyncio.sleep(step_delay)
        
        print(f"✨ Fade complete!")

async def test_display():
    """Test display control."""
    print("🎯 Testing Display Control")
    print("=" * 30)
    
    try:
        display = DisplayController()
        
        print(f"\n🔍 Current state:")
        print(f"   Brightness: {display.current_brightness}/{display.max_brightness}")
        
        # Test sequence
        print(f"\n🧪 Running test sequence...")
        
        # 1. Fade to full brightness (wake up)
        print(f"\n1. 🌅 Waking display (fade to full brightness)")
        await display.fade_to(display.max_brightness, duration=2.0)
        await asyncio.sleep(2)
        
        # 2. Fade to half brightness
        print(f"\n2. 🔆 Setting to half brightness")
        await display.fade_to(display.max_brightness // 2, duration=1.5)
        await asyncio.sleep(2)
        
        # 3. Fade to off (sleep)
        print(f"\n3. 🌙 Sleeping display (fade to off)")
        await display.fade_to(0, duration=3.0)
        await asyncio.sleep(1)
        
        # 4. Quick wake test
        print(f"\n4. ⚡ Quick wake test")
        await display.fade_to(display.max_brightness, duration=1.0)
        await asyncio.sleep(1)
        
        # 5. Return to original brightness
        print(f"\n5. 🔄 Returning to original brightness")
        await display.fade_to(display.current_brightness, duration=1.0)
        
        print(f"\n✅ Display test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        return False

async def main():
    """Main test function."""
    try:
        success = await test_display()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n👋 Test interrupted by user")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)