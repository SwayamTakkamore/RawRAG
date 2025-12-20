import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/podcast_models.dart';

/// Provider for managing sessions (indexed websites)
class SessionProvider with ChangeNotifier {
  List<SessionModel> _sessions = [];
  SessionModel? _currentSession;
  String _aiMode = 'api'; // 'api' or 'local'

  List<SessionModel> get sessions => _sessions;
  SessionModel? get currentSession => _currentSession;
  String get aiMode => _aiMode;

  SessionProvider() {
    _loadSessions();
  }

  /// Load sessions from local storage
  Future<void> _loadSessions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final sessionsJson = prefs.getStringList('sessions') ?? [];
      _sessions = sessionsJson
          .map((json) => SessionModel.fromJson(jsonDecode(json)))
          .toList();

      // Load AI mode preference
      _aiMode = prefs.getString('ai_mode') ?? 'api';

      notifyListeners();
    } catch (e) {
      debugPrint('Error loading sessions: $e');
    }
  }

  /// Save sessions to local storage
  Future<void> _saveSessions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final sessionsJson =
          _sessions.map((session) => jsonEncode(session.toJson())).toList();
      await prefs.setStringList('sessions', sessionsJson);
    } catch (e) {
      debugPrint('Error saving sessions: $e');
    }
  }

  /// Add a new session
  void addSession(SessionModel session) {
    _sessions.insert(0, session); // Add to beginning
    _currentSession = session;
    _saveSessions();
    notifyListeners();
  }

  /// Set current session
  void setCurrentSession(SessionModel? session) {
    _currentSession = session;
    notifyListeners();
  }

  /// Remove a session
  void removeSession(String sessionId) {
    _sessions.removeWhere((s) => s.sessionId == sessionId);
    if (_currentSession?.sessionId == sessionId) {
      _currentSession = null;
    }
    _saveSessions();
    notifyListeners();
  }

  /// Clear all sessions
  void clearSessions() {
    _sessions.clear();
    _currentSession = null;
    _saveSessions();
    notifyListeners();
  }

  /// Set AI mode
  Future<void> setAiMode(String mode) async {
    _aiMode = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('ai_mode', mode);
    notifyListeners();
  }

  /// Get session by ID
  SessionModel? getSessionById(String sessionId) {
    try {
      return _sessions.firstWhere((s) => s.sessionId == sessionId);
    } catch (e) {
      return null;
    }
  }
}
