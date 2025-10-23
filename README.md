# HomeDashSensor 🎯

**Smart Proximity-Based Display Control for Raspberry Pi**

A Python application that uses the HLK-LD2450 24GHz mmWave radar sensor to automatically control display brightness based on human presence. Perfect for home dashboards, kiosks, and smart displays that should wake when someone approaches and sleep when they leave.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

## ✨ Features

- 🎯 **Precise Proximity Detection** - Uses 24GHz mmWave radar for accurate human presence detection
- 🌅 **Smooth Brightness Control** - Gradual fade in/out transitions for comfortable viewing
- 🔍 **Advanced Filtering** - Intelligent algorithms to eliminate false readings and static objects
- ⚡ **Real-time Processing** - Async-based architecture for responsive control
- 🛡️ **Interference Resistant** - Smart filtering handles metal interference and environmental noise
- 📊 **Comprehensive Logging** - Detailed logging with configurable levels for debugging
- 🔧 **Easy Configuration** - Simple parameter adjustment for different mounting positions

## 🛠️ Hardware Requirements

- **Raspberry Pi 5** (or compatible)
- **HLK-LD2450 24GHz mmWave Radar Sensor**
- **Waveshare 13.3" DSI LCD** (or compatible display with brightness control)
- USB-to-Serial adapter (if needed for sensor connection)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/edizaziz-dev/homedashsensor.git
cd homedashsensor
```

### 2. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Hardware Setup

1. **Connect the LD2450 sensor** to your Raspberry Pi via USB or GPIO UART
2. **Mount the sensor** above your display for optimal detection (avoid placing behind metal)
3. **Configure display brightness permissions**:

```bash
# Add udev rule for brightness control
sudo tee /etc/udev/rules.d/99-backlight.rules << EOF
SUBSYSTEM=="backlight", ACTION=="add", RUN+="/bin/chgrp video %S%p/brightness", RUN+="/bin/chmod g+w %S%p/brightness"
EOF

# Add user to video group
sudo usermod -a -G video $USER

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. Configure Sensor Port

Edit the sensor port in `main.py` if needed:

```python
# Update this line with your sensor's serial port
sensor = LD2450(port='/dev/ttyUSB0')  # or /dev/ttyAMA0 for GPIO UART
```

## 🚀 Usage

### Basic Usage

```bash
cd homedashsensor
python main.py
```

### Configuration Options

Edit the `proximity_config` in `main.py` to customize behavior:

```python
proximity_config = {
    'proximity_threshold_mm': 500,        # Detection distance (mm)
    'min_detection_count': 2,            # Consecutive detections needed
    'min_speed_threshold': 0.5,          # Minimum speed to filter static objects (cm/s)
    'max_distance_change': 200,          # Maximum distance change between readings (mm)
    'detection_timeout': 2.5,            # Timeout before sleep (seconds)
}
```

### Testing and Calibration

Run the calibration tool to test sensor readings:

```bash
python calibrate_sensor.py
```

Test filtering algorithms:

```bash
python test_filtering.py
```

Demo proximity detection without hardware:

```bash
python demo_proximity.py
```

## 📁 Project Structure

```
homedashsensor/
├── __init__.py
├── main.py                 # Main application
├── ld2450_protocol.py      # LD2450 sensor communication
├── display_manager.py      # Display control and proximity logic
├── calibrate_sensor.py     # Sensor calibration tool
├── demo_proximity.py       # Hardware-free demo
├── test_*.py              # Various test scripts
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## 🎛️ Configuration Guide

### Above-Screen Mounting (Recommended)

- **Position**: Mount sensor above the display center
- **Threshold**: 500mm (50cm) for comfortable detection range
- **Timeout**: 2.5s for responsive sleep behavior

```python
proximity_config = {
    'proximity_threshold_mm': 500,
    'detection_timeout': 2.5,
    # ... other settings
}
```

### Behind-Screen Mounting (Not Recommended)

If you must mount behind the display, use these settings and ensure minimal metal interference:

```python
proximity_config = {
    'proximity_threshold_mm': 400,
    'detection_timeout': 3.0,
    'min_speed_threshold': 1.0,  # Higher threshold for metal interference
    # ... other settings
}
```

## 🔧 Troubleshooting

### Common Issues

**Sensor not detected:**
```bash
# Check USB devices
lsusb

# Check serial ports
ls /dev/tty*
```

**Permission denied for brightness control:**
```bash
# Verify group membership
groups $USER

# Test brightness control
echo 128 | sudo tee /sys/class/backlight/*/brightness
```

**False detections:**
- Increase `min_speed_threshold` to filter static objects
- Adjust `max_distance_change` for environmental stability
- Ensure sensor is not behind metal surfaces

**No detection:**
- Check sensor mounting position and orientation
- Verify `proximity_threshold_mm` is appropriate for your setup
- Run `calibrate_sensor.py` to test raw sensor readings

## 📊 Logging

The application uses structured logging with multiple levels:

- **INFO**: General operation status
- **DEBUG**: Detailed sensor readings and filtering decisions
- **ERROR**: Hardware errors and exceptions

Logs include emojis and structured data for easy monitoring and debugging.

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
- **Primary Developer**: [edizaziz-dev](https://github.com/edizaziz-dev) - Initial work and implementation
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
- **mmWave Radar Community**: For sharing knowledge about 24GHz radar sensors and protocol documentation
- **LD2450 Protocol Contributors**: Community members who reverse-engineered and documented the serial communication protocol
- **Home Automation Community**: For inspiration on proximity-based automation

### Protocol and Implementation
- **Serial Communication Protocol**: Implementation based on community-documented LD2450 binary protocol specifications
- **Data Parsing Logic**: Adapted from various open source implementations and official documentation
- **Command Structure**: Following Hi-Link's official command format documentation

### Special Thanks
- Thanks to the open source community for providing excellent libraries and documentation
- Thanks to Hi-Link Electronic for creating accessible and well-documented radar sensors
- Thanks to everyone who contributed to making this project possible

## 🔗 Related Projects

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