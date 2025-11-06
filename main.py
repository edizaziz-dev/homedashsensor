#!/usr/bin/env python3
import asyncio
import logging
import sys
from sensors.display_manager import DisplayManager
from sensors.environment_sensor import EnvironmentSensor
from sensors.lux_sensor import LuxSensor
from sensors.proximity_sensor import VL53L5CXSensor
from sensors.mqtt_publisher import MQTTPublisher
from config import ConfigManager
import numpy as np, time, os, glob

class HomeDashboardApp:
    __config_manager: ConfigManager
    __display_manager: DisplayManager
    __vl53: VL53L5CXSensor
    __lux_sensor: LuxSensor
    __environment_sensor: EnvironmentSensor
    __mqtt_publisher: MQTTPublisher

    def __init__(self):
        self.__config_manager = ConfigManager()
        
        self.__display_config = self.__config_manager.get_display_config()
        self.__proximity_sensor_config = self.__config_manager.get_vl53l5cx_config()
        self.__detection_config = self.__config_manager.get_detection_config()
        self.__light_sensor_config = self.__config_manager.get_lux_config()
        self.__environment_sensor_config = self.__config_manager.get_environment_sensor_config()
        self.__mqtt_config = self.__config_manager.get_mqtt_config()
        self.__system_config = self.__config_manager.get_system_config()
        
        # Setup logging (after configs are loaded)
        self._setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.__display_manager = DisplayManager(self.__display_config)
        self.__vl53 = VL53L5CXSensor(self.__proximity_sensor_config)
        self.__lux_sensor = LuxSensor(self.__light_sensor_config)
        self.__environment_sensor = EnvironmentSensor(self.__environment_sensor_config)
        self.__mqtt_publisher = MQTTPublisher(self.__mqtt_config) if self.__mqtt_config.enabled else None
        
        self.screen_on = False
        
    async def initialize(self) -> bool:
        self.logger.info("HomeDashboardApp starting...")
        await self.__lux_sensor.initialize()
        await self.__vl53.initialize()
        print("Proximity-based fade running (Ctrl-C to stop)")
        await self.__environment_sensor.initialize()
        
        # Initialize MQTT if enabled
        if self.__mqtt_publisher:
            mqtt_success = await self.__mqtt_publisher.initialize()
            if not mqtt_success:
                self.logger.warning("MQTT initialization failed, continuing without MQTT")
                self.__mqtt_publisher = None
                
        return True
        
    async def run(self):
        """Run the main system loop."""
        self.last_seen = time.monotonic()
        
        if not await self.initialize():
            return
        
        try:
            while True:
                if self.__vl53.sensor.data_ready():
                    frame = self.__vl53.sensor.get_data()
                    d = np.frombuffer(bytes(frame.distance_mm), dtype="<u2")[:self.__proximity_sensor_config.resolution]
                    valid = [x for x in d if 0 < x < 8191]

                    if valid:
                        near = min(valid)
                        human_detected = near < self.__detection_config.threshold_mm
                        
                        # Publish proximity state to MQTT
                        if self.__mqtt_publisher:
                            await self.__mqtt_publisher.publish_proximity_state(human_detected, near)
                        
                        # within threshold
                        if human_detected:
                            last_seen = time.monotonic()
                            if not self.screen_on:
                                reading = self.__lux_sensor.get_lux()  # read lux to update sensor state
                                self.logger.info(f"🙋 Human detected at {near}mm, lux={reading.lux:.2f}")
                                
                                # Publish light data
                                if self.__mqtt_publisher and reading.valid:
                                    await self.__mqtt_publisher.publish_light_data(reading.lux)

                                if self.__display_config.adaptive_brightness_enabled and reading.valid:
                                    await self.__display_manager.set_adaptive_brightness(reading.lux)
                                else:
                                    self.__display_manager.fade_to(self.__display_manager.max_brightness)
                                
                                # Publish display brightness
                                if self.__mqtt_publisher:
                                    brightness_percent = int((self.__display_manager.get_brightness() / 255) * 100)
                                    await self.__mqtt_publisher.publish_display_brightness(brightness_percent)

                                self.screen_on = True
                        else:
                            # object far away
                            if self.screen_on and (time.monotonic() - last_seen) > 2.0:
                                self.logger.info(f"🚶 Human left, distance {near}mm")
                                self.__display_manager.fade_to(0)
                                
                                # Publish display off state
                                if self.__mqtt_publisher:
                                    await self.__mqtt_publisher.publish_display_brightness(0)
                                
                                self.screen_on = False

                if self.__environment_sensor_config.enabled:
                    readings = await self.get_environment_readings()
                    if readings and self.__mqtt_publisher:
                        await self.__mqtt_publisher.publish_environment_data(readings)
                
                await asyncio.sleep(0.05)

        except KeyboardInterrupt:
            try:
                await self.__vl53.sensor.stop_ranging()
            except Exception:
                try:
                    self.__vl53.sensor.stop_ranging()
                except Exception:
                    pass
            
            # Clean up MQTT connection
            if self.__mqtt_publisher:
                await self.__mqtt_publisher.cleanup()
                
            self.__display_manager.fade_to(self.__display_manager.max_brightness)
            print("Stopped.")
            
    async def get_environment_readings(self):
        readings = await self.__environment_sensor.read_environmental()
        if readings:
            self.logger.info(f"🌡️ Environment: {readings.temperature_c:.1f}°C, {readings.humidity_percent:.1f}%, {readings.pressure_hpa:.1f}hPa")
        else:
            self.logger.warning("Failed to read environment sensor data.")
        return readings

    def _setup_logging(self) -> None:
        """Configure logging system."""
        log_level = getattr(logging, self.__system_config.log_level.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s.%(msecs)03d [%(levelname)-5s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Reduce noise from libraries
        logging.getLogger("asyncio").setLevel(logging.WARNING)

async def main():
    try:
        app = HomeDashboardApp()
        await app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
        
# ensure script runs and surface errors instead of exiting silently
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("Fatal error:", e, file=sys.stderr)
        raise
# ...existing code...