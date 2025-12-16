/**
 * Telemetry Card Component
 * Displays sensor readings in a grid layout.
 */
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { TelemetryData } from "../services/api";

interface Props {
  data: TelemetryData;
}

export default function TelemetryCard({ data }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>System Status</Text>

      <View style={styles.grid}>
        <SensorItem
          label="Temperature"
          value={`${data.temperature}°C`}
          alert={data.temperature > 30}
        />
        <SensorItem label="Humidity" value={`${data.humidity}%`} />
        <SensorItem label="Light" value={data.ldr_value.toString()} />
        <SensorItem label="Garage" value={`${data.garage_distance} cm`} />
        <SensorItem
          label="Motion"
          value={data.motion_detected ? "YES" : "No"}
          alert={data.motion_detected}
        />
        <SensorItem
          label="Rain"
          value={data.rain_detected ? "YES" : "No"}
          alert={data.rain_detected}
        />
        <SensorItem label="Water" value={`${data.water_level} cm`} />
        <SensorItem label="Soil" value={data.soil_moisture.toString()} />
        <SensorItem label="Pump" value={data.pump_active ? "ON" : "OFF"} />
        <SensorItem
          label="Smoke"
          value={data.smoke_level.toString()}
          alert={data.smoke_level > 150}
        />
      </View>

      <View style={styles.modeContainer}>
        <Text style={styles.modeText}>
          Auto Mode: {data.auto_mode ? "ON" : "OFF"}
        </Text>
      </View>
    </View>
  );
}

interface SensorItemProps {
  label: string;
  value: string;
  alert?: boolean;
}

function SensorItem({ label, value, alert }: SensorItemProps) {
  return (
    <View style={[styles.sensorItem, alert && styles.alertItem]}>
      <Text style={styles.sensorLabel}>{label}</Text>
      <Text style={[styles.sensorValue, alert && styles.alertValue]}>
        {value}
      </Text>
    </View>
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
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginHorizontal: -4,
  },
  sensorItem: {
    width: "50%",
    padding: 8,
    marginBottom: 8,
  },
  alertItem: {
    backgroundColor: "#FFEBEE",
    borderRadius: 8,
  },
  sensorLabel: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
  },
  sensorValue: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
  },
  alertValue: {
    color: "#F44336",
  },
  modeContainer: {
    marginTop: 16,
    padding: 12,
    backgroundColor: "#E3F2FD",
    borderRadius: 8,
  },
  modeText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1976D2",
    textAlign: "center",
  },
});
