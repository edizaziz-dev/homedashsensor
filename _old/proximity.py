"""
Proximity detection logic for HomeDashSensor.
Single responsibility: Process sensor data and determine human presence.
"""
import time
import logging
from typing import Optional, List
from dataclasses import dataclass, field
from config import DetectionConfig
from sensors import ProximityReading


@dataclass
class DetectionState:
    """Current proximity detection state."""
    human_present: bool = False
    consecutive_detections: int = 0
    consecutive_non_detections: int = 0
    last_detection_time: float = 0.0
    detection_history: List[bool] = field(default_factory=list)
    
    def add_detection(self, detected: bool) -> None:
        """Add detection result to history."""
        self.detection_history.append(detected)
        # Keep only recent history (last 20 readings for trend analysis)
        if len(self.detection_history) > 20:
            self.detection_history.pop(0)


class ProximityDetector:
    """High-performance proximity detection with advanced filtering."""
    
    def __init__(self, config: DetectionConfig):
        """Initialize proximity detector.
        
        Args:
            config: DetectionConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.state = DetectionState()
        self._last_valid_distance = None
        self._detection_start_time = None
    
    def process_reading(self, reading: Optional[ProximityReading]) -> bool:
        """Process proximity reading and determine human presence.
        
        Args:
            reading: ProximityReading instance or None
            
        Returns:
            True if human is detected, False otherwise
        """
        if not reading or not reading.valid:
            return self._handle_invalid_reading()
        
        # Check if detection criteria are met
        detected = self._is_detection_criteria_met(reading)
        
        # Add to detection history
        self.state.add_detection(detected)
        
        # Update detection counters
        if detected:
            self.state.consecutive_detections += 1
            self.state.consecutive_non_detections = 0
            if not self.state.human_present:
                self._detection_start_time = time.time()
        else:
            self.state.consecutive_detections = 0
            self.state.consecutive_non_detections += 1
        
        # Determine if state should change
        previous_state = self.state.human_present
        
        if not self.state.human_present and self._should_trigger_detection():
            self.state.human_present = True
            self.state.last_detection_time = time.time()
            self.logger.info(f"🙋 Human detected at {reading.distance_mm}mm "
                           f"(zones: {reading.zones_in_range}, consecutive: {self.state.consecutive_detections})")
        
        elif self.state.human_present and self._should_trigger_non_detection():
            self.state.human_present = False
            self.logger.info(f"🚶 Human left detection area "
                           f"(consecutive non-detections: {self.state.consecutive_non_detections})")
        
        # Store last valid distance for trend analysis
        self._last_valid_distance = reading.distance_mm
        
        return self.state.human_present
    
    def _is_detection_criteria_met(self, reading: ProximityReading) -> bool:
        """Check if reading meets detection criteria."""
        # Primary criteria: distance within threshold
        distance_ok = reading.distance_mm <= self.config.threshold_mm
        
        # Secondary criteria: sufficient zones detecting proximity
        zones_ok = reading.zones_in_range >= self.config.detection_zones
        
        # Advanced filtering: movement validation
        movement_ok = self._validate_movement(reading)
        
        return distance_ok and zones_ok and movement_ok
    
    def _validate_movement(self, reading: ProximityReading) -> bool:
        """Validate that movement appears natural (not noise/interference)."""
        if self._last_valid_distance is None:
            return True  # First reading
        
        # Check for unrealistic distance jumps (noise rejection)
        distance_change = abs(reading.distance_mm - self._last_valid_distance)
        max_realistic_change = 300  # 30cm max change between readings (at 10Hz = 3m/s max speed)
        
        if distance_change > max_realistic_change:
            self.logger.debug(f"Rejecting reading: unrealistic distance change "
                            f"({self._last_valid_distance}mm -> {reading.distance_mm}mm)")
            return False
        
        # Additional validation: check zone consistency
        # Human presence should typically activate multiple adjacent zones
        min_zones_for_validation = max(1, self.config.detection_zones - 1)  # Allow 1 less than required
        if reading.distance_mm <= self.config.threshold_mm and reading.zones_in_range < min_zones_for_validation:
            self.logger.debug(f"Rejecting reading: insufficient zone activation "
                            f"({reading.zones_in_range} zones at {reading.distance_mm}mm, need {min_zones_for_validation})")
            return False
        
        return True
    
    def _should_trigger_detection(self) -> bool:
        """Determine if detection should be triggered."""
        return self.state.consecutive_detections >= self.config.consecutive_required
    
    def _should_trigger_non_detection(self) -> bool:
        """Determine if non-detection should be triggered."""
        # Base requirement: consecutive non-detections
        if self.state.consecutive_non_detections < self.config.no_presence_required:
            return False
        
        # Additional check: ensure we had a stable detection before
        if self._detection_start_time is None:
            return True
        
        # Require minimum detection duration to avoid rapid toggling
        min_detection_duration = 2.0  # seconds
        detection_duration = time.time() - self._detection_start_time
        
        return detection_duration >= min_detection_duration
    
    def _handle_invalid_reading(self) -> bool:
        """Handle invalid or missing sensor readings."""
        # Treat invalid readings as non-detections but with reduced weight
        self.state.consecutive_detections = 0
        self.state.consecutive_non_detections += 1
        
        # Only trigger state change if we have many consecutive invalid readings
        if (self.state.human_present and 
            self.state.consecutive_non_detections >= self.config.no_presence_required * 2):
            self.state.human_present = False
            self.logger.warning("🚶 Human presence cleared due to sensor unavailability")
        
        return self.state.human_present
    
    def get_detection_confidence(self) -> float:
        """Get confidence level of current detection (0.0 to 1.0)."""
        if not self.state.detection_history:
            return 0.0
        
        # Calculate confidence based on recent detection history
        recent_detections = sum(self.state.detection_history[-10:])  # Last 10 readings
        confidence = recent_detections / min(10, len(self.state.detection_history))
        
        return confidence
    
    def get_detection_stats(self) -> dict:
        """Get detection statistics for debugging/monitoring."""
        return {
            "human_present": self.state.human_present,
            "consecutive_detections": self.state.consecutive_detections,
            "consecutive_non_detections": self.state.consecutive_non_detections,
            "detection_confidence": self.get_detection_confidence(),
            "last_detection_time": self.state.last_detection_time,
            "detection_history_length": len(self.state.detection_history),
            "recent_detection_rate": sum(self.state.detection_history[-5:]) / min(5, len(self.state.detection_history)) if self.state.detection_history else 0.0
        }
    
    def reset_detection_state(self) -> None:
        """Reset detection state (useful for testing or recalibration)."""
        self.logger.info("🔄 Resetting proximity detection state")
        self.state = DetectionState()
        self._last_valid_distance = None
        self._detection_start_time = None