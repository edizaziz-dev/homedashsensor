"""
MQTT Publisher for Home Assistant integration.
Provides auto-discovery and real-time sensor data publishing.
"""
import json
import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import asdict
import paho.mqtt.client as mqtt
from config import MQTTConfig


class MQTTPublisher:
    """MQTT publisher for Home Assistant integration."""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client: Optional[mqtt.Client] = None
        self._connected = False
        
    async def initialize(self) -> bool:
        """Initialize MQTT connection."""
        try:
            self.client = mqtt.Client(client_id=self.config.client_id)
            
            # Set credentials if provided
            if self.config.username and self.config.password:
                self.client.username_pw_set(self.config.username, self.config.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            # Connect to broker
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.client.connect, 
                self.config.broker_host, 
                self.config.broker_port, 
                60
            )
            
            # Start loop in background
            self.client.loop_start()
            
            # Wait for connection
            for _ in range(50):  # 5 second timeout
                if self._connected:
                    break
                await asyncio.sleep(0.1)
            
            if self._connected:
                await self._publish_discovery_configs()
                self.logger.info("🌐 MQTT publisher initialized successfully")
                return True
            else:
                self.logger.error("Failed to connect to MQTT broker")
                return False
                
        except Exception as e:
            self.logger.error(f"MQTT initialization failed: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection."""
        if rc == 0:
            self._connected = True
            self.logger.info(f"🔗 Connected to MQTT broker at {self.config.broker_host}")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection."""
        self._connected = False
        self.logger.warning("🔌 Disconnected from MQTT broker")
    
    async def _publish_discovery_configs(self):
        """Publish Home Assistant discovery configurations."""
        device_info = {
            "identifiers": [self.config.device_id],
            "name": "HomeDashSensor",
            "model": "VL53L5CX Proximity Display Controller",
            "manufacturer": "HomeDashSensor"
        }
        
        # Proximity sensor discovery
        proximity_config = {
            "name": "HomeDash Proximity",
            "unique_id": f"{self.config.device_id}_proximity",
            "state_topic": f"{self.config.topic_prefix}/proximity/state",
            "device_class": "occupancy",
            "payload_on": "detected",
            "payload_off": "clear",
            "device": device_info
        }
        
        # Environment sensors discovery
        sensors = [
            ("temperature", "Temperature", "°C", "temperature"),
            ("humidity", "Humidity", "%", "humidity"),
            ("pressure", "Pressure", "hPa", "pressure"),
            ("distance", "Distance", "mm", None),
            ("lux", "Ambient Light", "lx", "illuminance"),
            ("display_brightness", "Display Brightness", "%", None)
        ]
        
        for sensor_id, name, unit, device_class in sensors:
            sensor_config = {
                "name": f"HomeDash {name}",
                "unique_id": f"{self.config.device_id}_{sensor_id}",
                "state_topic": f"{self.config.topic_prefix}/sensor/{sensor_id}",
                "unit_of_measurement": unit,
                "device": device_info
            }
            if device_class:
                sensor_config["device_class"] = device_class
            
            await self._publish(
                f"homeassistant/sensor/{self.config.device_id}_{sensor_id}/config",
                json.dumps(sensor_config),
                retain=True
            )
        
        # Binary sensor for proximity
        await self._publish(
            f"homeassistant/binary_sensor/{self.config.device_id}_proximity/config",
            json.dumps(proximity_config),
            retain=True
        )
    
    async def publish_proximity_state(self, human_present: bool, distance_mm: int):
        """Publish proximity detection state."""
        state = "detected" if human_present else "clear"
        await self._publish(f"{self.config.topic_prefix}/proximity/state", state)
        await self._publish(f"{self.config.topic_prefix}/sensor/distance", str(distance_mm))
    
    async def publish_environment_data(self, reading):
        """Publish environmental sensor data."""
        if reading:
            await self._publish(f"{self.config.topic_prefix}/sensor/temperature", f"{reading.temperature_c:.2f}")
            await self._publish(f"{self.config.topic_prefix}/sensor/humidity", f"{reading.humidity_percent:.2f}")
            await self._publish(f"{self.config.topic_prefix}/sensor/pressure", f"{reading.pressure_hpa:.2f}")
    
    async def publish_light_data(self, lux: float):
        """Publish ambient light data."""
        await self._publish(f"{self.config.topic_prefix}/sensor/lux", f"{lux:.2f}")
    
    async def publish_display_brightness(self, brightness_percent: int):
        """Publish current display brightness."""
        await self._publish(f"{self.config.topic_prefix}/sensor/display_brightness", str(brightness_percent))
    
    async def _publish(self, topic: str, payload: str, retain: bool = False):
        """Publish message to MQTT broker."""
        if not self._connected or not self.client:
            return
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.publish,
                topic,
                payload,
                1,  # QoS
                retain
            )
        except Exception as e:
            self.logger.error(f"Failed to publish to {topic}: {e}")
    
    async def cleanup(self):
        """Clean up MQTT connection."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()