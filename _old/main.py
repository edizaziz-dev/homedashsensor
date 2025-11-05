"""
HomeDashSensor - Proximity-based display control system.
Optimized Python implementation with Single Responsibility Principle.
"""
import asyncio
import signal
import logging
import sys
from typing import Optional

from config import ConfigManager
from sensors import VL53L5CXSensor, LTR559Sensor, BME680Sensor
from display import DisplayController
from proximity import ProximityDetector


class HomeDashSensor:
    """Main application coordinating all system components."""
    
    def __init__(self, config_file: str = "proximity_config.ini"):
        """Initialize HomeDashSensor system.
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config_manager = ConfigManager(config_file)
        self.vl53l5cx_config = self.config_manager.get_vl53l5cx_config()
        self.detection_config = self.config_manager.get_detection_config()
        self.display_config = self.config_manager.get_display_config()
        self.system_config = self.config_manager.get_system_config()
        
        # Initialize components
        self.proximity_sensor = VL53L5CXSensor(self.vl53l5cx_config)
        self.light_sensor = LTR559Sensor()
        self.environmental_sensor = BME680Sensor()
        self.display_controller = DisplayController(self.display_config)
        self.proximity_detector = ProximityDetector(self.detection_config)
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Runtime state
        self._running = False
        self._tasks = []
        self._shutdown_event = asyncio.Event()
        
        # Performance monitoring
        self._stats = {
            "proximity_readings": 0,
            "light_readings": 0,
            "environmental_readings": 0,
            "detection_events": 0,
            "display_changes": 0
        }
    
    def _setup_logging(self) -> None:
        """Configure logging system."""
        log_level = getattr(logging, self.system_config.log_level.upper(), logging.INFO)
        
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
    
    async def initialize(self) -> bool:
        """Initialize all system components."""
        self.logger.info("🎯 HomeDashSensor starting...")
        
        try:
            # Initialize sensors
            self.logger.info("Initializing sensors...")
            sensors_ok = all(await asyncio.gather(
                self.proximity_sensor.initialize(),
                self.light_sensor.initialize(),
                self.environmental_sensor.initialize(),
                return_exceptions=False
            ))
            
            if not sensors_ok:
                self.logger.error("Failed to initialize one or more sensors")
                return False
            
            # Initialize display controller
            self.logger.info("Initializing display controller...")
            if not await self.display_controller.initialize():
                self.logger.error("Failed to initialize display controller")
                return False
            
            self.logger.info("✅ System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    async def run(self) -> None:
        """Run the main system loop."""
        if not await self.initialize():
            return
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self._running = True
        self.logger.info("🚀 Starting HomeDashSensor...")
        
        try:
            # Start all worker tasks
            self._tasks = [
                asyncio.create_task(self._proximity_worker(), name="proximity"),
                asyncio.create_task(self._light_worker(), name="light"),
                asyncio.create_task(self._environmental_worker(), name="environmental"),
                asyncio.create_task(self._stats_worker(), name="stats")
            ]
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
        finally:
            await self._shutdown()
    
    async def _proximity_worker(self) -> None:
        """High-frequency proximity monitoring worker."""
        self.logger.info("🎯 Proximity worker started")
        previous_human_present = False
        
        try:
            while self._running:
                # Read proximity sensor
                reading = await self.proximity_sensor.read_proximity()
                self._stats["proximity_readings"] += 1
                
                # Process detection
                human_present = self.proximity_detector.process_reading(reading)
                
                # Handle state changes
                if human_present != previous_human_present:
                    self._stats["detection_events"] += 1
                    self._stats["display_changes"] += 1
                    
                    if human_present:
                        await self.display_controller.wake_display()
                    else:
                        await self.display_controller.sleep_display()
                    
                    previous_human_present = human_present
                
                # High-frequency update for responsive detection
                await asyncio.sleep(self.system_config.update_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Proximity worker error: {e}")
        finally:
            self.logger.info("🎯 Proximity worker stopped")
    
    async def _light_worker(self) -> None:
        """Light sensor monitoring worker."""
        self.logger.info("🌟 Light sensor worker started")
        
        try:
            while self._running:
                # Read light sensor
                reading = await self.light_sensor.read_light()
                if reading and reading.valid:
                    self._stats["light_readings"] += 1
                    
                    # Update adaptive brightness
                    await self.display_controller.set_adaptive_brightness(reading.lux)
                
                # Lower frequency for light changes (1Hz)
                await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Light worker error: {e}")
        finally:
            self.logger.info("🌟 Light sensor worker stopped")
    
    async def _environmental_worker(self) -> None:
        """Environmental sensor monitoring worker."""
        self.logger.info("🌡️ Environmental sensor worker started")
        
        try:
            while self._running:
                # Read environmental sensor
                reading = await self.environmental_sensor.read_environmental()
                if reading and reading.valid:
                    self._stats["environmental_readings"] += 1
                    
                    # Log environmental data periodically
                    if self._stats["environmental_readings"] % 60 == 0:  # Every minute
                        self.logger.info(f"🌡️ Environment: {reading.temperature_c:.1f}°C, "
                                       f"{reading.humidity_percent:.1f}%RH, "
                                       f"{reading.pressure_hpa:.1f}hPa")
                
                # Low frequency for environmental changes (10s)
                await asyncio.sleep(10.0)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Environmental worker error: {e}")
        finally:
            self.logger.info("🌡️ Environmental sensor worker stopped")
    
    async def _stats_worker(self) -> None:
        """Performance statistics worker."""
        try:
            while self._running:
                await asyncio.sleep(60.0)  # Log stats every minute
                
                self.logger.info(f"📊 Stats: "
                               f"proximity={self._stats['proximity_readings']}, "
                               f"light={self._stats['light_readings']}, "
                               f"env={self._stats['environmental_readings']}, "
                               f"detections={self._stats['detection_events']}")
                
        except asyncio.CancelledError:
            pass
    
    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown signal handlers."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, requesting shutdown...")
            asyncio.create_task(self._request_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _request_shutdown(self) -> None:
        """Request graceful shutdown."""
        if self._running:
            self._running = False
            self._shutdown_event.set()
    
    async def _shutdown(self) -> None:
        """Graceful system shutdown."""
        self.logger.info("🛑 Shutting down HomeDashSensor...")
        
        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Cleanup components
        await asyncio.gather(
            self.proximity_sensor.cleanup(),
            self.light_sensor.cleanup(),
            self.environmental_sensor.cleanup(),
            self.display_controller.cleanup(),
            return_exceptions=True
        )
        
        self.logger.info("👋 HomeDashSensor shutdown complete")


async def main():
    """Main entry point."""
    try:
        app = HomeDashSensor()
        await app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())