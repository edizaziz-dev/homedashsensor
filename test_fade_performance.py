#!/usr/bin/env python3
"""
Test script to check fade performance over multiple cycles.
This helps identify memory leaks or performance degradation.
"""

import asyncio
import time
import gc
from proximity_display_control import DisplayController, ProximityConfig

config = ProximityConfig()

async def test_fade_performance():
    """Test fade performance over multiple cycles."""
    print("🎭 Starting fade performance test...")
    
    display = DisplayController()
    
    print(f"📊 Testing fade system with {config.fade_steps} steps, {config.fade_easing} easing")
    
    cycle_count = 15  # Test 15 fade cycles
    times = []
    
    for cycle in range(cycle_count):
        cycle_start = time.time()
        
        # Fade up
        fade_start = time.time()
        await display.fade_to(200, 1.5)  # 1.5 second fade to bright
        fade_up_time = time.time() - fade_start
        
        await asyncio.sleep(0.3)  # Brief pause
        
        # Fade down
        fade_start = time.time()
        await display.fade_to(0, 1.5)  # 1.5 second fade to dark
        fade_down_time = time.time() - fade_start
        
        cycle_time = time.time() - cycle_start
        times.append(cycle_time)
        
        print(f"🔄 Cycle {cycle+1:2d}: "
              f"Up={fade_up_time:.2f}s, Down={fade_down_time:.2f}s, "
              f"Total={cycle_time:.2f}s")
        
        # Force garbage collection to check for cleanup
        if cycle % 5 == 0:
            gc.collect()
            print(f"🧹 Garbage collection run")
        
        await asyncio.sleep(0.2)  # Brief pause between cycles
    
    # Performance analysis
    avg_time = sum(times) / len(times)
    first_5_avg = sum(times[:5]) / 5
    last_5_avg = sum(times[-5:]) / 5
    performance_change = ((last_5_avg - first_5_avg) / first_5_avg) * 100
    
    print(f"\n📈 Performance Summary:")
    print(f"   Average cycle time:  {avg_time:.2f}s")
    print(f"   First 5 cycles avg:  {first_5_avg:.2f}s")
    print(f"   Last 5 cycles avg:   {last_5_avg:.2f}s")
    print(f"   Performance change:  {performance_change:+.1f}%")
    
    if abs(performance_change) < 5:
        print(f"✅ Performance is stable!")
    elif performance_change > 10:
        print(f"❌ Performance degradation detected!")
    else:
        print(f"⚠️  Minor performance variation")

if __name__ == "__main__":
    asyncio.run(test_fade_performance())