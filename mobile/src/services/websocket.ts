/**
 * WebSocket Service - Real-time Telemetry Streaming
 */
import { TelemetryData } from "./api";

type TelemetryCallback = (data: TelemetryData) => void;
type ErrorCallback = (error: Event) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private telemetryCallbacks: Set<TelemetryCallback> = new Set();
  private errorCallbacks: Set<ErrorCallback> = new Set();

  constructor(url: string = "ws://192.168.100.16:8000/ws/telemetry") {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log("WebSocket already connected");
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log("WebSocket connected");
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === "telemetry") {
            this.telemetryCallbacks.forEach((callback) => {
              callback(message.data);
            });
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        this.errorCallbacks.forEach((callback) => callback(error));
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.attemptReconnect();
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      this.attemptReconnect();
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
  }

  onTelemetry(callback: TelemetryCallback): () => void {
    this.telemetryCallbacks.add(callback);
    return () => this.telemetryCallbacks.delete(callback);
  }

  onError(callback: ErrorCallback): () => void {
    this.errorCallbacks.add(callback);
    return () => this.errorCallbacks.delete(callback);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`
    );

    setTimeout(() => {
      this.connect();
    }, delay);
  }
}

export const wsService = new WebSocketService();
