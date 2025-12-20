import 'package:flutter/foundation.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';

/// Provider for managing chat state
class ChatProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  String? _error;

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Clear all messages
  void clearMessages() {
    _messages.clear();
    _error = null;
    notifyListeners();
  }

  /// Add a user message
  void addUserMessage(String content) {
    _messages.add(ChatMessage(
      role: 'user',
      content: content,
    ));
    notifyListeners();
  }

  /// Send a message and get response
  Future<void> sendMessage(
    String sessionId,
    String message,
    String aiMode,
  ) async {
    // Add user message
    addUserMessage(message);

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.sendChatMessage(
        sessionId,
        message,
        aiMode: aiMode,
      );

      _messages.add(response.toChatMessage());
      _error = null;
    } catch (e) {
      _error = e.toString();
      _messages.add(ChatMessage(
        role: 'assistant',
        content: 'Error: ${e.toString()}',
      ));
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load chat history (if implementing persistence)
  void loadHistory(List<ChatMessage> history) {
    _messages = history;
    notifyListeners();
  }
}
