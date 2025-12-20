import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/session_provider.dart';
import '../config/env_config.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final sessionProvider = context.watch<SessionProvider>();

    return Scaffold(
      backgroundColor: const Color(0xFF111827),
      appBar: AppBar(
        title: const Text('⚙️ Settings'),
        backgroundColor: const Color(0xFF1F2937),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // AI Mode Section
          _SettingsSection(
            title: 'AI Configuration',
            children: [
              _SettingsTile(
                icon: Icons.smart_toy,
                title: 'AI Mode',
                subtitle: sessionProvider.aiMode == 'api'
                    ? '⚡ Speed (API Mode)'
                    : '🏠 Local (Offline Mode)',
                trailing: Switch(
                  value: sessionProvider.aiMode == 'api',
                  onChanged: (value) {
                    sessionProvider.setAiMode(value ? 'api' : 'local');
                  },
                  activeColor: Colors.blue,
                ),
              ),
              _SettingsTile(
                icon: Icons.info_outline,
                title: 'About AI Modes',
                subtitle:
                    'Speed mode uses cloud API for faster responses.\nLocal mode runs models on device.',
                trailing: const SizedBox.shrink(),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Server Configuration
          _SettingsSection(
            title: 'Server Configuration',
            children: [
              _SettingsTile(
                icon: Icons.dns,
                title: 'Backend URL',
                subtitle: EnvConfig.apiBaseUrl,
                trailing: const Icon(
                  Icons.check_circle,
                  color: Colors.green,
                ),
              ),
              _SettingsTile(
                icon: Icons.info_outline,
                title: 'Change Backend URL',
                subtitle: 'Edit the .env file and rebuild the app',
                trailing: const SizedBox.shrink(),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Sessions Management
          _SettingsSection(
            title: 'Sessions',
            children: [
              _SettingsTile(
                icon: Icons.history,
                title: 'Stored Sessions',
                subtitle: '${sessionProvider.sessions.length} websites indexed',
                trailing: const SizedBox.shrink(),
              ),
              _SettingsTile(
                icon: Icons.delete_sweep,
                title: 'Clear All Sessions',
                subtitle: 'Remove all indexed websites',
                trailing: IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () {
                    _showClearConfirmation(context, sessionProvider);
                  },
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // App Info
          _SettingsSection(
            title: 'About',
            children: [
              const _SettingsTile(
                icon: Icons.apps,
                title: 'App Version',
                subtitle: '1.0.0',
                trailing: SizedBox.shrink(),
              ),
              const _SettingsTile(
                icon: Icons.code,
                title: 'Technology',
                subtitle: 'Flutter + FastAPI + RAG',
                trailing: SizedBox.shrink(),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showClearConfirmation(
    BuildContext context,
    SessionProvider provider,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1F2937),
        title: const Text(
          'Clear All Sessions?',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'This will remove all indexed websites. You cannot undo this action.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              provider.clearSessions();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('All sessions cleared'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: const Text(
              'Clear',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _SettingsSection({
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 12),
          child: Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF1F2937),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: const Color(0xFF374151),
              width: 1,
            ),
          ),
          child: Column(
            children: children,
          ),
        ),
      ],
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Widget trailing;

  const _SettingsTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: Colors.blue,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: Colors.white54,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          trailing,
        ],
      ),
    );
  }
}
