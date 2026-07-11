import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../core/api_client.dart';

class ChatMsg {
  final String role; // user | assistant
  final String content;
  final String? intent;
  ChatMsg(this.role, this.content, {this.intent});
}

class AIScreen extends ConsumerStatefulWidget {
  const AIScreen({super.key});
  @override
  ConsumerState<AIScreen> createState() => _AIScreenState();
}

class _AIScreenState extends ConsumerState<AIScreen> {
  final List<ChatMsg> _msgs = [
    ChatMsg('assistant',
        'Hi! Ask me about your bills, complaints, visitors or notices.'),
  ];
  final _input = TextEditingController();
  bool _busy = false;

  Future<void> _send(String text) async {
    if (text.trim().isEmpty) return;
    setState(() {
      _msgs.add(ChatMsg('user', text));
      _busy = true;
      _input.clear();
    });
    try {
      final res = await ref.read(apiClientProvider).dio.post('/ai/chat', data: {'message': text});
      final data = res.data as Map<String, dynamic>;
      setState(() {
        _msgs.add(ChatMsg('assistant', data['reply'] as String, intent: data['intent'] as String?));
      });
    } catch (e) {
      setState(() => _msgs.add(ChatMsg('assistant', 'Sorry, something went wrong.')));
    } finally {
      setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Assistant')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _msgs.length,
              itemBuilder: (_, i) {
                final m = _msgs[i];
                final isUser = m.role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    constraints: const BoxConstraints(maxWidth: 320),
                    decoration: BoxDecoration(
                      color: isUser ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(m.content, style: TextStyle(color: isUser ? Colors.white : null)),
                        if (m.intent != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text('intent: ${m.intent}', style: TextStyle(fontSize: 10, color: isUser ? Colors.white70 : Colors.grey)),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _input,
                      decoration: InputDecoration(hintText: 'Ask anything…', border: OutlineInputBorder(borderRadius: BorderRadius.circular(24))),
                      onSubmitted: _send,
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(onPressed: _busy ? null : () => _send(_input.text), child: _busy ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.send)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
