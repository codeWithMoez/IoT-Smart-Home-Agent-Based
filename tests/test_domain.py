"""
Unit Tests for Domain Entities
"""
import pytest
from datetime import datetime

from backend.domain import (
    DeviceType,
    DeviceState,
    RuntimeMode,
    SensorReading,
    DeviceCommand,
    TelemetrySnapshot,
    AutoModeCommand,
)


def test_sensor_reading_valid():
    """Test valid sensor reading creation."""
    reading = SensorReading(
        device_type=DeviceType.DHT_SENSOR,
        value=25.5,
        unit="C",
        timestamp=datetime.utcnow(),
    )
    assert reading.value == 25.5
    assert reading.unit == "C"


def test_sensor_reading_negative_value_raises():
    """Test that negative values raise ValueError."""
    with pytest.raises(ValueError):
        SensorReading(
            device_type=DeviceType.DHT_SENSOR,
            value=-10.0,
            unit="C",
            timestamp=datetime.utcnow(),
        )


def test_device_command_to_arduino_format():
    """Test Arduino command format generation."""
    cmd = DeviceCommand(
        device_type=DeviceType.NIGHT_LED,
        state=DeviceState.ON,
        timestamp=datetime.utcnow(),
    )
    assert cmd.to_arduino_format() == "L1"
    
    cmd = DeviceCommand(
        device_type=DeviceType.GARAGE_DOOR,
        state=DeviceState.CLOSED,
        timestamp=datetime.utcnow(),
    )
    assert cmd.to_arduino_format() == "G0"


def test_telemetry_snapshot_valid():
    """Test valid telemetry snapshot creation."""
    telemetry = TelemetrySnapshot(
        timestamp=datetime.utcnow(),
        ldr_value=650,
        garage_distance=20,
        motion_detected=False,
        rain_detected=False,
        water_level=3,
        soil_moisture=750,
        pump_active=False,
        flame_detected=False,
        smoke_level=45,
        temperature=24.5,
        humidity=55.0,
        auto_mode=True,
        runtime_mode=RuntimeMode.SIMULATION,
    )
    assert telemetry.temperature == 24.5
    assert telemetry.auto_mode is True


def test_telemetry_invalid_humidity_raises():
    """Test that invalid humidity raises ValueError."""
    with pytest.raises(ValueError):
        TelemetrySnapshot(
            timestamp=datetime.utcnow(),
            ldr_value=650,
            garage_distance=20,
            motion_detected=False,
            rain_detected=False,
            water_level=3,
            soil_moisture=750,
            pump_active=False,
            flame_detected=False,
            smoke_level=45,
            temperature=24.5,
            humidity=150.0,  # Invalid
            auto_mode=True,
            runtime_mode=RuntimeMode.SIMULATION,
        )


def test_telemetry_auto_mode_logic():
    """Test auto mode logic evaluation."""
    telemetry = TelemetrySnapshot(
        timestamp=datetime.utcnow(),
        ldr_value=600,  # > 500, LED should be ON
        garage_distance=10,  # 5-15cm, should OPEN
        motion_detected=False,
        rain_detected=True,  # Should CLOSE clothes
        water_level=3,  # 1-5cm
        soil_moisture=950,  # > 900, pump should ON
        pump_active=False,
        flame_detected=False,
        smoke_level=45,
        temperature=24.5,
        humidity=55.0,
        auto_mode=True,
        runtime_mode=RuntimeMode.SIMULATION,
    )
    
    commands = telemetry.evaluate_auto_mode_logic()
    
    # Should have 4 commands (LED, Garage, Clothes, Pump)
    assert len(commands) == 4
    
    # Check LED command
    led_cmd = next(c for c in commands if c.device_type == DeviceType.NIGHT_LED)
    assert led_cmd.state == DeviceState.ON
    
    # Check garage command
    garage_cmd = next(c for c in commands if c.device_type == DeviceType.GARAGE_DOOR)
    assert garage_cmd.state == DeviceState.OPEN
    
    # Check clothes command
    clothes_cmd = next(c for c in commands if c.device_type == DeviceType.CLOTHES_SERVO)
    assert clothes_cmd.state == DeviceState.CLOSED
    
    # Check pump command
    pump_cmd = next(c for c in commands if c.device_type == DeviceType.WATER_PUMP)
    assert pump_cmd.state == DeviceState.ON


def test_telemetry_has_emergency():
    """Test emergency detection."""
    telemetry = TelemetrySnapshot(
        timestamp=datetime.utcnow(),
        ldr_value=650,
        garage_distance=20,
        motion_detected=False,
        rain_detected=False,
        water_level=3,
        soil_moisture=750,
        pump_active=False,
        flame_detected=True,  # Emergency!
        smoke_level=45,
        temperature=24.5,
        humidity=55.0,
        auto_mode=True,
        runtime_mode=RuntimeMode.SIMULATION,
    )
    
    assert telemetry.has_emergency() is True


def test_auto_mode_command_format():
    """Test auto mode command Arduino format."""
    cmd = AutoModeCommand(enabled=True, timestamp=datetime.utcnow())
    assert cmd.to_arduino_format() == "A1"
    
    cmd = AutoModeCommand(enabled=False, timestamp=datetime.utcnow())
    assert cmd.to_arduino_format() == "A0"
