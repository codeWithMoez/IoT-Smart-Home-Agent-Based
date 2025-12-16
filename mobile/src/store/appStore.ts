/**
 * State Management - Zustand Store
 * Global application state with TypeScript type safety.
 */
import { create } from "zustand";
import { TelemetryData } from "../services/api";

interface AppState {
  // Telemetry state
  telemetry: TelemetryData | null;
  setTelemetry: (data: TelemetryData) => void;

  // Connection state
  isConnected: boolean;
  setIsConnected: (connected: boolean) => void;

  // Voice command state
  isRecording: boolean;
  setIsRecording: (recording: boolean) => void;

  lastCommandResponse: string;
  setLastCommandResponse: (response: string) => void;

  // UI state
  showEmergencyAlert: boolean;
  setShowEmergencyAlert: (show: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Telemetry
  telemetry: null,
  setTelemetry: (data) => {
    set({ telemetry: data });

    // Check for emergencies
    if (data.flame_detected || data.smoke_level > 150) {
      set({ showEmergencyAlert: true });
    } else {
      set({ showEmergencyAlert: false });
    }
  },

  // Connection
  isConnected: false,
  setIsConnected: (connected) => set({ isConnected: connected }),

  // Voice
  isRecording: false,
  setIsRecording: (recording) => set({ isRecording: recording }),

  lastCommandResponse: "",
  setLastCommandResponse: (response) => set({ lastCommandResponse: response }),

  // UI
  showEmergencyAlert: false,
  setShowEmergencyAlert: (show) => set({ showEmergencyAlert: show }),
}));
