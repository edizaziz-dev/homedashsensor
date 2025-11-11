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

## Automatic Startup Service

HomeDashSensor can be configured to start automatically on boot using systemd.

### Service Installation

```bash
# Navigate to project directory
cd /home/pi/apps/homedashsensor

# Install the service for automatic startup
./service-control.sh install

# Start the service immediately
./service-control.sh start
```

### Service Management

The `service-control.sh` script provides easy service management:

```bash
# Service control commands
./service-control.sh start       # Start the service
./service-control.sh stop        # Stop the service
./service-control.sh restart     # Restart the service
./service-control.sh status      # Show service status
./service-control.sh logs        # View recent logs
./service-control.sh logs-live   # Watch live logs (Ctrl+C to exit)
./service-control.sh uninstall   # Remove service from system
```

### Service Benefits

- **🔄 Auto-start** - Starts automatically when Pi boots
- **🔧 Easy management** - Simple start/stop commands
- **📋 System logging** - All output goes to systemd journal
- **🛡️ Process monitoring** - Automatic restart on crashes
- **👤 User permissions** - Runs as pi user with proper permissions

Once installed, HomeDashSensor will start automatically every time your Raspberry Pi boots, ensuring continuous monitoring without manual intervention.

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

## Restoring True Multitouch on Raspberry Pi 5 with TouchKio

I use this in conjunction with the brilliant [TouchKio](https://github.com/leukipp/touchkio) which allows your Pi to run HA in kiosk mode however if like this project you are using a display other than the official raspberry pi screen, you will likely encounter multi-touch disabled and you will need to use the instructions below which was generated by ChatGPT. Step 3B worked for me after disabling the mouse emulation in control panel on the Pi. At the time of writing, this worked with TouchKio 1.4.0.

### Overview
If your touchscreen only registers one touch at a time (or shows a grey cursor) after installing **[TouchKio](https://github.com/leukipp/touchkio)** via the "easy-way" script, it’s likely that:

1. Raspberry Pi OS was set to **Mouse Emulation** mode, and  
2. TouchKio’s Electron runtime was still forcing **mouse-based touch emulation**.

This guide restores proper multitouch behavior.

---

#### Step 1 — Check the Touch Mode in Raspberry Pi OS

1. On the desktop, open **Screen Configuration**.  
2. Right-click your display → **Touchscreen → Mode → Multitouch**.  
3. If it was on *Mouse Emulation*, change it and reboot.

---

#### Step 2 — Update TouchKio (optional but recommended)

TouchKio frequently adds touch fixes. Run:
```bash
bash <(wget -qO- https://raw.githubusercontent.com/leukipp/touchkio/main/install.sh) update
systemctl --user restart touchkio.service
```

---

#### Step 3 — Disable Electron’s Mouse Emulation in TouchKio

This step removes the internal Electron setting that converts touch input into single-pointer mouse events.  
Depending on how TouchKio was installed, your system will have either `app.asar` or an unpacked `app/` folder inside `/usr/lib/touchkio/resources/`.

#### Option A — If you see `app.asar`

1. **Inspect the folder:**
   ```bash
   ls -l /usr/lib/touchkio/resources
   ```
   If you see `app.asar`, follow these steps.

2. **Back up and unpack:**
   ```bash
   cd /usr/lib/touchkio/resources
   sudo cp app.asar app.asar.bak
   sudo apt-get update && sudo apt-get install -y nodejs npm
   sudo npx asar extract app.asar app_unpacked
   ```

3. **Remove the emulation line:**
   ```bash
   sudo grep -n "setEmitTouchEventsForMouse" -R app_unpacked/*.js || true
   sudo sed -i 's/Emulation\.setEmitTouchEventsForMouse[^;]*;//' app_unpacked/index.js
   ```

4. **Repack and restart:**
   ```bash
   sudo npx asar pack app_unpacked app.asar
   systemctl --user restart touchkio.service
   ```

#### Option B — If you see an unpacked `app/` folder

1. **Navigate to the app folder:**
   ```bash
   cd /usr/lib/touchkio/resources/app
   ```

2. **Back up the main file:**
   ```bash
   sudo cp index.js index.js.bak
   ```

3. **Remove the emulation line:**
   ```bash
   sudo sed -i 's/Emulation\.setEmitTouchEventsForMouse[^;]*;//' index.js
   ```

4. **Restart TouchKio:**
   ```bash
   systemctl --user restart touchkio.service
   ```

---

#### Step 4 — Test

After restart:
- Try **two-finger scroll** or **pinch-zoom** in the dashboard.  
- The grey circle cursor should be gone.  
- True multitouch gestures should now work.

---

#### Notes

- Installed binary location: `/usr/bin/touchkio`
- User service: `~/.config/systemd/user/touchkio.service`
- Logs: `journalctl --user -u touchkio.service -f`
- To revert the change:  
  ```bash
  sudo mv /usr/lib/touchkio/resources/app/index.js.bak           /usr/lib/touchkio/resources/app/index.js
  systemctl --user restart touchkio.service
  ```

---

#### Result

After switching the OS to **Multitouch** mode and applying either *Option A* or *Option B*, the Raspberry Pi 5 touchscreen now supports full multitouch input within TouchKio.

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