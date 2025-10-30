# Proximity Display Control - Usage Guide

## 🎯 What It Does

The proximity display control system automatically manages your display brightness based on human presence detection using the VL53L5CX ToF sensor:

- **Wake Display**: When someone comes within 40cm, the display smoothly fades ON over 2 seconds
- **Sleep Display**: When no one is detected for ~1 second, the display smoothly fades OFF over 3 seconds  
- **Smart Filtering**: Uses multiple sensor zones and consecutive detection to avoid false triggers

## 📁 Files Created

1. **`proximity_display_control.py`** - Main proximity display control system
2. **`test_display.py`** - Test script to verify display brightness control
3. **`proximity_config.ini`** - Configuration file for customizing behavior  
4. **`test_vl53l5cx.py`** - Original sensor test program

## 🚀 Quick Start

### 1. Test Display Control
```bash
source .venv/bin/activate
python test_display.py
```

### 2. Run Proximity Display Control
```bash
source .venv/bin/activate  
python proximity_display_control.py
```

### 3. Stop the System
- Press `Ctrl+C` to gracefully shutdown
- Display will fade to OFF automatically

## ⚙️ Configuration

Edit `proximity_config.ini` to customize:

```ini
[Detection]
threshold_mm = 400        # 40cm detection distance
detection_zones = 4       # Minimum zones that must detect
consecutive_required = 3  # Consecutive detections needed

[Display]  
fade_in_duration = 2.0    # Wake fade time (seconds)
fade_out_duration = 3.0   # Sleep fade time (seconds)

[System]
update_interval = 0.1     # Sensor polling rate
sensor_frequency = 15     # Sensor update rate (Hz)
```

## 🎛️ How It Works

### Proximity Detection Logic:
1. **8x8 ToF sensor** continuously scans for objects
2. **Multiple zones** must detect objects within 40cm threshold
3. **Consecutive filtering** requires 3 detections before triggering
4. **Anti-flicker** requires 10 consecutive non-detections before turning off

### Display Control:
1. **Automatic discovery** of brightness control path
2. **Smooth fading** using async transitions  
3. **Full brightness range** (0-255 or 0-max_brightness)
4. **Graceful shutdown** returns display to previous state

### Example Log Output:
```
2025-10-29 23:12:23,068 - INFO - ✅ System running - monitoring for presence...
2025-10-29 23:12:23,665 - INFO - 🙋 Human presence detected - Waking display
2025-10-29 23:12:23,665 - INFO - 🎭 Fading brightness: 0 → 255 over 2.0s  
2025-10-29 23:12:25,690 - INFO - ✨ Fade complete: brightness = 255
```

## 🔧 Troubleshooting

### Sensor Issues:
- **"Sensor not detected"**: Check I2C connections and `sudo i2cdetect -y 1`
- **"Error processing sensor data"**: Restart the system

### Display Issues:  
- **"No brightness control found"**: Check display connections and drivers
- **Permission errors**: Add user to video group: `sudo usermod -a -G video pi`

### System Issues:
- **Import errors**: Ensure virtual environment is activated
- **Slow response**: Adjust `consecutive_required` in config

## 🎯 Use Cases

- **Home dashboard/kiosk** - Save power when nobody is around
- **Digital photo frame** - Wake when people approach
- **Smart bathroom mirror** - Automatic activation  
- **Retail displays** - Engage customers when they approach
- **Security monitors** - Activate when motion detected

## 📊 Performance

- **Detection Range**: 2cm to 400cm (40cm threshold)
- **Response Time**: ~300ms detection + 2s fade = ~2.3s total
- **Update Rate**: 15Hz sensor polling for responsive detection
- **Power Efficient**: Display off when not needed
- **False Positive Resistant**: Multi-zone + consecutive filtering

## 🔄 System Service (Optional)

To run at startup, create a systemd service:

```bash
sudo nano /etc/systemd/system/proximity-display.service
```

```ini
[Unit]
Description=Proximity Display Control
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/apps/homedashsensor
ExecStart=/home/pi/apps/homedashsensor/.venv/bin/python proximity_display_control.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable proximity-display.service
sudo systemctl start proximity-display.service
```