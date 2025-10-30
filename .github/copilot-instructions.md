# Copilot Instructions for HomeDashSensor

## Project Overview
HomeDashSensor is a **proximity-based display control system** for Raspberry Pi that uses an LD2450 24GHz mmWave radar sensor to automatically wake/sleep displays when humans approach or leave. The architecture centers around three main components working together in an async event loop.

## Key Architecture Components

### 1. Sensor Layer (`ld2450_protocol.py`)
- **Based on csRon's protocol implementation** - Always credit Ron Martin's foundational work
- **Binary protocol parsing** - Handles 30-byte frames with header `AA FF 03 00` and tail `55 CC`
- **Target data structure**: `{x: int, y: int, speed: int, distance_resolution: int}` for 3 targets
- **Context manager support** - Use `with LD2450() as sensor:` pattern

### 2. Detection Layer (`display_manager.py`)
- **ProximityTracker** - Implements sophisticated filtering algorithms to eliminate false positives
- **Key filtering patterns**:
  - Consecutive detection requirement (default: 2 detections)
  - Speed threshold filtering (default: 0.5 cm/s minimum)
  - Distance change validation (max 200mm between readings)
  - Timeout-based presence tracking (3.0s default)
- **State machine**: Tracks `is_human_present`, `consecutive_detections`, `last_valid_distance`

### 3. Display Layer (`display_manager.py`)
- **DisplayManager** - Controls Waveshare DSI LCD brightness via Linux sysfs
- **Brightness path**: `/sys/class/backlight/11-0045/brightness` (0-255 range)
- **Async fade operations** - Smooth transitions over configurable duration
- **Wake/sleep cycle** - Coordinated with proximity detection

## Critical Integration Patterns

### Main Loop Architecture (`main.py`)
```python
# Standard pattern for sensor integration
sensor = LD2450(port='/dev/ttyUSB0', baudrate=256000)
proximity = ProximityTracker(proximity_threshold_mm=500)
display = DisplayManager()

# State change detection pattern
human_present = proximity.update_proximity(target_data)
if human_present != previous_state:
    if human_present:
        await display.wake_screen()
    else:
        await display.sleep_screen()
```

### Configuration Tuning
- **Above-screen mounting**: 500mm threshold, lower speed filtering (0.5 cm/s)
- **Behind-screen mounting**: 400mm threshold, higher speed filtering (1.0 cm/s)
- **Adjust `proximity_config` dict** in main.py for different scenarios

## Development Workflows

### Hardware Debugging
- Use `python calibrate_sensor.py` to debug sensor readings and false positives
- Check serial port with `dmesg | grep tty` after connecting USB-TTL adapter
- Test brightness permissions: `echo 128 | sudo tee /sys/class/backlight/*/brightness`

### Testing Without Hardware
- `python demo_proximity.py` - Simulates proximity detection without sensor
- `python test_filtering.py` - Validates filtering algorithms with mock data
- `python test_display.py` - Tests display brightness control

### Critical Dependencies
- **loguru** for structured logging with emojis and debug levels
- **pyserial** for LD2450 communication (256000 baud rate)
- **asyncio** for concurrent sensor reading and display control

## Project-Specific Conventions

### Error Handling Patterns
- Sensor failures return `None` - always check target_data before processing
- Brightness control failures log errors but don't crash the main loop
- Serial timeouts are handled gracefully with reconnection logic

### Logging Strategy
- Use emoji prefixes for visual scanning: 🎯 targets, 🙋 human detected, 🚶 human left
- DEBUG level for sensor data, INFO for state changes, ERROR for hardware issues
- Distance logging in mm, speed in cm/s, brightness 0-255

### State Management
- ProximityTracker maintains detection history for filtering consistency
- DisplayManager tracks current/target brightness and fade operations
- Main loop preserves previous_human_state for edge detection

## Hardware Integration Notes
- **LD2450 connections**: GND-GND, 5V-5V, RX-TX, TX-RX via USB-TTL adapter
- **Permission setup required**: Add user to `video` group for brightness control
- **Mounting affects filtering**: Metal behind sensor causes interference, above-screen optimal

When extending this codebase, maintain the async event loop pattern, preserve the filtering architecture for proximity detection, and ensure proper cleanup in signal handlers.