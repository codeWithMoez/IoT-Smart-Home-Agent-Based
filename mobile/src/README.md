# Mobile App - Source Code

## Structure

```
src/
├── components/          # Reusable UI components
│   ├── TelemetryCard.tsx
│   ├── DeviceControls.tsx
│   ├── VoiceCommandButton.tsx
│   └── EmergencyAlert.tsx
├── screens/             # App screens
│   └── DashboardScreen.tsx
├── services/            # External service integrations
│   ├── api.ts          # REST API client
│   └── websocket.ts    # WebSocket client
└── store/              # State management
    └── appStore.ts     # Zustand store
```

## Key Concepts

### State Management (Zustand)

The app uses Zustand for lightweight state management:

- Global telemetry state
- Connection status
- UI state (alerts, recording)

### Data Fetching (TanStack Query)

React Query handles:

- Health check polling
- Manual control mutations
- Automatic refetching

### Real-Time Updates (WebSocket)

WebSocket service provides:

- 1Hz telemetry streaming
- Auto-reconnection
- Error handling

## Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on specific platform
npm run android
npm run ios
npm run web
```

## Configuration

Edit backend URL in `services/api.ts`:

```typescript
// For local development
constructor(baseURL: string = 'http://localhost:8000')

// For device/emulator (use your computer's IP)
constructor(baseURL: string = 'http://192.168.1.100:8000')
```

## Future Enhancements

- [ ] Implement voice recording (expo-av)
- [ ] Add authentication
- [ ] Historical data charts
- [ ] Push notifications
- [ ] Theme customization
