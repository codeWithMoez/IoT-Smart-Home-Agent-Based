"""
Simulated Hardware Controller - High-Fidelity Virtual Environment
Implements exact Arduino logic in software for testing without physical hardware.
"""
import asyncio
import random
from datetime import datetime
from typing import Optional
import structlog

from backend.domain import (
    HardwareController,
    TelemetrySnapshot,
    DeviceCommand,
    AutoModeCommand,
    RuntimeMode,
    DeviceType,
    DeviceState,
)

logger = structlog.get_logger(__name__)


class SimulatedEnvironment:
    """
    Virtual environment with realistic sensor drift and physics.
    """
    
    def __init__(self) -> None:
        # Environmental state (with random walk)
        self.ambient_light: float = 300.0  # LDR value
        self.garage_distance: float = 50.0  # cm
        self.has_motion: bool = False
        self.is_raining: bool = False
        self.water_level: float = 3.0  # cm
        self.soil_moisture: float = 600.0  # analog value
        self.flame_present: bool = False
        self.smoke_level: float = 50.0
        self.temperature: float = 24.0  # Celsius
        self.humidity: float = 45.0  # percent
        
        # Device states
        self.night_led_on: bool = False
        self.garage_open: bool = False
        self.clothes_servo_open: bool = True
        self.pump_on: bool = False
        
        # Auto mode
        self.auto_mode: bool = True
    
    def update(self, delta_time: float) -> None:
        """
        Update environment with realistic drift.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        # Random walk for light (day/night cycle simulation)
        self.ambient_light += random.uniform(-20, 20)
        self.ambient_light = max(0, min(1023, self.ambient_light))
        
        # Garage distance (simulate car approaching/leaving)
        self.garage_distance += random.uniform(-2, 2)
        self.garage_distance = max(1, min(100, self.garage_distance))
        
        # Random motion events (5% chance per update)
        self.has_motion = random.random() < 0.05
        
        # Rain events (2% chance to toggle)
        if random.random() < 0.02:
            self.is_raining = not self.is_raining
        
        # Water level changes (evaporation when pump off, fill when pump on)
        if self.pump_on:
            self.water_level -= 0.1 * delta_time
        else:
            self.water_level += 0.05 * delta_time
        self.water_level = max(0, min(20, self.water_level))
        
        # Soil moisture (dries out over time, refills when pump on)
        if self.pump_on:
            self.soil_moisture -= 10 * delta_time
        else:
            self.soil_moisture += 5 * delta_time
        self.soil_moisture = max(0, min(1023, self.soil_moisture))
        
        # Fire/smoke (rare emergency events - 0.1% chance)
        if random.random() < 0.001:
            self.flame_present = True
            self.smoke_level = 200
        else:
            self.flame_present = False
            self.smoke_level = max(20, self.smoke_level - 5 * delta_time)
        
        # Temperature and humidity drift
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(-10, min(40, self.temperature))
        
        self.humidity += random.uniform(-1, 1)
        self.humidity = max(0, min(100, self.humidity))
    
    def apply_auto_mode_logic(self) -> None:
        """
        Apply Arduino auto mode logic to device states.
        This mirrors the exact logic in arduino_code.ino.
        """
        if not self.auto_mode:
            return
        
        # Night LED: ON if LDR > 500
        self.night_led_on = self.ambient_light > 500
        
        # Garage: OPEN if distance 5-15cm
        self.garage_open = 5 <= self.garage_distance <= 15
        
        # Clothes: CLOSE if raining
        self.clothes_servo_open = not self.is_raining
        
        # Pump: ON if water 1-5cm AND soil > 900
        self.pump_on = (
            1 <= self.water_level <= 5 and 
            self.soil_moisture > 900
        )


class SimulatedHardwareController:
    """
    Production-grade simulation controller for testing without hardware.
    Implements identical interface to SerialHardwareController.
    """
    
    def __init__(self, update_interval: float = 1.0) -> None:
        self._env = SimulatedEnvironment()
        self._update_interval = update_interval
        self._running = False
        self._last_update_time = datetime.utcnow()
    
    @property
    def runtime_mode(self) -> RuntimeMode:
        """Runtime mode is always SIMULATION for this controller."""
        return RuntimeMode.SIMULATION
    
    async def initialize(self) -> None:
        """Initialize simulation environment."""
        logger.info("initializing_simulation_controller")
        self._running = True
        self._last_update_time = datetime.utcnow()
        
        # Start simulation loop
        asyncio.create_task(self._simulation_loop())
        
        logger.info("simulation_initialized")
    
    async def shutdown(self) -> None:
        """Shutdown simulation."""
        logger.info("shutting_down_simulation")
        self._running = False
    
    async def send_command(self, command: DeviceCommand) -> bool:
        """
        Apply command to simulated devices.
        
        Args:
            command: Device command to execute
            
        Returns:
            Always True (simulation cannot fail)
        """
        logger.info(
            "simulation_command",
            device=command.device_type,
            state=command.state,
            manual=command.manual_override
        )
        
        # Manual commands only work when auto mode is off
        if self._env.auto_mode and not command.manual_override:
            logger.warning("simulation_command_blocked_by_auto_mode")
            return False
        
        # Apply command to environment
        if command.device_type == DeviceType.NIGHT_LED:
            self._env.night_led_on = command.state == DeviceState.ON
        elif command.device_type == DeviceType.GARAGE_DOOR:
            self._env.garage_open = command.state == DeviceState.OPEN
        elif command.device_type == DeviceType.CLOTHES_SERVO:
            self._env.clothes_servo_open = command.state == DeviceState.OPEN
        elif command.device_type == DeviceType.WATER_PUMP:
            self._env.pump_on = command.state == DeviceState.ON
        
        return True
    
    async def set_auto_mode(self, command: AutoModeCommand) -> bool:
        """
        Toggle auto mode in simulation.
        
        Args:
            command: Auto mode configuration
            
        Returns:
            Always True
        """
        self._env.auto_mode = command.enabled
        logger.info("simulation_auto_mode_toggled", enabled=command.enabled)
        return True
    
    async def get_telemetry(self) -> Optional[TelemetrySnapshot]:
        """
        Get current simulated telemetry.
        
        Returns:
            Simulated telemetry snapshot
        """
        try:
            return TelemetrySnapshot(
                timestamp=datetime.utcnow(),
                ldr_value=int(self._env.ambient_light),
                garage_distance=int(self._env.garage_distance),
                motion_detected=self._env.has_motion,
                rain_detected=self._env.is_raining,
                water_level=int(self._env.water_level),
                soil_moisture=int(self._env.soil_moisture),
                pump_active=self._env.pump_on,
                flame_detected=self._env.flame_present,
                smoke_level=int(self._env.smoke_level),
                temperature=round(self._env.temperature, 1),
                humidity=round(self._env.humidity, 1),
                auto_mode=self._env.auto_mode,
                runtime_mode=RuntimeMode.SIMULATION
            )
        except ValueError as e:
            logger.error("simulation_telemetry_error", error=str(e))
            return None
    
    async def health_check(self) -> bool:
        """
        Simulation is always healthy.
        
        Returns:
            Always True
        """
        return self._running
    
    async def _simulation_loop(self) -> None:
        """
        Background task to update simulation environment.
        """
        logger.info("simulation_loop_started")
        
        while self._running:
            try:
                current_time = datetime.utcnow()
                delta = (current_time - self._last_update_time).total_seconds()
                self._last_update_time = current_time
                
                # Update environment physics
                self._env.update(delta)
                
                # Apply auto mode logic (mirrors Arduino firmware)
                self._env.apply_auto_mode_logic()
                
                logger.debug(
                    "simulation_tick",
                    light=self._env.ambient_light,
                    temp=self._env.temperature,
                    auto_mode=self._env.auto_mode
                )
                
                await asyncio.sleep(self._update_interval)
                
            except Exception as e:
                logger.error("simulation_loop_error", error=str(e))
                await asyncio.sleep(1)
        
        logger.info("simulation_loop_stopped")
