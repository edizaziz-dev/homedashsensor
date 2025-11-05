from dataclasses import dataclass
import glob
import os
from pathlib import Path
from config import DisplayConfig
import time
from typing import Optional

@dataclass
class DisplayState:
    """Current display state."""
    current_brightness: int = 0
    target_brightness: int = 0
    is_fading: bool = False
    is_awake: bool = False

BRIGHTNESS_PATH = None       # autodetected below
#MAX_BRIGHTNESS = None          # will be read from system
FADE_STEP = 5             # brightness step size (smaller = smoother)
FADE_DELAY = 0.02         # delay between brightness steps

class DisplayManager:
    def __init__(self, config: DisplayConfig):
        self.config = config
        self.state = DisplayState()
        
        # --- locate the DSI backlight device ---
        self.brightness_path = None
        for path in glob.glob("/sys/class/backlight/*/brightness"):
            # prefer DSI/backlight entries; fall back to first match
            if "DSI" in path or "backlight" in path:
                self.brightness_path = path
                break
        if not self.brightness_path:
            matches = glob.glob("/sys/class/backlight/*/brightness")
            if matches:
                self.brightness_path = matches[0]
        if not self.brightness_path:
            raise RuntimeError("Could not find backlight path; try: ls /sys/class/backlight/")

        # --- get brightness range ---
        base = os.path.dirname(self.brightness_path)
        with open(os.path.join(base, "max_brightness")) as f:
            self.max_brightness = int(f.read().strip())

    def set_brightness(self, value: int) -> None:
        value = max(0, min(value, self.max_brightness))
        try:
            with open(self.brightness_path, "w") as f:
                f.write(str(value))
        except PermissionError:
            # don't exit the process here; let caller decide
            raise PermissionError("Need permission to write backlight brightness")
        
    async def set_adaptive_brightness(self, lux: float) -> None:
        """Set brightness based on ambient light level."""
        if not self.config.adaptive_brightness_enabled:
            return
        
        # Calculate target brightness based on ambient light
        if lux <= self.config.light_threshold_low:
            target = self.config.min_brightness + 50  # Dim but visible
        elif lux >= self.config.light_threshold_high:
            target = self.config.max_brightness
        else:
            # Linear interpolation between thresholds
            ratio = (lux - self.config.light_threshold_low) / (
                self.config.light_threshold_high - self.config.light_threshold_low
            )
            target = int(50 + ratio * (self.config.max_brightness - 50))
        
        # Only adjust if significantly different (avoid constant micro-adjustments)
        if abs(target - self.state.target_brightness) > 10:
            #async with self._lock:
                #await self._start_fade(target, self.config.fade_duration * 0.5)
            self.fade_to(target)


    def get_brightness(self) -> int:
        try:
            with open(self.brightness_path) as f:
                return int(f.read().strip())
        except Exception:
            return self.max_brightness

    def fade_to(self, target: int):
        current = self.get_brightness()
        step = FADE_STEP if target > current else -FADE_STEP
        if step == 0:
            return
        for b in range(current, target, step):
            self.set_brightness(b)
            time.sleep(FADE_DELAY)
        self.set_brightness(target)