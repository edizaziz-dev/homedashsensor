"""
Display brightness control for HomeDashSensor.
Single responsibility: Manage display brightness with smooth fading transitions.
"""
import asyncio
import logging
import glob
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from config import DisplayConfig


@dataclass
class DisplayState:
    """Current display state."""
    current_brightness: int = 0
    target_brightness: int = 0
    is_fading: bool = False
    is_awake: bool = False


class DisplayController:
    """High-performance display brightness controller with smooth fading."""
    
    def __init__(self, config: DisplayConfig):
        """Initialize display controller.
        
        Args:
            config: DisplayConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.state = DisplayState()
        self._brightness_path: Optional[Path] = None
        self._fade_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize display controller and find brightness path."""
        try:
            # Find brightness control path
            brightness_paths = glob.glob(self.config.brightness_path)
            if not brightness_paths:
                self.logger.error(f"No brightness control found at: {self.config.brightness_path}")
                return False
            
            self._brightness_path = Path(brightness_paths[0])
            
            # Test write permissions
            try:
                current = await self._read_brightness()
                await self._write_brightness(current)
                self.state.current_brightness = current
                self.state.target_brightness = current
                self.state.is_awake = current > 0
                
                self.logger.info(f"✅ Display controller initialized (current brightness: {current})")
                return True
                
            except PermissionError:
                self.logger.error(f"Permission denied writing to: {self._brightness_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize display controller: {e}")
            return False
    
    async def _read_brightness(self) -> int:
        """Read current brightness value."""
        if not self._brightness_path:
            return 0
        
        try:
            content = self._brightness_path.read_text().strip()
            return int(content)
        except Exception as e:
            self.logger.error(f"Failed to read brightness: {e}")
            return 0
    
    async def _write_brightness(self, brightness: int) -> bool:
        """Write brightness value to sysfs."""
        if not self._brightness_path:
            return False
        
        try:
            # Clamp brightness to valid range
            brightness = max(self.config.min_brightness, min(self.config.max_brightness, brightness))
            
            # Use async file operations for better performance
            def write_sync():
                self._brightness_path.write_text(str(brightness))
            
            await asyncio.get_event_loop().run_in_executor(None, write_sync)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write brightness {brightness}: {e}")
            return False
    
    async def wake_display(self, target_brightness: Optional[int] = None) -> None:
        """Wake display with smooth fade-in."""
        async with self._lock:
            if target_brightness is None:
                target_brightness = self.config.max_brightness
            
            if self.state.is_awake and self.state.target_brightness == target_brightness:
                return  # Already at target state
            
            self.logger.info(f"🌅 Waking display (target: {target_brightness})")
            await self._start_fade(target_brightness, self.config.fade_in_duration)
            self.state.is_awake = True
    
    async def sleep_display(self) -> None:
        """Sleep display with smooth fade-out."""
        async with self._lock:
            if not self.state.is_awake:
                return  # Already asleep
            
            self.logger.info("🌙 Sleeping display")
            await self._start_fade(self.config.min_brightness, self.config.fade_out_duration)
            self.state.is_awake = False
    
    async def set_adaptive_brightness(self, lux: float) -> None:
        """Set brightness based on ambient light level."""
        if not self.config.adaptive_brightness_enabled or not self.state.is_awake:
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
            async with self._lock:
                await self._start_fade(target, self.config.fade_duration * 0.5)
    
    async def _start_fade(self, target_brightness: int, duration: float) -> None:
        """Start a smooth brightness fade transition."""
        # Cancel any existing fade
        if self._fade_task and not self._fade_task.done():
            self._fade_task.cancel()
            try:
                await self._fade_task
            except asyncio.CancelledError:
                pass
        
        self.state.target_brightness = target_brightness
        self.state.is_fading = True
        
        # Start new fade task
        self._fade_task = asyncio.create_task(self._fade_worker(target_brightness, duration))
        
        try:
            await self._fade_task
        except asyncio.CancelledError:
            pass
        finally:
            self.state.is_fading = False
    
    async def _fade_worker(self, target_brightness: int, duration: float) -> None:
        """Perform smooth brightness fade with optimized easing."""
        start_brightness = self.state.current_brightness
        brightness_diff = target_brightness - start_brightness
        
        if brightness_diff == 0:
            return
        
        steps = self.config.fade_steps
        step_duration = duration / steps
        
        self.logger.debug(f"🎭 Fading from {start_brightness} to {target_brightness} over {duration:.1f}s")
        
        for step in range(steps + 1):
            if step == steps:
                # Ensure we hit exact target on final step
                new_brightness = target_brightness
            else:
                # Calculate progress with easing
                progress = step / steps
                eased_progress = self._apply_easing(progress)
                new_brightness = int(start_brightness + brightness_diff * eased_progress)
            
            # Write brightness
            if await self._write_brightness(new_brightness):
                self.state.current_brightness = new_brightness
            
            # Sleep for next step (except on final step)
            if step < steps:
                await asyncio.sleep(step_duration)
    
    def _apply_easing(self, progress: float) -> float:
        """Apply easing function for smooth transitions."""
        if self.config.fade_easing == "linear":
            return progress
        elif self.config.fade_easing == "ease_in_out":
            # Smooth acceleration and deceleration
            return progress * progress * (3.0 - 2.0 * progress)
        elif self.config.fade_easing == "quintic":
            # Very smooth quintic easing (best for 60Hz displays)
            return progress * progress * progress * (progress * (progress * 6 - 15) + 10)
        else:
            return progress
    
    async def get_current_brightness(self) -> int:
        """Get current display brightness."""
        return self.state.current_brightness
    
    async def cleanup(self) -> None:
        """Clean up display controller."""
        if self._fade_task and not self._fade_task.done():
            self._fade_task.cancel()
            try:
                await self._fade_task
            except asyncio.CancelledError:
                pass