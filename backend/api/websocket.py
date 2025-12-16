"""
WebSocket Handler - Real-time Telemetry Streaming
"""
import asyncio
import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import structlog

from backend.api.dependencies import get_container

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for telemetry broadcasting.
    """
    
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept new WebSocket connection.
        
        Args:
            websocket: Client WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            "websocket_connected",
            total_connections=len(self.active_connections)
        )
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove WebSocket connection.
        
        Args:
            websocket: Client WebSocket connection
        """
        self.active_connections.remove(websocket)
        logger.info(
            "websocket_disconnected",
            total_connections=len(self.active_connections)
        )
    
    async def broadcast(self, message: dict) -> None:
        """
        Broadcast message to all connected clients.
        
        Args:
            message: JSON-serializable message
        """
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_send_error", error=str(e))
                disconnected.append(connection)
        
        # Clean up dead connections
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time telemetry streaming.
    
    Broadcasts telemetry updates every second to all connected clients.
    """
    await manager.connect(websocket)
    
    try:
        container = get_container()
        telemetry_uc = container.get_telemetry_use_case()
        
        # Keep connection alive and stream telemetry
        while True:
            try:
                # Get latest telemetry
                telemetry = await telemetry_uc.execute()
                
                if telemetry:
                    message = {
                        "type": "telemetry",
                        "timestamp": telemetry.timestamp.isoformat(),
                        "data": {
                            "ldr_value": telemetry.ldr_value,
                            "garage_distance": telemetry.garage_distance,
                            "motion_detected": telemetry.motion_detected,
                            "rain_detected": telemetry.rain_detected,
                            "water_level": telemetry.water_level,
                            "soil_moisture": telemetry.soil_moisture,
                            "pump_active": telemetry.pump_active,
                            "flame_detected": telemetry.flame_detected,
                            "smoke_level": telemetry.smoke_level,
                            "temperature": telemetry.temperature,
                            "humidity": telemetry.humidity,
                            "auto_mode": telemetry.auto_mode,
                            "runtime_mode": telemetry.runtime_mode.value,
                        }
                    }
                    
                    await websocket.send_json(message)
                
                # Wait before next update
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("telemetry_stream_error", error=str(e))
                await asyncio.sleep(1.0)
    
    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected")
    except Exception as e:
        logger.error("websocket_error", error=str(e))
    finally:
        manager.disconnect(websocket)
