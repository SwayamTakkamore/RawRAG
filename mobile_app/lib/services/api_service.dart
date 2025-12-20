import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/env_config.dart';
import '../models/crawl_models.dart';
import '../models/chat_models.dart';
import '../models/debate_models.dart';
import '../models/podcast_models.dart';

/// API Service for communicating with the RawRAG backend
class ApiService {
  final String baseUrl;

  ApiService() : baseUrl = EnvConfig.apiEndpoint;

  /// Crawl and index a website
  Future<CrawlResponse> crawlWebsite(
    String url, {
    String aiMode = 'api',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/crawl?ai_mode=$aiMode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(CrawlRequest(url: url).toJson()),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return CrawlResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to crawl website');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Send a chat message
  Future<ChatResponse> sendChatMessage(
    String sessionId,
    String message, {
    String aiMode = 'api',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat?ai_mode=$aiMode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(
          ChatRequest(sessionId: sessionId, message: message).toJson(),
        ),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ChatResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to send message');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Start a debate between two websites
  Future<DebateResponse> startDebate(DebateRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/debate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return DebateResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to start debate');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Generate a podcast from a session
  Future<PodcastResponse> generatePodcast(String sessionId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/podcast'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'session_id': sessionId, 'message': ''}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return PodcastResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to generate podcast');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Generate a diagram from a session
  Future<DiagramResponse> generateDiagram(
    String sessionId, {
    String message = '',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/diagram'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return DiagramResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to generate diagram');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get session status
  Future<Map<String, dynamic>> getSessionStatus(String sessionId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/status/$sessionId'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Session not found');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Health check
  Future<bool> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Get graph data for visualization
  Future<Map<String, dynamic>> getGraphData(String sessionId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/graph/$sessionId'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to load graph data');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
