"""
Serial Hardware Controller - Physical Arduino Communication
"""
import asyncio
import re
from datetime import datetime
from typing import Optional
import structlog
from serial import Serial, SerialException
from serial.tools import list_ports
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from backend.domain import (
    HardwareController,
    TelemetrySnapshot,
    DeviceCommand,
    AutoModeCommand,
    RuntimeMode,
)

logger = structlog.get_logger(__name__)


class SerialHardwareController:
    """
    Production-grade Arduino serial communication controller.
    Implements defensive programming with retry logic.
    """
    
    def __init__(
        self,
        port: Optional[str] = None,
        baud_rate: int = 9600,
        timeout: float = 2.0,
    ) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: Optional[Serial] = None
        self._latest_telemetry: Optional[TelemetrySnapshot] = None
        self._telemetry_lock = asyncio.Lock()
        self._running = False
    
    @property
    def runtime_mode(self) -> RuntimeMode:
        """Runtime mode is always ARDUINO for this controller."""
        return RuntimeMode.ARDUINO
    
    async def initialize(self) -> None:
        """
        Initialize serial connection with auto-detection.
        
        Raises:
            RuntimeError: If Arduino cannot be detected
        """
        logger.info("initializing_serial_controller")
        
        # Auto-detect Arduino port if not specified
        if not self._port:
            self._port = self._detect_arduino_port()
        
        if not self._port:
            raise RuntimeError(
                "Arduino not detected. Ensure device is connected via USB."
            )
        
        try:
            self._serial = Serial(
                port=self._port,
                baudrate=self._baud_rate,
                timeout=self._timeout,
            )
            # Wait for Arduino to reset (DTR toggle)
            await asyncio.sleep(2)
            
            # Flush any initial garbage
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            
            logger.info(
                "serial_connection_established",
                port=self._port,
                baud_rate=self._baud_rate
            )
            
            # Start telemetry reader task
            self._running = True
            asyncio.create_task(self._telemetry_reader_loop())
            
        except SerialException as e:
            logger.error("serial_connection_failed", error=str(e))
            raise RuntimeError(f"Failed to open serial port {self._port}: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully close serial connection."""
        logger.info("shutting_down_serial_controller")
        self._running = False
        
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info("serial_connection_closed")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(SerialException),
    )
    async def send_command(self, command: DeviceCommand) -> bool:
        """
        Send command to Arduino with retry logic.
        
        Args:
            command: Device command to execute
            
        Returns:
            True if command was successfully sent
        """
        if not self._serial or not self._serial.is_open:
            logger.error("serial_not_connected")
            return False
        
        arduino_cmd = command.to_arduino_format()
        
        try:
            # Run blocking I/O in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_raw,
                arduino_cmd
            )
            
            logger.info(
                "command_sent",
                device=command.device_type,
                raw_command=arduino_cmd
            )
            return True
            
        except SerialException as e:
            logger.error("command_send_failed", error=str(e))
            raise
    
    async def set_auto_mode(self, command: AutoModeCommand) -> bool:
        """
        Toggle auto mode on Arduino.
        
        Args:
            command: Auto mode configuration
            
        Returns:
            True if command was successfully sent
        """
        if not self._serial or not self._serial.is_open:
            logger.error("serial_not_connected")
            return False
        
        arduino_cmd = command.to_arduino_format()
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_raw,
                arduino_cmd
            )
            
            logger.info("auto_mode_toggled", enabled=command.enabled)
            return True
            
        except SerialException as e:
            logger.error("auto_mode_toggle_failed", error=str(e))
            return False
    
    async def get_telemetry(self) -> Optional[TelemetrySnapshot]:
        """
        Get latest telemetry snapshot.
        
        Returns:
            Most recent telemetry or None
        """
        async with self._telemetry_lock:
            return self._latest_telemetry
    
    async def health_check(self) -> bool:
        """
        Check if serial connection is healthy.
        
        Returns:
            True if connection is active and recent telemetry exists
        """
        if not self._serial or not self._serial.is_open:
            return False
        
        # Check if we've received telemetry in the last 5 seconds
        if self._latest_telemetry:
            age = (datetime.utcnow() - self._latest_telemetry.timestamp).total_seconds()
            return age < 5
        
        return False
    
    def _send_raw(self, command: str) -> None:
        """
        Synchronous raw serial write (runs in executor).
        
        Args:
            command: Raw command string
        """
        if self._serial:
            self._serial.write(f"{command}\n".encode('ascii'))
            self._serial.flush()
    
    async def _telemetry_reader_loop(self) -> None:
        """
        Background task to continuously read telemetry.
        Runs for the lifetime of the controller.
        """
        logger.info("telemetry_reader_started")
        
        while self._running:
            try:
                if self._serial and self._serial.is_open:
                    # Read line in executor (blocking I/O)
                    loop = asyncio.get_event_loop()
                    line = await loop.run_in_executor(
                        None,
                        self._serial.readline
                    )
                    
                    if line:
                        decoded = line.decode('ascii', errors='ignore').strip()
                        telemetry = self._parse_telemetry(decoded)
                        
                        if telemetry:
                            async with self._telemetry_lock:
                                self._latest_telemetry = telemetry
                            logger.debug("telemetry_updated", line=decoded)
                
                await asyncio.sleep(0.1)  # Small delay to prevent tight loop
                
            except Exception as e:
                logger.error("telemetry_reader_error", error=str(e))
                await asyncio.sleep(1)
        
        logger.info("telemetry_reader_stopped")
    
    def _parse_telemetry(self, line: str) -> Optional[TelemetrySnapshot]:
        """
        Parse Arduino telemetry string into TelemetrySnapshot.
        
        Expected format:
        LDR: <val> | Garage Dist: <cm> | Motion!/No Motion | Rain!/No Rain | 
        Water Lvl: <cm> | Soil: <val> | Pump ON/Pump OFF | Flame: YES/NO | 
        Smoke: <val> | Temp: <C> | Hum: <percent>
        
        Args:
            line: Raw telemetry line from Arduino
            
        Returns:
            Parsed TelemetrySnapshot or None if parsing fails
        """
        try:
            # Regex patterns for each field
            ldr_match = re.search(r'LDR:\s*(\d+)', line)
            garage_match = re.search(r'Garage Dist:\s*(\d+)\s*cm', line)
            motion_match = re.search(r'(Motion!|No Motion)', line)
            rain_match = re.search(r'(Rain!|No Rain)', line)
            water_match = re.search(r'Water Lvl:\s*(\d+)\s*cm', line)
            soil_match = re.search(r'Soil:\s*(\d+)', line)
            pump_match = re.search(r'Pump (ON|OFF)', line)
            flame_match = re.search(r'Flame:\s*(YES|NO)', line)
            smoke_match = re.search(r'Smoke:\s*(\d+)', line)
            temp_match = re.search(r'Temp:\s*([\d.]+)\s*C', line)
            hum_match = re.search(r'Hum:\s*([\d.]+)%', line)
            
            if not all([
                ldr_match, garage_match, motion_match, rain_match,
                water_match, soil_match, pump_match, flame_match,
                smoke_match, temp_match, hum_match
            ]):
                return None
            
            return TelemetrySnapshot(
                timestamp=datetime.utcnow(),
                ldr_value=int(ldr_match.group(1)),
                garage_distance=int(garage_match.group(1)),
                motion_detected=motion_match.group(1) == "Motion!",
                rain_detected=rain_match.group(1) == "Rain!",
                water_level=int(water_match.group(1)),
                soil_moisture=int(soil_match.group(1)),
                pump_active=pump_match.group(1) == "ON",
                flame_detected=flame_match.group(1) == "YES",
                smoke_level=int(smoke_match.group(1)),
                temperature=float(temp_match.group(1)),
                humidity=float(hum_match.group(1)),
                auto_mode=True,  # Assume auto mode unless explicitly toggled
                runtime_mode=RuntimeMode.ARDUINO
            )
            
        except (ValueError, AttributeError) as e:
            logger.warning("telemetry_parse_error", error=str(e), line=line)
            return None
    
    def _detect_arduino_port(self) -> Optional[str]:
        """
        Auto-detect Arduino USB port.
        
        Returns:
            Port name or None if not found
        """
        ports = list_ports.comports()
        
        for port in ports:
            # Look for common Arduino identifiers
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'ch341']):
                logger.info("arduino_detected", port=port.device)
                return port.device
        
        logger.warning("arduino_not_detected")
        return None
