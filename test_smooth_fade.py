#!/usr/bin/env python3
"""
Display Fade Test - Smooth Easing Demo
Demonstrates different fade easing methods for brightness control.
"""

import asyncio
import time
import sys
from pathlib import Path

class SmoothDisplayController:
    """Test controller for demonstrating smooth fade effects."""
    
    def __init__(self):
        """Initialize test display controller."""
        self.brightness_path = self._find_brightness_path()
        self.max_brightness = self._get_max_brightness()
        self.current_brightness = self._get_current_brightness()
        
        print(f"🖥️  Test Display Controller")
        print(f"📁 Brightness path: {self.brightness_path}")
        print(f"🔆 Max brightness: {self.max_brightness}")
        print(f"💡 Current brightness: {self.current_brightness}")
    
    def _find_brightness_path(self) -> Path:
        """Find the brightness control path."""
        from glob import glob
        paths = glob("/sys/class/backlight/*/brightness")
        if not paths:
            raise FileNotFoundError("No brightness control found")
        return Path(paths[0])
    
    def _get_max_brightness(self) -> int:
        """Get maximum brightness."""
        max_path = self.brightness_path.parent / "max_brightness"
        try:
            return int(max_path.read_text().strip())
        except:
            return 255
    
    def _get_current_brightness(self) -> int:
        """Get current brightness."""
        try:
            return int(self.brightness_path.read_text().strip())
        except:
            return 0
    
    def set_brightness(self, value: int) -> bool:
        """Set display brightness."""
        value = max(0, min(value, self.max_brightness))
        try:
            self.brightness_path.write_text(str(value))
            self.current_brightness = value
            return True
        except Exception as e:
            print(f"❌ Failed to set brightness: {e}")
            return False
    
    async def fade_linear(self, target: int, duration: float = 2.0, steps: int = 100):
        """Linear fade (constant speed)."""
        start = self.current_brightness
        print(f"📈 Linear fade: {start} → {target} over {duration}s")
        
        step_delay = duration / steps
        for i in range(steps + 1):
            t = i / steps
            brightness = int(start + (target - start) * t)
            self.set_brightness(brightness)
            if i < steps:
                await asyncio.sleep(step_delay)
        print(f"✅ Linear fade complete")
    
    async def fade_ease_in_out(self, target: int, duration: float = 2.0, steps: int = 100):
        """Smooth ease-in-out fade (slow-fast-slow)."""
        start = self.current_brightness
        print(f"🌊 Ease-in-out fade: {start} → {target} over {duration}s")
        
        step_delay = duration / steps
        for i in range(steps + 1):
            t = i / steps
            # Cubic ease-in-out
            if t < 0.5:
                eased_t = 4 * t * t * t
            else:
                eased_t = 1 - pow(-2 * t + 2, 3) / 2
            
            brightness = int(start + (target - start) * eased_t)
            self.set_brightness(brightness)
            if i < steps:
                await asyncio.sleep(step_delay)
        print(f"✅ Ease-in-out fade complete")
    
    async def fade_exponential(self, target: int, duration: float = 2.0, steps: int = 100):
        """Exponential fade (natural feeling)."""
        start = self.current_brightness
        print(f"📊 Exponential fade: {start} → {target} over {duration}s")
        
        step_delay = duration / steps
        for i in range(steps + 1):
            t = i / steps
            # Exponential easing
            if target > start:
                # Fade in - slow start, fast end
                eased_t = t * t
            else:
                # Fade out - fast start, slow end
                eased_t = 1 - (1 - t) * (1 - t)
            
            brightness = int(start + (target - start) * eased_t)
            self.set_brightness(brightness)
            if i < steps:
                await asyncio.sleep(step_delay)
        print(f"✅ Exponential fade complete")

async def demo_fade_styles():
    """Demonstrate different fade styles."""
    controller = SmoothDisplayController()
    
    print(f"\n🎬 Fade Style Demonstration")
    print(f"=" * 50)
    
    try:
        # Start from off
        controller.set_brightness(0)
        await asyncio.sleep(1)
        
        print(f"\n1️⃣  Testing Linear Fade (constant speed)")
        await controller.fade_linear(controller.max_brightness, 2.0, 80)
        await asyncio.sleep(1)
        
        await controller.fade_linear(0, 2.0, 80)
        await asyncio.sleep(2)
        
        print(f"\n2️⃣  Testing Ease-In-Out Fade (smooth acceleration/deceleration)")
        await controller.fade_ease_in_out(controller.max_brightness, 2.0, 100)
        await asyncio.sleep(1)
        
        await controller.fade_ease_in_out(0, 2.0, 100)
        await asyncio.sleep(2)
        
        print(f"\n3️⃣  Testing Exponential Fade (natural feeling)")
        await controller.fade_exponential(controller.max_brightness, 2.0, 100)
        await asyncio.sleep(1)
        
        await controller.fade_exponential(0, 2.0, 100)
        await asyncio.sleep(1)
        
        print(f"\n✨ Demo complete! The ease-in-out method provides the smoothest experience.")
        print(f"💡 This is now implemented in the main proximity system.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted")
        controller.set_brightness(0)

if __name__ == "__main__":
    try:
        asyncio.run(demo_fade_styles())
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye!")
        sys.exit(0)