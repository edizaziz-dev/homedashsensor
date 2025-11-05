#!/usr/bin/env python3
"""
Demo script for HomeDashSensor functionality.
Shows proximity detection, display control, and sensor simulation.
"""
import asyncio
import logging
from config import ConfigManager
from sensors import VL53L5CXSensor, ProximityReading
from display import DisplayController
from proximity import ProximityDetector


async def demo_proximity_detection():
    """Demonstrate proximity detection with simulated readings."""
    print("🎯 HomeDashSensor Demo - Proximity Detection")
    print("=" * 50)
    
    # Setup
    config_manager = ConfigManager()
    detection_config = config_manager.get_detection_config()
    display_config = config_manager.get_display_config()
    
    detector = ProximityDetector(detection_config)
    display = DisplayController(display_config)
    
    await display.initialize()
    
    # Simulate a person approaching
    print("\n📡 Simulating person approaching...")
    test_readings = [
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Far away
        ProximityReading(distance_mm=1500, zones_in_range=1),  # Getting closer
        ProximityReading(distance_mm=800, zones_in_range=3),   # Closer
        ProximityReading(distance_mm=400, zones_in_range=6),   # In threshold - 1st detection
        ProximityReading(distance_mm=350, zones_in_range=7),   # In threshold - 2nd detection  
        ProximityReading(distance_mm=300, zones_in_range=8),   # In threshold - 3rd detection (triggers!)
        ProximityReading(distance_mm=280, zones_in_range=8),   # Stable presence
        ProximityReading(distance_mm=290, zones_in_range=8),   # Stable presence
    ]
    
    for i, reading in enumerate(test_readings):
        human_present = detector.process_reading(reading)
        stats = detector.get_detection_stats()
        
        print(f"Reading {i+1}: {reading.distance_mm}mm, {reading.zones_in_range} zones")
        print(f"  → Human present: {human_present}")
        print(f"  → Consecutive detections: {stats['consecutive_detections']}")
        print(f"  → Confidence: {stats['detection_confidence']:.2f}")
        
        # Trigger display wake when human detected
        if human_present and not display.state.is_awake:
            print("  → 🌅 Waking display!")
            await display.wake_display(200)  # Wake to 200 brightness
        
        await asyncio.sleep(0.5)
    
    print("\n📡 Simulating person leaving...")
    leave_readings = [
        ProximityReading(distance_mm=600, zones_in_range=2),   # Moving away
        ProximityReading(distance_mm=800, zones_in_range=1),   # Further away
        ProximityReading(distance_mm=1200, zones_in_range=0),  # Gone - 1st non-detection
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 2nd
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 3rd
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 4th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 5th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 6th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 7th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 8th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 9th
        ProximityReading(distance_mm=2000, zones_in_range=0),  # Gone - 10th (triggers!)
    ]
    
    for i, reading in enumerate(leave_readings):
        human_present = detector.process_reading(reading)
        stats = detector.get_detection_stats()
        
        print(f"Leave {i+1}: {reading.distance_mm}mm, {reading.zones_in_range} zones")
        print(f"  → Human present: {human_present}")
        print(f"  → Consecutive non-detections: {stats['consecutive_non_detections']}")
        
        # Trigger display sleep when human leaves
        if not human_present and display.state.is_awake:
            print("  → 🌙 Sleeping display!")
            await display.sleep_display()
        
        await asyncio.sleep(0.3)
    
    print(f"\n✅ Demo complete! Final brightness: {await display.get_current_brightness()}")
    await display.cleanup()


async def demo_performance():
    """Demonstrate performance characteristics."""
    print("\n⚡ Performance Demo")
    print("=" * 30)
    
    config_manager = ConfigManager()
    vl53l5cx_config = config_manager.get_vl53l5cx_config()
    sensor = VL53L5CXSensor(vl53l5cx_config)
    
    await sensor.initialize()
    
    import time
    start_time = time.time()
    readings = 0
    
    print("Reading sensor at high frequency for 5 seconds...")
    while time.time() - start_time < 5.0:
        reading = await sensor.read_proximity()
        if reading:
            readings += 1
        await asyncio.sleep(0.1)  # 10Hz
    
    elapsed = time.time() - start_time
    frequency = readings / elapsed
    
    print(f"📊 Performance Results:")
    print(f"  • Readings: {readings}")
    print(f"  • Time: {elapsed:.1f}s")
    print(f"  • Frequency: {frequency:.1f} Hz")
    print(f"  • Target: 10 Hz")
    print(f"  • Performance: {'✅ Good' if frequency >= 9.0 else '⚠️ Slow'}")
    
    await sensor.cleanup()


async def main():
    """Run all demos."""
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise for demo
    
    await demo_proximity_detection()
    await demo_performance()
    
    print("\n🎉 All demos complete!")
    print("\nTo run the full system:")
    print("  python3 main.py")


if __name__ == "__main__":
    asyncio.run(main())