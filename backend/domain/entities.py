"""
Domain Entities - Pure Business Objects
NO EXTERNAL DEPENDENCIES ALLOWED
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DeviceType(str, Enum):
    """Hardware device types in the system."""
    NIGHT_LED = "night_led"
    GARAGE_DOOR = "garage_door"
    MOTION_SENSOR = "motion_sensor"
    RAIN_SENSOR = "rain_sensor"
    CLOTHES_SERVO = "clothes_servo"
    WATER_PUMP = "water_pump"
    FLAME_SENSOR = "flame_sensor"
    SMOKE_SENSOR = "smoke_sensor"
    DHT_SENSOR = "dht_sensor"


class DeviceState(str, Enum):
    """Device operational states."""
    ON = "on"
    OFF = "off"
    OPEN = "open"
    CLOSED = "closed"
    DETECTED = "detected"
    NOT_DETECTED = "not_detected"


class RuntimeMode(str, Enum):
    """System runtime modes."""
    AUTO = "auto"
    ARDUINO = "arduino"
    SIMULATION = "simulation"


@dataclass(frozen=True)
class SensorReading:
    """Immutable sensor reading value object."""
    device_type: DeviceType
    value: float
    unit: str
    timestamp: datetime
    
    def __post_init__(self) -> None:
        """Validate sensor reading constraints."""
        if self.value < 0:
            raise ValueError(f"Sensor value cannot be negative: {self.value}")


@dataclass(frozen=True)
class DeviceCommand:
    """Immutable command to be sent to hardware."""
    device_type: DeviceType
    state: DeviceState
    timestamp: datetime
    manual_override: bool = False
    
    def to_arduino_format(self) -> str:
        """
        Convert domain command to Arduino protocol.
        
        Returns:
            str: Command in format <LETTER><0|1>
        """
        command_map = {
            DeviceType.NIGHT_LED: ("L", self.state == DeviceState.ON),
            DeviceType.GARAGE_DOOR: ("G", self.state == DeviceState.OPEN),
            DeviceType.WATER_PUMP: ("P", self.state == DeviceState.ON),
            DeviceType.CLOTHES_SERVO: ("C", self.state == DeviceState.OPEN),
        }
        
        if self.device_type not in command_map:
            raise ValueError(f"Device {self.device_type} does not accept commands")
        
        letter, is_active = command_map[self.device_type]
        return f"{letter}{'1' if is_active else '0'}"


@dataclass
class TelemetrySnapshot:
    """Complete system state at a point in time."""
    timestamp: datetime
    ldr_value: int
    garage_distance: int
    motion_detected: bool
    rain_detected: bool
    water_level: int
    soil_moisture: int
    pump_active: bool
    flame_detected: bool
    smoke_level: int
    temperature: float
    humidity: float
    auto_mode: bool
    runtime_mode: RuntimeMode
    
    def __post_init__(self) -> None:
        """Validate telemetry constraints."""
        if not (0 <= self.ldr_value <= 1023):
            raise ValueError(f"Invalid LDR value: {self.ldr_value}")
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"Invalid humidity: {self.humidity}")
        if self.temperature < -40 or self.temperature > 80:
            raise ValueError(f"Invalid temperature: {self.temperature}")
    
    def evaluate_auto_mode_logic(self) -> list[DeviceCommand]:
        """
        Business logic for automatic device control.
        This mirrors the Arduino firmware logic.
        
        Returns:
            List of commands that should be executed in auto mode.
        """
        if not self.auto_mode:
            return []
        
        commands: list[DeviceCommand] = []
        now = datetime.utcnow()
        
        # Night LED: ON if LDR > 500
        led_state = DeviceState.ON if self.ldr_value > 500 else DeviceState.OFF
        commands.append(DeviceCommand(
            device_type=DeviceType.NIGHT_LED,
            state=led_state,
            timestamp=now,
            manual_override=False
        ))
        
        # Garage: OPEN if distance 5-15cm
        garage_state = (
            DeviceState.OPEN 
            if 5 <= self.garage_distance <= 15 
            else DeviceState.CLOSED
        )
        commands.append(DeviceCommand(
            device_type=DeviceType.GARAGE_DOOR,
            state=garage_state,
            timestamp=now,
            manual_override=False
        ))
        
        # Clothes: CLOSE if rain detected
        clothes_state = (
            DeviceState.CLOSED 
            if self.rain_detected 
            else DeviceState.OPEN
        )
        commands.append(DeviceCommand(
            device_type=DeviceType.CLOTHES_SERVO,
            state=clothes_state,
            timestamp=now,
            manual_override=False
        ))
        
        # Pump: ON if water 1-5cm AND soil > 900
        pump_state = (
            DeviceState.ON 
            if (1 <= self.water_level <= 5 and self.soil_moisture > 900)
            else DeviceState.OFF
        )
        commands.append(DeviceCommand(
            device_type=DeviceType.WATER_PUMP,
            state=pump_state,
            timestamp=now,
            manual_override=False
        ))
        
        return commands
    
    def has_emergency(self) -> bool:
        """Check if emergency conditions exist (fire/smoke)."""
        return self.flame_detected or self.smoke_level > 150


@dataclass
class AutoModeCommand:
    """Special command to toggle auto mode."""
    enabled: bool
    timestamp: datetime
    
    def to_arduino_format(self) -> str:
        """Convert to Arduino protocol."""
        return f"A{'1' if self.enabled else '0'}"
