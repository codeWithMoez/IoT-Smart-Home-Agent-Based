"""Test configuration."""
import pytest


@pytest.fixture
def mock_telemetry():
    """Fixture providing mock telemetry data."""
    from datetime import datetime
    from backend.domain import TelemetrySnapshot, RuntimeMode
    
    return TelemetrySnapshot(
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
