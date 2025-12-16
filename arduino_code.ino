// --- Module 1: LDR and Night LED ---
const int ldrPin = A0;
const int nightLed = 3;
const int threshold = 500; // LDR threshold

// --- Module 2: Garage Door (Ultrasonic & Servo) ---
#include <Servo.h>
const int trigPin = 4;
const int echoPin = 5;
Servo garageServo;
long duration;
int distance;

// --- Module 3: Motion Sensor ---
const int motionSensorPin = 13; 
const int buzzerPin = 11;

// --- Module 4: Rain Detection ---
const int rainSensorPin = 7;
const int clothesServoPin = 8;
Servo clothesServo;

// --- Module 5: Soil Moisture + Water Level ---
const int soilPin = A5;
const int pumpPin = 2;
const int waterTrigPin = A3;
const int waterEchoPin = A4;
long waterDuration;
int waterDistance;

// --- Module 6: Fire + Smoke ---
const int flameSensorPin = 9;
const int smokeSensorAnalog = A1;
const int buzzerPinModule6 = 11;
const int ledPin = 12;
const int smokeThreshold = 150;

// --- Module 7: DHT Sensor ---
#include "DHT.h"
#define DHTPIN A2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

bool autoMode = true;
unsigned long lastSensorUpdate = 0;
const long updateInterval = 1000;

void setup() {
  pinMode(nightLed, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(motionSensorPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(rainSensorPin, INPUT);
  pinMode(pumpPin, OUTPUT);
  pinMode(flameSensorPin, INPUT);
  pinMode(smokeSensorAnalog, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(waterTrigPin, OUTPUT);
  pinMode(waterEchoPin, INPUT);

  garageServo.attach(6);
  clothesServo.attach(clothesServoPin);

  garageServo.write(0);
  clothesServo.write(90);
  digitalWrite(pumpPin, LOW);

  Serial.begin(9600);
  dht.begin();
}

void processCommand(String command) {
  command.trim();
  if (command.length() < 2) return;

  char type = command.charAt(0);
  int value = command.substring(1).toInt();

  if (type == 'A') {
    autoMode = (value == 1);
    Serial.print("Auto Mode: ");
    Serial.println(autoMode ? "ON" : "OFF");
  } 
  else if (!autoMode) {
    // Manual Control
    switch (type) {
      case 'G': // Garage
        garageServo.write(value == 1 ? 180 : 0);
        Serial.print("Manual Garage: ");
        Serial.println(value == 1 ? "OPEN" : "CLOSE");
        break;
      case 'P': // Pump
        digitalWrite(pumpPin, value == 1 ? HIGH : LOW);
        Serial.print("Manual Pump: ");
        Serial.println(value == 1 ? "ON" : "OFF");
        break;
      case 'L': // Light (Night LED)
        digitalWrite(nightLed, value == 1 ? LOW : HIGH); // Active LOW
        Serial.print("Manual Light: ");
        Serial.println(value == 1 ? "ON" : "OFF");
        break;
      case 'C': // Clothes
        clothesServo.write(value == 1 ? 0 : 90);
        Serial.print("Manual Clothes: ");
        Serial.println(value == 1 ? "OPEN" : "CLOSE");
        break;
    }
  }
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorUpdate >= updateInterval) {
    lastSensorUpdate = currentMillis;
    
    // --- Module 1: LDR ---
    int ldrValue = analogRead(ldrPin);
    Serial.print("LDR: ");
    Serial.print(ldrValue);
    Serial.print(" | ");

    if (autoMode) {
      if (ldrValue > threshold) {
        digitalWrite(nightLed, LOW);
      } else {
        digitalWrite(nightLed, HIGH);
      }
    }

    // --- Module 2: Garage Door ---
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    duration = pulseIn(echoPin, HIGH);
    distance = duration * 0.034 / 2;

    Serial.print("Garage Dist: ");
    Serial.print(distance);
    Serial.print(" cm | ");

    if (autoMode) {
      if (distance >= 5 && distance <= 15) {
        garageServo.write(180);
      } else {
        garageServo.write(0);
      }
    }

    // --- Module 3: Motion ---
    int motionDetected = digitalRead(motionSensorPin);

    if (motionDetected == HIGH) {
      digitalWrite(buzzerPin, HIGH);
      Serial.print("Motion! | ");
    } else {
      digitalWrite(buzzerPin, LOW);
      Serial.print("No Motion | ");
    }

    // --- Module 4: Rain Detection ---
    int rainStatus = digitalRead(rainSensorPin);

    if (autoMode) {
      if (rainStatus == LOW) {
        clothesServo.write(0);
        Serial.print("Rain! | ");
      } else {
        clothesServo.write(90);
        Serial.print("No Rain | ");
      }
    }

    // --- Module 5: Water Level ---
    digitalWrite(waterTrigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(waterTrigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(waterTrigPin, LOW);

    waterDuration = pulseIn(waterEchoPin, HIGH);
    waterDistance = waterDuration * 0.034 / 2;

    int soilValue = analogRead(soilPin);

    Serial.print("Water Lvl: ");
    Serial.print(waterDistance);
    Serial.print(" cm | Soil: ");
    Serial.print(soilValue);
    Serial.print(" | ");

    if (autoMode) {
      if (waterDistance >= 1 && waterDistance <= 5 && soilValue > 900) {
        digitalWrite(pumpPin, HIGH);
        Serial.print("Pump ON | ");
      } else {
        digitalWrite(pumpPin, LOW);
        Serial.print("Pump OFF | ");
      }
    }

    // --- Module 6: Fire + Smoke ---
    int flameDetected = digitalRead(flameSensorPin);
    int smokeLevel = analogRead(smokeSensorAnalog);

    Serial.print("Flame: ");
    Serial.print(flameDetected == LOW ? "YES" : "NO");
    Serial.print(" | Smoke: ");
    Serial.print(smokeLevel);
    Serial.print(" | ");

    if (flameDetected == LOW || smokeLevel > smokeThreshold) {
      digitalWrite(buzzerPinModule6, HIGH);
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(buzzerPinModule6, LOW);
      digitalWrite(ledPin, LOW);
    }

    // --- Module 7: Temperature + Humidity ---
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (!isnan(humidity) && !isnan(temperature)) {
      Serial.print("Temp: ");
      Serial.print(temperature);
      Serial.print(" C | Hum: ");
      Serial.print(humidity);
      Serial.print("%");
    }

    Serial.println();
  }
}
