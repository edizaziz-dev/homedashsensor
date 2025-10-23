#!/usr/bin/env python3
"""
Demo script to simulate proximity detection and screen control
This works without the actual LD2450 sensor hardware
"""
import asyncio
import sys
import time
from loguru import logger
from display_manager import DisplayManager, ProximityTracker

running = True

def _stop(*_):
    global running
    logger.info("Shutting down demo...")
    running = False

async def demo_proximity_control():
    """
    Demo the proximity-based screen control with simulated sensor data
    """
    logger.info("🎭 Starting Proximity Control Demo")
    logger.info("This demo simulates human proximity without needing the actual sensor")
    
    # Initialize display manager and proximity tracker
    display = DisplayManager()
    proximity = ProximityTracker(proximity_threshold_mm=400)  # 40cm threshold
    
    logger.info("Display initialized. Starting simulation...")
    
    # Simulation sequence
    simulation_steps = [
        (5, "far", "Human far away (60cm)"),
        (5, "close", "Human approaches (30cm)"),
        (3, "close", "Human stays close"),
        (5, "far", "Human moves away (60cm)"),
        (2, "none", "No detection"),
        (3, "close", "Human returns (25cm)"),
        (4, "far", "Human backs away again"),
        (2, "none", "Human leaves completely")
    ]
    
    step_duration = 1.0  # seconds per step
    previous_human_state = None
    
    try:
        for duration, proximity_state, description in simulation_steps:
            if not running:
                break
                
            logger.info(f"📍 Simulation: {description}")
            
            for step in range(int(duration / step_duration)):
                if not running:
                    break
                
                # Generate mock sensor data based on simulation state
                if proximity_state == "close":
                    # Simulate human at 30cm (300mm)
                    mock_data = {
                        'target1': {'x': 200, 'y': 200, 'speed': 2, 'distance_resolution': 10},
                        'target2': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0},
                        'target3': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0}
                    }
                elif proximity_state == "far":
                    # Simulate human at 60cm (600mm)
                    mock_data = {
                        'target1': {'x': 400, 'y': 400, 'speed': 1, 'distance_resolution': 10},
                        'target2': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0},
                        'target3': {'x': 0, 'y': 0, 'speed': 0, 'distance_resolution': 0}
                    }
                else:  # "none"
                    # No detection
                    mock_data = None
                
                # Update proximity detection
                human_present = proximity.update_proximity(mock_data)
                
                # Handle screen wake/sleep based on proximity
                if human_present != previous_human_state:
                    if human_present:
                        logger.info("🙋 Human detected within 40cm - Waking screen")
                        await display.wake_screen()
                    else:
                        logger.info("🚶 Human moved away - Sleeping screen")
                        await display.sleep_screen()
                    
                    previous_human_state = human_present
                
                await asyncio.sleep(step_duration)
    
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        # Clean up
        logger.info("Cleaning up demo...")
        display.cleanup()
        logger.info("✅ Demo completed!")

async def main():
    import signal
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, _stop)
    
    logger.add(sys.stderr, level="INFO")
    await demo_proximity_control()

if __name__ == "__main__":
    asyncio.run(main())