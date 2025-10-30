#!/usr/bin/env python3
"""
VL53L5CX Proximity Display Control
Automatically controls display brightness based on human presence detection.

Features:
- Detects human presence within 40cm threshold
- Smooth brightness fading (fade in/out)
- Uses multiple zones for reliable detection
- Configurable timing and thresholds
- Comprehensive logging

Hardware requirements:
- VL53L5CX 8x8 ToF sensor
- Display with brightness control via sysfs
"""

import time
import sys
import asyncio
import signal
import logging
import configparser
from pathlib import Path
from typing import Optional, List
import vl53l5cx_ctypes as vl53l5cx

# Try to import LTR-559 light sensor
try:
    import ltr559
    LTR559_AVAILABLE = True
except ImportError:
    LTR559_AVAILABLE = False

# Try to import BME690 environmental sensor
try:
    import bme680
    BME690_AVAILABLE = True
except ImportError:
    BME690_AVAILABLE = False

class ProximityConfig:
    """Configuration loader for proximity display control system."""
    
    def __init__(self, config_file: str = "proximity_config.ini"):
        """Load configuration from INI file.
        
        Args:
            config_file: Path to configuration file
        """
        self.config = configparser.ConfigParser()
        self.config_file = Path(config_file)
        
        # Set defaults
        self._set_defaults()
        
        # Load from file if it exists
        if self.config_file.exists():
            self.config.read(self.config_file)
            # Logger will report this after it's initialized
        else:
            # Logger will report this after it's initialized
            pass
    
    def _set_defaults(self):
        """Set default configuration values."""
        self.config['VL53L5CX'] = {
            'enabled': 'true',
            'i2c_address': '0x29',
            'resolution': '64',
            'frequency_hz': '15',
            'integration_time': '20',
            'sharpener_percent': '5'
        }
        
        self.config['Detection'] = {
            'threshold_mm': '400',
            'detection_zones': '4', 
            'consecutive_required': '2',
            'no_presence_required': '10'
        }
        
        self.config['Display'] = {
            'fade_in_duration': '2.0',
            'fade_out_duration': '3.0',
            'brightness_path': '/sys/class/backlight/*/brightness',
            'adaptive_brightness_enabled': 'true',
            'min_brightness': '20',
            'max_brightness': '255',
            'light_threshold_low': '10.0',
            'light_threshold_high': '500.0',
            'fade_steps': '120',
            'fade_easing': 'ease_in_out'
        }
        
        self.config['System'] = {
            'update_interval': '0.1',
            'sensor_frequency': '15',
            'log_level': 'INFO',
            'log_file': 'proximity_display.log',
            'i2c_bus': '1',
            'i2c_frequency': '400000',
            'gpio_interrupt_pin': '18',
            'gpio_reset_pin': '24'
        }
        
        self.config['LightSensor'] = {
            'enabled': 'true',
            'i2c_address': '0x23',
            'i2c_bus': '1',
            'update_interval': '2.0',
            'gain': '1',
            'integration_time': '100',
            'measurement_rate': '500'
        }
        
        self.config['BME690'] = {
            'enabled': 'true',
            'i2c_address': '0x76',
            'i2c_bus': '1',
            'update_interval': '5.0',
            'temperature_oversample': '8',
            'pressure_oversample': '4',
            'humidity_oversample': '2',
            'gas_enabled': 'true',
            'gas_heater_temperature': '320',
            'gas_heater_duration': '150',
            'filter_size': '3'
        }
    
    @property
    def threshold_mm(self) -> int:
        """Distance threshold in millimeters."""
        return self.config.getint('Detection', 'threshold_mm')
    
    @property
    def detection_zones(self) -> int:
        """Minimum zones that must detect proximity."""
        return self.config.getint('Detection', 'detection_zones')
    
    @property
    def consecutive_required(self) -> int:
        """Consecutive detections required."""
        return self.config.getint('Detection', 'consecutive_required')
    
    @property
    def no_presence_required(self) -> int:
        """Consecutive non-detections required."""
        return self.config.getint('Detection', 'no_presence_required')
    
    @property
    def fade_in_duration(self) -> float:
        """Fade in duration in seconds."""
        return self._getfloat_clean('Display', 'fade_in_duration', fallback=2.0)
    
    @property
    def fade_out_duration(self) -> float:
        """Fade out duration in seconds."""
        return self._getfloat_clean('Display', 'fade_out_duration', fallback=3.0)
    
    @property
    def brightness_path(self) -> str:
        """Display brightness control path."""
        return self.config.get('Display', 'brightness_path')
    
    @property
    def update_interval(self) -> float:
        """Sensor polling interval in seconds."""
        return self.config.getfloat('System', 'update_interval')
    
    @property
    def sensor_frequency(self) -> int:
        """Sensor frequency in Hz."""
        return self.config.getint('System', 'sensor_frequency')
    
    @property
    def log_level(self) -> str:
        """Logging level."""
        return self.config.get('System', 'log_level')
    
    # VL53L5CX sensor properties
    @property
    def vl53l5cx_enabled(self) -> bool:
        """Whether VL53L5CX sensor is enabled."""
        return self.config.getboolean('VL53L5CX', 'enabled')
    
    @property
    def vl53l5cx_address(self) -> int:
        """VL53L5CX I2C address."""
        addr_str = self.config.get('VL53L5CX', 'i2c_address', fallback='0x29')
        if addr_str.startswith('0x'):
            return int(addr_str, 16)  # Parse as hex
        else:
            return int(addr_str)  # Parse as decimal
    
    @property
    def vl53l5cx_resolution(self) -> int:
        """VL53L5CX resolution (4x4=16 or 8x8=64)."""
        return self.config.getint('VL53L5CX', 'resolution')
    
    @property
    def vl53l5cx_frequency(self) -> int:
        """VL53L5CX ranging frequency in Hz."""
        return self.config.getint('VL53L5CX', 'frequency_hz')
    
    @property
    def vl53l5cx_integration_time(self) -> int:
        """VL53L5CX integration time in ms."""
        return self.config.getint('VL53L5CX', 'integration_time')
    
    @property
    def vl53l5cx_sharpener(self) -> int:
        """VL53L5CX sharpener percentage."""
        return self.config.getint('VL53L5CX', 'sharpener_percent')
    
    # System properties
    @property
    def log_file(self) -> str:
        """Log file path."""
        return self.config.get('System', 'log_file')
    
    @property
    def i2c_bus(self) -> int:
        """I2C bus number."""
        return self.config.getint('System', 'i2c_bus')
    
    @property
    def i2c_frequency(self) -> int:
        """I2C frequency in Hz."""
        return self.config.getint('System', 'i2c_frequency')
    
    @property
    def gpio_interrupt_pin(self) -> int:
        """GPIO interrupt pin number."""
        return self.config.getint('System', 'gpio_interrupt_pin')
    
    @property
    def gpio_reset_pin(self) -> int:
        """GPIO reset pin number."""
        return self.config.getint('System', 'gpio_reset_pin')
    
    # Light sensor properties (enhanced)
    @property
    def light_sensor_i2c_bus(self) -> int:
        """Light sensor I2C bus number."""
        return self.config.getint('LightSensor', 'i2c_bus', fallback=1)
    
    @property
    def light_sensor_measurement_rate(self) -> int:
        """Light sensor measurement rate in ms."""
        return self.config.getint('LightSensor', 'measurement_rate', fallback=500)
    
    # BME690 environmental sensor properties
    @property
    def bme690_enabled(self) -> bool:
        """Whether BME690 sensor is enabled."""
        return self.config.getboolean('BME690', 'enabled')
    
    @property
    def bme690_address(self) -> int:
        """BME690 I2C address."""
        addr_str = self.config.get('BME690', 'i2c_address', fallback='0x76')
        if addr_str.startswith('0x'):
            return int(addr_str, 16)  # Parse as hex
        else:
            return int(addr_str)  # Parse as decimal
    
    @property
    def bme690_i2c_bus(self) -> int:
        """BME690 I2C bus number."""
        return self.config.getint('BME690', 'i2c_bus', fallback=1)
    
    @property
    def bme690_update_interval(self) -> float:
        """BME690 update interval in seconds."""
        return self.config.getfloat('BME690', 'update_interval')
    
    @property
    def bme690_temperature_oversample(self) -> int:
        """BME690 temperature oversampling."""
        return self.config.getint('BME690', 'temperature_oversample')
    
    @property
    def bme690_pressure_oversample(self) -> int:
        """BME690 pressure oversampling."""
        return self.config.getint('BME690', 'pressure_oversample')
    
    @property
    def bme690_humidity_oversample(self) -> int:
        """BME690 humidity oversampling."""
        return self.config.getint('BME690', 'humidity_oversample')
    
    @property
    def bme690_gas_enabled(self) -> bool:
        """Whether BME690 gas sensing is enabled."""
        return self.config.getboolean('BME690', 'gas_enabled')
    
    @property
    def bme690_gas_heater_temperature(self) -> int:
        """BME690 gas heater temperature in Celsius."""
        return self.config.getint('BME690', 'gas_heater_temperature')
    
    @property
    def bme690_gas_heater_duration(self) -> int:
        """BME690 gas heater duration in milliseconds."""
        return self.config.getint('BME690', 'gas_heater_duration')
    
    @property
    def bme690_filter_size(self) -> int:
        """BME690 IIR filter size."""
        return self.config.getint('BME690', 'filter_size')
    
    # Light sensor properties
    @property
    def adaptive_brightness_enabled(self) -> bool:
        """Whether adaptive brightness is enabled."""
        return self.config.getboolean('Display', 'adaptive_brightness_enabled')
    
    @property
    def min_brightness(self) -> int:
        """Minimum brightness value."""
        return self.config.getint('Display', 'min_brightness')
    
    @property
    def max_brightness_config(self) -> int:
        """Maximum brightness value from config."""
        return self.config.getint('Display', 'max_brightness')
    
    @property
    def light_threshold_low(self) -> float:
        """Low light threshold in lux."""
        return self.config.getfloat('Display', 'light_threshold_low')
    
    @property
    def light_threshold_high(self) -> float:
        """High light threshold in lux."""
        return self.config.getfloat('Display', 'light_threshold_high')
    
    def _get_clean_value(self, section: str, option: str, fallback=None) -> str:
        """Get configuration value with inline comments stripped."""
        try:
            raw_value = self.config.get(section, option, fallback=str(fallback) if fallback is not None else None)
            if raw_value is None:
                return None
            # Strip inline comments (everything after #)
            if '#' in raw_value:
                return raw_value.split('#')[0].strip()
            return raw_value.strip()
        except:
            return str(fallback) if fallback is not None else None

    def _getint_clean(self, section: str, option: str, fallback: int = None) -> int:
        """Get integer value with inline comments stripped."""
        clean_value = self._get_clean_value(section, option, fallback)
        if clean_value is None and fallback is not None:
            return fallback
        return int(clean_value)

    def _getfloat_clean(self, section: str, option: str, fallback: float = None) -> float:
        """Get float value with inline comments stripped."""
        clean_value = self._get_clean_value(section, option, fallback)
        if clean_value is None and fallback is not None:
            return fallback
        return float(clean_value)

    @property
    def fade_steps(self) -> int:
        """Number of steps for fade animation."""
        return self._getint_clean('Display', 'fade_steps', fallback=120)
    
    @property
    def fade_easing(self) -> str:
        """Fade easing method."""
        return self._get_clean_value('Display', 'fade_easing', fallback='ease_in_out')
    
    @property
    def light_sensor_enabled(self) -> bool:
        """Whether light sensor is enabled."""
        return self.config.getboolean('LightSensor', 'enabled')
    
    @property
    def light_sensor_address(self) -> int:
        """Light sensor I2C address."""
        addr_str = self.config.get('LightSensor', 'i2c_address', fallback='0x23')
        if addr_str.startswith('0x'):
            return int(addr_str, 16)  # Parse as hex
        else:
            return int(addr_str)  # Parse as decimal
    
    @property
    def light_sensor_update_interval(self) -> float:
        """Light sensor update interval in seconds."""
        return self.config.getfloat('LightSensor', 'update_interval')
    
    @property
    def light_sensor_gain(self) -> int:
        """Light sensor gain setting."""
        return self.config.getint('LightSensor', 'gain')
    
    @property
    def light_sensor_integration_time(self) -> int:
        """Light sensor integration time in ms."""
        return self.config.getint('LightSensor', 'integration_time')

# Load configuration first
config = ProximityConfig()

# Configure logging with level from config
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.log_file)
    ]
)
logger = logging.getLogger(__name__)

# Log that config was loaded after logger is ready
if config.config_file.exists():
    logger.info(f"📋 Configuration loaded from {config.config_file}")
else:
    logger.warning(f"⚠️  Config file {config.config_file} not found, using defaults")

# Check light sensor availability
if not LTR559_AVAILABLE:
    logger.warning("⚠️  LTR-559 library not available, adaptive brightness disabled")

# Check BME690 availability
if not BME690_AVAILABLE:
    logger.warning("⚠️  BME690 library not available, environmental monitoring disabled")

class EnvironmentalSensorController:
    """Controls BME690 environmental sensor for air quality monitoring."""
    
    def __init__(self):
        """Initialize environmental sensor controller."""
        self.sensor = None
        self.enabled = config.bme690_enabled and BME690_AVAILABLE
        self.current_data = {
            'temperature': 0.0,
            'pressure': 0.0,
            'humidity': 0.0,
            'gas_resistance': 0.0,
            'air_quality_score': 0
        }
        
        if not self.enabled:
            logger.info("🌡️  Environmental sensor disabled")
            return
        
        try:
            self.sensor = bme680.BME680(i2c_addr=config.bme690_address)
            
            # Configure oversampling
            self.sensor.set_temperature_oversample(config.bme690_temperature_oversample)
            self.sensor.set_pressure_oversample(config.bme690_pressure_oversample)
            self.sensor.set_humidity_oversample(config.bme690_humidity_oversample)
            
            # Configure IIR filter
            self.sensor.set_filter(config.bme690_filter_size)
            
            # Configure gas sensing if enabled
            if config.bme690_gas_enabled:
                self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
                self.sensor.set_gas_heater_temperature(config.bme690_gas_heater_temperature)
                self.sensor.set_gas_heater_duration(config.bme690_gas_heater_duration)
            else:
                self.sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
            
            logger.info(f"🌡️  Environmental sensor initialized at I2C 0x{config.bme690_address:02X}")
            logger.info(f"⚙️  T:{config.bme690_temperature_oversample}x, P:{config.bme690_pressure_oversample}x, H:{config.bme690_humidity_oversample}x")
            if config.bme690_gas_enabled:
                logger.info(f"🔥 Gas heater: {config.bme690_gas_heater_temperature}°C for {config.bme690_gas_heater_duration}ms")
            
        except Exception as e:
            logger.error(f"❌ Environmental sensor initialization failed: {e}")
            logger.warning("🌡️  Continuing without environmental monitoring")
            self.enabled = False
    
    def read_environmental_data(self) -> dict:
        """Read environmental data from BME690.
        
        Returns:
            Dictionary with temperature, pressure, humidity, gas resistance, and air quality score
        """
        if not self.enabled or not self.sensor:
            return self.current_data
        
        try:
            if self.sensor.get_sensor_data():
                self.current_data.update({
                    'temperature': self.sensor.data.temperature,
                    'pressure': self.sensor.data.pressure,
                    'humidity': self.sensor.data.humidity,
                    'gas_resistance': self.sensor.data.gas_resistance if self.sensor.data.heat_stable else 0
                })
                
                # Calculate simple air quality score (0-100, higher is better)
                if self.sensor.data.heat_stable and config.bme690_gas_enabled:
                    # Simple scoring based on gas resistance (higher resistance = better air quality)
                    gas_res = self.sensor.data.gas_resistance
                    if gas_res > 200000:
                        air_quality = 90 + min(10, (gas_res - 200000) / 50000)  # Excellent (90-100)
                    elif gas_res > 100000:
                        air_quality = 70 + (gas_res - 100000) / 5000  # Good (70-90)
                    elif gas_res > 50000:
                        air_quality = 40 + (gas_res - 50000) / 2500  # Moderate (40-70)
                    elif gas_res > 10000:
                        air_quality = 10 + (gas_res - 10000) / 1334  # Poor (10-40)
                    else:
                        air_quality = max(0, gas_res / 1000)  # Very Poor (0-10)
                    
                    self.current_data['air_quality_score'] = int(air_quality)
                
                return self.current_data
                
        except Exception as e:
            logger.error(f"❌ Failed to read environmental sensor: {e}")
        
        return self.current_data
    
    def get_air_quality_description(self) -> str:
        """Get human-readable air quality description."""
        score = self.current_data['air_quality_score']
        if score >= 90:
            return "Excellent 🌟"
        elif score >= 70:
            return "Good 😊"
        elif score >= 40:
            return "Moderate 😐"
        elif score >= 10:
            return "Poor 😞"
        else:
            return "Very Poor ⚠️"

class LightSensorController:
    """Controls LTR-559 light sensor for adaptive brightness."""
    
    def __init__(self):
        """Initialize light sensor controller."""
        self.sensor = None
        self.current_lux = 0.0
        self.enabled = config.light_sensor_enabled and LTR559_AVAILABLE
        
        if not self.enabled:
            logger.info("💡 Light sensor disabled")
            return
        
        try:
            self.sensor = ltr559.LTR559()  # Use default initialization
            # Configure light sensor with correct parameters
            self.sensor.set_light_options(
                active=True,
                gain=config.light_sensor_gain
            )
            # Set measurement rate separately if available
            try:
                if hasattr(self.sensor, 'set_light_measurement_rate'):
                    self.sensor.set_light_measurement_rate(config.light_sensor_measurement_rate)
            except:
                logger.debug("🔧 Advanced light sensor configuration not available")
            
            logger.info(f"💡 Light sensor initialized with default I2C settings")
            logger.info(f"⚙️  Gain: {config.light_sensor_gain}, Rate: {config.light_sensor_measurement_rate}ms")
        except Exception as e:
            logger.error(f"❌ Light sensor initialization failed: {e}")
            logger.warning("💡 Continuing without adaptive brightness (static mode)")
            self.enabled = False
    
    def read_light_level(self) -> float:
        """Read current light level in lux.
        
        Returns:
            Light level in lux, or 0.0 if sensor unavailable
        """
        if not self.enabled or not self.sensor:
            return 0.0
        
        try:
            # Get light reading
            lux = self.sensor.get_lux()
            self.current_lux = lux
            return lux
        except Exception as e:
            logger.error(f"❌ Failed to read light sensor: {e}")
            return self.current_lux  # Return last known value
    
    def calculate_adaptive_brightness(self, lux: float, max_brightness: int) -> int:
        """Calculate adaptive brightness based on ambient light.
        
        Args:
            lux: Current light level in lux
            max_brightness: Maximum allowed brightness
            
        Returns:
            Calculated brightness value
        """
        if not config.adaptive_brightness_enabled:
            return max_brightness
        
        # Clamp lux to thresholds
        low_threshold = config.light_threshold_low
        high_threshold = config.light_threshold_high
        
        if lux <= low_threshold:
            # Very dark - use minimum brightness
            brightness = config.min_brightness
        elif lux >= high_threshold:
            # Very bright - use maximum brightness
            brightness = max_brightness
        else:
            # Linear interpolation between thresholds
            ratio = (lux - low_threshold) / (high_threshold - low_threshold)
            brightness = int(config.min_brightness + ratio * (max_brightness - config.min_brightness))
        
        # Ensure within bounds
        brightness = max(config.min_brightness, min(brightness, max_brightness))
        
        logger.debug(f"🌞 Adaptive brightness: {lux:.1f} lux → {brightness}/{max_brightness}")
        return brightness

class DisplayController:
    """Controls display brightness via Linux sysfs interface."""
    
    def __init__(self, brightness_path: Optional[str] = None):
        """Initialize display controller.
        
        Args:
            brightness_path: Path to brightness control file (uses config if None)
        """
        path = brightness_path or config.brightness_path
        self.brightness_path = self._find_brightness_path(path)
        self.max_brightness = self._get_max_brightness()
        self.current_brightness = self._get_current_brightness()
        
        logger.info(f"🖥️  Display controller initialized")
        logger.info(f"📁 Brightness path: {self.brightness_path}")
        logger.info(f"🔆 Max brightness: {self.max_brightness}")
        logger.info(f"💡 Current brightness: {self.current_brightness}")
    
    def _find_brightness_path(self, pattern: str) -> Path:
        """Find the actual brightness control path."""
        from glob import glob
        paths = glob(pattern)
        if not paths:
            # Try common alternatives
            alternatives = [
                "/sys/class/backlight/*/brightness",
                "/sys/class/backlight/rpi_backlight/brightness",
                "/sys/class/backlight/11-0045/brightness",  # Common for Waveshare displays
                "/sys/class/backlight/10-0045/brightness"
            ]
            for alt in alternatives:
                paths = glob(alt)
                if paths:
                    break
        
        if not paths:
            raise FileNotFoundError("❌ No brightness control found. Check display connections.")
        
        return Path(paths[0])
    
    def _get_max_brightness(self) -> int:
        """Get maximum brightness value."""
        max_path = self.brightness_path.parent / "max_brightness"
        try:
            return int(max_path.read_text().strip())
        except:
            return 255  # Default fallback
    
    def _get_current_brightness(self) -> int:
        """Get current brightness value."""
        try:
            return int(self.brightness_path.read_text().strip())
        except:
            return 0
    
    def set_brightness(self, value: int) -> bool:
        """Set display brightness (0-max_brightness).
        
        Args:
            value: Brightness value (0 = off, max_brightness = full)
            
        Returns:
            True if successful, False otherwise
        """
        value = max(0, min(value, self.max_brightness))
        try:
            self.brightness_path.write_text(str(value))
            self.current_brightness = value
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set brightness: {e}")
            return False
    
    async def fade_to(self, target: int, duration: float = 1.0, steps: Optional[int] = None) -> None:
        """Smoothly fade brightness to target value with easing optimized for 60Hz displays.
        
        Args:
            target: Target brightness (0-max_brightness)
            duration: Fade duration in seconds
            steps: Number of fade steps (uses config if None)
        """
        target = max(0, min(target, self.max_brightness))
        start = self.current_brightness
        
        if start == target:
            return
        
        # Use configured steps if not specified
        if steps is None:
            steps = config.fade_steps
        
        # Calculate step delay
        step_delay = duration / steps
        
        # For 60Hz displays, ensure we don't go faster than the refresh rate
        # but allow much smaller delays for ultra-smooth fades
        min_step_delay = (1000 / 60) / 1000 / 10  # 1.67ms (1/10th of refresh rate)
        if step_delay < min_step_delay:
            # Only reduce steps if we're going too fast for the hardware
            steps = int(duration / min_step_delay)
            step_delay = duration / steps
        
        logger.info(f"🎭 Fading brightness: {start} → {target} over {duration:.1f}s ({steps} steps, {step_delay*1000:.1f}ms/step)")
        
        # Use a more memory-efficient approach for the fade loop
        last_brightness = start
        
        for i in range(steps + 1):
            # Check for cancellation more thoroughly
            try:
                if asyncio.current_task().cancelled():
                    logger.debug("🚫 Fade task cancelled during loop")
                    return
            except AttributeError:
                # Handle case where current_task() might not be available
                pass
            
            # Use enhanced ease-in-out quintic function for ultra-smooth motion
            t = i / steps  # Progress from 0 to 1
            if config.fade_easing == 'quintic':
                # Quintic ease-in-out for even smoother motion than cubic
                if t < 0.5:
                    eased_t = 16 * t * t * t * t * t
                else:
                    eased_t = 1 - pow(-2 * t + 2, 5) / 2
            elif config.fade_easing == 'ease_in_out':
                # Enhanced cubic ease-in-out
                if t < 0.5:
                    eased_t = 4 * t * t * t
                else:
                    eased_t = 1 - pow(-2 * t + 2, 3) / 2
            elif config.fade_easing == 'linear':
                eased_t = t  # Linear progression
            else:
                # Default to ease_in_out
                if t < 0.5:
                    eased_t = 4 * t * t * t
                else:
                    eased_t = 1 - pow(-2 * t + 2, 3) / 2
            
            # Calculate brightness with sub-pixel precision and proper rounding
            brightness_float = start + (target - start) * eased_t
            brightness = int(round(brightness_float))
            
            # Only update if brightness actually changed (reduces I/O and flicker)
            if brightness != last_brightness:
                self.set_brightness(brightness)
                last_brightness = brightness
            
            if i < steps:  # Don't sleep after last step
                try:
                    await asyncio.sleep(step_delay)
                except asyncio.CancelledError:
                    logger.debug("🚫 Fade cancelled during sleep")
                    raise
        
        logger.info(f"✨ Fade complete: brightness = {self.current_brightness}")


class ProximityDetector:
    """Detects human presence using VL53L5CX sensor data."""
    
    def __init__(self, threshold_mm: Optional[int] = None, detection_zones: Optional[int] = None,
                 consecutive_required: Optional[int] = None, no_presence_required: Optional[int] = None):
        """Initialize proximity detector.
        
        Args:
            threshold_mm: Distance threshold in millimeters (uses config if None)
            detection_zones: Minimum number of zones that must detect proximity (uses config if None)
            consecutive_required: Consecutive detections required (uses config if None)
            no_presence_required: Consecutive non-detections required (uses config if None)
        """
        self.threshold_mm = threshold_mm or config.threshold_mm
        self.detection_zones = detection_zones or config.detection_zones
        self.consecutive_required = consecutive_required or config.consecutive_required
        self.no_presence_required = no_presence_required or config.no_presence_required
        
        self.consecutive_detections = 0
        self.no_presence_count = 0
        
        logger.info(f"🎯 Proximity detector initialized")
        logger.info(f"📏 Detection threshold: {self.threshold_mm}mm ({self.threshold_mm/10:.1f}cm)")
        logger.info(f"🔍 Required zones: {self.detection_zones}")
        logger.info(f"🔄 Consecutive detections required: {self.consecutive_required}")
        logger.info(f"⏳ No presence count required: {self.no_presence_required}")
    
    def analyze_distances(self, distances: List[int]) -> bool:
        """Analyze distance data to detect human presence.
        
        Args:
            distances: List of 64 distance measurements from 8x8 grid
            
        Returns:
            True if human presence detected, False otherwise
        """
        # Filter valid measurements within threshold
        close_distances = [
            d for d in distances 
            if 0 < d < self.threshold_mm
        ]
        
        # Check if enough zones detect close objects
        zones_detected = len(close_distances)
        presence_detected = zones_detected >= self.detection_zones
        
        # Apply consecutive detection filtering
        if presence_detected:
            self.consecutive_detections += 1
            self.no_presence_count = 0
            
            if self.consecutive_detections >= self.consecutive_required:
                logger.debug(f"👤 Presence detected: {zones_detected} zones < {self.threshold_mm}mm")
                return True
        else:
            self.consecutive_detections = 0
            self.no_presence_count += 1
            
            if self.no_presence_count >= self.no_presence_required:
                logger.debug(f"🚶 No presence: {zones_detected} zones < {self.threshold_mm}mm")
                return False
        
        # Return previous state if not enough consecutive readings
        return self.consecutive_detections >= self.consecutive_required


class ProximityDisplaySystem:
    """Main system combining sensor, detection, and display control."""
    
    def __init__(self):
        """Initialize the complete system."""
        self.running = False
        self.sensor: Optional[vl53l5cx.VL53L5CX] = None
        self.display = DisplayController()
        self.detector = ProximityDetector()
        self.light_sensor = LightSensorController()
        self.environmental_sensor = EnvironmentalSensorController()
        self.human_present = False
        self.frame_count = 0
        self._fading = False  # Track if display is currently fading
        self._fade_task: Optional[asyncio.Task] = None  # Track current fade task
        self.current_target_brightness = 0  # Track adaptive brightness target
        self._last_state_change = 0  # Track last presence state change time
        
        # Load timing configuration from config file
        self.fade_in_duration = config.fade_in_duration
        self.fade_out_duration = config.fade_out_duration
        self.update_interval = config.update_interval
        self.sensor_frequency = config.sensor_frequency
        
        logger.info("🚀 Proximity Display System initialized")
        logger.info(f"⚡ Fade in: {self.fade_in_duration}s, Fade out: {self.fade_out_duration}s")
        logger.info(f"🔄 Update interval: {self.update_interval}s ({1/self.update_interval:.1f} Hz)")
        logger.info(f"📡 Sensor frequency: {self.sensor_frequency} Hz")
        if self.light_sensor.enabled:
            logger.info(f"💡 Adaptive brightness enabled (range: {config.min_brightness}-{config.max_brightness_config})")
        else:
            logger.info("💡 Static brightness mode")
        if self.environmental_sensor.enabled:
            logger.info("🌡️  Environmental monitoring enabled")
        else:
            logger.info("🌡️  Environmental monitoring disabled")
    
    async def initialize_sensor(self) -> bool:
        """Initialize the VL53L5CX sensor.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Initializing VL53L5CX sensor...")
            
            if not config.vl53l5cx_enabled:
                logger.warning("⚠️  VL53L5CX sensor disabled in configuration")
                return False
            
            self.sensor = vl53l5cx.VL53L5CX()
            
            if not self.sensor.is_alive():
                logger.error("❌ Sensor not detected. Check I2C connections.")
                return False
            
            # Configure sensor with config values
            self.sensor.set_resolution(config.vl53l5cx_resolution)
            self.sensor.set_ranging_frequency_hz(config.vl53l5cx_frequency)
            
            # Set integration time and sharpener if available
            try:
                if hasattr(self.sensor, 'set_integration_time'):
                    self.sensor.set_integration_time(config.vl53l5cx_integration_time)
                if hasattr(self.sensor, 'set_sharpener_percent'):
                    self.sensor.set_sharpener_percent(config.vl53l5cx_sharpener)
            except:
                logger.debug("🔧 Advanced sensor configuration not available")
            
            self.sensor.start_ranging()
            
            logger.info("✅ Sensor initialized and ranging started")
            logger.info(f"⚙️  Resolution: {config.vl53l5cx_resolution} zones")
            logger.info(f"📡 Frequency: {config.vl53l5cx_frequency} Hz")
            logger.info(f"⏱️  Integration: {config.vl53l5cx_integration_time} ms")
            return True
            return True
            
        except Exception as e:
            logger.error(f"❌ Sensor initialization failed: {e}")
            return False
    
    async def run(self) -> None:
        """Main system loop with separated sensor and display tasks."""
        logger.info("🎯 Starting Proximity Display Control System")
        
        # Initialize sensor
        if not await self.initialize_sensor():
            return
        
        # Set initial display state (off)
        await self.display.fade_to(0, 0.5)
        
        self.running = True
        logger.info("✅ System running - monitoring for presence...")
        
        try:
            # Create separate tasks for sensor processing and light sensor
            tasks = [asyncio.create_task(self._sensor_loop())]
            
            # Add light sensor task if enabled
            if self.light_sensor.enabled:
                tasks.append(asyncio.create_task(self._light_sensor_loop()))
            
            # Add environmental sensor task if enabled
            if self.environmental_sensor.enabled:
                tasks.append(asyncio.create_task(self._environmental_sensor_loop()))
            
            # Run all tasks concurrently
            await asyncio.gather(*tasks)
                
        except asyncio.CancelledError:
            logger.info("🛑 System shutdown requested")
        except Exception as e:
            logger.error(f"❌ System error: {e}")
        finally:
            await self.shutdown()
    
    async def _sensor_loop(self):
        """Dedicated sensor processing loop that doesn't block on display fades."""
        logger.debug("🎯 Starting sensor loop")
        
        while self.running:
            try:
                if not self.sensor or not self.sensor.data_ready():
                    await asyncio.sleep(self.update_interval)
                    continue
                
                # Get sensor data
                data = self.sensor.get_data()
                distances = list(data.distance_mm[0])  # Extract distance array
                
                self.frame_count += 1
                
                # Detect presence
                presence_detected = self.detector.analyze_distances(distances)
                
                # Handle state changes with debouncing
                if presence_detected != self.human_present:
                    current_time = time.time()
                    # Add 200ms debounce to prevent rapid state changes
                    if current_time - self._last_state_change > 0.2:
                        self.human_present = presence_detected
                        self._last_state_change = current_time
                        
                        if self.human_present:
                            logger.info("🙋 Human presence detected - Waking display")
                            # Use adaptive brightness based on light level
                            target_brightness = self._get_adaptive_brightness()
                            # Start fade and track the task
                            self._fade_task = asyncio.create_task(self._fade_display(target_brightness, self.fade_in_duration))
                        else:
                            logger.info("🚶 Human left - Sleeping display")
                            # Start fade and track the task
                            self._fade_task = asyncio.create_task(self._fade_display(0, self.fade_out_duration))
                
                # Log periodic status
                if self.frame_count % 50 == 0:  # Every ~5 seconds at 10Hz
                    valid_readings = sum(1 for d in distances if 0 < d < 4000)
                    close_readings = sum(1 for d in distances if 0 < d < self.detector.threshold_mm)
                    
                    log_msg = (
                        f"📊 Frame {self.frame_count}: "
                        f"Valid={valid_readings}/64, "
                        f"Close={close_readings}, "
                        f"Present={self.human_present}, "
                        f"Brightness={self.display.current_brightness}"
                    )
                    
                    # Add light info if sensor is available
                    if self.light_sensor.enabled:
                        log_msg += f", Light={self.light_sensor.current_lux:.1f}lux"
                    
                    logger.info(log_msg)
                
                await asyncio.sleep(self.update_interval)
                    
            except Exception as e:
                logger.error(f"❌ Sensor loop error: {e}")
                await asyncio.sleep(1.0)  # Longer delay on error
    
    async def _light_sensor_loop(self):
        """Dedicated light sensor loop for adaptive brightness."""
        logger.debug("🌞 Starting light sensor loop")
        
        while self.running:
            try:
                # Read light level
                lux = self.light_sensor.read_light_level()
                
                # If human is present and adaptive brightness changed, update display
                if self.human_present:
                    new_target = self._get_adaptive_brightness()
                    if new_target != self.current_target_brightness:
                        old_target = self.current_target_brightness
                        self.current_target_brightness = new_target
                        logger.info(f"🌞 Light change: {lux:.1f} lux → brightness {old_target} → {new_target}")
                        # Smoothly adjust to new brightness
                        self._fade_task = asyncio.create_task(self._fade_display(new_target, 1.0))
                
                # Log light level periodically
                if self.frame_count % 100 == 0:  # Every ~10 seconds at 10Hz
                    logger.debug(f"🌞 Light level: {lux:.1f} lux, target brightness: {self.current_target_brightness}")
                
                await asyncio.sleep(config.light_sensor_update_interval)
                
            except Exception as e:
                logger.error(f"❌ Light sensor loop error: {e}")
                await asyncio.sleep(5.0)  # Longer delay on error
    
    async def _environmental_sensor_loop(self):
        """Dedicated environmental sensor loop for air quality monitoring."""
        logger.debug("🌡️  Starting environmental sensor loop")
        
        while self.running:
            try:
                # Read environmental data
                env_data = self.environmental_sensor.read_environmental_data()
                
                # Log environmental data periodically
                if self.frame_count % 150 == 0:  # Every ~15 seconds at 10Hz
                    temp = env_data['temperature']
                    pressure = env_data['pressure']
                    humidity = env_data['humidity']
                    gas_res = env_data['gas_resistance']
                    air_quality = env_data['air_quality_score']
                    air_desc = self.environmental_sensor.get_air_quality_description()
                    
                    logger.info(
                        f"🌡️  Environment: {temp:.1f}°C, {pressure:.1f}hPa, {humidity:.1f}%RH"
                    )
                    if config.bme690_gas_enabled and gas_res > 0:
                        logger.info(
                            f"🌬️  Air Quality: {air_quality}/100 ({air_desc}), Gas: {gas_res:.0f}Ω"
                        )
                
                await asyncio.sleep(config.bme690_update_interval)
                
            except Exception as e:
                logger.error(f"❌ Environmental sensor loop error: {e}")
                await asyncio.sleep(10.0)  # Longer delay on error
    
    def _get_adaptive_brightness(self) -> int:
        """Get current adaptive brightness based on light sensor."""
        if not self.light_sensor.enabled:
            return self.display.max_brightness
        
        lux = self.light_sensor.current_lux
        brightness = self.light_sensor.calculate_adaptive_brightness(lux, self.display.max_brightness)
        self.current_target_brightness = brightness
        return brightness
    
    async def _fade_display(self, target_brightness: int, duration: float):
        """Handle display fading without blocking sensor loop."""
        # Cancel any existing fade task first
        if self._fade_task and not self._fade_task.done():
            self._fade_task.cancel()
            try:
                await self._fade_task
            except asyncio.CancelledError:
                pass
            self._fade_task = None
        
        # Wait for any ongoing fade to complete before starting new one
        while self._fading:
            await asyncio.sleep(0.01)  # Small delay to avoid busy waiting
        
        try:
            self._fading = True
            await self.display.fade_to(target_brightness, duration)
        except asyncio.CancelledError:
            logger.debug("🚫 Fade cancelled")
            raise
        except Exception as e:
            logger.error(f"❌ Display fade error: {e}")
        finally:
            self._fading = False
    
    async def shutdown(self) -> None:
        """Clean shutdown of the system."""
        logger.info("🔄 Shutting down system...")
        
        self.running = False
        
        # Cancel any pending fade task
        if self._fade_task and not self._fade_task.done():
            self._fade_task.cancel()
            try:
                await self._fade_task
            except asyncio.CancelledError:
                pass
        
        # Stop sensor
        if self.sensor:
            try:
                self.sensor.stop_ranging()
                logger.info("🛑 Sensor stopped")
            except:
                pass
        
        # Turn off display
        try:
            await self.display.fade_to(0, 1.0)
            logger.info("🖥️  Display turned off")
        except:
            pass
        
        logger.info("✅ System shutdown complete")


async def main():
    """Main application entry point."""
    system = ProximityDisplaySystem()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}")
        system.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await system.run()
    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)