"""
Pydantic Models - API Request/Response Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    """Request body for voice command endpoint."""
    transcription: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Speech-to-text transcription of user command"
    )


class VoiceCommandResponse(BaseModel):
    """Response from voice command execution."""
    status: str = Field(
        ...,
        description="Execution status: success, error, clarification_needed, safety_violation"
    )
    actions: list[str] = Field(
        default_factory=list,
        description="List of actions performed"
    )
    question: Optional[str] = Field(
        None,
        description="Clarifying question if status is clarification_needed"
    )
    reason: Optional[str] = Field(
        None,
        description="Error/violation reason"
    )


class ManualControlRequest(BaseModel):
    """Request body for manual device control."""
    device: str = Field(
        ...,
        pattern="^(night_led|garage_door|water_pump|clothes_servo)$",
        description="Device to control"
    )
    action: str = Field(
        ...,
        pattern="^(on|off|open|close)$",
        description="Action to perform"
    )
    manual_override: bool = Field(
        default=False,
        description="Override auto mode"
    )


class AutoModeRequest(BaseModel):
    """Request body for auto mode toggle."""
    enabled: bool = Field(
        ...,
        description="Enable or disable auto mode"
    )


class TelemetryResponse(BaseModel):
    """Telemetry data response."""
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
    runtime_mode: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-16T10:30:00Z",
                "ldr_value": 650,
                "garage_distance": 20,
                "motion_detected": False,
                "rain_detected": False,
                "water_level": 3,
                "soil_moisture": 750,
                "pump_active": False,
                "flame_detected": False,
                "smoke_level": 45,
                "temperature": 24.5,
                "humidity": 55.0,
                "auto_mode": True,
                "runtime_mode": "arduino"
            }
        }


class HealthResponse(BaseModel):
    """System health check response."""
    healthy: bool
    runtime_mode: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
