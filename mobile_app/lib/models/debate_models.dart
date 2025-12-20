/// Debate turn model
class DebateTurn {
  final String speaker;
  final String content;

  DebateTurn({required this.speaker, required this.content});

  factory DebateTurn.fromJson(Map<String, dynamic> json) {
    return DebateTurn(
      speaker: json['speaker'] as String,
      content: json['content'] as String,
    );
  }

  Map<String, dynamic> toJson() => {'speaker': speaker, 'content': content};
}

/// Request model for starting a debate
class DebateRequest {
  final String sessionId1;
  final String sessionId2;
  final String topic;
  final int rounds;

  DebateRequest({
    required this.sessionId1,
    required this.sessionId2,
    required this.topic,
    this.rounds = 3,
  });

  Map<String, dynamic> toJson() => {
    'session_id_1': sessionId1,
    'session_id_2': sessionId2,
    'topic': topic,
    'rounds': rounds,
  };
}

/// Response model for debate
class DebateResponse {
  final List<DebateTurn> transcript;
  final String winner;

  DebateResponse({required this.transcript, required this.winner});

  factory DebateResponse.fromJson(Map<String, dynamic> json) {
    return DebateResponse(
      transcript:
          (json['transcript'] as List<dynamic>)
              .map((turn) => DebateTurn.fromJson(turn as Map<String, dynamic>))
              .toList(),
      winner: json['winner'] as String,
    );
  }
}
