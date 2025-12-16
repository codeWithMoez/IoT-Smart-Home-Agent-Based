"""
Hardware Controller Factory - Runtime Mode Selection
Implements AUTO mode with fallback logic.
"""
import structlog
from typing import Optional

from backend.domain import HardwareController, RuntimeMode
from backend.infrastructure.serial_controller import SerialHardwareController
from backend.infrastructure.simulation_controller import SimulatedHardwareController

logger = structlog.get_logger(__name__)


class HardwareControllerFactory:
    """
    Factory for creating appropriate hardware controller based on runtime mode.
    Implements AUTO mode with Arduino-first fallback.
    """
    
    @staticmethod
    async def create(
        mode: RuntimeMode,
        serial_port: Optional[str] = None,
        baud_rate: int = 9600,
    ) -> HardwareController:
        """
        Create and initialize hardware controller.
        
        Args:
            mode: Desired runtime mode (AUTO, ARDUINO, SIMULATION)
            serial_port: Optional serial port for Arduino
            baud_rate: Serial baud rate
            
        Returns:
            Initialized hardware controller
            
        Raises:
            RuntimeError: If ARDUINO mode requested but hardware unavailable
        """
        logger.info("creating_hardware_controller", mode=mode.value)
        
        if mode == RuntimeMode.ARDUINO:
            controller = SerialHardwareController(
                port=serial_port,
                baud_rate=baud_rate
            )
            await controller.initialize()
            logger.info("arduino_controller_initialized")
            return controller
        
        elif mode == RuntimeMode.SIMULATION:
            controller = SimulatedHardwareController()
            await controller.initialize()
            logger.info("simulation_controller_initialized")
            return controller
        
        elif mode == RuntimeMode.AUTO:
            # Try Arduino first, fallback to Simulation
            logger.info("auto_mode_attempting_arduino")
            try:
                controller = SerialHardwareController(
                    port=serial_port,
                    baud_rate=baud_rate
                )
                await controller.initialize()
                logger.info("auto_mode_using_arduino")
                return controller
            
            except RuntimeError as e:
                logger.warning(
                    "auto_mode_arduino_failed_falling_back",
                    error=str(e)
                )
                controller = SimulatedHardwareController()
                await controller.initialize()
                logger.info("auto_mode_using_simulation")
                return controller
        
        else:
            raise ValueError(f"Unknown runtime mode: {mode}")
