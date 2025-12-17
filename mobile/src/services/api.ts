/**
 * API Client - Backend Communication Layer
 * Type-safe HTTP client for all backend endpoints.
 */
import axios, { AxiosInstance } from "axios";
import { config } from "../config";

export interface TelemetryData {
  timestamp: string;
  ldr_value: number;
  garage_distance: number;
  motion_detected: boolean;
  rain_detected: boolean;
  water_level: number;
  soil_moisture: number;
  pump_active: boolean;
  flame_detected: boolean;
  smoke_level: number;
  temperature: number;
  humidity: number;
  auto_mode: boolean;
  runtime_mode: "arduino" | "simulation" | "auto";
}

export interface VoiceCommandRequest {
  transcription: string;
}

export interface VoiceCommandResponse {
  status: "success" | "error" | "clarification_needed" | "safety_violation";
  actions: string[];
  question?: string;
  reason?: string;
}

export interface ManualControlRequest {
  device: "night_led" | "garage_door" | "water_pump" | "clothes_servo";
  action: "on" | "off" | "open" | "close";
  manual_override?: boolean;
}

export interface HealthResponse {
  healthy: boolean;
  runtime_mode: string;
  timestamp: string;
}

export class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = config.apiUrl) {
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      timeout: config.apiTimeout,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  async transcribeAudio(audioUri: string): Promise<{ transcription: string }> {
    const formData = new FormData();

    // Create file object from URI
    const filename = audioUri.split("/").pop() || "recording.m4a";
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `audio/${match[1]}` : "audio/m4a";

    formData.append("audio", {
      uri: audioUri,
      name: filename,
      type: type,
    } as any);

    const response = await this.client.post<{ transcription: string }>(
      "/transcribe",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 30000, // 30 seconds for transcription
      }
    );
    return response.data;
  }

  async sendVoiceCommand(transcription: string): Promise<VoiceCommandResponse> {
    const response = await this.client.post<VoiceCommandResponse>(
      "/voice-command",
      { transcription }
    );
    return response.data;
  }

  async manualControl(
    request: ManualControlRequest
  ): Promise<{ success: boolean }> {
    const response = await this.client.post<{ success: boolean }>(
      "/manual-control",
      request
    );
    return response.data;
  }

  async toggleAutoMode(enabled: boolean): Promise<{ success: boolean }> {
    const response = await this.client.post<{ success: boolean }>(
      "/auto-mode",
      { enabled }
    );
    return response.data;
  }

  async getTelemetry(): Promise<TelemetryData> {
    const response = await this.client.get<TelemetryData>("/telemetry");
    return response.data;
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>("/health");
    return response.data;
  }
}

export const apiClient = new ApiClient();
