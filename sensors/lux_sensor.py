import asyncio
from dataclasses import dataclass
import logging
import time
import ltr559

from sensors.sensor_interface import SensorInterface

@dataclass
class LightReading:
    """Light sensor reading data."""
    lux: float
    valid: bool = True
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
            
class LuxSensor(SensorInterface):
    """Ambient light sensor interface."""
    
    def __init__(self, config):
        self.config = config
        self.sensor = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize ambient light sensor."""
        if not self.config.enabled:
            self.logger.info("Ambient light sensor disabled in configuration.")
            return False
        try:            
            self.logger.info("Initializing ambient light sensor...")
            
            # Initialize sensor with appropriate library
            self.sensor = ltr559.LTR559()
            
            # Configure sensor for optimal performance
            self.sensor.set_light_integration_time_ms(100)  # 100ms for good balance
            self.sensor.set_light_repeat_rate_ms(500)       # 500ms repeat rate
            
            self._initialized = True
            self.logger.info("Ambient light sensor initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ambient light sensor: {e}")
            self.sensor = None            
            return True
    
    def get_lux(self) -> LightReading:
        """Get the current ambient light level in lux."""
        if not self._initialized or self.sensor is None:
            return LightReading(lux=0.0, valid=False)
        
        try:
            lux_value = self.sensor.get_lux()
            return LightReading(lux=lux_value, valid=True)
        except Exception as e:
            self.logger.error(f"Error reading lux value: {e}")
            return LightReading(lux=0.0, valid=False)
    
    async def cleanup(self) -> None:
        """Clean up LTR559 sensor."""
        # LTR559 doesn't require explicit cleanup
        pass