# HomeDashSensor# HomeDashSensor 🎯# HomeDashSensor 🎯# VL53L5CX ToF Sensor Test



Smart display control using proximity sensors on Raspberry Pi.



## What it does**Advanced proximity-based display control system for Raspberry Pi with ultra-smooth 60Hz fading**



Automatically turns your display on/off when you approach or leave. Uses multiple sensors for brightness control and environmental monitoring.



## Hardware neededA sophisticated multi-sensor system that automatically controls display brightness based on human presence detection, ambient light levels, and environmental conditions. Features professional-grade fade animations optimized for high refresh rate displays.**Advanced proximity-based display control system for Raspberry Pi with ultra-smooth 60Hz fading**A simple test program for the VL53L5CX 8x8 Time of Flight (ToF) array sensor.



- Raspberry Pi (any model with I2C)

- VL53L5CX proximity sensor (required)

- LTR-559 light sensor (optional - for auto brightness)## ✨ Features

- BME690 environmental sensor (optional - for air quality)



## Wiring

### 🎯 **Precision Proximity Detection**A sophisticated multi-sensor system that automatically controls display brightness based on human presence detection, ambient light levels, and environmental conditions. Features professional-grade fade animations optimized for high refresh rate displays.## Hardware Setup

Connect all sensors to I2C:

- VCC → 3.3V- **VL53L5CX 8x8 ToF Sensor** - 64-zone time-of-flight detection with millimeter precision

- GND → Ground  

- SDA → GPIO 2- **Configurable thresholds** - Adjustable detection distance (default: 400mm)

- SCL → GPIO 3

- **Multi-zone filtering** - Requires multiple zones for reliable detection

## Setup

- **Consecutive detection logic** - Prevents false triggers from sensor noise## ✨ Features### Connections (Pi 5)

```bash

# Enable I2C

sudo raspi-config

# Interface Options → I2C → Enable### 🎭 **Ultra-Smooth Display Control**Connect the VL53L5CX sensor to your Raspberry Pi:



# Install- **600-step fade animations** - Optimized for 60Hz displays (3.3ms per step)

git clone https://github.com/edizaziz-dev/homedashsensor.git

cd homedashsensor- **Quintic ease-in-out curves** - Imperceptible transitions with professional smoothness### 🎯 **Precision Proximity Detection**

python3 -m venv venv

source venv/bin/activate- **Frame-rate synchronized** - Aligned to display refresh cycles for perfect motion

pip install -r requirements.txt

- **Task management** - Prevents overlapping fades with proper cancellation- **VL53L5CX 8x8 ToF Sensor** - 64-zone time-of-flight detection with millimeter precision```

# Test sensors

python test_vl53l5cx.py



# Run### 🌞 **Adaptive Brightness**- **Configurable thresholds** - Adjustable detection distance (default: 400mm)VL53L5CX    →    Raspberry Pi

python proximity_display_control.py

```- **LTR-559 Light Sensor** - Automatic brightness adjustment based on ambient light



## Configuration- **Configurable thresholds** - 10-500 lux range with linear interpolation- **Multi-zone filtering** - Requires multiple zones for reliable detectionVCC         →    3.3V (Pin 1) or 5V (Pin 2)



Edit `proximity_config.ini` to adjust:- **Real-time adaptation** - Smooth transitions when lighting conditions change

- Detection distance (default 400mm)

- Brightness levels - **Manual override** - Can be disabled for static brightness mode- **Consecutive detection logic** - Prevents false triggers from sensor noiseGND         →    GND (Pin 6)

- Fade speed

- Sensor settings



## Troubleshooting### 🌡️ **Environmental Monitoring**SDA         →    GPIO 2 / SDA (Pin 3)



**Sensor not found:**- **BME690 4-in-1 Sensor** - Temperature, pressure, humidity, and air quality

```bash

sudo i2cdetect -y 1- **Gas resistance measurement** - Air quality scoring (0-100 scale)### 🎭 **Ultra-Smooth Display Control**SCL         →    GPIO 3 / SCL (Pin 5)

# Should show 0x29 for VL53L5CX

```- **Configurable sampling** - Adjustable oversampling and heating parameters



**Brightness control not working:**- **Comprehensive logging** - Periodic environmental data reporting- **600-step fade animations** - Optimized for 60Hz displays (3.3ms per step)```

```bash

sudo usermod -a -G video $USER

# Then logout/login

```### ⚙️ **Professional Configuration**- **Quintic ease-in-out curves** - Imperceptible transitions with professional smoothness



That's it. Simple proximity-based display control.- **INI-based configuration** - Comprehensive settings for all devices and behaviors

- **Inline comment support** - Clean configuration parsing with comment handling- **Frame-rate synchronized** - Aligned to display refresh cycles for perfect motion### I2C Configuration

- **Hot-reload capability** - Runtime configuration updates

- **Extensive validation** - Built-in configuration checking and status reporting- **Task management** - Prevents overlapping fades with proper cancellationThe sensor uses I2C address `0x29`. Ensure I2C is enabled:



## 🔧 Hardware Requirements



### **Core Components**### 🌞 **Adaptive Brightness**```bash

- **Raspberry Pi** (any model with I2C support)

- **VL53L5CX 8x8 ToF Sensor** (I2C address: 0x29)- **LTR-559 Light Sensor** - Automatic brightness adjustment based on ambient lightsudo raspi-config

- **Display with brightness control** (via Linux sysfs)

- **Configurable thresholds** - 10-500 lux range with linear interpolation# Navigate to: Interface Options → I2C → Enable

### **Optional Sensors**

- **LTR-559 Light Sensor** (I2C address: 0x23) - For adaptive brightness- **Real-time adaptation** - Smooth transitions when lighting conditions change```

- **BME690 Environmental Sensor** (I2C address: 0x76) - For air quality monitoring

- **Manual override** - Can be disabled for static brightness mode

### **Wiring Guide**

## Software Setup

```

VL53L5CX ToF Sensor:### 🌡️ **Environmental Monitoring**

├── VCC → 3.3V

├── GND → Ground- **BME690 4-in-1 Sensor** - Temperature, pressure, humidity, and air quality### 1. Install Dependencies

├── SDA → GPIO 2 (I2C SDA)

└── SCL → GPIO 3 (I2C SCL)- **Gas resistance measurement** - Air quality scoring (0-100 scale)```bash



LTR-559 Light Sensor (Optional):- **Configurable sampling** - Adjustable oversampling and heating parameters# Install the VL53L5CX Python library

├── VCC → 3.3V

├── GND → Ground- **Comprehensive logging** - Periodic environmental data reportingpip install vl53l5cx-python numpy

├── SDA → GPIO 2 (I2C SDA)

└── SCL → GPIO 3 (I2C SCL)



BME690 Environmental Sensor (Optional):### ⚙️ **Professional Configuration**# Or install from requirements.txt

├── VCC → 3.3V

├── GND → Ground- **INI-based configuration** - Comprehensive settings for all devices and behaviorspip install -r requirements.txt

├── SDA → GPIO 2 (I2C SDA)

└── SCL → GPIO 3 (I2C SCL)- **Inline comment support** - Clean configuration parsing with comment handling```

```

- **Hot-reload capability** - Runtime configuration updates

## 🚀 Quick Start

- **Extensive validation** - Built-in configuration checking and status reporting### 2. Test I2C Connection

### **1. System Preparation**

```bash```bash

# Enable I2C interface

sudo raspi-config## 🔧 Hardware Requirements# Check if sensor is detected

# Navigate to: Interface Options → I2C → Enable

sudo i2cdetect -y 1

# Install system dependencies

sudo apt update### **Core Components**

sudo apt install python3-pip python3-venv git i2c-tools

```- **Raspberry Pi** (any model with I2C support)# You should see "29" in the output grid



### **2. Installation**- **VL53L5CX 8x8 ToF Sensor** (I2C address: 0x29)```

```bash

# Clone the repository- **Display with brightness control** (via Linux sysfs)

git clone https://github.com/edizaziz-dev/homedashsensor.git

cd homedashsensor### 3. Run the Test Program



# Create virtual environment### **Optional Sensors**```bash

python3 -m venv venv

source venv/bin/activate- **LTR-559 Light Sensor** (I2C address: 0x23) - For adaptive brightnesspython test_vl53l5cx.py



# Install dependencies- **BME690 Environmental Sensor** (I2C address: 0x76) - For air quality monitoring```

pip install -r requirements.txt



# Verify hardware detection

python check_install.py### **Wiring Guide**## What the Test Does

```

```

### **3. Configuration**

```bashVL53L5CX ToF Sensor:The test program will:

# Check current configuration status

python check_config.py├── VCC → 3.3V



# Edit configuration file (optional)├── GND → Ground1. 🔄 Initialize the VL53L5CX sensor

nano proximity_config.ini

```├── SDA → GPIO 2 (I2C SDA)2. ✅ Verify the sensor is responsive



### **4. Testing Individual Components**└── SCL → GPIO 3 (I2C SCL)3. 🚀 Configure for 8x8 ranging mode

```bash

# Test VL53L5CX proximity sensor4. 📡 Start continuous distance measurements

python test_vl53l5cx.py

LTR-559 Light Sensor (Optional):5. � Display real-time 8x8 distance grid

# Test LTR-559 light sensor (if connected)

python test_ltr559.py├── VCC → 3.3V6. 📈 Show min/max/average distance statistics



# Test BME690 environmental sensor (if connected)├── GND → Ground

python test_bme690.py

├── SDA → GPIO 2 (I2C SDA)## Expected Output

# Test display fade performance

python test_smooth_fade.py└── SCL → GPIO 3 (I2C SCL)

```

```

### **5. Run the Main System**

```bashBME690 Environmental Sensor (Optional):🎯 VL53L5CX 8x8 ToF Sensor Test

# Run in foreground (with detailed logging)

python proximity_display_control.py├── VCC → 3.3V========================================



# Run in background├── GND → Ground🔄 Initializing VL53L5CX sensor...

nohup python proximity_display_control.py > sensor.log 2>&1 &

```├── SDA → GPIO 2 (I2C SDA)✅ Sensor detected and responsive!



## ⚙️ Configuration Reference└── SCL → GPIO 3 (I2C SCL)� Starting sensor initialization...



The system uses `proximity_config.ini` for comprehensive configuration. Here are the key sections:```📡 Ranging started!



### **VL53L5CX Proximity Detection**

```ini

[VL53L5CX]## 🚀 Quick StartPress Ctrl+C to stop...

i2c_address = 0x29

frequency_hz = 15

proximity_threshold_mm = 400

min_zones_required = 3### **1. System Preparation**📊 Frame #1

consecutive_detections_required = 2

max_range_mm = 4000```bash

```

# Enable I2C interface8x8 Distance Grid (mm):

### **Display Control**

```inisudo raspi-config+--------------------------------------------------+

[Display]

brightness_path = /sys/class/backlight/11-0045/brightness# Navigate to: Interface Options → I2C → Enable|  1234  1245  1256  1267  1278  1289  1290  1301 |

min_brightness = 20

max_brightness = 255|  1312  1323  1334  1345  1356  1367  1378  1389 |

fade_duration_seconds = 2.0

fade_steps = 600# Install system dependencies|  1400  1411  1422  1433  1444  1455  1466  1477 |

fade_algorithm = quintic_ease_in_out

```sudo apt update|  1488  1499  1510  1521  1532  1543  1554  1565 |



### **LTR-559 Light Sensor**sudo apt install python3-pip python3-venv git i2c-tools|  1576  1587  1598  1609  1620  1631  1642  1653 |

```ini

[LightSensor]```|  1664  1675  1686  1697  1708  1719  1730  1741 |

enabled = true

i2c_address = 0x23|  1752  1763  1774  1785  1796  1807  1818  1829 |

min_lux_threshold = 10

max_lux_threshold = 500### **2. Installation**|  1840  1851  1862  1873  1884  1895  1906  1917 |

update_interval_seconds = 1.0

``````bash+--------------------------------------------------+



### **BME690 Environmental Sensor**# Clone the repository

```ini

[BME690]git clone https://github.com/edizaziz-dev/homedashsensor.git📈 Stats: Min=1234mm, Max=1917mm, Avg=1575.5mm

enabled = true

i2c_address = 0x76cd homedashsensor🎯 Valid readings: 64/64

update_interval_seconds = 10.0

temperature_oversampling = 8```

pressure_oversampling = 4

humidity_oversampling = 2# Create virtual environment

```

python3 -m venv venv## Sensor Specifications

## 🔍 Advanced Usage

source venv/bin/activate

### **Performance Optimization**

The system is optimized for 60Hz displays with 600-step fade animations. Key parameters:- **Field of View**: 63° diagonal

- **Frame timing**: 3.33ms per step (aligned to 60Hz refresh)

- **Fade algorithm**: Quintic ease-in-out for imperceptible motion# Install dependencies- **Range**: 2cm to 4 meters

- **Task management**: Prevents overlapping fades with proper cancellation

pip install -r requirements.txt- **Resolution**: 8x8 array (64 zones)

### **Debugging and Monitoring**

```bash- **Update Rate**: Up to 60Hz

# Monitor system logs in real-time

tail -f sensor.log# Verify hardware detection- **Interface**: I2C (address 0x29)



# Check sensor detectionpython check_install.py- **Accuracy**: ±3% typical

sudo i2cdetect -y 1

```

# Verify brightness control permissions

ls -la /sys/class/backlight/*/brightness## Troubleshooting



# Test fade performance### **3. Configuration**

python test_fade_performance.py

``````bash### Sensor Not Detected



### **Service Installation**# Check current configuration```

```bash

# Create systemd servicepython check_config.py❌ Sensor not detected. Check connections!

sudo nano /etc/systemd/system/homedashsensor.service

```

# Service content:

[Unit]# Edit configuration if needed- Verify wiring connections

Description=HomeDashSensor Display Control

After=multi-user.targetnano proximity_config.ini- Check I2C is enabled: `sudo raspi-config`



[Service]```- Test I2C: `sudo i2cdetect -y 1`

Type=simple

User=pi- Ensure 3.3V/5V power supply

WorkingDirectory=/home/pi/apps/homedashsensor

Environment=PATH=/home/pi/apps/homedashsensor/venv/bin### **4. Testing**

ExecStart=/home/pi/apps/homedashsensor/venv/bin/python proximity_display_control.py

Restart=always```bash### Import Error



[Install]# Test individual sensors```

WantedBy=multi-user.target

python test_vl53l5cx.py      # ToF sensor❌ VL53L5CX library not installed!

# Enable and start service

sudo systemctl enable homedashsensor.servicepython test_ltr559.py        # Light sensor (if connected)```

sudo systemctl start homedashsensor.service

```python test_bme690.py        # Environmental sensor (if connected)- Install library: `pip install vl53l5cx-python`



## 🛠️ Troubleshooting- Check Python environment



### **Common Issues**# Test display control



**Sensor not detected:**python test_smooth_fade.py   # Fade performance### Permission Error

```bash

# Check I2C bus- Try with sudo: `sudo python test_vl53l5cx.py`

sudo i2cdetect -y 1

# Should show devices at 0x29 (VL53L5CX), 0x23 (LTR-559), 0x76 (BME690)# Test complete system- Add user to i2c group: `sudo usermod -a -G i2c pi`



# Check I2C permissionspython proximity_display_control.py

sudo usermod -a -G i2c $USER

# Logout and login again```## Next Steps

```



**Brightness control not working:**

```bash## 📋 ConfigurationOnce the test is working:

# Check brightness file exists

ls -la /sys/class/backlight/*/brightness1. Experiment with different ranging frequencies (1-60Hz)



# Test write permissionsThe system uses `proximity_config.ini` for comprehensive configuration:2. Try 4x4 mode for faster updates: `sensor.set_resolution(4*4)`

echo 128 | sudo tee /sys/class/backlight/*/brightness

3. Add motion detection algorithms

# Add user to video group

sudo usermod -a -G video $USER### **Key Settings**4. Integrate with display/LED feedback

```

```ini5. Build proximity detection system

**Fade appears stuttery:**

- Increase `fade_steps` in configuration (try 800-1000 for very high refresh displays)[Detection]

- Verify system isn't under high CPU load

- Check if other processes are controlling brightnessthreshold_mm = 400              # Detection distance (400mm = 40cm)```bash



### **Performance Monitoring**detection_zones = 4             # Minimum zones required# Add udev rule for brightness control

```bash

# Check system resource usageconsecutive_required = 2        # Consecutive detections neededsudo tee /etc/udev/rules.d/99-backlight.rules << EOF

htop

no_presence_required = 10       # Frames to confirm absenceSUBSYSTEM=="backlight", ACTION=="add", RUN+="/bin/chgrp video %S%p/brightness", RUN+="/bin/chmod g+w %S%p/brightness"

# Monitor I2C traffic

sudo apt install i2c-toolsEOF

watch -n 1 'sudo i2cdetect -y 1'

[Display]

# Test sensor update rates

python debug_vl53l5cx.pyfade_in_duration = 2.0          # Wake fade duration (seconds)# Add user to video group

```

fade_out_duration = 3.0         # Sleep fade duration (seconds)sudo usermod -a -G video $USER

## 📋 Hardware Specifications

fade_steps = 600                # Fade smoothness (600 = 60Hz optimized)

### **VL53L5CX ToF Sensor**

- **Resolution**: 8x8 array (64 zones)fade_easing = quintic           # Motion curve (quintic/ease_in_out/linear)# Reload udev rules

- **Range**: 2cm to 4 meters

- **Field of View**: 63° diagonaladaptive_brightness_enabled = truesudo udevadm control --reload-rules

- **Update Rate**: Up to 60Hz

- **Interface**: I2C (address 0x29)min_brightness = 20             # Minimum display brightnesssudo udevadm trigger

- **Accuracy**: ±3% typical

max_brightness = 255            # Maximum display brightness```

### **LTR-559 Light Sensor**

- **Light Range**: 0.01 to 64,000 lux

- **Proximity Range**: 0 to 100mm

- **Interface**: I2C (address 0x23)[LightSensor]### 4. Configure Sensor Port

- **Resolution**: 16-bit light, 11-bit proximity

enabled = true                  # Enable adaptive brightness

### **BME690 Environmental Sensor**

- **Temperature**: -40°C to +85°C (±1°C accuracy)light_threshold_low = 10.0      # Dark threshold (lux)Edit the sensor port in `main.py` if needed:

- **Pressure**: 300-1100 hPa (±0.12 hPa accuracy)

- **Humidity**: 0-100% RH (±3% accuracy)light_threshold_high = 500.0    # Bright threshold (lux)

- **Gas Sensor**: VOC detection for air quality

- **Interface**: I2C (address 0x76)``````python



## 📜 License# Update this line with your sensor's serial port



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.See `PROXIMITY_USAGE.md` for complete configuration reference.sensor = LD2450(port='/dev/ttyUSB0')  # or /dev/ttyAMA0 for GPIO UART



## 🤝 Contributing```



1. Fork the repository## 🎭 Performance & Optimization

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

3. Commit your changes (`git commit -m 'Add amazing feature'`)## 🚀 Usage

4. Push to the branch (`git push origin feature/amazing-feature`)

5. Open a Pull Request### **60Hz Display Optimization**



## 🙏 Acknowledgments- **600 fade steps** provide 3.3ms transitions (imperceptible on 60Hz displays)### Basic Usage



- VL53L5CX library contributors for ToF sensor integration- **Quintic easing** delivers professional motion curves

- CircuitPython community for sensor driver inspiration

- Raspberry Pi Foundation for excellent hardware documentation- **Frame synchronization** eliminates visual artifacts```bash

- **Memory efficiency** prevents performance degradation over timecd homedashsensor

python main.py

### **System Performance**```

- **Async architecture** - Non-blocking sensor loops with concurrent processing

- **Task management** - Proper cancellation and cleanup prevents memory leaks### Configuration Options

- **Debouncing** - 200ms state change filtering prevents rapid oscillations

- **Error resilience** - Graceful handling of sensor failures and I2C issuesEdit the `proximity_config` in `main.py` to customize behavior:



## 🧪 Testing & Validation```python

proximity_config = {

### **Built-in Test Suite**    'proximity_threshold_mm': 500,        # Detection distance (mm)

```bash    'min_detection_count': 2,            # Consecutive detections needed

# Individual sensor tests    'min_speed_threshold': 0.5,          # Minimum speed to filter static objects (cm/s)

python test_vl53l5cx.py      # Proximity detection validation    'max_distance_change': 200,          # Maximum distance change between readings (mm)

python test_ltr559.py        # Light sensor calibration    'detection_timeout': 2.5,            # Timeout before sleep (seconds)

python test_bme690.py        # Environmental readings}

```

# Performance testing

python test_fade_performance.py    # Memory leak detection### Testing and Calibration

python test_smooth_fade.py         # Fade quality validation

Run the calibration tool to test sensor readings:

# System verification

python check_config.py       # Configuration validation```bash

python check_install.py      # Hardware detectionpython calibrate_sensor.py

``````



### **Performance Benchmarks**Test filtering algorithms:

- **Fade consistency**: <1% variation over 15+ cycles

- **Memory stability**: <2MB growth over extended operation```bash

- **Response time**: <200ms from detection to fade startpython test_filtering.py

- **Accuracy**: 64-zone precision with configurable thresholds```



## 📚 DocumentationDemo proximity detection without hardware:



- **`PROXIMITY_USAGE.md`** - Complete usage guide and configuration reference```bash

- **`SMOOTHNESS_SUMMARY.md`** - Technical details on fade optimizationpython demo_proximity.py

- **Inline comments** - Comprehensive code documentation```

- **Configuration comments** - Detailed setting explanations

## 📁 Project Structure

## 🔧 Advanced Usage

```

### **Service Installation**homedashsensor/

```bash├── __init__.py

# Create systemd service for auto-start├── main.py                 # Main application

sudo nano /etc/systemd/system/homedashsensor.service├── ld2450_protocol.py      # LD2450 sensor communication

```├── display_manager.py      # Display control and proximity logic

├── calibrate_sensor.py     # Sensor calibration tool

```ini├── demo_proximity.py       # Hardware-free demo

[Unit]├── test_*.py              # Various test scripts

Description=HomeDashSensor Proximity Display Control├── requirements.txt        # Python dependencies

After=network.target├── pyproject.toml         # Project configuration

└── README.md              # This file

[Service]```

Type=simple

User=pi## 🎛️ Configuration Guide

WorkingDirectory=/home/pi/homedashsensor

Environment=PATH=/home/pi/homedashsensor/venv/bin### Above-Screen Mounting (Recommended)

ExecStart=/home/pi/homedashsensor/venv/bin/python proximity_display_control.py

Restart=always- **Position**: Mount sensor above the display center

RestartSec=3- **Threshold**: 500mm (50cm) for comfortable detection range

- **Timeout**: 2.5s for responsive sleep behavior

[Install]

WantedBy=multi-user.target```python

```proximity_config = {

    'proximity_threshold_mm': 500,

```bash    'detection_timeout': 2.5,

# Enable and start service    # ... other settings

sudo systemctl enable homedashsensor.service}

sudo systemctl start homedashsensor.service```



# Check status### Behind-Screen Mounting (Not Recommended)

sudo systemctl status homedashsensor.service

```If you must mount behind the display, use these settings and ensure minimal metal interference:



### **Debugging**```python

```bashproximity_config = {

# Debug sensor communication    'proximity_threshold_mm': 400,

python debug_vl53l5cx.py    'detection_timeout': 3.0,

    'min_speed_threshold': 1.0,  # Higher threshold for metal interference

# Monitor logs    # ... other settings

tail -f proximity_display.log}

```

# Check I2C devices

i2cdetect -y 1## 🔧 Troubleshooting

```

### Common Issues

## 🤝 Contributing

**Sensor not detected:**

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.```bash

# Check USB devices

### **Development Setup**lsusb

```bash

git clone https://github.com/edizaziz-dev/homedashsensor.git# Check serial ports

cd homedashsensorls /dev/tty*

python3 -m venv venv```

source venv/bin/activate

pip install -r requirements.txt**Permission denied for brightness control:**

``````bash

# Verify group membership

### **Code Style**groups $USER

- Follow PEP 8 guidelines

- Use type hints where appropriate# Test brightness control

- Add comprehensive docstringsecho 128 | sudo tee /sys/class/backlight/*/brightness

- Include emoji in log messages for visual scanning```



## 📄 License**False detections:**

- Increase `min_speed_threshold` to filter static objects

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.- Adjust `max_distance_change` for environmental stability

- Ensure sensor is not behind metal surfaces

## 🙏 Acknowledgments

**No detection:**

- **VL53L5CX sensor library** - Community-contributed Python bindings- Check sensor mounting position and orientation

- **Pimoroni libraries** - LTR-559 and BME690 sensor support- Verify `proximity_threshold_mm` is appropriate for your setup

- **Raspberry Pi Foundation** - I2C and GPIO support- Run `calibrate_sensor.py` to test raw sensor readings



## 📞 Support## 📊 Logging



- **GitHub Issues** - Bug reports and feature requestsThe application uses structured logging with multiple levels:

- **Discussions** - Community support and questions

- **Wiki** - Extended documentation and tutorials- **INFO**: General operation status

- **DEBUG**: Detailed sensor readings and filtering decisions

---- **ERROR**: Hardware errors and exceptions



**Built with ❤️ for the Raspberry Pi community**Logs include emojis and structured data for easy monitoring and debugging.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run type checking (if you add type hints)
python -m mypy homedashsensor/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits and Acknowledgments

### Authors
- **Primary Developer**: [edizaziz-dev](https://github.com/edizaziz-dev) - Proximity detection application and advanced filtering
- **Protocol Implementation**: [Ron Martin (csRon)](https://github.com/csRon) - Original LD2450 protocol reverse engineering and Python implementation
- **AI Assistant**: GitHub Copilot - Code assistance and optimization

### Hardware and Documentation
- **HLK-LD2450 Sensor**: Hi-Link Electronic Co., Ltd. for the excellent 24GHz mmWave radar sensor and official documentation
- **LD2450 Protocol Implementation**: Based on official Hi-Link documentation and community reverse engineering efforts
- **Serial Protocol Credits**: Community contributors who documented the binary communication protocol
- **Waveshare**: For the DSI LCD display and documentation

### Libraries and Dependencies
- **[pyserial](https://github.com/pyserial/pyserial)**: Serial communication with the LD2450 sensor
- **[loguru](https://github.com/Delgan/loguru)**: Beautiful and powerful logging
- **[matplotlib](https://matplotlib.org/)**: Data visualization for calibration tools

### Community and Inspiration
- **Raspberry Pi Community**: For extensive documentation and support
- **Ron Martin (csRon)**: For the foundational LD2450 protocol implementation that made this project possible
- **mmWave Radar Community**: For sharing knowledge about 24GHz radar sensors and protocol documentation
- **LD2450 Protocol Contributors**: Community members who reverse-engineered and documented the serial communication protocol
- **Home Automation Community**: For inspiration on proximity-based automation

### Protocol and Implementation
- **LD2450 Protocol**: Based on [csRon/HLK-LD2450](https://github.com/csRon/HLK-LD2450) by Ron Martin (MIT License)
- **Serial Communication**: Core protocol functions adapted from Ron's excellent reverse engineering work
- **Data Parsing Logic**: Binary protocol implementation following Ron's documented format
- **Command Structure**: Extended from Ron's implementation with object-oriented design
- **Hardware Integration**: Building on the solid foundation of Ron's protocol documentation

### Special Thanks
- Thanks to the open source community for providing excellent libraries and documentation
- Thanks to Hi-Link Electronic for creating accessible and well-documented radar sensors
- Thanks to everyone who contributed to making this project possible

## 🔗 Related Projects

- **[csRon/HLK-LD2450](https://github.com/csRon/HLK-LD2450)** - Original Python protocol implementation by Ron Martin (Foundation for this project)
- [LD2450 Arduino Library](https://github.com/ncmreynolds/ld2450) - Arduino implementation
- [Home Assistant LD2450 Integration](https://github.com/rain931215/ESPHome-LD2450) - ESPHome component
- [mmWave Radar Projects](https://github.com/topics/mmwave-radar) - Other radar sensor projects

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing [Issues](https://github.com/edizaziz-dev/homedashsensor/issues)
3. Create a new issue with detailed information about your setup and problem

---

**Made with ❤️ for the Raspberry Pi and Home Automation community**