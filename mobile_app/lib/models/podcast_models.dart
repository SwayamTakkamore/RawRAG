/// Podcast response model
class PodcastResponse {
  final String title;
  final String script;

  PodcastResponse({required this.title, required this.script});

  factory PodcastResponse.fromJson(Map<String, dynamic> json) {
    return PodcastResponse(
      title: json['title'] as String,
      script: json['script'] as String,
    );
  }
}

/// Diagram response model
class DiagramResponse {
  final String mermaidCode;
  final String description;

  DiagramResponse({required this.mermaidCode, required this.description});

  factory DiagramResponse.fromJson(Map<String, dynamic> json) {
    return DiagramResponse(
      mermaidCode: json['mermaid_code'] as String,
      description: json['description'] as String,
    );
  }
}

/// Session model for storing indexed websites
class SessionModel {
  final String sessionId;
  final String url;
  final String title;
  final int pagesIndexed;
  final int totalLinks;
  final DateTime createdAt;

  SessionModel({
    required this.sessionId,
    required this.url,
    required this.title,
    required this.pagesIndexed,
    required this.totalLinks,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() => {
    'sessionId': sessionId,
    'url': url,
    'title': title,
    'pagesIndexed': pagesIndexed,
    'totalLinks': totalLinks,
    'createdAt': createdAt.toIso8601String(),
  };

  factory SessionModel.fromJson(Map<String, dynamic> json) {
    return SessionModel(
      sessionId: json['sessionId'] as String,
      url: json['url'] as String,
      title: json['title'] as String,
      pagesIndexed: json['pagesIndexed'] as int,
      totalLinks: json['totalLinks'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }
}
