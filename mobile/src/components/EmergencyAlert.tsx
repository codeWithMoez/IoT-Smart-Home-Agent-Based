/**
 * Emergency Alert Component
 * Displayed when fire or smoke is detected.
 */
import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function EmergencyAlert() {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>🚨</Text>
      <Text style={styles.text}>EMERGENCY: Fire/Smoke Detected!</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#F44336",
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  icon: {
    fontSize: 24,
    marginRight: 8,
  },
  text: {
    color: "white",
    fontSize: 16,
    fontWeight: "bold",
  },
});
