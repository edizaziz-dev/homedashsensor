#!/usr/bin/env python3
"""
Test the improved proximity detection with mock sensor data
This simulates the issue you reported (false readings at 200-300mm)
"""
import asyncio
import sys
from loguru import logger
from display_manager import ProximityTracker

async def test_improved_filtering():
    """Test the new filtering logic with problematic sensor data"""
    logger.info("🧪 Testing Improved Proximity Detection")
    logger.info("Simulating the issue: false readings at 200-300mm when you're actually far away")
    
    # Create proximity tracker with new filtering
    proximity = ProximityTracker(proximity_threshold_mm=400)
    
    test_scenarios = [
        {
            'description': "❌ FALSE POSITIVE: Stationary reflection at 250mm (speed=0)",
            'data': {'target1': {'x': 200, 'y': 150, 'speed': 0, 'distance_resolution': 10}},
            'expected': False  # Should be filtered out due to zero speed
        },
        {
            'description': "❌ FALSE POSITIVE: Very slow noise at 300mm (speed=0.5cm/s)",
            'data': {'target1': {'x': 250, 'y': 180, 'speed': 0.5, 'distance_resolution': 10}},
            'expected': False  # Should be filtered out due to low speed
        },
        {
            'description': "❌ FALSE POSITIVE: Unrealistic close reading (30mm)",
            'data': {'target1': {'x': 20, 'y': 20, 'speed': 5, 'distance_resolution': 10}},
            'expected': False  # Should be filtered out as too close (sensor error)
        },
        {
            'description': "✅ VALID: Real human at 300mm with movement (speed=3cm/s)",
            'data': {'target1': {'x': 200, 'y': 224, 'speed': 3, 'distance_resolution': 10}},
            'expected': True  # Should pass (after consecutive detections)
        },
        {
            'description': "❌ INCONSISTENT: Sudden jump from 300mm to 500mm",
            'data': {'target1': {'x': 400, 'y': 300, 'speed': 2, 'distance_resolution': 10}},
            'expected': False  # Should be filtered due to large distance change
        }
    ]
    
    logger.info("Running filtering tests...\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"Test {i}: {scenario['description']}")
        
        # Run the detection multiple times to test consecutive detection requirement
        results = []
        for detection_round in range(5):
            result = proximity.update_proximity(scenario['data'])
            results.append(result)
            logger.debug(f"  Detection round {detection_round + 1}: {result}")
        
        final_result = results[-1]  # Last result after all consecutive checks
        
        if final_result == scenario['expected']:
            logger.info(f"  ✅ PASS: Expected {scenario['expected']}, got {final_result}")
        else:
            logger.info(f"  ❌ FAIL: Expected {scenario['expected']}, got {final_result}")
        
        # Reset state between tests
        proximity.consecutive_detections = 0
        proximity.is_human_present = False
        proximity.last_valid_distance = None
        
        logger.info("")
    
    # Test the scenario you reported specifically
    logger.info("🎯 Testing YOUR specific scenario:")
    logger.info("You moved >40cm away but sensor shows 200-300mm readings")
    
    proximity = ProximityTracker(proximity_threshold_mm=400)  # Fresh instance
    
    # Simulate persistent false readings
    false_readings = [
        {'target1': {'x': 200, 'y': 100, 'speed': 0, 'distance_resolution': 10}},    # 223mm, no movement
        {'target1': {'x': 180, 'y': 180, 'speed': 0.2, 'distance_resolution': 10}}, # 254mm, tiny movement
        {'target1': {'x': 220, 'y': 160, 'speed': 0, 'distance_resolution': 10}},   # 272mm, no movement
        {'target1': {'x': 190, 'y': 200, 'speed': 0.1, 'distance_resolution': 10}}, # 284mm, minimal movement
    ]
    
    logger.info("Sending 4 consecutive false readings (stationary reflections):")
    for i, reading in enumerate(false_readings, 1):
        distance = (reading['target1']['x']**2 + reading['target1']['y']**2) ** 0.5
        speed = reading['target1']['speed']
        result = proximity.update_proximity(reading)
        logger.info(f"  Reading {i}: {distance:.1f}mm, speed={speed}cm/s → Human detected: {result}")
    
    logger.info("")
    if not proximity.is_human_present:
        logger.info("🎉 SUCCESS: False readings were correctly filtered out!")
        logger.info("   The improved filtering prevents stationary reflections from triggering wake")
    else:
        logger.warning("⚠️  ISSUE: False readings still triggered detection")
        logger.info("   You may need to increase min_speed_threshold or min_detection_count")

async def main():
    logger.add(sys.stderr, level="INFO")
    await test_improved_filtering()

if __name__ == "__main__":
    asyncio.run(main())