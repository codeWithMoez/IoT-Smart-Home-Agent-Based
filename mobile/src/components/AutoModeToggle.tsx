/**
 * Auto Mode Toggle Component
 * Controls whether the system operates in automatic or manual mode.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, Switch, Alert } from "react-native";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../services/api";
import { useAppStore } from "../store/appStore";

export default function AutoModeToggle() {
  const { telemetry } = useAppStore();
  const [isEnabled, setIsEnabled] = useState(telemetry?.auto_mode ?? true);

  const toggleMutation = useMutation({
    mutationFn: (enabled: boolean) => apiClient.toggleAutoMode(enabled),
    onSuccess: (data, enabled) => {
      setIsEnabled(enabled);
      Alert.alert(
        "Success",
        `Auto mode ${enabled ? "enabled" : "disabled"}. ${
          enabled
            ? "System will now control devices automatically."
            : "You can now manually control devices."
        }`
      );
    },
    onError: (error: any) => {
      Alert.alert("Error", error.message || "Failed to toggle auto mode");
      // Revert switch state on error
      setIsEnabled(!isEnabled);
    },
  });

  const handleToggle = (value: boolean) => {
    setIsEnabled(value);
    toggleMutation.mutate(value);
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <View style={styles.content}>
          <View style={styles.textContainer}>
            <Text style={styles.title}>Auto Mode</Text>
            <Text style={styles.description}>
              {isEnabled
                ? "System controls devices automatically based on sensor data"
                : "Manual control enabled - you have full control"}
            </Text>
          </View>
          <Switch
            value={isEnabled}
            onValueChange={handleToggle}
            disabled={toggleMutation.isPending}
            trackColor={{ false: "#767577", true: "#81b0ff" }}
            thumbColor={isEnabled ? "#2196F3" : "#f4f3f4"}
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  content: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  textContainer: {
    flex: 1,
    marginRight: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    color: "#666",
    lineHeight: 20,
  },
});
