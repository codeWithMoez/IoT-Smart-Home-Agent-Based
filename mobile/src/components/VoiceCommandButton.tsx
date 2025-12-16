/**
 * Voice Command Button Component
 * Records voice commands and sends to backend for AI processing.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
} from "expo-audio";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../services/api";

export default function VoiceCommandButton() {
  const [isRecording, setIsRecording] = useState(false);
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);

  const voiceCommandMutation = useMutation({
    mutationFn: (transcription: string) =>
      apiClient.sendVoiceCommand(transcription),
    onSuccess: (data) => {
      const message = data.reason || data.question || "Command executed";
      Alert.alert(
        "Voice Command",
        `Status: ${data.status}\n${message}\n\nActions: ${data.actions.join(
          ", "
        )}`
      );
    },
    onError: (error: any) => {
      Alert.alert("Error", error.message || "Failed to execute voice command");
    },
  });

  const startRecording = async () => {
    try {
      console.log("Requesting permissions...");
      // Request permissions
      const { granted } = await AudioModule.requestRecordingPermissionsAsync();
      console.log("Permission granted:", granted);
      
      if (!granted) {
        Alert.alert("Permission Denied", "Please grant microphone access");
        return;
      }

      // Start recording
      console.log("Starting recording...");
      console.log("Recorder state before prepareToRecord:", audioRecorder.isRecording);
      
      // Prepare and start recording
      try {
        await audioRecorder.prepareToRecordAsync();
        console.log("Prepared to record");
      } catch (prepErr) {
        console.log("prepareToRecordAsync not available or failed:", prepErr);
      }
      
      await audioRecorder.record();
      
      // Wait a moment for state to update
      await new Promise((resolve) => setTimeout(resolve, 100));
      
      // Check if recording actually started
      console.log("After record() - isRecording:", audioRecorder.isRecording);
      
      if (audioRecorder.isRecording) {
        setIsRecording(true);
        console.log("Recording started successfully");
      } else {
        console.error("Recording failed to start - isRecording is false");
        Alert.alert("Error", "Failed to start recording. Please try again.");
      }
    } catch (err) {
      console.error("Failed to start recording:", err);
      setIsRecording(false);
      Alert.alert("Error", `Failed to start recording: ${err}`);
    }
  };

  const stopRecording = async () => {
    try {
      console.log("Stopping recording...");
      console.log("Recorder state before stop:", {
        isRecording: audioRecorder.isRecording,
        uri: audioRecorder.uri,
      });

      setIsRecording(false);
      await audioRecorder.stop();

      // Wait a bit for the URI to be available
      await new Promise((resolve) => setTimeout(resolve, 100));

      const uri = audioRecorder.uri;
      console.log("Recording stopped, URI:", uri);

      if (!uri) {
        console.error("No URI available after recording");
        Alert.alert("Error", "No audio recorded. Please try again.");
        return;
      }

      // Transcribe the audio using OpenAI Whisper
      try {
        Alert.alert("Processing", "Transcribing your voice...");

        const { transcription } = await apiClient.transcribeAudio(uri);

        console.log("Transcription:", transcription);

        // Send transcribed text to AI agent
        voiceCommandMutation.mutate(transcription);
      } catch (transcribeError: any) {
        console.error("Transcription error:", transcribeError);
        Alert.alert(
          "Transcription Failed",
          transcribeError.message ||
            "Could not transcribe audio. Please try again."
        );
      }
    } catch (err) {
      console.error("Failed to stop recording:", err);
      setIsRecording(false);
      Alert.alert("Error", "Failed to stop recording");
    }
  };

  const handlePress = () => {
    console.log("Button pressed, isRecording:", isRecording);
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.button, isRecording && styles.buttonRecording]}
        onPress={handlePress}
        activeOpacity={0.8}
        disabled={voiceCommandMutation.isPending}
      >
        <Text style={styles.buttonText}>{isRecording ? "⏹️" : "🎤"}</Text>
        <Text style={styles.label}>
          {voiceCommandMutation.isPending
            ? "Processing..."
            : isRecording
            ? "Tap to Stop"
            : "Voice Command"}
        </Text>
      </TouchableOpacity>
      {voiceCommandMutation.isPending && (
        <Text style={styles.processing}>Transcribing & Processing...</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  button: {
    backgroundColor: "#4CAF50",
    borderRadius: 12,
    padding: 24,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  buttonRecording: {
    backgroundColor: "#F44336",
  },
  buttonText: {
    fontSize: 48,
    marginBottom: 8,
  },
  label: {
    fontSize: 18,
    fontWeight: "bold",
    color: "white",
  },
  processing: {
    marginTop: 8,
    textAlign: "center",
    fontSize: 14,
    color: "#666",
  },
});
