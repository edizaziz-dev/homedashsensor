from loguru import logger
import asyncio
import signal
import sys
from ld2450_protocol import LD2450
from display_manager import DisplayManager, ProximityTracker

running = True

def _stop(*_):
    global running
    logger.info("Shutting down…")
    running = False

async def work():
    # Initialize the LD2450 sensor
    # Note: You may need to change '/dev/ttyUSB0' to the correct port for your system
    # Use 'dmesg | grep tty' to find the correct port after connecting the sensor
    sensor = LD2450(port='/dev/ttyUSB0', baudrate=256000, timeout=1.0)
    
    # Initialize display manager and proximity tracker
    display = DisplayManager()
    
    # Proximity detection configuration - optimized for above-screen mounting
    proximity_config = {
        'proximity_threshold_mm': 500,    # 50cm - accounts for angled detection from above
        'min_detection_count': 2,         # Can be more responsive with clear line-of-sight
        'min_speed_threshold': 0.5,       # Lower threshold since no interference
        'max_distance_change': 300,       # Allow for natural movement patterns
        'detection_timeout': 3.0          # Standard timeout
    }
    
    proximity = ProximityTracker(
        proximity_threshold_mm=proximity_config['proximity_threshold_mm']
    )
    
    # Apply advanced filtering configuration
    proximity.min_detection_count = proximity_config['min_detection_count']
    proximity.min_speed_threshold = proximity_config['min_speed_threshold'] 
    proximity.max_distance_change = proximity_config['max_distance_change']
    proximity.detection_timeout = proximity_config['detection_timeout']
    
    # Try to connect to the sensor
    if not sensor.connect():
        logger.error("Failed to connect to LD2450 sensor")
        return
    
    logger.info("Successfully connected to LD2450 sensor")
    logger.info("Starting proximity-based display control with improved filtering...")
    logger.info(f"Configuration (Above-Screen Mounting):")
    logger.info(f"  🎯 Detection threshold: {proximity_config['proximity_threshold_mm']}mm (50cm)")
    logger.info(f"  🔢 Min consecutive detections: {proximity_config['min_detection_count']}")
    logger.info(f"  💨 Min speed threshold: {proximity_config['min_speed_threshold']}cm/s")
    logger.info(f"  📏 Max distance change: {proximity_config['max_distance_change']}mm")
    logger.info(f"  ⏱️  Detection timeout: {proximity_config['detection_timeout']}s")
    logger.info("")
    logger.info("🔧 If you experience false detections, run: python homedashsensor/calibrate_sensor.py")
    
    i = 0
    previous_human_state = None
    
    try:
        while running:
            # Read target data from the sensor
            target_data = sensor.read_targets()
            
            # Update proximity detection
            human_present = proximity.update_proximity(target_data)
            
            # Handle screen wake/sleep based on proximity
            if human_present != previous_human_state:
                if human_present:
                    logger.info("🙋 Human detected within 40cm - Waking screen")
                    await display.wake_screen()
                else:
                    logger.info("🚶 Human moved away - Sleeping screen")
                    await display.sleep_screen()
                
                previous_human_state = human_present
            
            # Log sensor data more frequently for debugging detection issues
            if target_data:
                has_valid_targets = False
                for target_name, target_info in target_data.items():
                    # Only log targets that have valid data (not all zeros)
                    if target_info['x'] != 0 or target_info['y'] != 0:
                        has_valid_targets = True
                        distance = (target_info['x']**2 + target_info['y']**2) ** 0.5
                        within_threshold = distance <= 400
                        logger.info(f"🎯 {target_name}: "
                                  f"distance={distance:.1f}mm "
                                  f"{'✅ CLOSE' if within_threshold else '❌ FAR'} "
                                  f"(x={target_info['x']}, y={target_info['y']}, "
                                  f"speed={target_info['speed']}cm/s)")
                
                if has_valid_targets:
                    logger.info(f"👤 Human state: {'PRESENT' if human_present else 'ABSENT'} "
                              f"(threshold: 400mm)")
                    logger.info("─" * 60)
            else:
                logger.debug(f"Tick {i} - No sensor data received")
            
            await asyncio.sleep(0.1)  # Read at 10Hz
            i += 1
            
    except Exception as e:
        logger.error(f"Error during sensor operation: {e}")
    finally:
        # Clean up
        logger.info("Cleaning up...")
        sensor.disconnect()
        display.cleanup()
        logger.info("Sensor disconnected and display manager cleaned up")

def main():
    logger.add(sys.stderr, level="INFO")
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, _stop)
    asyncio.run(work())

if __name__ == "__main__":
    main()
