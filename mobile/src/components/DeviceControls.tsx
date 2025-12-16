/**
 * Device Controls Component
 * Manual device control buttons.
 */
import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useMutation } from "@tanstack/react-query";
import { apiClient, ManualControlRequest } from "../services/api";

export default function DeviceControls() {
  const controlMutation = useMutation({
    mutationFn: (request: ManualControlRequest) =>
      apiClient.manualControl(request),
    onSuccess: () => {
      Alert.alert("Success", "Command executed");
    },
    onError: (error: any) => {
      Alert.alert("Error", error.message || "Command failed");
    },
  });

  const handleControl = (
    device: ManualControlRequest["device"],
    action: ManualControlRequest["action"]
  ) => {
    controlMutation.mutate({ device, action, manual_override: false });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manual Controls</Text>

      <View style={styles.deviceRow}>
        <Text style={styles.deviceLabel}>Night LED</Text>
        <View style={styles.buttonRow}>
          <ControlButton
            label="ON"
            onPress={() => handleControl("night_led", "on")}
          />
          <ControlButton
            label="OFF"
            onPress={() => handleControl("night_led", "off")}
          />
        </View>
      </View>

      <View style={styles.deviceRow}>
        <Text style={styles.deviceLabel}>Garage</Text>
        <View style={styles.buttonRow}>
          <ControlButton
            label="OPEN"
            onPress={() => handleControl("garage_door", "open")}
          />
          <ControlButton
            label="CLOSE"
            onPress={() => handleControl("garage_door", "close")}
          />
        </View>
      </View>

      <View style={styles.deviceRow}>
        <Text style={styles.deviceLabel}>Water Pump</Text>
        <View style={styles.buttonRow}>
          <ControlButton
            label="ON"
            onPress={() => handleControl("water_pump", "on")}
          />
          <ControlButton
            label="OFF"
            onPress={() => handleControl("water_pump", "off")}
          />
        </View>
      </View>
    </View>
  );
}

interface ControlButtonProps {
  label: string;
  onPress: () => void;
}

function ControlButton({ label, onPress }: ControlButtonProps) {
  return (
    <TouchableOpacity
      style={styles.button}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.buttonText}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "white",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 16,
  },
  deviceRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  deviceLabel: {
    fontSize: 16,
    color: "#333",
    flex: 1,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 8,
  },
  button: {
    backgroundColor: "#2196F3",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    minWidth: 70,
  },
  buttonText: {
    color: "white",
    fontSize: 14,
    fontWeight: "600",
    textAlign: "center",
  },
});
