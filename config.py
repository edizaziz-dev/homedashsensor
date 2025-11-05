"""
Configuration management for HomeDashSensor.
Single responsibility: Load and validate configuration from INI files.
"""
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VL53L5CXConfig:
    """VL53L5CX sensor configuration."""
    enabled: bool = True
    i2c_address: int = 0x29
    resolution: int = 64
    frequency_hz: int = 15
    integration_time: Optional[int] = None
    sharpener_percent: Optional[int] = None


@dataclass
class DetectionConfig:
    """Proximity detection configuration."""
    threshold_mm: int = 400
    detection_zones: int = 6
    consecutive_required: int = 3
    no_presence_required: int = 10


@dataclass
class DisplayConfig:
    """Display control configuration."""
    fade_in_duration: float = 2.0
    fade_out_duration: float = 3.0
    brightness_path: str = "/sys/class/backlight/*/brightness"
    adaptive_brightness_enabled: bool = True
    min_brightness: int = 0
    max_brightness: int = 255
    light_threshold_low: float = 10.0
    light_threshold_high: float = 500.0
    fade_duration: float = 1.0
    fade_steps: int = 600
    fade_easing: str = "quintic"
    
@dataclass
class EnvironmentSensorConfig:
    """Environment configuration."""
    enabled: bool = True
    i2c_address: int = 0x76
    i2c_bus: int = 1
    update_interval: float = 2.0
    temperature_oversample: int = 8
    pressure_oversample: int = 4
    humidity_oversample: int = 2
    gas_enabled: bool = False
    gas_heater_temp: int = 320
    gas_heater_duration: int = 150
    filter_size: int = 3
    location: str = "indoor"
    temperature_unit: str = "Celsius"


@dataclass
class SystemConfig:
    """System-wide configuration."""
    update_interval: float = 0.1
    sensor_frequency: int = 15
    log_level: str = "INFO"
    
@dataclass
class LightSensorConfig:
    """Ambient light sensor configuration."""
    enabled: bool = True
    i2c_address: int = 0x23
    i2c_bus: int = 1
    update_interval: float = 2.0
    gain: int = 1
    integration_time: int = 100
    measurement_rate: int = 500


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_file: str = "proximity_config.ini"):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self._config = configparser.ConfigParser()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        self._config.read(self.config_file)
        
        # Validate required sections
        required_sections = ["VL53L5CX", "Detection", "Display", "System"]
        missing = [s for s in required_sections if s not in self._config.sections()]
        if missing:
            raise ValueError(f"Missing configuration sections: {missing}")
    
    def get_vl53l5cx_config(self) -> VL53L5CXConfig:
        """Get VL53L5CX sensor configuration."""
        section = self._config["VL53L5CX"]
        return VL53L5CXConfig(
            enabled=section.getboolean("enabled", True),
            i2c_address=int(section.get("i2c_address", "0x29"), 16),
            resolution=section.getint("resolution", 64),
            frequency_hz=section.getint("frequency_hz", 15),
            integration_time=section.getint("integration_time", fallback=None) if section.get("integration_time", None) else None,
            sharpener_percent=section.getint("sharpener_percent", fallback=None) if section.get("sharpener_percent", None) else None
        )
    
    def get_detection_config(self) -> DetectionConfig:
        """Get proximity detection configuration."""
        section = self._config["Detection"]
        return DetectionConfig(
            threshold_mm=section.getint("threshold_mm", 400),
            detection_zones=section.getint("detection_zones", 6),
            consecutive_required=section.getint("consecutive_required", 3),
            no_presence_required=section.getint("no_presence_required", 10)
        )
    
    def get_display_config(self) -> DisplayConfig:
        """Get display control configuration."""
        section = self._config["Display"]
        return DisplayConfig(
            fade_in_duration=section.getfloat("fade_in_duration", 2.0),
            fade_out_duration=section.getfloat("fade_out_duration", 3.0),
            brightness_path=section.get("brightness_path", "/sys/class/backlight/*/brightness"),
            adaptive_brightness_enabled=section.getboolean("adaptive_brightness_enabled", True),
            min_brightness=section.getint("min_brightness", 0),
            max_brightness=section.getint("max_brightness", 255),
            light_threshold_low=section.getfloat("light_threshold_low", 10.0),
            light_threshold_high=section.getfloat("light_threshold_high", 500.0),
            fade_duration=section.getfloat("fade_duration", 1.0),
            fade_steps=section.getint("fade_steps", 600),
            fade_easing=section.get("fade_easing", "quintic")
        )
    
    def get_system_config(self) -> SystemConfig:
        """Get system-wide configuration."""
        section = self._config["System"]
        return SystemConfig(
            update_interval=section.getfloat("update_interval", 0.1),
            sensor_frequency=section.getint("sensor_frequency", 15),
            log_level=section.get("log_level", "INFO")
        )
        
    def get_lux_config(self) -> LightSensorConfig:
        """Get ambient light sensor configuration."""
        section = self._config["LightSensor"]
        return LightSensorConfig(
            enabled=section.getboolean("enabled", True),
            i2c_address=int(section.get("i2c_address", "0x23"), 16),
            i2c_bus=section.getint("i2c_bus", 1),
            update_interval=section.getfloat("update_interval", 2.0),
            gain=section.getint("gain", 1),
            integration_time=section.getint("integration_time", 100),
            measurement_rate=section.getint("measurement_rate", 500)
        )
    
    def get_environment_sensor_config(self) -> EnvironmentSensorConfig:
        """Get environment sensor configuration."""
        section = self._config["EnvironmentSensor"]
        return EnvironmentSensorConfig(
            enabled=section.getboolean("enabled", True),
            i2c_address=int(section.get("i2c_address", "0x76"), 16),
            i2c_bus=section.getint("i2c_bus", 1),
            update_interval=section.getfloat("update_interval", 2.0),
            temperature_oversample=section.getint("temperature_oversample", 8),
            pressure_oversample=section.getint("pressure_oversample", 4),
            humidity_oversample=section.getint("humidity_oversample", 2),
            gas_enabled=section.getboolean("gas_enabled", False),
            gas_heater_temp=section.getint("gas_heater_temp", 320),
            gas_heater_duration=section.getint("gas_heater_duration", 150),
            filter_size=section.getint("filter_size", 3),
            location=section.get("location", "indoor"),
            temperature_unit=section.get("temperature_unit", "Celsius")
        )