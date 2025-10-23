#!/usr/bin/env python3
"""
Test script for Display Manager functionality
"""
import asyncio
import sys
from loguru import logger
from display_manager import DisplayManager, ProximityTracker

async def test_display_manager():
    """Test the display manager brightness control"""
    logger.info("🧪 Testing Display Manager...")
    
    # Initialize display manager
    display = DisplayManager()
    
    # Test current brightness
    current = display.get_current_brightness()
    logger.info(f"Current brightness: {current}/{display.max_brightness}")
    
    # Test brightness setting
    logger.info("Testing immediate brightness control...")
    await asyncio.sleep(1)
    
    display.set_brightness(100)
    await asyncio.sleep(1)
    
    display.set_brightness(200)
    await asyncio.sleep(1)
    
    # Test fade functionality
    logger.info("Testing fade to dim...")
    await display.fade_to_brightness(50, duration=2.0)
    
    await asyncio.sleep(1)
    
    logger.info("Testing fade to bright...")
    await display.fade_to_brightness(255, duration=2.0)
    
    await asyncio.sleep(1)
    
    # Test wake/sleep
    logger.info("Testing screen sleep...")
    await display.sleep_screen()
    
    await asyncio.sleep(2)
    
    logger.info("Testing screen wake...")
    await display.wake_screen()
    
    display.cleanup()
    logger.info("✅ Display Manager test completed!")

async def test_proximity_tracker():
    """Test the proximity tracker with mock data"""
    logger.info("🧪 Testing Proximity Tracker...")
    
    proximity = ProximityTracker(proximity_threshold_mm=400)
    
    # Test with mock sensor data
    mock_data_far = {
        'target1': {'x': 800, 'y': 600, 'speed': 0, 'distance_resolution': 10},  # ~1000mm away
        'target2': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0},
        'target3': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0}
    }
    
    mock_data_close = {
        'target1': {'x': 200, 'y': 300, 'speed': 5, 'distance_resolution': 10},  # ~360mm away
        'target2': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0},
        'target3': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0}
    }
    
    # Test far detection
    human_present = proximity.update_proximity(mock_data_far)
    logger.info(f"Human far away (1000mm): {human_present}")
    
    # Test close detection
    human_present = proximity.update_proximity(mock_data_close)
    logger.info(f"Human close (360mm): {human_present}")
    
    # Test no data
    human_present = proximity.update_proximity(None)
    logger.info(f"No sensor data: {human_present}")
    
    logger.info("✅ Proximity Tracker test completed!")

async def main():
    logger.add(sys.stderr, level="INFO")
    
    try:
        await test_display_manager()
        await asyncio.sleep(1)
        await test_proximity_tracker()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())