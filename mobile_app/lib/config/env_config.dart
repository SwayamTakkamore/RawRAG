import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Environment configuration loaded from .env file
class EnvConfig {
  /// Load environment variables from .env file
  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }

  /// Get the API base URL from environment
  /// Falls back to localhost if not set
  static String get apiBaseUrl {
    return dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000';
  }

  /// Get the API endpoint with /api prefix
  static String get apiEndpoint => '$apiBaseUrl/api';

  /// Check if environment is loaded
  static bool get isLoaded => dotenv.isEveryDefined(['API_BASE_URL']);
}
