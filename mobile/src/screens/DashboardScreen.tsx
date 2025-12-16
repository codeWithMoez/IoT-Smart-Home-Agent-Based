/**
 * Main Dashboard Screen
 * Displays real-time telemetry and device controls.
 */
import React, { useEffect } from "react";
import { View, Text, StyleSheet, ScrollView, Alert } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { StatusBar } from "expo-status-bar";
import { apiClient } from "../services/api";
import { wsService } from "../services/websocket";
import { useAppStore } from "../store/appStore";
import TelemetryCard from "../components/TelemetryCard";
import DeviceControls from "../components/DeviceControls";
import VoiceCommandButton from "../components/VoiceCommandButton";
import EmergencyAlert from "../components/EmergencyAlert";
import AutoModeToggle from "../components/AutoModeToggle";

export default function DashboardScreen() {
  const {
    telemetry,
    setTelemetry,
    isConnected,
    setIsConnected,
    showEmergencyAlert,
  } = useAppStore();

  // Health check query
  const { data: healthData } = useQuery({
    queryKey: ["health"],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 5000,
  });

  // WebSocket setup
  useEffect(() => {
    const unsubscribe = wsService.onTelemetry((data) => {
      setTelemetry(data);
      setIsConnected(true);
    });

    wsService.connect();

    return () => {
      unsubscribe();
      wsService.disconnect();
    };
  }, []);

  // Emergency alerts
  useEffect(() => {
    if (showEmergencyAlert) {
      Alert.alert(
        "🚨 EMERGENCY",
        "Fire or smoke detected! Check your home immediately.",
        [{ text: "OK" }]
      );
    }
  }, [showEmergencyAlert]);

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />

      <View style={styles.header}>
        <Text style={styles.title}>IoT Smart Home</Text>
        <View style={styles.statusRow}>
          <View
            style={[
              styles.statusDot,
              isConnected ? styles.online : styles.offline,
            ]}
          />
          <Text style={styles.statusText}>
            {healthData?.runtime_mode.toUpperCase() || "DISCONNECTED"}
          </Text>
        </View>
      </View>

      {showEmergencyAlert && <EmergencyAlert />}

      <ScrollView style={styles.content}>
        {telemetry && <TelemetryCard data={telemetry} />}

        <AutoModeToggle />

        <DeviceControls />

        <VoiceCommandButton />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  header: {
    backgroundColor: "#2196F3",
    padding: 20,
    paddingTop: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "white",
  },
  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  online: {
    backgroundColor: "#4CAF50",
  },
  offline: {
    backgroundColor: "#F44336",
  },
  statusText: {
    color: "white",
    fontSize: 14,
  },
  content: {
    flex: 1,
    padding: 16,
  },
});
