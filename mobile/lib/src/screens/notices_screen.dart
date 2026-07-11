import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../services/services.dart';

class NoticesScreen extends ConsumerWidget {
  const NoticesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(noticeListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Notice Board')),
      body: RefreshIndicator(
        onRefresh: () => ref.read(noticeListProvider.notifier).refresh(),
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Failed: $e')),
          data: (items) => items.isEmpty
              ? const Center(child: Text('Nothing posted yet'))
              : ListView.separated(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final n = items[i];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(children: [
                              if (n.isPinned) const Icon(Icons.push_pin, size: 18, color: Colors.amber),
                              const SizedBox(width: 6),
                              Expanded(child: Text(n.title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700))),
                            ]),
                            const SizedBox(height: 4),
                            Text(
                              DateFormat.yMMMd().add_Hm().format(DateTime.parse(n.publishedAt)),
                              style: const TextStyle(color: Colors.grey, fontSize: 12),
                            ),
                            const SizedBox(height: 8),
                            Text(n.body),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
