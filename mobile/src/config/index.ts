/**
 * App Configuration
 * Loads environment variables and provides app-wide config
 */

// Get API URL from environment or use default
const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

// Convert http to ws for WebSocket
const WS_URL = API_URL.replace("http://", "ws://").replace(
  "https://",
  "wss://"
);

export const config = {
  // API Configuration
  apiUrl: API_URL,
  wsUrl: `${WS_URL}/ws/telemetry`,

  // Timeouts
  apiTimeout: 10000,
  wsReconnectDelay: 1000,
  wsMaxReconnectAttempts: 5,

  // Development
  isDevelopment: process.env.NODE_ENV === "development",
} as const;

// Log configuration in development
if (config.isDevelopment) {
  console.log("🔧 App Config:", {
    apiUrl: config.apiUrl,
    wsUrl: config.wsUrl,
  });
}
