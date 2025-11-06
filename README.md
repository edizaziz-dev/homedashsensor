# HomeDashSensor

HomeDashSensor is a proximity-based display controller for Raspberry Pi with Home Assistant integration. It uses a VL53L5CX ToF sensor to detect presence and a Waveshare display (via Linux backlight sysfs) to smoothly fade the screen in/out. Environmental data is monitored via BME690 and ambient light via LTR-559, with all sensor data published to Home Assistant via MQTT.

Simply put:
- Walk up to screen → it switches on  
- Walk away → it switches off
- All sensor data appears in Home Assistant automatically

The project includes comprehensive sensor monitoring and smart home integration, making it perfect for Home Assistant dashboards, kiosk displays, or any proximity-controlled screen application.

Main use case for me was that I wanted a full hd screen to run HomeAssistant in kiosk mode but didn't want a tablet on my wall and worry about lithium battery memory effects or going 💥.

My setup at the time of writing uses the following hardware (no affiliate links):
- Raspberry Pi 5 (to drive a Full HD screen via DSI @ 60Hz)
- [Waveshare POE hat](https://www.waveshare.com/wiki/PoE_HAT_(F))
- [Waveshare 13.3" Full HD Touchscreen](https://www.waveshare.com/wiki/13.3inch_DSI_LCD)
- [BME690 air quality, gas, temperature, pressure, humidity sensor](https://thepihut.com/products/bme690-4-in-1-air-quality-breakout-gas-temperature-pressure-humidity)
- [LTR599 light sensor](https://thepihut.com/products/ltr-559-light-proximity-sensor-breakout)
- [VL53L5CX Time of Flight Proximity Sensor](https://thepihut.com/products/vl53l5cx-8x8-time-of-flight-tof-array-sensor-breakout)

All the sensors use the I2C protocol and should be simple to wire up.

## Requirements
- Raspberry Pi (tested on recent Pi OS releases)
- Python 3.8+ (project currently runs under Python 3.11/3.13 in a virtualenv)
- Hardware:
  - VL53L5CX breakout (I2C address 0x29)
  - BME690 or compatible environmental sensor (optional)
  - LTR-559 ambient light sensor (optional)

## Quick setup
Open a terminal on the Pi and run the following from the project root (`/home/pi/apps/homedashsensor`):

```bash
# create and activate virtualenv (adjust python executable as needed)
python3 -m venv venv
source venv/bin/activate

# install pinned requirements (uses pinned bme690 GitHub release)
pip install --upgrade pip
pip install -r requirements.txt
```

Notes:
- The `requirements.txt` pins `bme690` to a tested tag. If you prefer a PyPI release, replace the `bme690` line with the desired version.
- On first run the VL53L5CX driver uploads firmware to the sensor which can take ~8–15 seconds. Expect the app to start slowly the first time.

## Run
With the venv activated:

```bash
python main.py
```

The program prints status logs; press Ctrl-C to stop. Logs include VL53 firmware upload, sensor initialization, and regular environment readings.

## Configuration
- `proximity_config.ini` contains proximity tuning, thresholds and device-specific settings.
- `config.py` reads configuration and provides typed dataclasses for use by sensor modules.

## Home Assistant Integration

HomeDashSensor includes built-in MQTT integration for Home Assistant with auto-discovery support.

### Setup MQTT Integration

1. **Enable MQTT in configuration:**
   Edit `proximity_config.ini` and update the `[MQTT]` section:
   ```ini
   [MQTT]
   enabled = true
   broker_host = your-home-assistant-ip
   broker_port = 1883
   username = your-mqtt-username
   password = your-mqtt-password
   topic_prefix = homedashsensor
   device_id = homedash_01
   client_id = homedashsensor_main
   ```

2. **Install MQTT dependency:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Available Sensors

The following entities will automatically appear in Home Assistant:

**Binary Sensors:**
- `binary_sensor.homedash_proximity` - Human presence detection

**Sensors:**
- `sensor.homedash_temperature` - Environment temperature (°C)
- `sensor.homedash_humidity` - Environment humidity (%)
- `sensor.homedash_pressure` - Environment pressure (hPa)
- `sensor.homedash_distance` - Distance to detected object (mm)
- `sensor.homedash_ambient_light` - Ambient light level (lx)
- `sensor.homedash_display_brightness` - Current display brightness (%)

### Example Automations

```yaml
# Turn on lights when someone approaches
automation:
  - alias: "HomeDash Presence Detected"
    trigger:
      platform: state
      entity_id: binary_sensor.homedash_proximity
      to: 'on'
    action:
      service: light.turn_on
      target:
        entity_id: light.hallway

# Notification for high temperature
automation:
  - alias: "HomeDash Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.homedash_temperature
      above: 30
    action:
      service: notify.mobile_app
      data:
        message: "High temperature detected: {{ states('sensor.homedash_temperature') }}°C"
```

## Troubleshooting
- I2C address confusion: the VL53L5CX address 0x29 is 41 in decimal. Both are equivalent; 0x29 is correct in most docs.
- If the display brightness changes fail, check permissions on `/sys/class/backlight/*/brightness`. You may need to add a udev rule or add your user to the `video` or `backlight` group depending on your distro.
- If environment readings fail immediately after sensor init, a short warm-up (0.5–1.0s) or a one-time read retry usually fixes it. See `sensors/environment_sensor.py` for the warm-up logic.

## Development notes
- The code is asyncio-based; blocking sensor calls are offloaded to executors where needed.
- If you make changes to sensor libraries, reinstall the venv packages and re-run the app.

## Contributing
Feel free to open issues or PRs. When changing hardware-related behaviour, include logs and any wiring/configuration details.

## TODOs
- ✅ ~~Expose values as entities for use in HomeAssistant~~ (Completed - MQTT integration with auto-discovery)
- Touchscreen interrupt when in use to prevent screen fadeouts (doesn't happen if you are standing in front of screen and sensor is looking directly at you)
- 3D printable bezel or bracket for sensor housing
- Wiring Diagram for sensors
- Add support for additional MQTT features (device triggers, commands)

## Features
- 🎯 **Proximity Detection** - VL53L5CX 8x8 ToF sensor for accurate human presence
- 🌡️ **Environmental Monitoring** - BME690 for temperature, humidity, pressure, and air quality
- 💡 **Adaptive Brightness** - LTR-559 ambient light sensor for automatic screen brightness
- 🖥️ **Smooth Display Control** - Configurable fade animations with multiple easing functions
- 🏠 **Home Assistant Integration** - MQTT auto-discovery with real-time sensor data
- ⚙️ **Flexible Configuration** - INI-based config with validation and type safety
- 📊 **Comprehensive Logging** - Structured logging with emojis for easy monitoring

**Made with ❤️ for the Raspberry Pi and Home Automation community**