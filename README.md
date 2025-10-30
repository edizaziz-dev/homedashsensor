# HomeDashSensor 🎯# VL53L5CX ToF Sensor Test



**Advanced proximity-based display control system for Raspberry Pi with ultra-smooth 60Hz fading**A simple test program for the VL53L5CX 8x8 Time of Flight (ToF) array sensor.



A sophisticated multi-sensor system that automatically controls display brightness based on human presence detection, ambient light levels, and environmental conditions. Features professional-grade fade animations optimized for high refresh rate displays.## Hardware Setup



## ✨ Features### Connections (Pi 5)

Connect the VL53L5CX sensor to your Raspberry Pi:

### 🎯 **Precision Proximity Detection**

- **VL53L5CX 8x8 ToF Sensor** - 64-zone time-of-flight detection with millimeter precision```

- **Configurable thresholds** - Adjustable detection distance (default: 400mm)VL53L5CX    →    Raspberry Pi

- **Multi-zone filtering** - Requires multiple zones for reliable detectionVCC         →    3.3V (Pin 1) or 5V (Pin 2)

- **Consecutive detection logic** - Prevents false triggers from sensor noiseGND         →    GND (Pin 6)

SDA         →    GPIO 2 / SDA (Pin 3)

### 🎭 **Ultra-Smooth Display Control**SCL         →    GPIO 3 / SCL (Pin 5)

- **600-step fade animations** - Optimized for 60Hz displays (3.3ms per step)```

- **Quintic ease-in-out curves** - Imperceptible transitions with professional smoothness

- **Frame-rate synchronized** - Aligned to display refresh cycles for perfect motion### I2C Configuration

- **Task management** - Prevents overlapping fades with proper cancellationThe sensor uses I2C address `0x29`. Ensure I2C is enabled:



### 🌞 **Adaptive Brightness**```bash

- **LTR-559 Light Sensor** - Automatic brightness adjustment based on ambient lightsudo raspi-config

- **Configurable thresholds** - 10-500 lux range with linear interpolation# Navigate to: Interface Options → I2C → Enable

- **Real-time adaptation** - Smooth transitions when lighting conditions change```

- **Manual override** - Can be disabled for static brightness mode

## Software Setup

### 🌡️ **Environmental Monitoring**

- **BME690 4-in-1 Sensor** - Temperature, pressure, humidity, and air quality### 1. Install Dependencies

- **Gas resistance measurement** - Air quality scoring (0-100 scale)```bash

- **Configurable sampling** - Adjustable oversampling and heating parameters# Install the VL53L5CX Python library

- **Comprehensive logging** - Periodic environmental data reportingpip install vl53l5cx-python numpy



### ⚙️ **Professional Configuration**# Or install from requirements.txt

- **INI-based configuration** - Comprehensive settings for all devices and behaviorspip install -r requirements.txt

- **Inline comment support** - Clean configuration parsing with comment handling```

- **Hot-reload capability** - Runtime configuration updates

- **Extensive validation** - Built-in configuration checking and status reporting### 2. Test I2C Connection

```bash

## 🔧 Hardware Requirements# Check if sensor is detected

sudo i2cdetect -y 1

### **Core Components**

- **Raspberry Pi** (any model with I2C support)# You should see "29" in the output grid

- **VL53L5CX 8x8 ToF Sensor** (I2C address: 0x29)```

- **Display with brightness control** (via Linux sysfs)

### 3. Run the Test Program

### **Optional Sensors**```bash

- **LTR-559 Light Sensor** (I2C address: 0x23) - For adaptive brightnesspython test_vl53l5cx.py

- **BME690 Environmental Sensor** (I2C address: 0x76) - For air quality monitoring```



### **Wiring Guide**## What the Test Does

```

VL53L5CX ToF Sensor:The test program will:

├── VCC → 3.3V

├── GND → Ground1. 🔄 Initialize the VL53L5CX sensor

├── SDA → GPIO 2 (I2C SDA)2. ✅ Verify the sensor is responsive

└── SCL → GPIO 3 (I2C SCL)3. 🚀 Configure for 8x8 ranging mode

4. 📡 Start continuous distance measurements

LTR-559 Light Sensor (Optional):5. � Display real-time 8x8 distance grid

├── VCC → 3.3V6. 📈 Show min/max/average distance statistics

├── GND → Ground

├── SDA → GPIO 2 (I2C SDA)## Expected Output

└── SCL → GPIO 3 (I2C SCL)

```

BME690 Environmental Sensor (Optional):🎯 VL53L5CX 8x8 ToF Sensor Test

├── VCC → 3.3V========================================

├── GND → Ground🔄 Initializing VL53L5CX sensor...

├── SDA → GPIO 2 (I2C SDA)✅ Sensor detected and responsive!

└── SCL → GPIO 3 (I2C SCL)� Starting sensor initialization...

```📡 Ranging started!



## 🚀 Quick StartPress Ctrl+C to stop...



### **1. System Preparation**📊 Frame #1

```bash

# Enable I2C interface8x8 Distance Grid (mm):

sudo raspi-config+--------------------------------------------------+

# Navigate to: Interface Options → I2C → Enable|  1234  1245  1256  1267  1278  1289  1290  1301 |

|  1312  1323  1334  1345  1356  1367  1378  1389 |

# Install system dependencies|  1400  1411  1422  1433  1444  1455  1466  1477 |

sudo apt update|  1488  1499  1510  1521  1532  1543  1554  1565 |

sudo apt install python3-pip python3-venv git i2c-tools|  1576  1587  1598  1609  1620  1631  1642  1653 |

```|  1664  1675  1686  1697  1708  1719  1730  1741 |

|  1752  1763  1774  1785  1796  1807  1818  1829 |

### **2. Installation**|  1840  1851  1862  1873  1884  1895  1906  1917 |

```bash+--------------------------------------------------+

# Clone the repository

git clone https://github.com/edizaziz-dev/homedashsensor.git📈 Stats: Min=1234mm, Max=1917mm, Avg=1575.5mm

cd homedashsensor🎯 Valid readings: 64/64

```

# Create virtual environment

python3 -m venv venv## Sensor Specifications

source venv/bin/activate

- **Field of View**: 63° diagonal

# Install dependencies- **Range**: 2cm to 4 meters

pip install -r requirements.txt- **Resolution**: 8x8 array (64 zones)

- **Update Rate**: Up to 60Hz

# Verify hardware detection- **Interface**: I2C (address 0x29)

python check_install.py- **Accuracy**: ±3% typical

```

## Troubleshooting

### **3. Configuration**

```bash### Sensor Not Detected

# Check current configuration```

python check_config.py❌ Sensor not detected. Check connections!

```

# Edit configuration if needed- Verify wiring connections

nano proximity_config.ini- Check I2C is enabled: `sudo raspi-config`

```- Test I2C: `sudo i2cdetect -y 1`

- Ensure 3.3V/5V power supply

### **4. Testing**

```bash### Import Error

# Test individual sensors```

python test_vl53l5cx.py      # ToF sensor❌ VL53L5CX library not installed!

python test_ltr559.py        # Light sensor (if connected)```

python test_bme690.py        # Environmental sensor (if connected)- Install library: `pip install vl53l5cx-python`

- Check Python environment

# Test display control

python test_smooth_fade.py   # Fade performance### Permission Error

- Try with sudo: `sudo python test_vl53l5cx.py`

# Test complete system- Add user to i2c group: `sudo usermod -a -G i2c pi`

python proximity_display_control.py

```## Next Steps



## 📋 ConfigurationOnce the test is working:

1. Experiment with different ranging frequencies (1-60Hz)

The system uses `proximity_config.ini` for comprehensive configuration:2. Try 4x4 mode for faster updates: `sensor.set_resolution(4*4)`

3. Add motion detection algorithms

### **Key Settings**4. Integrate with display/LED feedback

```ini5. Build proximity detection system

[Detection]

threshold_mm = 400              # Detection distance (400mm = 40cm)```bash

detection_zones = 4             # Minimum zones required# Add udev rule for brightness control

consecutive_required = 2        # Consecutive detections neededsudo tee /etc/udev/rules.d/99-backlight.rules << EOF

no_presence_required = 10       # Frames to confirm absenceSUBSYSTEM=="backlight", ACTION=="add", RUN+="/bin/chgrp video %S%p/brightness", RUN+="/bin/chmod g+w %S%p/brightness"

EOF

[Display]

fade_in_duration = 2.0          # Wake fade duration (seconds)# Add user to video group

fade_out_duration = 3.0         # Sleep fade duration (seconds)sudo usermod -a -G video $USER

fade_steps = 600                # Fade smoothness (600 = 60Hz optimized)

fade_easing = quintic           # Motion curve (quintic/ease_in_out/linear)# Reload udev rules

adaptive_brightness_enabled = truesudo udevadm control --reload-rules

min_brightness = 20             # Minimum display brightnesssudo udevadm trigger

max_brightness = 255            # Maximum display brightness```



[LightSensor]### 4. Configure Sensor Port

enabled = true                  # Enable adaptive brightness

light_threshold_low = 10.0      # Dark threshold (lux)Edit the sensor port in `main.py` if needed:

light_threshold_high = 500.0    # Bright threshold (lux)

``````python

# Update this line with your sensor's serial port

See `PROXIMITY_USAGE.md` for complete configuration reference.sensor = LD2450(port='/dev/ttyUSB0')  # or /dev/ttyAMA0 for GPIO UART

```

## 🎭 Performance & Optimization

## 🚀 Usage

### **60Hz Display Optimization**

- **600 fade steps** provide 3.3ms transitions (imperceptible on 60Hz displays)### Basic Usage

- **Quintic easing** delivers professional motion curves

- **Frame synchronization** eliminates visual artifacts```bash

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