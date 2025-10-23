#!/usr/bin/env python3
"""
LD2450 Sensor Calibration and Debug Tool
This helps identify what the sensor is detecting and tune the filtering parameters
"""
import asyncio
import sys
import time
import signal
from loguru import logger
from ld2450_protocol import LD2450

running = True

def _stop(*_):
    global running
    logger.info("Stopping calibration...")
    running = False

async def calibrate_sensor():
    """
    Run calibration mode to understand sensor behavior
    """
    logger.info("🔧 LD2450 Sensor Calibration Mode")
    logger.info("This will show you exactly what the sensor is detecting")
    logger.info("Use this to understand false readings and tune your thresholds")
    
    # Initialize sensor
    sensor = LD2450(port='/dev/ttyUSB0', baudrate=256000, timeout=1.0)
    
    if not sensor.connect():
        logger.error("❌ Failed to connect to LD2450 sensor")
        logger.info("Make sure:")
        logger.info("  1. Sensor is connected to USB-TTL adapter")
        logger.info("  2. Adapter is connected to Raspberry Pi")  
        logger.info("  3. Check port with: dmesg | grep tty")
        return
    
    logger.info("✅ Connected to LD2450 sensor")
    logger.info("📏 Position yourself at different distances and observe readings:")
    logger.info("  - Stand 20cm away, then 40cm, then 60cm, then 100cm")
    logger.info("  - Try moving slowly vs quickly")
    logger.info("  - Try standing still vs moving")
    logger.info("  - Note any persistent false readings")
    logger.info("")
    logger.info("🎯 Ideal readings should show:")
    logger.info("  - Distance matches your actual position")
    logger.info("  - Speed > 0 when moving, low when still")
    logger.info("  - No targets when nobody is present")
    logger.info("")
    logger.info("Press Ctrl+C to stop calibration")
    logger.info("=" * 80)
    
    try:
        tick = 0
        while running:
            target_data = sensor.read_targets()
            
            if target_data:
                timestamp = time.strftime("%H:%M:%S")
                logger.info(f"[{timestamp}] Tick {tick}")
                
                has_targets = False
                for target_name, target_info in target_data.items():
                    x, y, speed = target_info['x'], target_info['y'], target_info['speed']
                    
                    if x != 0 or y != 0:  # Valid target
                        has_targets = True
                        distance = (x*x + y*y) ** 0.5
                        
                        # Categorize the detection
                        if distance <= 400:
                            distance_cat = "🟢 CLOSE"
                        elif distance <= 600:
                            distance_cat = "🟡 MEDIUM"
                        else:
                            distance_cat = "🔴 FAR"
                        
                        speed_abs = abs(speed)
                        if speed_abs < 1:
                            speed_cat = "🔵 STILL"
                        elif speed_abs < 5:
                            speed_cat = "🟠 SLOW"
                        else:
                            speed_cat = "🟣 FAST"
                        
                        logger.info(f"  {target_name}: {distance_cat} {distance:.1f}mm | "
                                  f"{speed_cat} {speed_abs:.1f}cm/s | "
                                  f"pos({x:+4d},{y:+4d})")
                
                if not has_targets:
                    logger.info("  📭 No targets detected")
                
                logger.info("  " + "─" * 50)
            else:
                logger.debug(f"Tick {tick} - No sensor data")
            
            await asyncio.sleep(0.2)  # 5Hz for better readability
            tick += 1
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Calibration stopped by user")
    except Exception as e:
        logger.error(f"❌ Calibration error: {e}")
    finally:
        sensor.disconnect()
        logger.info("📡 Sensor disconnected")

async def main():
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, _stop)
    
    logger.add(sys.stderr, level="INFO")
    await calibrate_sensor()

if __name__ == "__main__":
    asyncio.run(main())