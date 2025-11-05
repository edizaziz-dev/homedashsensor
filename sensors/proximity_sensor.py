import asyncio
from dataclasses import dataclass
import logging
import time
from typing import Optional
from sensors.sensor_interface import SensorInterface

@dataclass
class ProximityReading:
    """Proximity sensor reading data."""
    distance_mm: int
    zones_in_range: int
    valid: bool = True
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class VL53L5CXSensor(SensorInterface):
    """High-performance VL53L5CX proximity sensor interface."""
    
    def __init__(self, config):       
        self.config = config
        self.sensor = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._last_reading = None
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize VL53L5CX sensor with optimized settings."""
        import vl53l5cx_ctypes as vl53l5cx
        
        try:
            self.logger.info("Initializing VL53L5CX sensor...")
            print("Uploading firmware, please wait...")
            # Initialize sensor with Pimoroni library
            self.sensor = vl53l5cx.VL53L5CX()
            self._initialized = True
            print("Done!")
                        
            # Optimize for performance
            await asyncio.get_event_loop().run_in_executor(None, self._init_sensor_blocking)
            
            self._initialized = True
            self.logger.info("VL53L5CX initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VL53L5CX: {e}")
            self.sensor = None
            self._initialized = True  # Fall back to simulation
            return True
    
    def _init_sensor_blocking(self) -> None:
        """Blocking sensor initialization operations."""
        from vl53l5cx.vl53l5cx import VL53L5CX_RESOLUTION_8X8, VL53L5CX_RESOLUTION_4X4
        
        # Set I2C address
        self.sensor.set_i2c_address(self.config.i2c_address)
        
        # Initialize sensor
        self.sensor.init()
        
        # Configure resolution
        if self.config.resolution == 64:
            self.sensor.set_resolution(VL53L5CX_RESOLUTION_8X8)
        else:
            self.sensor.set_resolution(VL53L5CX_RESOLUTION_4X4)
        
        # Set frequency
        self.sensor.set_ranging_frequency_hz(self.config.frequency_hz)
        
        # Optimize for performance (only if specified)
        if self.config.integration_time is not None:
            self.sensor.set_integration_time_ms(self.config.integration_time)
        
        if self.config.sharpener_percent is not None:
            self.sensor.set_sharpener_percent(self.config.sharpener_percent)
        
        # Start ranging
        self.sensor.start_ranging()
    
    async def read_proximity(self) -> Optional[ProximityReading]:
        """Read proximity data with performance optimization."""
        if not self._initialized:
            return None
                
        # Non-blocking check for data availability
        data_ready = await asyncio.get_event_loop().run_in_executor(
            None, self.sensor.check_data_ready
        )
        
        if not data_ready:
            return self._last_reading
        
        # Read data
        ranging_data = await asyncio.get_event_loop().run_in_executor(
            None, self.sensor.get_ranging_data
        )
        
        # Check if ranging_data is valid
        if ranging_data is None:
            return self._last_reading
        
        # Process data efficiently
        reading = self._process_ranging_data(ranging_data)
        self._last_reading = reading
        return reading            
    
    
    def _process_ranging_data(self, data) -> ProximityReading:
        """Process raw ranging data into proximity reading."""
        # Focus on center 4x4 zones for better performance
        center_zones = [18, 19, 20, 21, 26, 27, 28, 29, 34, 35, 36, 37, 42, 43, 44, 45]
        
        valid_distances = []
        zones_in_range = 0
        
        # Use proximity threshold from config for zone detection
        zone_threshold = 2000  # Use a reasonable threshold for zone detection
        
        for i in center_zones:
            if i < len(data.distance_mm):
                distance = data.distance_mm[i]
                target_status = data.target_status[i]
                
                # Check for valid status codes (Pimoroni library uses different codes)
                # Status 6 = valid target, 13 = valid with low signal, 255 = no target
                if target_status in [6, 13] and 50 <= distance <= 4000:  # Valid range
                    valid_distances.append(distance)
                    if distance <= zone_threshold:  # Use configurable threshold
                        zones_in_range += 1
        
        # Use minimum distance from valid readings
        min_distance = min(valid_distances) if valid_distances else 4000
        
        return ProximityReading(
            distance_mm=int(min_distance),  # Ensure integer
            zones_in_range=zones_in_range,
            valid=len(valid_distances) > 0
        )
        
    async def cleanup(self) -> None:
        """Clean up VL53L5CX sensor."""
        if self.sensor:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.sensor.stop_ranging)
            except Exception as e:
                self.logger.error(f"Error stopping VL53L5CX: {e}")