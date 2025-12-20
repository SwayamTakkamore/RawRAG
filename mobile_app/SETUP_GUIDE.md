# RawRAG Mobile App - Complete Setup Guide 📱

## Project Overview

This Flutter mobile app provides full access to the RawRAG system features:
- ✅ Website crawling and indexing
- ✅ AI-powered Q&A with RAG
- ✅ Debate mode (two websites competing)
- ✅ AI Podcast generation with TTS
- ✅ Mermaid diagram generation
- ✅ Session management
- ✅ Both API and Local AI modes
- ✅ Beautiful "Bloxy" UI design

---

## Prerequisites

### Required Software

1. **Flutter SDK** (3.0.0 or higher)
   ```bash
   # Download from: https://flutter.dev/docs/get-started/install
   # Verify installation:
   flutter doctor
   ```

2. **Android Studio** (for Android development)
   - Download: https://developer.android.com/studio
   - Install Android SDK
   - Install Android Emulator

3. **Xcode** (for iOS development - Mac only)
   - Install from Mac App Store
   - Run: `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`

4. **VS Code** (Optional but recommended)
   - Install Flutter extension
   - Install Dart extension

---

## Step-by-Step Setup

### 1. Backend Setup (Required First)

The mobile app connects to the RawRAG backend, so start the backend first:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Configure .env file with your API keys
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Start the backend server
python main.py
```

The backend should now be running at `http://localhost:8000`

### 2. Flutter App Setup

```bash
# Navigate to mobile app directory
cd mobile_app

# Get all dependencies
flutter pub get

# Verify Flutter installation
flutter doctor
```

### 3. Configure Backend URL

**IMPORTANT**: Configure the backend URL based on how you're testing:

#### Option A: Android Emulator
Edit `mobile_app/.env`:
```env
API_BASE_URL=http://10.0.2.2:8000
```
> `10.0.2.2` is a special IP that maps to `localhost` on the host machine

#### Option B: iOS Simulator
Edit `mobile_app/.env`:
```env
API_BASE_URL=http://localhost:8000
```

#### Option C: Real Device (Phone/Tablet)
1. Find your computer's IP address:
   - **Windows**: Open CMD and run `ipconfig` → Look for IPv4 Address
   - **Mac/Linux**: Run `ifconfig` or `ip addr show` → Look for inet address
   
2. Edit `mobile_app/.env`:
   ```env
   API_BASE_URL=http://192.168.1.XXX:8000
   ```
   Replace `192.168.1.XXX` with your actual IP address

3. **Important**: Ensure your phone and computer are on the same WiFi network!

4. **Firewall**: Allow port 8000 through your firewall:
   - **Windows**: `netsh advfirewall firewall add rule name="RawRAG" dir=in action=allow protocol=TCP localport=8000`
   - **Mac**: System Preferences → Security & Privacy → Firewall → Firewall Options → Add Python

### 4. Run the App

#### Android Emulator
```bash
# List available devices
flutter devices

# Run on Android emulator
flutter run
```

#### iOS Simulator (Mac only)
```bash
# Open iOS simulator
open -a Simulator

# Run on iOS
flutter run
```

#### Real Device
```bash
# Connect your phone via USB
# Enable USB debugging (Android) or Trust Computer (iOS)

# List devices
flutter devices

# Run on connected device
flutter run -d <device_id>
```

---

## Testing Checklist

After running the app, test these features:

### ✅ Basic Features
- [ ] App launches without errors
- [ ] Home screen displays correctly
- [ ] Can switch between API/Local modes
- [ ] Backend connection works (check Settings → Backend URL shows green check)

### ✅ Core Functionality
- [ ] Enter a URL (e.g., `https://github.com/facebook/react`)
- [ ] Click "START CRAWLING" - confetti should appear
- [ ] Wait for crawling to complete
- [ ] Navigate to chat screen
- [ ] Send a message and receive AI response
- [ ] Sources are displayed
- [ ] Markdown formatting works

### ✅ Advanced Features
- [ ] Click headset icon → Podcast generates and plays with TTS
- [ ] Click graph icon → Diagram renders in WebView
- [ ] Index a second website
- [ ] Go to Debate Arena
- [ ] Select two websites and start debate
- [ ] Debate transcript displays correctly

### ✅ Persistence
- [ ] Close and reopen app
- [ ] Recent sessions appear on home screen
- [ ] Click on a session to resume chat

---

## Common Issues & Solutions

### Issue: "Cannot connect to backend"

**Solution 1**: Verify backend is running
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}
```

**Solution 2**: Check firewall
- Disable firewall temporarily to test
- If it works, add exception for port 8000

**Solution 3**: Verify .env configuration
- Android Emulator: Use `10.0.2.2:8000`
- Real device: Use computer's actual IP address
- Both devices must be on same WiFi

### Issue: "Hot reload doesn't update .env changes"

**Solution**: Environment variables load at build time
```bash
# Stop the app (Ctrl+C)
# Rebuild and run
flutter run
```

### Issue: "Plugin errors" or "Missing dependencies"

**Solution**: Clean and rebuild
```bash
flutter clean
flutter pub get
flutter run
```

### Issue: "TTS not working"

**Solution**: Check permissions
- Android: Add to `AndroidManifest.xml`:
  ```xml
  <uses-permission android:name="android.permission.INTERNET"/>
  ```
- iOS: TTS should work by default

### Issue: "WebView not rendering diagrams"

**Solution**: Ensure WebView is enabled
- Android: Should work by default in emulator
- iOS: Should work by default

---

## Building for Release

### Android APK
```bash
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (for Play Store)
```bash
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS (Mac only)
```bash
flutter build ios --release

# Then open Xcode and archive
```

---

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── config/
│   │   └── env_config.dart          # Environment variables
│   ├── models/
│   │   ├── crawl_models.dart        # Crawl request/response
│   │   ├── chat_models.dart         # Chat messages
│   │   ├── debate_models.dart       # Debate data
│   │   └── podcast_models.dart      # Podcast/diagram/session
│   ├── services/
│   │   └── api_service.dart         # HTTP client
│   ├── providers/
│   │   ├── session_provider.dart    # Session state
│   │   └── chat_provider.dart       # Chat state
│   ├── screens/
│   │   ├── home_screen.dart         # Main page
│   │   ├── chat_screen.dart         # Chat interface
│   │   ├── debate_screen.dart       # Debate arena
│   │   └── settings_screen.dart     # Settings
│   └── widgets/
│       ├── podcast_player.dart      # TTS player
│       └── diagram_viewer.dart      # Mermaid renderer
├── .env                             # Environment config (gitignored)
├── .env.example                     # Template
├── pubspec.yaml                     # Dependencies
└── README.md                        # Documentation
```

---

## Architecture Notes

### State Management
- Uses `Provider` for global state
- `SessionProvider`: Manages indexed websites and AI mode
- `ChatProvider`: Manages chat messages and loading states

### API Communication
- `ApiService` handles all HTTP requests
- Base URL loaded from `.env` file
- Supports both API and Local modes

### Data Persistence
- Sessions stored in `SharedPreferences`
- Chat history can be persisted (currently in-memory)
- AI mode preference saved locally

---

## Next Steps

### Suggested Enhancements
1. **Voice Input**: Add speech-to-text for messages
2. **Offline Mode**: Cache responses for offline viewing
3. **Push Notifications**: Notify when crawling completes
4. **Dark/Light Theme**: Add theme toggle
5. **Export Chat**: Save conversations as PDF/text
6. **Graph Visualization**: Add 3D graph view like web version

### Performance Optimizations
1. Implement pagination for long chat histories
2. Cache API responses
3. Lazy load sessions list
4. Compress images/assets

---

## Support & Troubleshooting

### Getting Help
1. Check this guide first
2. Review Flutter doctor output: `flutter doctor -v`
3. Check backend logs in terminal
4. Enable debug mode: `flutter run --verbose`

### Debug Commands
```bash
# View logs
flutter logs

# Analyze dependencies
flutter pub deps

# Check for updates
flutter upgrade

# Clear cache
flutter clean
```

---

## License

Same as main RawRAG project.

---

## Acknowledgments

Built with:
- Flutter & Dart
- Provider (state management)
- http/dio (networking)
- flutter_markdown (rendering)
- flutter_tts (text-to-speech)
- webview_flutter (diagram rendering)
- shared_preferences (persistence)

Backend: FastAPI + OpenRouter + FAISS + RAG

---

**Happy Coding! 🚀**
