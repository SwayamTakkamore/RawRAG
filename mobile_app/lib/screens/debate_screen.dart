import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/debate_models.dart';
import '../providers/session_provider.dart';
import '../services/api_service.dart';
import '../models/podcast_models.dart';

class DebateScreen extends StatefulWidget {
  const DebateScreen({super.key});

  @override
  State<DebateScreen> createState() => _DebateScreenState();
}

class _DebateScreenState extends State<DebateScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _topicController = TextEditingController();
  final TextEditingController _url1Controller = TextEditingController();
  final TextEditingController _url2Controller = TextEditingController();

  SessionModel? _session1;
  SessionModel? _session2;
  int _rounds = 3;
  bool _isLoading = false;
  bool _isLoadingUrl1 = false;
  bool _isLoadingUrl2 = false;
  DebateResponse? _debateResult;
  String? _error;

  @override
  void dispose() {
    _topicController.dispose();
    _url1Controller.dispose();
    _url2Controller.dispose();
    super.dispose();
  }

  Future<void> _crawlUrl1() async {
    if (_url1Controller.text.trim().isEmpty) {
      setState(() => _error = 'Please enter URL for Contender A');
      return;
    }

    setState(() {
      _isLoadingUrl1 = true;
      _error = null;
    });

    try {
      final response =
          await _apiService.crawlWebsite(_url1Controller.text.trim());
      final sessionProvider = context.read<SessionProvider>();

      final newSession = SessionModel(
        sessionId: response.sessionId,
        url: _url1Controller.text.trim(),
        title: _url1Controller.text.trim(),
        pagesIndexed: response.pagesIndexed,
        totalLinks: response.totalLinksFound ?? 0,
      );

      sessionProvider.addSession(newSession);
      setState(() => _session1 = newSession);
    } catch (e) {
      setState(() => _error = 'Failed to crawl URL 1: ${e.toString()}');
    } finally {
      setState(() => _isLoadingUrl1 = false);
    }
  }

  Future<void> _crawlUrl2() async {
    if (_url2Controller.text.trim().isEmpty) {
      setState(() => _error = 'Please enter URL for Contender B');
      return;
    }

    setState(() {
      _isLoadingUrl2 = true;
      _error = null;
    });

    try {
      final response =
          await _apiService.crawlWebsite(_url2Controller.text.trim());
      final sessionProvider = context.read<SessionProvider>();

      final newSession = SessionModel(
        sessionId: response.sessionId,
        url: _url2Controller.text.trim(),
        title: _url2Controller.text.trim(),
        pagesIndexed: response.pagesIndexed,
        totalLinks: response.totalLinksFound ?? 0,
      );

      sessionProvider.addSession(newSession);
      setState(() => _session2 = newSession);
    } catch (e) {
      setState(() => _error = 'Failed to crawl URL 2: ${e.toString()}');
    } finally {
      setState(() => _isLoadingUrl2 = false);
    }
  }

  Future<void> _startDebate() async {
    if (_session1 == null || _session2 == null) {
      setState(() => _error = 'Please select two sessions');
      return;
    }

    if (_topicController.text.trim().isEmpty) {
      setState(() => _error = 'Please enter a debate topic');
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _debateResult = null;
    });

    try {
      final result = await _apiService.startDebate(
        DebateRequest(
          sessionId1: _session1!.sessionId,
          sessionId2: _session2!.sessionId,
          topic: _topicController.text.trim(),
          rounds: _rounds,
        ),
      );

      setState(() => _debateResult = result);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final sessionProvider = context.watch<SessionProvider>();
    final sessions = sessionProvider.sessions;

    return Scaffold(
      backgroundColor: const Color(0xFF111827),
      appBar: AppBar(
        title: const Text('⚔️ Debate Arena'),
        backgroundColor: const Color(0xFF1F2937),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.red.shade700, Colors.orange.shade700],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Column(
                children: [
                  Text(
                    '⚔️',
                    style: TextStyle(fontSize: 48),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'DEBATE ARENA',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Watch two AI agents battle it out!',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Contender A - URL Input
            _ContenderCard(
              label: '🔴 Contender A',
              color: Colors.blue,
              urlController: _url1Controller,
              isLoading: _isLoadingUrl1,
              hasSession: _session1 != null,
              onCrawl: _crawlUrl1,
              placeholder: 'https://apple.com',
            ),

            const SizedBox(height: 16),

            // Contender B - URL Input
            _ContenderCard(
              label: '🔵 Contender B',
              color: Colors.red,
              urlController: _url2Controller,
              isLoading: _isLoadingUrl2,
              hasSession: _session2 != null,
              onCrawl: _crawlUrl2,
              placeholder: 'https://samsung.com',
            ),

            const SizedBox(height: 16),

            // OR use existing sessions
            if (sessions.isNotEmpty) ...[
              const Center(
                child: Text(
                  '--- OR USE EXISTING SESSIONS ---',
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              ),
              const SizedBox(height: 16),
              _SessionSelector(
                label: '🔴 Agent A (from history)',
                selectedSession: _session1,
                sessions: sessions,
                onChanged: (session) => setState(() => _session1 = session),
              ),
              const SizedBox(height: 16),
              _SessionSelector(
                label: '🔵 Agent B (from history)',
                selectedSession: _session2,
                sessions: sessions,
                onChanged: (session) => setState(() => _session2 = session),
              ),
              const SizedBox(height: 24),
            ] else
              const SizedBox(height: 24),

            // Topic input
            TextField(
              controller: _topicController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Debate Topic',
                labelStyle: const TextStyle(color: Colors.white70),
                hintText: 'e.g., Which technology is better?',
                hintStyle: const TextStyle(color: Colors.white38),
                filled: true,
                fillColor: const Color(0xFF1F2937),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFF374151)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFF374151)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Colors.blue),
                ),
              ),
              maxLines: 2,
            ),

            const SizedBox(height: 16),

            // Rounds selector
            Row(
              children: [
                const Text(
                  'Rounds:',
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
                const SizedBox(width: 12),
                ...List.generate(3, (index) {
                  final roundCount = index + 2;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text('$roundCount'),
                      selected: _rounds == roundCount,
                      onSelected: (selected) {
                        if (selected) {
                          setState(() => _rounds = roundCount);
                        }
                      },
                      selectedColor: Colors.red,
                      backgroundColor: Colors.grey.shade800,
                      labelStyle: TextStyle(
                        color: _rounds == roundCount
                            ? Colors.white
                            : Colors.white70,
                      ),
                    ),
                  );
                }),
              ],
            ),

            if (_error != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red),
                ),
                child: Text(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ],

            const SizedBox(height: 24),

            // Start button
            ElevatedButton(
              onPressed: _isLoading ? null : _startDebate,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text(
                      '⚔️ START DEBATE',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),

            // Debate transcript
            if (_debateResult != null) ...[
              const SizedBox(height: 32),
              const Text(
                'Debate Transcript',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),

              ..._debateResult!.transcript.map((turn) {
                final isAgentA = turn.speaker == 'Agent A';
                return Container(
                  margin: const EdgeInsets.only(bottom: 16),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1F2937),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isAgentA ? Colors.red : Colors.blue,
                      width: 2,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: isAgentA ? Colors.red : Colors.blue,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              turn.speaker,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        turn.content,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                );
              }),

              // Winner
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.yellow.shade700, Colors.orange.shade700],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    const Text(
                      '🏆',
                      style: TextStyle(fontSize: 48),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'WINNER',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _debateResult!.winner,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ContenderCard extends StatelessWidget {
  final String label;
  final Color color;
  final TextEditingController urlController;
  final bool isLoading;
  final bool hasSession;
  final VoidCallback onCrawl;
  final String placeholder;

  const _ContenderCard({
    required this.label,
    required this.color,
    required this.urlController,
    required this.isLoading,
    required this.hasSession,
    required this.onCrawl,
    required this.placeholder,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                flex: 3,
                child: TextField(
                  controller: urlController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: placeholder,
                    hintStyle:
                        const TextStyle(color: Colors.white38, fontSize: 13),
                    filled: true,
                    fillColor: Colors.black38,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 10,
                    ),
                  ),
                  enabled: !hasSession,
                ),
              ),
              const SizedBox(width: 6),
              Flexible(
                flex: 1,
                child: ElevatedButton(
                  onPressed: (isLoading || hasSession) ? null : onCrawl,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 10,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    minimumSize: const Size(60, 40),
                  ),
                  child: isLoading
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : Text(
                          hasSession ? 'READY' : 'PREP',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                ),
              ),
            ],
          ),
          if (hasSession)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                '✅ Knowledge Loaded',
                style: TextStyle(color: Colors.green, fontSize: 12),
              ),
            ),
        ],
      ),
    );
  }
}

class _SessionSelector extends StatelessWidget {
  final String label;
  final SessionModel? selectedSession;
  final List<SessionModel> sessions;
  final ValueChanged<SessionModel?> onChanged;

  const _SessionSelector({
    required this.label,
    required this.selectedSession,
    required this.sessions,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF374151),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<SessionModel>(
            value: selectedSession,
            isExpanded: true,
            decoration: InputDecoration(
              filled: true,
              fillColor: Colors.black38,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 8,
              ),
            ),
            dropdownColor: const Color(0xFF1F2937),
            hint: const Text(
              'Select a session',
              style: TextStyle(color: Colors.white54),
              overflow: TextOverflow.ellipsis,
            ),
            selectedItemBuilder: (BuildContext context) {
              return sessions.map((session) {
                return Text(
                  session.title,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                );
              }).toList();
            },
            items: sessions.map((session) {
              return DropdownMenuItem(
                value: session,
                child: Text(
                  session.title,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              );
            }).toList(),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
