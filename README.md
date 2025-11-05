# HomeDashboard

HomeDashboard is a proximity-based display controller for Raspberry Pi. It uses a VL53L5CX ToF sensor to detect presence and a Waveshare display (via Linux backlight sysfs) to smoothly fade the screen in/out. 

Simply put:
I walk up to screen, it switches on. 
I walk away, it switches off.

The project is far from perfect but this README contains quick setup and run steps for a Raspberry Pi development environment.

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
- Expose values as entities for use in HomeAssistant.
- Touchscreen interrupt when in use to prevent screen fadeouts (doesn't happen if you are standing in front of screen and sensor is looking directly at you)
- 3D printable bezel or bracket for sensor housing
- Wiring Diagram for sensors

**Made with ❤️ for the Raspberry Pi and Home Automation community**