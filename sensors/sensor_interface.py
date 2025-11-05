from abc import ABC, abstractmethod

class SensorInterface(ABC):
    """Abstract base class for all sensors."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the sensor. Returns True if successful."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up sensor resources."""
        pass    