"""
Use Cases - Application Business Logic
Orchestrates domain entities and infrastructure services.
"""
from datetime import datetime
from typing import Optional
import structlog

from backend.domain import (
    HardwareController,
    IntentParser,
    DeviceCommand,
    AutoModeCommand,
    TelemetrySnapshot,
    RuntimeMode,
)

logger = structlog.get_logger(__name__)


class VoiceCommandUseCase:
    """
    Process voice commands through AI agent and execute on hardware.
    """
    
    def __init__(
        self,
        hardware: HardwareController,
        intent_parser: IntentParser,
    ) -> None:
        self._hardware = hardware
        self._intent_parser = intent_parser
    
    async def execute(
        self,
        transcription: str,
    ) -> dict[str, str | list[str]]:
        """
        Execute voice command workflow.
        
        Args:
            transcription: Speech-to-text output
            
        Returns:
            Execution result with status and actions
        """
        logger.info("voice_command_received", transcription=transcription)
        
        # Get current state for context
        current_state = await self._hardware.get_telemetry()
        
        # Parse intent
        parse_result = await self._intent_parser.parse_voice_command(
            transcription,
            current_state
        )
        
        # Handle clarifying question
        if isinstance(parse_result, str):
            logger.info("clarification_needed", question=parse_result)
            return {
                "status": "clarification_needed",
                "question": parse_result,
                "actions": []
            }
        
        # Handle auto mode toggle
        if isinstance(parse_result, AutoModeCommand):
            success = await self._hardware.set_auto_mode(parse_result)
            action = f"Auto mode {'enabled' if parse_result.enabled else 'disabled'}"
            return {
                "status": "success" if success else "error",
                "actions": [action]
            }
        
        # Handle device commands
        commands: list[DeviceCommand] = parse_result
        
        # Safety check
        if current_state:
            is_safe, reason = await self._intent_parser.check_safety(
                commands,
                current_state
            )
            if not is_safe:
                logger.warning("safety_check_failed", reason=reason)
                return {
                    "status": "safety_violation",
                    "reason": reason,
                    "actions": []
                }
        
        # Execute commands
        executed_actions = []
        for cmd in commands:
            success = await self._hardware.send_command(cmd)
            if success:
                action = f"{cmd.device_type.value}: {cmd.state.value}"
                executed_actions.append(action)
                logger.info("command_executed", action=action)
            else:
                logger.error("command_failed", device=cmd.device_type)
        
        return {
            "status": "success" if executed_actions else "error",
            "actions": executed_actions
        }


class GetTelemetryUseCase:
    """
    Retrieve current system telemetry.
    """
    
    def __init__(self, hardware: HardwareController) -> None:
        self._hardware = hardware
    
    async def execute(self) -> Optional[TelemetrySnapshot]:
        """
        Get latest telemetry snapshot.
        
        Returns:
            Current telemetry or None if unavailable
        """
        logger.debug("fetching_telemetry")
        telemetry = await self._hardware.get_telemetry()
        
        if telemetry:
            logger.info(
                "telemetry_retrieved",
                temperature=telemetry.temperature,
                humidity=telemetry.humidity,
                runtime_mode=telemetry.runtime_mode
            )
        else:
            logger.warning("telemetry_unavailable")
        
        return telemetry


class ManualControlUseCase:
    """
    Execute manual device control (bypasses AI agent).
    """
    
    def __init__(self, hardware: HardwareController) -> None:
        self._hardware = hardware
    
    async def execute(self, command: DeviceCommand) -> bool:
        """
        Send manual command to hardware.
        
        Args:
            command: Device command with manual_override=True
            
        Returns:
            True if command was successfully executed
        """
        logger.info(
            "manual_control",
            device=command.device_type,
            state=command.state,
            override=command.manual_override
        )
        
        # Ensure auto mode is disabled for manual control
        current_telemetry = await self._hardware.get_telemetry()
        if current_telemetry and current_telemetry.auto_mode and not command.manual_override:
            logger.warning("manual_control_blocked_by_auto_mode")
            return False
        
        success = await self._hardware.send_command(command)
        
        if success:
            logger.info("manual_control_success")
        else:
            logger.error("manual_control_failed")
        
        return success


class SystemHealthUseCase:
    """
    Monitor system health and connectivity.
    """
    
    def __init__(self, hardware: HardwareController) -> None:
        self._hardware = hardware
    
    async def execute(self) -> dict[str, bool | str]:
        """
        Check system health.
        
        Returns:
            Health status with runtime mode
        """
        is_healthy = await self._hardware.health_check()
        runtime_mode = self._hardware.runtime_mode
        
        logger.info(
            "health_check",
            healthy=is_healthy,
            runtime_mode=runtime_mode
        )
        
        return {
            "healthy": is_healthy,
            "runtime_mode": runtime_mode.value,
        }
