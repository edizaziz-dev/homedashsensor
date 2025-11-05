"""
Sensor interfaces for HomeDashSensor.
Single responsibility: Abstract sensor communication and data processing.
"""
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

# Optional sensor imports with graceful fallbacks
try:
    from vl53l5cx.vl53l5cx import VL53L5CX
    VL53L5CX_AVAILABLE = True
except ImportError:
    VL53L5CX_AVAILABLE = False

try:
    import ltr559
    LTR559_AVAILABLE = True
except ImportError:
    LTR559_AVAILABLE = False

try:
    import bme680
    BME680_AVAILABLE = True
except ImportError:
    BME680_AVAILABLE = False


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


@dataclass
class LightReading:
    """Light sensor reading data."""
    lux: float
    valid: bool = True
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class EnvironmentalReading:
    """Environmental sensor reading data."""
    temperature_c: float
    humidity_percent: float
    pressure_hpa: float
    gas_resistance_ohms: Optional[float] = None
    valid: bool = True
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class SensorInterface(ABC):
    """Abstract base class for all sensors."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the sensor. Returns True if successful."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up sensor resources."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if sensor hardware/library is available."""
        pass


class VL53L5CXSensor(SensorInterface):
    """High-performance VL53L5CX proximity sensor interface."""
    
    def __init__(self, config):
        """Initialize VL53L5CX sensor.
        
        Args:
            config: VL53L5CXConfig instance
        """
        self.config = config
        self.sensor = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._last_reading = None
        self._initialized = False
    
    def is_available(self) -> bool:
        """Check if VL53L5CX is available."""
        return VL53L5CX_AVAILABLE and self.config.enabled
    
    async def initialize(self) -> bool:
        """Initialize VL53L5CX sensor with optimized settings."""
        if not self.is_available():
            self.logger.info("VL53L5CX not available, using simulation mode")
            self._initialized = True
            return True
        
        try:
            self.logger.info("Initializing VL53L5CX sensor...")
            
            # Initialize sensor with Pimoroni library
            self.sensor = VL53L5CX()
            
            # Optimize for performance
            await asyncio.get_event_loop().run_in_executor(None, self._init_sensor_blocking)
            
            self._initialized = True
            self.logger.info("✅ VL53L5CX initialized successfully")
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
        
        # Simulation mode
        if self.sensor is None:
            return self._simulate_proximity_reading()
        
        try:
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
            
        except Exception as e:
            # Filter out common VL53L5CX status codes that aren't real errors
            error_str = str(e).strip()
            if error_str in ['133', '134', '135'] or error_str.endswith('133') or error_str.endswith('134') or error_str.endswith('135'):
                # These are normal "no new data" status codes, not errors
                return self._last_reading
            else:
                self.logger.error(f"VL53L5CX read error: {e}")
                return self._simulate_proximity_reading()
    
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
    
    def _simulate_proximity_reading(self) -> ProximityReading:
        """Generate simulated proximity reading for testing."""
        # Simulate human detection occasionally
        import random
        if random.random() < 0.1:  # 10% chance of detecting someone
            return ProximityReading(distance_mm=300, zones_in_range=8)
        else:
            return ProximityReading(distance_mm=2000, zones_in_range=0)
    
    async def cleanup(self) -> None:
        """Clean up VL53L5CX sensor."""
        if self.sensor:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.sensor.stop_ranging)
            except Exception as e:
                self.logger.error(f"Error stopping VL53L5CX: {e}")


class LTR559Sensor(SensorInterface):
    """LTR-559 light sensor interface."""
    
    def __init__(self):
        """Initialize LTR559 sensor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
        self.sensor = None
    
    def is_available(self) -> bool:
        """Check if LTR559 is available."""
        return LTR559_AVAILABLE
    
    async def initialize(self) -> bool:
        """Initialize LTR559 sensor."""
        if not self.is_available():
            self.logger.info("LTR559 not available, using simulation mode")
            self._initialized = True
            return True
        
        try:
            # Create sensor instance
            self.sensor = ltr559.LTR559()
            
            # Configure sensor for optimal performance
            self.sensor.set_light_integration_time_ms(100)  # 100ms for good balance
            self.sensor.set_light_repeat_rate_ms(500)       # 500ms repeat rate
            
            self._initialized = True
            self.logger.info("✅ LTR559 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LTR559: {e}")
            self.sensor = None
            self._initialized = True  # Fall back to simulation
            return True
    
    async def read_light(self) -> Optional[LightReading]:
        """Read light sensor data."""
        if not self._initialized:
            return None
        
        if self.sensor is None:
            # Simulate varying light conditions
            import random
            return LightReading(lux=random.uniform(10, 1000))
        
        try:
            lux = self.sensor.get_lux()
            return LightReading(lux=lux, valid=lux > 0)
            
        except Exception as e:
            self.logger.error(f"LTR559 read error: {e}")
            return LightReading(lux=100.0, valid=False)  # Default fallback
    
    async def cleanup(self) -> None:
        """Clean up LTR559 sensor."""
        # LTR559 doesn't require explicit cleanup
        pass


class BME680Sensor(SensorInterface):
    """BME680 environmental sensor interface."""
    
    def __init__(self):
        """Initialize BME680 sensor."""
        self.sensor = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    def is_available(self) -> bool:
        """Check if BME680 is available."""
        return BME680_AVAILABLE
    
    async def initialize(self) -> bool:
        """Initialize BME680 sensor."""
        if not self.is_available():
            self.logger.info("BME680 not available, using simulation mode")
            self._initialized = True
            return True
        
        try:
            self.sensor = bme680.BME680()
            
            # Configure sensor for optimal performance
            self.sensor.set_humidity_oversample(bme680.OS_2X)
            self.sensor.set_pressure_oversample(bme680.OS_4X)
            self.sensor.set_temperature_oversample(bme680.OS_8X)
            self.sensor.set_filter(bme680.FILTER_SIZE_3)
            
            # Configure gas sensor
            self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)
            
            self._initialized = True
            self.logger.info("✅ BME680 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BME680: {e}")
            self.sensor = None
            self._initialized = True  # Fall back to simulation
            return True
    
    async def read_environmental(self) -> Optional[EnvironmentalReading]:
        """Read environmental sensor data."""
        if not self._initialized:
            return None
        
        if self.sensor is None:
            # Simulate reasonable environmental conditions
            import random
            return EnvironmentalReading(
                temperature_c=random.uniform(18, 26),
                humidity_percent=random.uniform(30, 70),
                pressure_hpa=random.uniform(1000, 1025),
                gas_resistance_ohms=random.uniform(10000, 200000)
            )
        
        try:
            if self.sensor.get_sensor_data():
                return EnvironmentalReading(
                    temperature_c=self.sensor.data.temperature,
                    humidity_percent=self.sensor.data.humidity,
                    pressure_hpa=self.sensor.data.pressure,
                    gas_resistance_ohms=self.sensor.data.gas_resistance if self.sensor.data.heat_stable else None
                )
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"BME680 read error: {e}")
            return EnvironmentalReading(temperature_c=22.0, humidity_percent=50.0, pressure_hpa=1013.25, valid=False)
    
    async def cleanup(self) -> None:
        """Clean up BME680 sensor."""
        # BME680 doesn't require explicit cleanup
        pass