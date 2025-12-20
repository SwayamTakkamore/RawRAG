/// Chat message model
class ChatMessage {
  final String role; // 'user' or 'assistant'
  final String content;
  final List<String>? sources;
  final String? confidence;
  final DateTime timestamp;

  ChatMessage({
    required this.role,
    required this.content,
    this.sources,
    this.confidence,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';

  Map<String, dynamic> toJson() => {
    'role': role,
    'content': content,
    'sources': sources,
    'confidence': confidence,
    'timestamp': timestamp.toIso8601String(),
  };

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      role: json['role'] as String,
      content: json['content'] as String,
      sources: (json['sources'] as List<dynamic>?)?.cast<String>(),
      confidence: json['confidence'] as String?,
      timestamp:
          json['timestamp'] != null
              ? DateTime.parse(json['timestamp'] as String)
              : DateTime.now(),
    );
  }
}

/// Request model for sending a chat message
class ChatRequest {
  final String sessionId;
  final String message;

  ChatRequest({required this.sessionId, required this.message});

  Map<String, dynamic> toJson() => {
    'session_id': sessionId,
    'message': message,
  };
}

/// Response model for chat API
class ChatResponse {
  final String answer;
  final List<String> sources;
  final String confidence;

  ChatResponse({
    required this.answer,
    required this.sources,
    required this.confidence,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      answer: json['answer'] as String,
      sources: (json['sources'] as List<dynamic>).cast<String>(),
      confidence: json['confidence'] as String,
    );
  }

  /// Convert to ChatMessage
  ChatMessage toChatMessage() {
    return ChatMessage(
      role: 'assistant',
      content: answer,
      sources: sources,
      confidence: confidence,
    );
  }
}
