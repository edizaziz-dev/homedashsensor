#!/usr/bin/env python3
"""
Display Manager for Waveshare 13.3" DSI LCD
Handles brightness control and screen wake/sleep based on proximity
"""
import asyncio
import time
from pathlib import Path
from loguru import logger


class DisplayManager:
    """
    Manages display brightness and power state for Waveshare DSI LCD
    """
    
    def __init__(self, backlight_path: str = "/sys/class/backlight/11-0045"):
        """
        Initialize the display manager
        
        Args:
            backlight_path (str): Path to the backlight control directory
        """
        self.backlight_path = Path(backlight_path)
        self.brightness_file = self.backlight_path / "brightness"
        self.max_brightness_file = self.backlight_path / "max_brightness"
        
        # Read maximum brightness value
        try:
            self.max_brightness = int(self.max_brightness_file.read_text().strip())
            logger.info(f"Display max brightness: {self.max_brightness}")
        except Exception as e:
            logger.error(f"Failed to read max brightness: {e}")
            self.max_brightness = 255  # Default fallback
        
        # State tracking
        self.current_brightness = self.get_current_brightness()
        self.target_brightness = self.current_brightness
        self.is_awake = self.current_brightness > 0
        self.fade_task = None
        
        # Configuration
        self.fade_duration = 2.0  # seconds for fade in/out
        self.fade_steps = 50      # Number of steps in fade animation
        self.min_brightness = 0   # Minimum brightness (off)
        self.wake_brightness = self.max_brightness  # Full brightness when awake
        
        logger.info(f"Display manager initialized. Current brightness: {self.current_brightness}")
    
    def get_current_brightness(self) -> int:
        """
        Get the current brightness value
        
        Returns:
            int: Current brightness value (0-max_brightness)
        """
        try:
            return int(self.brightness_file.read_text().strip())
        except Exception as e:
            logger.error(f"Failed to read current brightness: {e}")
            return 0
    
    def set_brightness(self, value: int) -> bool:
        """
        Set the display brightness immediately
        
        Args:
            value (int): Brightness value (0-max_brightness)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Clamp value to valid range
        value = max(0, min(value, self.max_brightness))
        
        try:
            self.brightness_file.write_text(str(value))
            self.current_brightness = value
            logger.debug(f"Set brightness to {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set brightness to {value}: {e}")
            return False
    
    async def fade_to_brightness(self, target: int, duration: float = None) -> bool:
        """
        Smoothly fade to target brightness
        
        Args:
            target (int): Target brightness value
            duration (float): Fade duration in seconds (uses default if None)
            
        Returns:
            bool: True if fade completed successfully
        """
        if duration is None:
            duration = self.fade_duration
        
        # Cancel any existing fade task
        if self.fade_task and not self.fade_task.done():
            self.fade_task.cancel()
        
        # Clamp target to valid range
        target = max(0, min(target, self.max_brightness))
        self.target_brightness = target
        
        start_brightness = self.current_brightness
        brightness_diff = target - start_brightness
        
        if brightness_diff == 0:
            logger.debug("Already at target brightness")
            return True
        
        step_delay = duration / self.fade_steps
        brightness_step = brightness_diff / self.fade_steps
        
        logger.info(f"Fading from {start_brightness} to {target} over {duration}s")
        
        try:
            for step in range(self.fade_steps + 1):
                if step == self.fade_steps:
                    # Ensure we hit the exact target on the final step
                    new_brightness = target
                else:
                    new_brightness = int(start_brightness + (brightness_step * step))
                
                if not self.set_brightness(new_brightness):
                    logger.error(f"Failed to set brightness during fade at step {step}")
                    return False
                
                await asyncio.sleep(step_delay)
            
            logger.info(f"Fade completed. Final brightness: {self.current_brightness}")
            return True
            
        except asyncio.CancelledError:
            logger.info("Fade operation cancelled")
            return False
        except Exception as e:
            logger.error(f"Error during fade: {e}")
            return False
    
    async def wake_screen(self) -> bool:
        """
        Wake the screen with a smooth fade-in
        
        Returns:
            bool: True if successful
        """
        if self.is_awake:
            logger.debug("Screen already awake")
            return True
        
        logger.info("Waking screen...")
        success = await self.fade_to_brightness(self.wake_brightness)
        
        if success:
            self.is_awake = True
            logger.info("Screen wake completed")
        else:
            logger.error("Screen wake failed")
        
        return success
    
    async def sleep_screen(self) -> bool:
        """
        Put the screen to sleep with a smooth fade-out
        
        Returns:
            bool: True if successful
        """
        if not self.is_awake:
            logger.debug("Screen already asleep")
            return True
        
        logger.info("Putting screen to sleep...")
        success = await self.fade_to_brightness(self.min_brightness)
        
        if success:
            self.is_awake = False
            logger.info("Screen sleep completed")
        else:
            logger.error("Screen sleep failed")
        
        return success
    
    def cleanup(self):
        """
        Clean up resources
        """
        if self.fade_task and not self.fade_task.done():
            self.fade_task.cancel()
        logger.info("Display manager cleanup completed")


class ProximityTracker:
    """
    Tracks proximity using LD2450 sensor data with improved filtering
    """
    
    def __init__(self, proximity_threshold_mm: int = 400):  # 40cm = 400mm
        """
        Initialize proximity tracker
        
        Args:
            proximity_threshold_mm (int): Distance threshold in millimeters
        """
        self.proximity_threshold = proximity_threshold_mm
        self.is_human_present = False
        self.last_detection_time = 0
        self.detection_timeout = 3.0  # seconds to wait before considering human gone
        
        # Filtering parameters
        self.min_detection_count = 3  # Require 3 consecutive detections
        self.max_distance_change = 200  # Max mm change between readings to be considered same object
        self.min_speed_threshold = 1  # Minimum speed to consider it a real moving object (cm/s)
        
        # Tracking state
        self.recent_detections = []  # Store recent valid detections
        self.consecutive_detections = 0
        self.last_valid_distance = None
        
        logger.info(f"Proximity tracker initialized. Threshold: {proximity_threshold_mm}mm")
        logger.info(f"Filtering: min_detections={self.min_detection_count}, "
                   f"max_distance_change={self.max_distance_change}mm, "
                   f"min_speed={self.min_speed_threshold}cm/s")
    
    def update_proximity(self, target_data: dict) -> bool:
        """
        Update proximity state based on sensor data with improved filtering
        
        Args:
            target_data (dict): Target data from LD2450 sensor
            
        Returns:
            bool: True if human is within proximity threshold
        """
        if not target_data:
            return self._check_timeout_and_update()
        
        current_time = time.time()
        valid_close_targets = []
        
        # First pass: find all potentially valid targets
        for target_name, target_info in target_data.items():
            x, y, speed = target_info['x'], target_info['y'], target_info['speed']
            
            # Skip empty targets (all zeros usually means no detection)
            if x == 0 and y == 0:
                continue
            
            # Calculate distance from sensor
            distance = (x*x + y*y) ** 0.5
            
            # Apply basic filters
            if self._is_valid_detection(target_info, distance):
                valid_close_targets.append({
                    'name': target_name,
                    'distance': distance,
                    'speed': abs(speed),  # Use absolute speed
                    'x': x,
                    'y': y
                })
                logger.debug(f"{target_name}: distance={distance:.1f}mm, speed={abs(speed)}cm/s - VALID")
            else:
                logger.debug(f"{target_name}: distance={distance:.1f}mm, speed={abs(speed)}cm/s - FILTERED OUT")
        
        # Check if we have any valid close detections
        if valid_close_targets:
            # Sort by distance (closest first)
            valid_close_targets.sort(key=lambda t: t['distance'])
            closest_target = valid_close_targets[0]
            
            # Check if this detection is consistent with recent history
            if self._is_consistent_detection(closest_target['distance']):
                self.consecutive_detections += 1
                self.last_valid_distance = closest_target['distance']
                
                logger.debug(f"Consistent detection: {closest_target['distance']:.1f}mm "
                           f"(consecutive: {self.consecutive_detections})")
                
                # Only consider human present after minimum consecutive detections
                if self.consecutive_detections >= self.min_detection_count:
                    if not self.is_human_present:
                        logger.info(f"🙋 Human presence confirmed after {self.consecutive_detections} consistent detections")
                    self.is_human_present = True
                    self.last_detection_time = current_time
            else:
                # Reset if detection is inconsistent
                logger.debug(f"Inconsistent detection: {closest_target['distance']:.1f}mm - resetting counter")
                self.consecutive_detections = 0
                self.last_valid_distance = None
        else:
            # No valid targets found
            self.consecutive_detections = 0
            self.last_valid_distance = None
            
            # Check timeout for human leaving
            was_present = self.is_human_present
            if was_present:
                # Only check timeout if we had a previous detection
                if self.last_detection_time > 0 and self._check_timeout():
                    self.is_human_present = False
                    logger.info("🚶 Human presence lost - detection timeout reached")
                # If no previous detection time, consider human not present
                elif self.last_detection_time == 0:
                    self.is_human_present = False
                    logger.debug("🚶 Human presence lost - no valid targets detected")
            else:
                # Was already not present, stay not present
                self.is_human_present = False
        
        return self.is_human_present
    
    def _is_valid_detection(self, target_info: dict, distance: float) -> bool:
        """
        Check if a target detection is valid based on filtering criteria
        
        Args:
            target_info (dict): Target information
            distance (float): Calculated distance
            
        Returns:
            bool: True if detection is valid
        """
        # Must be within threshold
        if distance > self.proximity_threshold:
            return False
        
        # Filter out very slow or stationary objects (likely noise/reflections)
        speed = abs(target_info['speed'])
        if speed < self.min_speed_threshold:
            logger.debug(f"Filtered out: speed too low ({speed} < {self.min_speed_threshold})")
            return False
        
        # Filter out unrealistic close detections (likely sensor errors)
        if distance < 50:  # 5cm minimum
            logger.debug(f"Filtered out: too close ({distance:.1f}mm < 50mm)")
            return False
        
        return True
    
    def _is_consistent_detection(self, distance: float) -> bool:
        """
        Check if detection is consistent with recent history
        
        Args:
            distance (float): Current detection distance
            
        Returns:
            bool: True if consistent
        """
        if self.last_valid_distance is None:
            return True  # First detection is always considered consistent
        
        distance_change = abs(distance - self.last_valid_distance)
        if distance_change > self.max_distance_change:
            logger.debug(f"Distance change too large: {distance_change:.1f}mm > {self.max_distance_change}mm")
            return False
        
        return True
    
    def _check_timeout_and_update(self) -> bool:
        """
        Check timeout and update presence state when no sensor data
        
        Returns:
            bool: Current presence state after timeout check
        """
        if self.is_human_present and self.last_detection_time > 0:
            if self._check_timeout():
                self.is_human_present = False
                logger.debug("Human presence state changed: True -> False (no data + timeout)")
        elif self.last_detection_time == 0:
            # No previous detection, definitely not present
            self.is_human_present = False
        
        return self.is_human_present
    
    def _check_timeout(self) -> bool:
        """
        Check if detection has timed out
        
        Returns:
            bool: True if timed out (human no longer present)
        """
        if self.last_detection_time == 0:
            return False
        
        return (time.time() - self.last_detection_time) > self.detection_timeout