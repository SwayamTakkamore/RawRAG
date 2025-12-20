# RawRAG Mobile App 📱

A Flutter mobile application for the RawRAG system - Turn any website into an AI-powered chatbot!

## Features ✨

- 🌐 **Website Crawling**: Index any website for RAG-based chatting
- 💬 **AI Chat**: Ask questions about indexed websites
- ⚔️ **Debate Mode**: Watch two websites debate on any topic
- 🎙️ **Podcast Generation**: Generate AI podcast summaries
- 📊 **Diagram Visualization**: Create Mermaid diagrams from content
- 🗣️ **Voice Control**: Speech-to-text and text-to-speech support
- 🎨 **Modern UI**: Beautiful, playful "Bloxy" design

## Setup Instructions

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Android Studio / Xcode (for mobile development)
- RawRAG Backend running (see main README)

### Installation

1. **Navigate to the mobile app directory:**
   ```bash
   cd mobile_app
   ```

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Configure Backend URL:**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set the correct backend URL:
   
   - **Android Emulator**: `API_BASE_URL=http://10.0.2.2:8000`
   - **iOS Simulator**: `API_BASE_URL=http://localhost:8000`
   - **Real Device**: `API_BASE_URL=http://YOUR_COMPUTER_IP:8000`
   
   To find your computer's IP:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Mac/Linux: `ifconfig` or `ip addr show`

4. **Run the backend server:**
   ```bash
   cd ../backend
   python main.py
   ```

5. **Run the Flutter app:**
   ```bash
   cd ../mobile_app
   flutter run
   ```

## Configuration

### Changing Backend IP Address

The app uses a `.env` file for configuration. This is useful when:

- Testing on different devices
- Switching between emulator and real device
- Deploying to different environments

Simply edit the `.env` file:

```env
# For Android Emulator
API_BASE_URL=http://10.0.2.2:8000

# For Real Device (replace with your IP)
API_BASE_URL=http://192.168.1.100:8000
```

**Note**: After changing the `.env` file, you need to rebuild the app (hot reload won't work for .env changes).

## Usage

1. **Home Screen**: Enter any website URL and choose AI mode (API or Local)
2. **Chat Screen**: Ask questions about the indexed website
3. **Debate Screen**: Select two indexed websites and watch them debate
4. **Features**: Access podcast, diagrams, and voice controls from the chat screen

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── config/
│   │   └── env_config.dart       # Environment configuration
│   ├── models/
│   │   ├── crawl_models.dart     # Crawl request/response models
│   │   ├── chat_models.dart      # Chat message models
│   │   ├── debate_models.dart    # Debate models
│   │   └── podcast_models.dart   # Podcast & diagram models
│   ├── services/
│   │   └── api_service.dart      # HTTP API client
│   ├── providers/
│   │   ├── session_provider.dart # Session state management
│   │   └── chat_provider.dart    # Chat state management
│   ├── screens/
│   │   ├── home_screen.dart      # URL input & crawling
│   │   ├── chat_screen.dart      # Chat interface
│   │   ├── debate_screen.dart    # Debate feature
│   │   └── settings_screen.dart  # App settings
│   └── widgets/
│       ├── message_bubble.dart   # Chat message widget
│       ├── podcast_player.dart   # Audio player widget
│       └── diagram_viewer.dart   # Mermaid diagram viewer
├── .env                          # Environment variables (not committed)
├── .env.example                  # Example environment file
└── pubspec.yaml                  # Dependencies
```

## Building for Release

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## Troubleshooting

### Cannot connect to backend

1. Check if backend is running: `curl http://localhost:8000/api/health`
2. Verify `.env` file has correct IP address
3. For real devices, ensure phone and computer are on same WiFi network
4. Check firewall settings allow connections on port 8000

### Hot reload doesn't update .env changes

Environment variables are loaded at build time. After changing `.env`:
```bash
flutter run
```

## License

Same as main RawRAG project.
