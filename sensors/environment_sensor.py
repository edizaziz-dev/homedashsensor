from dataclasses import dataclass
import time
import asyncio
from typing import Optional
from sensors.sensor_interface import SensorInterface
import logging
from config import EnvironmentSensorConfig

# Prefer Pimoroni bme690 library when available; fall back to bme680 for compatibility
try:
    import bme690 as _bme_lib  # type: ignore
    BME_LIB_NAME = "bme690"
except Exception:
    import bme680 as _bme_lib  # type: ignore
    BME_LIB_NAME = "bme680"

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

class EnvironmentSensor(SensorInterface):
    def __init__(self, config: EnvironmentSensorConfig):
        """Initialize BME680 sensor.

        Args:
            config: EnvironmentSensorConfig instance with sensor settings
        """
        self.config = config
        self.sensor = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize BME680 sensor."""
        try:
            # construct sensor using configured I2C address (adapter handles lib differences)
            # bme690 and bme680 constructors differ; try to be flexible
            try:
                self.sensor = _bme_lib.BME690(self.config.i2c_address) if BME_LIB_NAME == "bme690" else _bme_lib.BME680(self.config.i2c_address)
            except Exception:
                # some libraries accept no args
                self.sensor = _bme_lib.BME690() if BME_LIB_NAME == "bme690" else _bme_lib.BME680()
            
            # Configure sensor for optimal performance
            # Map oversample and filter constants from the selected library
            # The Pimoroni bme690 exposes similar constants to bme680; try to adapt
            lib = _bme_lib

            def _os_const(kind: str, value: int):
                # kind is one of 'OS' (oversample) or 'FILTER'
                try:
                    if kind == 'OS':
                        return getattr(lib, f"OS_{value}X")
                except Exception:
                    pass
                # fallback constants expected by bme680/bme690
                try:
                    return getattr(lib, f"OS_{value}X")
                except Exception:
                    return None

            TEMPERATURE_OVERSAMPLE = _os_const('OS', self.config.temperature_oversample) or getattr(lib, 'OS_8X', None)
            PRESSURE_OVERSAMPLE = _os_const('OS', self.config.pressure_oversample) or getattr(lib, 'OS_8X', None)
            HUMIDITY_OVERSAMPLE = _os_const('OS', self.config.humidity_oversample) or getattr(lib, 'OS_8X', None)

            if TEMPERATURE_OVERSAMPLE is not None:
                try:
                    self.sensor.set_temperature_oversample(TEMPERATURE_OVERSAMPLE)
                except Exception:
                    pass
            if PRESSURE_OVERSAMPLE is not None:
                try:
                    self.sensor.set_pressure_oversample(PRESSURE_OVERSAMPLE)
                except Exception:
                    pass
            if HUMIDITY_OVERSAMPLE is not None:
                try:
                    self.sensor.set_humidity_oversample(HUMIDITY_OVERSAMPLE)
                except Exception:
                    pass

            # Map configured filter size to library constant if possible
            try:
                filt = int(self.config.filter_size)
                filt = max(0, min(filt, 3))
                filter_const = getattr(lib, f"FILTER_SIZE_{filt}")
                try:
                    self.sensor.set_filter(filter_const)
                except Exception:
                    pass
            except Exception:
                # ignore if constants not present
                pass
            
            # Configure gas sensor
            if self.config.gas_enabled:
                try:
                    if hasattr(lib, 'ENABLE_GAS_MEAS'):
                        self.sensor.set_gas_status(getattr(lib, 'ENABLE_GAS_MEAS'))
                    else:
                        self.sensor.set_gas_status(True)
                except Exception:
                    pass
                try:
                    self.sensor.set_gas_heater_temperature(self.config.gas_heater_temp)
                    self.sensor.set_gas_heater_duration(self.config.gas_heater_duration)
                    if hasattr(self.sensor, 'select_gas_heater_profile'):
                        self.sensor.select_gas_heater_profile(0)
                except Exception:
                    pass
            
            self._initialized = True
            # Allow sensor a short warm-up before the first read
            try:
                await asyncio.sleep(0.5)
            except Exception:
                # if event loop isn't available for some reason, ignore
                pass

            self._initialized = True
            self.logger.info("BME690 initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"BME690 init failed: {e}")
            self.sensor = None
            self._initialized = False
            return False
    
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
            self.logger.error(f"BME690 read error: {e}")
            return None
    
    async def cleanup(self) -> None:
        """Clean up BME690 sensor."""
        # BME690 doesn't require explicit cleanup
        pass