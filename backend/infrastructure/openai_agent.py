"""
OpenAI Agent - LLM-based Intent Parser with Function Calling
"""
from datetime import datetime
from typing import Optional, Any
import json
import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from backend.domain import (
    IntentParser,
    DeviceCommand,
    AutoModeCommand,
    TelemetrySnapshot,
    DeviceType,
    DeviceState,
)

logger = structlog.get_logger(__name__)


class OpenAIIntentParser:
    """
    GPT-4o-mini powered intent parser using function calling.
    Converts natural language to structured device commands.
    """
    
    SYSTEM_PROMPT = """You are an AI assistant for a smart home IoT system.
Your role is to interpret user voice commands and convert them into device actions.

Available devices:
- Night LED: Can be turned on/off
- Garage Door: Can be opened/closed
- Water Pump: Can be turned on/off
- Clothes Servo: Can be opened/closed (for rain protection)

System modes:
- Auto Mode: When enabled, devices are controlled by sensors automatically
- Manual Mode: When disabled, devices respond to user commands

Safety rules:
1. Never disable auto mode during fire/smoke emergencies
2. If user command conflicts with auto mode logic, ask for confirmation
3. If command is ambiguous, ask clarifying questions
4. Always prioritize user safety

Current system state will be provided for context."""
    
    FUNCTIONS = [
        {
            "name": "control_device",
            "description": "Control a specific smart home device",
            "parameters": {
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "enum": ["night_led", "garage_door", "water_pump", "clothes_servo"],
                        "description": "The device to control"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["on", "off", "open", "close"],
                        "description": "The action to perform"
                    },
                    "manual_override": {
                        "type": "boolean",
                        "description": "Whether to override auto mode",
                        "default": False
                    }
                },
                "required": ["device", "action"]
            }
        },
        {
            "name": "toggle_auto_mode",
            "description": "Enable or disable automatic device control",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "True to enable auto mode, False to disable"
                    }
                },
                "required": ["enabled"]
            }
        },
        {
            "name": "ask_clarification",
            "description": "Ask user a clarifying question when command is ambiguous",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The clarifying question to ask"
                    }
                },
                "required": ["question"]
            }
        }
    ]
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
    
    async def parse_voice_command(
        self,
        transcription: str,
        current_state: Optional[TelemetrySnapshot] = None
    ) -> list[DeviceCommand] | AutoModeCommand | str:
        """
        Parse natural language into device commands using GPT-4o-mini.
        
        Args:
            transcription: User's speech-to-text output
            current_state: Current system state for context
            
        Returns:
            - List of DeviceCommands if intent is clear
            - AutoModeCommand if toggling auto mode
            - Clarifying question string if ambiguous
        """
        logger.info("parsing_voice_command", transcription=transcription)
        
        # Build context message
        context = self._build_context_message(current_state)
        
        try:
            response: ChatCompletion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "system", "content": context},
                    {"role": "user", "content": transcription}
                ],
                functions=self.FUNCTIONS,
                function_call="auto",
                temperature=0.3,
            )
            
            message = response.choices[0].message
            
            # Handle function call
            if message.function_call:
                return self._process_function_call(
                    message.function_call.name,
                    message.function_call.arguments
                )
            
            # If no function call, treat as clarification
            return message.content or "I didn't understand that. Could you rephrase?"
            
        except Exception as e:
            logger.error("openai_api_error", error=str(e))
            return "I'm having trouble processing that command. Please try again."
    
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
        # Check for emergency conditions
        if current_state.has_emergency():
            # Don't allow disabling auto mode during emergencies
            if any(cmd.device_type == DeviceType.NIGHT_LED for cmd in commands):
                return (
                    False,
                    "Cannot control lights during fire/smoke emergency. Auto mode must remain active."
                )
        
        # Check for auto mode conflicts
        if current_state.auto_mode:
            manual_commands = [cmd for cmd in commands if not cmd.manual_override]
            if manual_commands:
                return (
                    False,
                    "Auto mode is active. Disable auto mode first or use manual override."
                )
        
        return (True, "")
    
    def _build_context_message(
        self,
        state: Optional[TelemetrySnapshot]
    ) -> str:
        """
        Build context message from current system state.
        
        Args:
            state: Current telemetry
            
        Returns:
            Formatted context string
        """
        if not state:
            return "Current system state: Unknown (no telemetry available)"
        
        context_parts = [
            "Current system state:",
            f"- Auto Mode: {'ON' if state.auto_mode else 'OFF'}",
            f"- Runtime: {state.runtime_mode.value.upper()}",
            f"- Temperature: {state.temperature}°C",
            f"- Humidity: {state.humidity}%",
            f"- Light Level: {state.ldr_value} (threshold: 500)",
            f"- Motion: {'DETECTED' if state.motion_detected else 'None'}",
            f"- Rain: {'YES' if state.rain_detected else 'No'}",
            f"- Pump: {'ON' if state.pump_active else 'OFF'}",
        ]
        
        if state.has_emergency():
            context_parts.append("⚠️ EMERGENCY: Fire or smoke detected!")
        
        return "\n".join(context_parts)
    
    def _process_function_call(
        self,
        function_name: str,
        arguments: str
    ) -> list[DeviceCommand] | AutoModeCommand | str:
        """
        Process LLM function call into domain objects.
        
        Args:
            function_name: Name of called function
            arguments: JSON arguments
            
        Returns:
            Appropriate domain object
        """
        try:
            args: dict[str, Any] = json.loads(arguments)
            
            if function_name == "control_device":
                return self._create_device_commands(args)
            
            elif function_name == "toggle_auto_mode":
                return AutoModeCommand(
                    enabled=args["enabled"],
                    timestamp=datetime.utcnow()
                )
            
            elif function_name == "ask_clarification":
                return args["question"]
            
            else:
                logger.warning("unknown_function_call", function=function_name)
                return "I'm not sure how to handle that command."
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("function_call_parse_error", error=str(e))
            return "I had trouble processing that command."
    
    def _create_device_commands(
        self,
        args: dict[str, Any]
    ) -> list[DeviceCommand]:
        """
        Create DeviceCommand from function call arguments.
        
        Args:
            args: Function call arguments
            
        Returns:
            List containing single DeviceCommand
        """
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
        
        device_type = device_map[args["device"]]
        state = state_map[args["action"]]
        manual_override = args.get("manual_override", False)
        
        return [DeviceCommand(
            device_type=device_type,
            state=state,
            timestamp=datetime.utcnow(),
            manual_override=manual_override
        )]
    
    async def transcribe_audio(self, audio_file: Any) -> str:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file: UploadFile object containing audio data
            
        Returns:
            Transcribed text
        """
        logger.info("transcribing_audio", filename=audio_file.filename)
        
        try:
            # Read audio file content
            audio_content = await audio_file.read()
            
            # Create a file-like object for the OpenAI API
            # The API expects a file with a name and content
            audio_file_obj = (audio_file.filename, audio_content, audio_file.content_type)
            
            # Call Whisper API for transcription
            response = await self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_obj,
                language="en"  # Set to English, or remove to auto-detect
            )
            
            transcription = response.text
            logger.info("transcription_complete", length=len(transcription))
            
            return transcription
            
        except Exception as e:
            logger.error("whisper_api_error", error=str(e))
            raise
