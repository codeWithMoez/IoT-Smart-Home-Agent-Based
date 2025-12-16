"""
Dependency Injection Container
Manages lifecycle of infrastructure services.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import structlog

from backend.domain import HardwareController, IntentParser, RuntimeMode
from backend.infrastructure import (
    HardwareControllerFactory,
    OpenAIIntentParser,
)
from backend.application import (
    VoiceCommandUseCase,
    GetTelemetryUseCase,
    ManualControlUseCase,
    SystemHealthUseCase,
)
from backend.api.config import Settings

logger = structlog.get_logger(__name__)


class DependencyContainer:
    """
    Dependency Injection container for application services.
    Implements singleton pattern for infrastructure services.
    """
    
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._hardware: HardwareController | None = None
        self._intent_parser: IntentParser | None = None
    
    async def initialize(self) -> None:
        """Initialize infrastructure services."""
        logger.info("initializing_dependencies")
        
        # Parse runtime mode from settings
        runtime_mode = RuntimeMode(self._settings.iot_mode.lower())
        
        # Initialize hardware controller
        self._hardware = await HardwareControllerFactory.create(
            mode=runtime_mode,
            serial_port=self._settings.serial_port,
            baud_rate=self._settings.baud_rate,
        )
        
        # Initialize AI agent
        if self._settings.openai_api_key:
            self._intent_parser = OpenAIIntentParser(
                api_key=self._settings.openai_api_key,
                model=self._settings.openai_model,
            )
            logger.info("openai_agent_initialized")
        else:
            logger.warning("openai_api_key_missing_agent_disabled")
        
        logger.info("dependencies_initialized")
    
    async def shutdown(self) -> None:
        """Cleanup infrastructure services."""
        logger.info("shutting_down_dependencies")
        
        if self._hardware:
            await self._hardware.shutdown()
        
        logger.info("dependencies_shutdown_complete")
    
    @property
    def hardware(self) -> HardwareController:
        """Get hardware controller instance."""
        if not self._hardware:
            raise RuntimeError("Hardware controller not initialized")
        return self._hardware
    
    @property
    def intent_parser(self) -> IntentParser:
        """Get intent parser instance."""
        if not self._intent_parser:
            raise RuntimeError("Intent parser not initialized (check OpenAI API key)")
        return self._intent_parser
    
    def get_voice_command_use_case(self) -> VoiceCommandUseCase:
        """Create VoiceCommandUseCase instance."""
        return VoiceCommandUseCase(
            hardware=self.hardware,
            intent_parser=self.intent_parser,
        )
    
    def get_telemetry_use_case(self) -> GetTelemetryUseCase:
        """Create GetTelemetryUseCase instance."""
        return GetTelemetryUseCase(hardware=self.hardware)
    
    def get_manual_control_use_case(self) -> ManualControlUseCase:
        """Create ManualControlUseCase instance."""
        return ManualControlUseCase(hardware=self.hardware)
    
    def get_health_use_case(self) -> SystemHealthUseCase:
        """Create SystemHealthUseCase instance."""
        return SystemHealthUseCase(hardware=self.hardware)


# Global container instance
_container: DependencyContainer | None = None


def get_container() -> DependencyContainer:
    """
    Get global dependency container.
    
    Returns:
        Initialized container instance
        
    Raises:
        RuntimeError: If container not initialized
    """
    if not _container:
        raise RuntimeError("Dependency container not initialized")
    return _container


def set_container(container: DependencyContainer) -> None:
    """
    Set global dependency container.
    
    Args:
        container: Container instance to use
    """
    global _container
    _container = container


@asynccontextmanager
async def lifespan_manager(settings: Settings) -> AsyncGenerator[DependencyContainer, None]:
    """
    Manage application lifecycle.
    
    Args:
        settings: Application settings
        
    Yields:
        Initialized dependency container
    """
    container = DependencyContainer(settings)
    await container.initialize()
    set_container(container)
    
    try:
        yield container
    finally:
        await container.shutdown()
