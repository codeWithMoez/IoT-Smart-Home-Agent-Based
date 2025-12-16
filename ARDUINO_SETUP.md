# 🔌 Arduino Hardware Setup Guide

Complete guide for setting up real Arduino hardware with the IoT Smart Home system.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ Arduino Uno board
- ✅ USB cable (Type A to Type B)
- ✅ Computer with Arduino IDE installed
- ✅ All required sensors and actuators (see components list below)
- ✅ Breadboard and jumper wires
- ✅ 5V power supply (optional, for standalone operation)

---

## 🛠️ Required Components

### Sensors

- **DHT22** - Temperature & Humidity sensor
- **LDR (Light Dependent Resistor)** - Light level sensor
- **PIR (HC-SR501)** - Motion detection sensor
- **Ultrasonic (HC-SR04)** - Distance measurement (for rain detection)
- **MQ-2** - Gas/Smoke sensor (optional, for fire detection)

### Actuators

- **Servo Motor (x2)** - For garage door and clothes line
- **Relay Module** - For water pump control
- **LED** - Night light
- **Buzzer** - Alert system
- **Water Pump** - Garden irrigation

### Other

- Breadboard
- Jumper wires (male-to-male, male-to-female)
- 10kΩ resistors (x2) - For LDR and other sensors
- 5V power adapter (if running standalone)

---

## 🔧 Step-by-Step Setup

### Step 1: Install Arduino IDE

1. Download Arduino IDE from: https://www.arduino.cc/en/software
2. Install for your operating system (Windows/Mac/Linux)
3. Open Arduino IDE

### Step 2: Prepare the Firmware

1. **Locate the firmware file:**

   ```
   IoT-Smart-Home-Agent-Based/arduino_code.ino
   ```

2. **Open in Arduino IDE:**

   - Double-click `arduino_code.ino` OR
   - File → Open → Select `arduino_code.ino`

3. **Review pin configuration** (default pins):

   ```cpp
   // Sensors
   #define DHT_PIN 2          // DHT22 temperature/humidity
   #define LDR_PIN A0         // Light sensor (analog)
   #define PIR_PIN 3          // Motion sensor
   #define ULTRASONIC_TRIG 4  // Ultrasonic trigger
   #define ULTRASONIC_ECHO 5  // Ultrasonic echo
   #define GAS_SENSOR_PIN A1  // Gas/smoke sensor (analog)

   // Actuators
   #define NIGHT_LED_PIN 6    // Night LED
   #define GARAGE_SERVO_PIN 9 // Garage door servo
   #define CLOTHES_SERVO_PIN 10 // Clothes line servo
   #define PUMP_RELAY_PIN 7   // Water pump relay
   #define BUZZER_PIN 8       // Alert buzzer
   ```

### Step 3: Wire the Components

#### Power Rails Setup

```
Arduino 5V  → Breadboard + rail (red)
Arduino GND → Breadboard - rail (blue/black)
```

#### Sensors Wiring

**DHT22 (Temperature/Humidity):**

```
Pin 1 (VCC) → 5V
Pin 2 (Data) → Digital Pin 2
Pin 3 (NC) → Not Connected
Pin 4 (GND) → GND
```

**LDR (Light Sensor):**

```
One leg → 5V
Other leg → A0 AND 10kΩ resistor to GND
```

**PIR Motion Sensor:**

```
VCC → 5V
OUT → Digital Pin 3
GND → GND
```

**Ultrasonic Sensor (HC-SR04):**

```
VCC → 5V
Trig → Digital Pin 4
Echo → Digital Pin 5
GND → GND
```

**MQ-2 Gas Sensor (Optional):**

```
VCC → 5V
A0 → Analog Pin A1
GND → GND
```

#### Actuators Wiring

**LED (Night Light):**

```
Long leg (Anode) → Digital Pin 6
Short leg (Cathode) → GND (through 220Ω resistor)
```

**Servo Motors (x2):**

```
Garage Servo:
  Red (VCC) → 5V
  Brown (GND) → GND
  Orange (Signal) → Digital Pin 9

Clothes Servo:
  Red (VCC) → 5V
  Brown (GND) → GND
  Orange (Signal) → Digital Pin 10
```

**Relay Module (Water Pump):**

```
VCC → 5V
IN → Digital Pin 7
GND → GND

Water Pump:
  Connect through relay's NO (Normally Open) terminals
  Pump + → External 12V supply
  Pump - → Relay COM
```

**Buzzer:**

```
Positive (+) → Digital Pin 8
Negative (-) → GND
```

### Step 4: Upload Firmware

1. **Connect Arduino to Computer:**

   - Plug USB cable into Arduino and computer
   - Arduino power LED should light up

2. **Select Board:**

   - Tools → Board → Arduino Uno

3. **Select Port:**

   - Tools → Port → COMx (Windows) or /dev/ttyUSB0 (Linux) or /dev/cu.usbmodem (Mac)
   - The port with "(Arduino Uno)" in the name

4. **Compile (Verify):**

   - Click ✓ (Verify) button
   - Wait for "Done compiling"
   - Check for any errors in the console

5. **Upload:**

   - Click → (Upload) button
   - Wait for "Done uploading"
   - Arduino will reset automatically

6. **Verify Upload:**
   - Open Serial Monitor: Tools → Serial Monitor
   - Set baud rate to **9600**
   - You should see: `{"status":"ready","mode":"auto"}`

### Step 5: Configure Backend

1. **Find Arduino Port:**

   **Windows:**

   ```bash
   # Check Device Manager → Ports (COM & LPT)
   # Look for "Arduino Uno (COMx)"
   ```

   **Linux:**

   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   # Usually /dev/ttyUSB0 or /dev/ttyACM0
   ```

   **Mac:**

   ```bash
   ls /dev/cu.usbmodem*
   # Usually /dev/cu.usbmodem14201 or similar
   ```

2. **Update `.env` file:**

   ```env
   # Hardware Mode - Use ARDUINO for real hardware
   IOT_MODE=ARDUINO

   # Serial Port - Update with your port
   SERIAL_PORT=COM3              # Windows
   # SERIAL_PORT=/dev/ttyUSB0    # Linux
   # SERIAL_PORT=/dev/cu.usbmodem14201  # Mac

   BAUD_RATE=9600
   ```

3. **Set Permissions (Linux only):**

   ```bash
   # Add your user to dialout group
   sudo usermod -a -G dialout $USER

   # Or give temporary permission
   sudo chmod 666 /dev/ttyUSB0

   # Logout and login for group changes to take effect
   ```

### Step 6: Test Connection

1. **Start the backend:**

   ```bash
   # Windows
   start.bat run

   # Linux/Mac
   bash start.sh run
   ```

2. **Check backend logs:**

   ```bash
   tail -f backend.log | grep -i "arduino\|serial"
   ```

3. **Expected logs:**

   ```
   initializing_serial_controller
   arduino_detected port=COM3
   runtime_mode=arduino
   ```

4. **If successful:**
   - Backend shows "runtime_mode=arduino"
   - Real sensor data appears in logs
   - Device commands control actual hardware

---

## ✅ Verification Checklist

After setup, verify everything works:

### Hardware Check

- [ ] Arduino power LED is on
- [ ] All sensors are powered (LEDs on if present)
- [ ] Servos are at initial position
- [ ] USB cable is firmly connected
- [ ] No loose wires

### Software Check

- [ ] Arduino IDE shows "Done uploading"
- [ ] Serial Monitor shows JSON messages at 9600 baud
- [ ] Backend logs show "arduino_detected"
- [ ] Backend logs show "runtime_mode=arduino"
- [ ] Mobile app connects successfully

### Sensor Check

- [ ] DHT22: Temperature and humidity readings are reasonable
- [ ] LDR: Light level changes when you cover/expose it
- [ ] PIR: Motion detection triggers (wave your hand)
- [ ] Ultrasonic: Distance readings change
- [ ] Gas sensor: Readings are stable (if installed)

### Actuator Check

- [ ] LED: Turns on/off via app
- [ ] Servos: Move when commanded (garage door, clothes line)
- [ ] Pump: Relay clicks when toggled
- [ ] Buzzer: Makes sound when alert triggered

---

## 🔄 Resetting Arduino

### When to Reset

You need to reset Arduino when:

- ✅ First time connecting to the system
- ✅ After uploading new firmware
- ✅ If Arduino becomes unresponsive
- ✅ If sensors show incorrect readings
- ✅ After changing wiring

### How to Reset

**Method 1: Hardware Reset (Recommended)**

1. Press the **RESET** button on Arduino board
2. Wait 2-3 seconds
3. Arduino will restart automatically
4. Serial Monitor will show boot messages

**Method 2: Power Cycle**

1. Unplug USB cable from Arduino
2. Wait 5 seconds
3. Plug USB cable back in
4. Arduino will restart

**Method 3: Software Reset**

1. Close backend application
2. Re-upload firmware from Arduino IDE
3. Arduino resets automatically after upload
4. Restart backend

### After Reset

1. **Check Serial Monitor:**

   - Should show: `{"status":"ready","mode":"auto"}`

2. **Restart Backend:**

   ```bash
   start.bat stop
   start.bat run
   ```

3. **Verify Connection:**
   - Backend logs should show "arduino_detected"
   - Mobile app should show real sensor data

---

## 🐛 Troubleshooting

### Arduino Not Detected

**Problem:** Backend logs show "Arduino not detected" or falls back to simulation

**Solutions:**

1. **Check USB Connection:**

   ```bash
   # Windows - Device Manager
   devmgmt.msc
   # Look under "Ports (COM & LPT)"

   # Linux
   ls -l /dev/ttyUSB* /dev/ttyACM*

   # Mac
   ls -l /dev/cu.usbmodem*
   ```

2. **Check .env Configuration:**

   ```env
   IOT_MODE=ARDUINO  # Must be ARDUINO, not AUTO
   SERIAL_PORT=COM3  # Must match your actual port
   BAUD_RATE=9600    # Must match Arduino code
   ```

3. **Test with Arduino IDE:**

   - Open Serial Monitor (9600 baud)
   - Should see JSON messages
   - If not, re-upload firmware

4. **Driver Issues (Windows):**
   - Install CH340 drivers if using clone Arduino
   - Download from: http://www.wch.cn/downloads/CH341SER_ZIP.html

### Sensors Not Reading

**Problem:** Sensor values are 0, -999, or not changing

**Solutions:**

1. **Check Wiring:**

   - Verify VCC → 5V
   - Verify GND → GND
   - Verify signal pins match code

2. **Test Individual Sensors:**

   ```cpp
   // Add debug prints in arduino_code.ino
   Serial.print("DHT Temp: ");
   Serial.println(temperature);
   ```

3. **DHT22 Specific:**

   - Needs 10kΩ pull-up resistor between Data and VCC
   - Wait 2 seconds between readings
   - Check for fake sensors (common issue)

4. **LDR Specific:**
   - Check 10kΩ resistor is in place
   - Test with flashlight/darkness
   - Value should range 0-1023

### Actuators Not Working

**Problem:** LED, servos, or pump don't respond to commands

**Solutions:**

1. **Check Power:**

   - Servos need stable 5V (use external supply if needed)
   - Pump needs 12V external supply
   - Arduino USB can't power everything

2. **Check Pin Assignments:**

   - Verify pins in code match physical wiring
   - Use digitalWrite() test in Arduino IDE

3. **Test Manually:**

   ```cpp
   // Add in loop() for testing
   digitalWrite(NIGHT_LED_PIN, HIGH);
   delay(1000);
   digitalWrite(NIGHT_LED_PIN, LOW);
   ```

4. **Servo Issues:**
   - Check servo power (separate 5V supply recommended)
   - Test servo.attach() and servo.write()
   - Ensure servo angle is 0-180°

### Serial Communication Errors

**Problem:** "Port already in use" or "Permission denied"

**Solutions:**

1. **Windows:**

   ```bash
   # Close Arduino IDE Serial Monitor
   # Kill any programs using the port
   tasklist | findstr COM
   ```

2. **Linux:**

   ```bash
   # Close Arduino IDE Serial Monitor
   # Check what's using the port
   fuser /dev/ttyUSB0

   # Give permission
   sudo chmod 666 /dev/ttyUSB0
   ```

3. **Multiple Programs:**
   - Only ONE program can use serial port at a time
   - Close Arduino IDE Serial Monitor before starting backend
   - Stop backend before opening Serial Monitor

### Backend Shows Wrong Mode

**Problem:** Backend shows "runtime_mode=simulation" instead of "arduino"

**Solutions:**

1. **Check IOT_MODE:**

   ```env
   IOT_MODE=ARDUINO  # Not AUTO, not SIMULATION
   ```

2. **Check Backend Logs:**

   ```bash
   grep -i "arduino\|serial\|hardware" backend.log
   ```

3. **Look for Error Messages:**

   - "Arduino not detected"
   - "Serial port not found"
   - "Permission denied"

4. **Restart Backend:**
   ```bash
   start.bat stop
   start.bat run
   ```

---

## 💡 Tips & Best Practices

### Power Management

1. **Use External Power for Servos:**

   - Arduino 5V can't power multiple servos
   - Use separate 5V 2A power supply
   - Connect grounds together (Arduino GND + External GND)

2. **Use External 12V for Pump:**
   - Water pump needs 12V
   - Use relay to control pump
   - Never connect pump directly to Arduino

### Wiring

1. **Use Color-Coded Wires:**

   - Red = 5V/VCC
   - Black/Blue = GND
   - Other colors = Signal

2. **Keep Wires Short:**

   - Reduces interference
   - Keeps breadboard organized

3. **Double-Check Before Powering:**
   - No shorts between 5V and GND
   - All connections are secure
   - Correct pins used

### Development

1. **Test Sensors Individually First:**

   - Upload simple test sketches
   - Verify each sensor before integrating

2. **Use Serial Monitor for Debug:**

   - Print sensor values
   - Check command reception
   - Monitor system state

3. **Start with Simulation, Then Hardware:**
   - Test software logic in simulation
   - Switch to hardware when ready

### Maintenance

1. **Regular Checks:**

   - Inspect wire connections monthly
   - Clean sensors (dust affects readings)
   - Check servo movement (lubricate if needed)

2. **Keep Backup:**

   - Save working firmware
   - Document any custom changes
   - Take photos of wiring

3. **Update Firmware:**
   - Check for firmware updates
   - Test in simulation first
   - Upload during off-peak hours

---

## 🔗 Serial Protocol Reference

### Messages FROM Arduino

**Telemetry (every 1 second):**

```json
{
  "temperature": 24.5,
  "humidity": 60.2,
  "ldr_value": 512,
  "motion": 0,
  "distance": 50,
  "gas_level": 100,
  "auto_mode": 1,
  "led_state": 0,
  "garage_state": 0,
  "pump_state": 0,
  "clothes_state": 0
}
```

**Status Messages:**

```json
{"status":"ready","mode":"auto"}           // Boot complete
{"status":"command_received"}               // Command acknowledged
{"status":"command_executed"}               // Action completed
{"status":"error","message":"Invalid pin"}  // Error occurred
```

### Commands TO Arduino

**Device Control:**

```json
{"device":"led","state":"on"}       // Turn LED on/off
{"device":"garage","state":"open"}  // Open/close garage
{"device":"pump","state":"on"}      // Turn pump on/off
{"device":"clothes","state":"open"} // Open/close clothes line
```

**Mode Control:**

```json
{"command":"auto_mode","value":"on"}  // Enable auto mode
{"command":"auto_mode","value":"off"} // Disable auto mode
```

**System Commands:**

```json
{"command":"reset"}         // Reset Arduino
{"command":"status"}        // Request status
{"command":"calibrate"}     // Calibrate sensors
```

---

## 📊 Expected Sensor Ranges

| Sensor     | Type        | Range         | Normal Values               |
| ---------- | ----------- | ------------- | --------------------------- |
| DHT22      | Temperature | -40°C to 80°C | 15-35°C (room temp)         |
| DHT22      | Humidity    | 0-100%        | 30-70% (comfortable)        |
| LDR        | Light Level | 0-1023        | <500 (dark), >500 (bright)  |
| PIR        | Motion      | 0/1           | 0 (no motion), 1 (detected) |
| Ultrasonic | Distance    | 2-400 cm      | <10cm (rain detected)       |
| MQ-2       | Gas         | 0-1023        | <300 (safe), >500 (alert)   |

---

## 🆘 Getting Help

If you're still having issues:

1. **Check Backend Logs:**

   ```bash
   tail -100 backend.log
   ```

2. **Check Serial Monitor:**

   - Open Arduino IDE → Tools → Serial Monitor
   - Set baud to 9600
   - Watch for messages

3. **Test in Simulation First:**

   ```env
   IOT_MODE=SIMULATION
   ```

   - If it works in simulation, issue is hardware-related
   - If it fails in simulation, issue is software-related

4. **Common Issues:**
   - Wrong COM port → Check Device Manager
   - Permission denied → Run with sudo (Linux) or as Admin (Windows)
   - No data → Check wiring and sensor power
   - Random values → Ground connection issue

---

## ✅ Quick Reference Card

**After Wiring:**

1. Upload `arduino_code.ino` from Arduino IDE
2. Note your COM port (e.g., COM3)
3. Update `.env`: `IOT_MODE=ARDUINO`, `SERIAL_PORT=COM3`
4. Close Arduino Serial Monitor
5. Run `start.bat run` (Windows) or `bash start.sh run` (Linux/Mac)
6. Check logs for "arduino_detected"
7. Test with mobile app

**To Reset:**

1. Press RESET button on Arduino
2. Wait 3 seconds
3. Backend will reconnect automatically

**To Switch Back to Simulation:**

1. Update `.env`: `IOT_MODE=SIMULATION`
2. Restart backend
3. Arduino can stay connected

---

**Happy Building! 🚀**

For software issues, see main [README.md](README.md)
