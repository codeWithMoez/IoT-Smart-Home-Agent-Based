# 🏠 IoT Smart Home Agent-Based System

**AI-Powered Voice-Controlled Smart Home Platform**

A production-ready IoT platform that lets you control your smart home devices using natural language voice commands. Built with Clean Architecture principles and powered by OpenAI GPT-4o-mini and Whisper APIs.

---

## ✨ Features

- 🎤 **Voice Control** - Speak naturally to control devices
- 🤖 **AI-Powered** - GPT-4o-mini interprets commands intelligently
- 🔄 **Real-Time Updates** - WebSocket streaming of sensor data
- 🔌 **Dual Mode** - Works with real Arduino hardware OR simulation
- 📱 **Mobile App** - React Native app for iOS/Android
- 🛡️ **Safety First** - Built-in safety rules and validations
- 🎯 **Auto Mode** - Automatic device control based on sensors

---

## 🚀 Quick Start

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/codeWithMoez/IoT-Smart-Home-Agent-Based.git
cd IoT-Smart-Home-Agent-Based

# Run setup (Windows)
start.bat setup

# Or on Linux/Mac/Git Bash
bash start.sh setup
```

### Step 2: Configure OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Configure Mobile App (Optional - For Physical Device)

**If testing on a physical phone** (not browser/emulator), run the configuration helper:

```bash
# Windows
configure-mobile.bat

# Linux/Mac/Git Bash
bash configure-mobile.sh
```

This automatically configures `mobile/.env` with your computer's IP address.

> **Skip this** if using a web browser or emulator on the same computer.

### Step 4: Run the System

```bash
# Windows
start.bat run

# Linux/Mac/Git Bash
bash start.sh run
```

That's it! 🎉 The backend will start at `http://localhost:8000` and the mobile app will open with a QR code.

### Step 5: Connect Your Phone

1. Install **Expo Go** app on your phone ([iOS](https://apps.apple.com/app/expo-go/id982107779) | [Android](https://play.google.com/store/apps/details?id=host.exp.exponent))

2. **Ensure both devices are on the same WiFi network**

3. Scan the QR code shown in the terminal

4. Wait for the app to load (first load takes ~30 seconds)

5. Start controlling your smart home! 🎤

> **Manual Configuration**: If you prefer, edit `mobile/.env` and set `EXPO_PUBLIC_API_URL=http://YOUR_IP:8000`

---

## 📱 Using the App

### Initial Setup in App

1. **Toggle Auto Mode OFF** - This allows manual control
2. **Test Device Controls** - Try the LED, Garage, Pump buttons
3. **Use Voice Commands** - Press the microphone button and speak

### Voice Command Examples

Try saying:

- _"Turn on the night light"_
- _"Open the garage door"_
- _"Turn on the water pump"_
- _"Close the garage and turn off the LED"_
- _"Enable auto mode"_

The AI understands natural language and will:

- ✅ Execute your commands
- ❓ Ask clarifying questions if ambiguous
- ⚠️ Warn about safety issues
- 🔒 Block dangerous operations

### App Features

#### 📊 Dashboard

- Real-time temperature & humidity
- Device status indicators
- Connection status
- Emergency alerts

#### 🎛️ Auto Mode Toggle

- **ON** - System controls devices automatically based on sensors
- **OFF** - You have full manual control

#### 🕹️ Device Controls

- **Night LED** - Turn on/off
- **Garage Door** - Open/close
- **Water Pump** - Turn on/off
- **Clothes Servo** - Open/close (rain protection)

#### 🎤 Voice Commands

1. Press microphone button
2. Speak your command
3. Wait for transcription & processing
4. See the AI's response with actions taken

---

## 🏗️ Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────┐
│           API Layer (FastAPI)               │
│  Routes, WebSocket, Request/Response        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Application Layer (Use Cases)        │
│  VoiceCommand, ManualControl, Telemetry     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Domain Layer (Entities)            │
│  DeviceCommand, TelemetrySnapshot, Enums    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Infrastructure Layer (Adapters)        │
│  OpenAI Agent, Serial/Simulation Hardware   │
└─────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**

- Python 3.13+ with FastAPI
- OpenAI GPT-4o-mini (AI agent)
- OpenAI Whisper (speech-to-text)
- PySerial (Arduino communication)
- Structlog (structured logging)
- Pydantic (data validation)

**Mobile:**

- Expo SDK 54 / React Native
- TypeScript
- Zustand (state management)
- TanStack Query (API calls)
- expo-audio (voice recording)
- WebSocket (real-time updates)

**Hardware:**

- Arduino Uno
- DHT22 (temperature/humidity)
- LDR (light sensor)
- PIR (motion sensor)
- Ultrasonic (distance/rain detection)
- Servos, relays, buzzer

---

## 📁 Project Structure

```
IoT-Smart-Home-Agent-Based/
├── backend/                 # Python FastAPI backend
│   ├── api/                # API routes, schemas, config
│   ├── application/        # Business logic (use cases)
│   ├── domain/            # Core entities, interfaces
│   ├── infrastructure/    # OpenAI, hardware controllers
│   └── main.py           # Application entry point
│
├── mobile/                 # React Native Expo app
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── screens/       # App screens
│   │   ├── services/      # API & WebSocket clients
│   │   └── store/         # State management
│   └── app.json          # Expo configuration
│
├── arduino_code.ino       # Arduino firmware
├── .env                   # Environment configuration
├── start.sh              # Universal setup/run script (Unix)
├── start.bat             # Universal setup/run script (Windows)
├── requirements.txt      # Python dependencies
└── README.md            # This file

```

---

## 🎮 Available Commands

### Universal Scripts

**Windows:**

```bash
start.bat setup    # Install all dependencies
start.bat run      # Start backend + mobile
start.bat stop     # Stop all services
```

**Linux/Mac/Git Bash:**

```bash
bash start.sh setup    # Install all dependencies
bash start.sh run      # Start backend + mobile
bash start.sh stop     # Stop all services
```

### Manual Commands

**Backend:**

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run backend
python -m backend.main

# View logs
tail -f backend.log
```

**Mobile:**

```bash
cd mobile
npm start              # Start Expo
npm run android       # Open on Android
npm run ios          # Open on iOS
npm run web          # Open in browser
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Application
APP_NAME="IoT Smart Home Agent Platform"
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Hardware Mode
# AUTO = Try Arduino, fallback to Simulation
# ARDUINO = Require real hardware
# SIMULATION = Force virtual hardware
IOT_MODE=AUTO
SERIAL_PORT=
BAUD_RATE=9600

# OpenAI (Required for voice commands)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Telemetry
TELEMETRY_BROADCAST_INTERVAL=1.0
```

### Modes

**AUTO Mode (Default)**

- Tries to connect to Arduino via USB
- Falls back to simulation if Arduino not found
- Best for development and testing

**ARDUINO Mode**

- Requires real Arduino hardware
- Fails if Arduino not detected
- Best for production deployment

**SIMULATION Mode**

- Forces simulation even if Arduino available
- Generates realistic sensor data
- Best for testing without hardware

---

## 🔌 Arduino Hardware Setup

**Want to connect real Arduino hardware?**

👉 **See the complete guide:** [ARDUINO_SETUP.md](ARDUINO_SETUP.md)

The guide covers:

- 🛠️ Required components (sensors, actuators, wiring)
- 📝 Step-by-step firmware upload instructions
- 🔌 Pin configuration and wiring diagrams
- ⚙️ Backend configuration for hardware mode
- 🔄 When and how to reset Arduino
- 🐛 Comprehensive troubleshooting
- 💡 Tips & best practices

### Quick Start with Arduino

1. **Upload the firmware:**

   - Open `arduino_code.ino` in Arduino IDE
   - Select your board and port
   - Click Upload

2. **Update `.env` file:**

   ```env
   IOT_MODE=ARDUINO
   SERIAL_PORT=COM3  # Your Arduino port
   ```

3. **Restart the backend:**
   ```bash
   start.bat run  # or bash start.sh run
   ```

For detailed wiring, troubleshooting, and component lists, see [ARDUINO_SETUP.md](ARDUINO_SETUP.md).

### Without Arduino (Simulation)

If you don't have Arduino hardware:

- **Nothing needed!** The system works perfectly in simulation mode
- Generates realistic sensor data automatically
- All features work exactly the same

---

## 🐛 Troubleshooting

### Backend Won't Start

**Check Python version:**

```bash
python --version  # Should be 3.11+
```

**Check virtual environment:**

```bash
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
pip list  # Should show installed packages
```

**Check backend logs:**

```bash
tail -50 backend.log
```

### Mobile App Won't Load

**Clear Metro bundler cache:**

```bash
cd mobile
npm start --clear
```

**Reinstall dependencies:**

```bash
cd mobile
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Voice Commands Not Working

**Check OpenAI API key:**

```bash
# In .env file
OPENAI_API_KEY=sk-proj-...  # Must start with sk-
```

**Test API key:**

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Check backend logs:**

```bash
grep -i "openai\|whisper\|transcription" backend.log
```

### Buttons Show 400 Error

**Solution:** Toggle Auto Mode OFF first

- Auto mode blocks manual control
- Switch must be OFF to use buttons

### No Audio Recorded

**Check permissions:**

- Android: Settings → Apps → Expo Go → Permissions → Microphone
- iOS: Settings → Expo Go → Microphone

**Check console logs:**

- Look for "Recording started" message
- Check for permission errors

### WebSocket Connection Failed

**Update mobile API config:**

```typescript
// mobile/src/services/api.ts
baseURL: "http://YOUR_IP_ADDRESS:8000";

// mobile/src/services/websocket.ts
defaultUrl: "ws://YOUR_IP_ADDRESS:8000/ws/telemetry";
```

**Find your IP:**

```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

---

## 📊 API Documentation

Once the backend is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health

### Key Endpoints

**POST /api/v1/transcribe**

- Upload audio file
- Returns transcribed text (Whisper API)

**POST /api/v1/voice-command**

- Send transcribed text
- AI processes and executes commands
- Returns status and actions taken

**POST /api/v1/manual-control**

- Direct device control (bypasses AI)
- Requires auto mode OFF

**POST /api/v1/auto-mode**

- Toggle automatic device control

**GET /api/v1/telemetry**

- Get current sensor readings

**WebSocket /ws/telemetry**

- Real-time sensor data stream

---

## 🧪 Testing

### Test Voice Commands

```bash
# Test transcription endpoint
curl -X POST http://localhost:8000/api/v1/transcribe \
  -F "audio=@recording.m4a"

# Test voice command (with transcription)
curl -X POST http://localhost:8000/api/v1/voice-command \
  -H "Content-Type: application/json" \
  -d '{"transcription": "Turn on the night light"}'
```

### Test Manual Control

```bash
# Turn on LED
curl -X POST http://localhost:8000/api/v1/manual-control \
  -H "Content-Type: application/json" \
  -d '{"device": "night_led", "action": "on", "manual_override": false}'
```

### Monitor Logs

```bash
# Backend logs with colors
tail -f backend.log | grep -E "voice_command|transcription|command_executed"

# Real-time API calls
tail -f backend.log | grep "HTTP"
```

---

## � Troubleshooting

### Mobile App Can't Connect to Backend

**Problem**: WebSocket errors or "Network Error" when using app on phone

**Solutions**:

1. **Check Same WiFi Network**: Ensure your phone and computer are on the same WiFi network

2. **Update mobile/.env with your computer's IP**:

   ```bash
   # Find your IP
   ipconfig          # Windows
   ifconfig          # Mac/Linux

   # Edit mobile/.env
   EXPO_PUBLIC_API_URL=http://YOUR_IP:8000
   ```

3. **Check Firewall**: Allow port 8000 in your firewall

   ```bash
   # Windows Firewall (Run as Administrator)
   netsh advfirewall firewall add rule name="IoT Backend" dir=in action=allow protocol=TCP localport=8000
   ```

4. **Restart Expo**: After changing `.env`, restart the mobile app

   ```bash
   # Stop current process (Ctrl+C)
   ./start.sh run
   ```

5. **Verify Backend is Accessible**:
   ```bash
   # On your phone's browser, visit:
   http://YOUR_IP:8000/docs
   ```

### Backend Fails to Start

**Problem**: "Backend failed to start" error

**Solutions**:

1. **Check Python version**: Must be Python 3.11+

   ```bash
   python --version
   ```

2. **Activate virtual environment**:

   ```bash
   source venv/Scripts/activate    # Windows Git Bash
   source venv/bin/activate        # Mac/Linux
   ```

3. **Check backend.log**:

   ```bash
   cat backend.log
   ```

4. **Reinstall dependencies**:
   ```bash
   ./start.sh setup
   ```

### Voice Commands Not Working

**Problem**: "Transcription failed" or no response

**Solutions**:

1. **Check OpenAI API Key** in `.env`:

   ```bash
   OPENAI_API_KEY=sk-proj-...your-key-here...
   ```

2. **Check API Key Balance**: Visit [OpenAI Platform](https://platform.openai.com/usage)

3. **Test API manually**:

   ```bash
   curl http://localhost:8000/api/v1/health
   ```

4. **Check logs**:
   ```bash
   tail -f backend.log | grep -i "error"
   ```

### Arduino Not Detected

**Problem**: "Serial port not found" error

**Solutions**:

1. **Check Arduino is connected**: LED should be on

2. **Find correct port**:

   ```bash
   # Windows
   mode

   # Mac/Linux
   ls /dev/tty*
   ```

3. **Update .env**:

   ```bash
   SERIAL_PORT=COM3          # Windows
   SERIAL_PORT=/dev/ttyUSB0  # Linux
   SERIAL_PORT=/dev/cu.usbmodem14101  # Mac
   ```

4. **Check drivers**: Install Arduino drivers from [Arduino.cc](https://www.arduino.cc/en/software)

---

## �💡 Tips & Best Practices

### For Development

1. **Use Simulation Mode** - Test without hardware
2. **Watch Logs** - Monitor `backend.log` in real-time
3. **Test API** - Use Swagger UI at `/docs`
4. **Mobile Debugging** - Use Expo DevTools (press `j` in terminal)

### For Production

1. **Use ARDUINO Mode** - Ensure hardware is connected
2. **Set LOG_LEVEL=WARNING** - Reduce log noise
3. **Secure API Key** - Never commit `.env` file
4. **Monitor Resources** - Check CPU/memory usage
5. **Backup Logs** - Rotate `backend.log` regularly

### Voice Command Tips

- **Speak clearly** - 2-3 seconds of clear speech
- **Be specific** - Say device names explicitly
- **Natural language** - No need for exact keywords
- **Check logs** - See how AI interpreted your command

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Moez**

- GitHub: [@codeWithMoez](https://github.com/codeWithMoez)

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini and Whisper APIs
- **Expo** - React Native development platform
- **FastAPI** - Modern Python web framework
- **Arduino** - Hardware platform

---

## 📞 Support

Having issues? Check:

1. **Troubleshooting section** above
2. **Backend logs:** `backend.log`
3. **Mobile console:** Look for errors in Expo DevTools
4. **API docs:** http://localhost:8000/docs

---

## 🎯 What's Next?

Now that you have the system running:

1. ✅ **Test Voice Commands** - Try different natural language commands
2. ✅ **Explore Auto Mode** - Let the AI control devices based on sensors
3. ✅ **Monitor Telemetry** - Watch real-time sensor data updates
4. ✅ **Connect Arduino** - Use real hardware for full experience
5. ✅ **Customize** - Modify devices, add new commands, extend AI logic

**Happy Coding! 🚀**
