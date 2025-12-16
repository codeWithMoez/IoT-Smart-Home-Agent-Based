"""
FastAPI Routes - REST API Endpoints
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import structlog

from backend.domain import DeviceCommand, AutoModeCommand, DeviceType, DeviceState
from backend.application import (
    VoiceCommandUseCase,
    GetTelemetryUseCase,
    ManualControlUseCase,
    SystemHealthUseCase,
)
from backend.api.schemas import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    ManualControlRequest,
    AutoModeRequest,
    TelemetryResponse,
    HealthResponse,
    ErrorResponse,
)
from backend.api.dependencies import get_container, DependencyContainer

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_voice_command_uc(
    container: DependencyContainer = Depends(get_container)
) -> VoiceCommandUseCase:
    """Dependency injection for VoiceCommandUseCase."""
    return container.get_voice_command_use_case()


def get_telemetry_uc(
    container: DependencyContainer = Depends(get_container)
) -> GetTelemetryUseCase:
    """Dependency injection for GetTelemetryUseCase."""
    return container.get_telemetry_use_case()


def get_manual_control_uc(
    container: DependencyContainer = Depends(get_container)
) -> ManualControlUseCase:
    """Dependency injection for ManualControlUseCase."""
    return container.get_manual_control_use_case()


def get_health_uc(
    container: DependencyContainer = Depends(get_container)
) -> SystemHealthUseCase:
    """Dependency injection for SystemHealthUseCase."""
    return container.get_health_use_case()


@router.post(
    "/transcribe",
    response_model=dict[str, str],
    responses={500: {"model": ErrorResponse}},
    summary="Transcribe audio to text using OpenAI Whisper",
)
async def transcribe_audio(
    audio: UploadFile = File(...),
    container: DependencyContainer = Depends(get_container),
) -> dict[str, str]:
    """
    Transcribe audio file to text using OpenAI Whisper API.
    
    Accepts audio files in various formats (m4a, mp3, wav, webm, etc.)
    and returns the transcribed text.
    """
    logger.info("api_transcribe_audio", filename=audio.filename)
    
    try:
        # Get the OpenAI client from the intent parser
        intent_parser = container.intent_parser
        transcription = await intent_parser.transcribe_audio(audio)
        
        logger.info("transcription_success", text=transcription[:100])
        return {"transcription": transcription}
        
    except Exception as e:
        logger.error("transcription_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post(
    "/voice-command",
    response_model=VoiceCommandResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Execute voice command via AI agent",
)
async def execute_voice_command(
    request: VoiceCommandRequest,
    use_case: VoiceCommandUseCase = Depends(get_voice_command_uc),
) -> VoiceCommandResponse:
    """
    Process natural language voice command through AI agent.
    
    The AI will interpret the command, check safety constraints,
    and execute appropriate device actions.
    """
    logger.info("api_voice_command", transcription=request.transcription)
    
    try:
        result = await use_case.execute(request.transcription)
        return VoiceCommandResponse(**result)
    except Exception as e:
        logger.error("voice_command_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/manual-control",
    response_model=dict[str, bool],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Manual device control (bypasses AI)",
)
async def manual_control(
    request: ManualControlRequest,
    use_case: ManualControlUseCase = Depends(get_manual_control_uc),
) -> dict[str, bool]:
    """
    Directly control a device without AI interpretation.
    
    Requires auto mode to be disabled unless manual_override is True.
    """
    logger.info(
        "api_manual_control",
        device=request.device,
        action=request.action
    )
    
    try:
        # Map request to domain objects
        device_map = {
            "night_led": DeviceType.NIGHT_LED,
            "garage_door": DeviceType.GARAGE_DOOR,
            "water_pump": DeviceType.WATER_PUMP,
            "clothes_servo": DeviceType.CLOTHES_SERVO,
        }
        
        state_map = {
            "on": DeviceState.ON,
            "off": DeviceState.OFF,
            "open": DeviceState.OPEN,
            "close": DeviceState.CLOSED,
        }
        
        command = DeviceCommand(
            device_type=device_map[request.device],
            state=state_map[request.action],
            timestamp=datetime.utcnow(),
            manual_override=request.manual_override,
        )
        
        success = await use_case.execute(command)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Command failed. Check if auto mode is disabled."
            )
        
        return {"success": True}
        
    except HTTPException:
        # Re-raise HTTPException without catching
        raise
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid device or action: {e}")
    except Exception as e:
        logger.error("manual_control_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/auto-mode",
    response_model=dict[str, bool],
    responses={500: {"model": ErrorResponse}},
    summary="Toggle auto mode",
)
async def toggle_auto_mode(
    request: AutoModeRequest,
    container: DependencyContainer = Depends(get_container),
) -> dict[str, bool]:
    """
    Enable or disable automatic device control based on sensors.
    """
    logger.info("api_auto_mode_toggle", enabled=request.enabled)
    
    try:
        command = AutoModeCommand(
            enabled=request.enabled,
            timestamp=datetime.utcnow(),
        )
        
        success = await container.hardware.set_auto_mode(command)
        return {"success": success}
        
    except Exception as e:
        logger.error("auto_mode_toggle_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/telemetry",
    response_model=TelemetryResponse,
    responses={503: {"model": ErrorResponse}},
    summary="Get current system telemetry",
)
async def get_telemetry(
    use_case: GetTelemetryUseCase = Depends(get_telemetry_uc),
) -> TelemetryResponse:
    """
    Retrieve current sensor readings and device states.
    """
    logger.debug("api_get_telemetry")
    
    telemetry = await use_case.execute()
    
    if not telemetry:
        raise HTTPException(
            status_code=503,
            detail="Telemetry unavailable"
        )
    
    return TelemetryResponse(
        timestamp=telemetry.timestamp,
        ldr_value=telemetry.ldr_value,
        garage_distance=telemetry.garage_distance,
        motion_detected=telemetry.motion_detected,
        rain_detected=telemetry.rain_detected,
        water_level=telemetry.water_level,
        soil_moisture=telemetry.soil_moisture,
        pump_active=telemetry.pump_active,
        flame_detected=telemetry.flame_detected,
        smoke_level=telemetry.smoke_level,
        temperature=telemetry.temperature,
        humidity=telemetry.humidity,
        auto_mode=telemetry.auto_mode,
        runtime_mode=telemetry.runtime_mode.value,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
)
async def health_check(
    use_case: SystemHealthUseCase = Depends(get_health_uc),
) -> HealthResponse:
    """
    Check if hardware is connected and responsive.
    """
    logger.debug("api_health_check")
    
    result = await use_case.execute()
    
    return HealthResponse(
        healthy=result["healthy"],
        runtime_mode=result["runtime_mode"],
        timestamp=datetime.utcnow(),
    )
