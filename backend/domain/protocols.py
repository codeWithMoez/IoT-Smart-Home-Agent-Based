"""
Domain Protocols - Interface Definitions
Defines contracts without implementation details.
"""
from abc import abstractmethod
from typing import Protocol, Optional

from backend.domain.entities import (
    TelemetrySnapshot,
    DeviceCommand,
    AutoModeCommand,
    RuntimeMode,
)


class HardwareController(Protocol):
    """
    Hardware Abstraction Layer (HAL) Protocol.
    All hardware implementations must conform to this interface.
    """
    
    @property
    @abstractmethod
    def runtime_mode(self) -> RuntimeMode:
        """Get the current runtime mode."""
        ...
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize hardware connection."""
        ...
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown hardware connection."""
        ...
    
    @abstractmethod
    async def send_command(self, command: DeviceCommand) -> bool:
        """
        Send a command to the hardware.
        
        Args:
            command: The device command to execute
            
        Returns:
            True if command was successfully sent
        """
        ...
    
    @abstractmethod
    async def set_auto_mode(self, command: AutoModeCommand) -> bool:
        """
        Toggle auto mode on hardware.
        
        Args:
            command: Auto mode configuration
            
        Returns:
            True if command was successfully sent
        """
        ...
    
    @abstractmethod
    async def get_telemetry(self) -> Optional[TelemetrySnapshot]:
        """
        Read current telemetry from hardware.
        
        Returns:
            Latest telemetry snapshot or None if unavailable
        """
        ...
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if hardware is responsive.
        
        Returns:
            True if hardware is healthy
        """
        ...


class IntentParser(Protocol):
    """
    AI Agent Protocol for natural language understanding.
    """
    
    @abstractmethod
    async def parse_voice_command(
        self,
        transcription: str,
        current_state: Optional[TelemetrySnapshot] = None
    ) -> list[DeviceCommand] | AutoModeCommand | str:
        """
        Parse natural language into device commands.
        
        Args:
            transcription: User's speech-to-text output
            current_state: Current system state for context
            
        Returns:
            - List of DeviceCommands if intent is clear
            - AutoModeCommand if toggling auto mode
            - Clarifying question string if ambiguous
        """
        ...
    
    @abstractmethod
    async def check_safety(
        self,
        commands: list[DeviceCommand],
        current_state: TelemetrySnapshot
    ) -> tuple[bool, str]:
        """
        Validate commands for safety constraints.
        
        Args:
            commands: Commands to validate
            current_state: Current system state
            
        Returns:
            (is_safe, reason) tuple
        """
        ...
