import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../services/services.dart';

class ComplaintsScreen extends ConsumerWidget {
  const ComplaintsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(complaintListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Complaints')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openCreate(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('New'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(complaintListProvider.notifier).refresh(),
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Failed: $e')),
          data: (items) => items.isEmpty
              ? const Center(child: Text('No complaints yet'))
              : ListView.separated(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final c = items[i];
                    return Card(
                      child: ListTile(
                        leading: Icon(
                          _iconFor(c.priority),
                          color: _colorForPriority(c.priority),
                        ),
                        title: Text(c.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('${c.status} · ${DateFormat.yMMMd().add_jm().format(DateTime.parse(c.createdAt))}'),
                        trailing: c.aiCategory != null
                            ? Chip(label: Text(c.aiCategory!, style: const TextStyle(fontSize: 11)))
                            : null,
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }

  IconData _iconFor(String p) {
    switch (p) {
      case 'URGENT':
        return Icons.warning_amber;
      case 'HIGH':
        return Icons.priority_high;
      case 'LOW':
        return Icons.info_outline;
      default:
        return Icons.report_problem;
    }
  }

  Color _colorForPriority(String p) {
    switch (p) {
      case 'URGENT':
        return Colors.red;
      case 'HIGH':
        return Colors.orange;
      case 'LOW':
        return Colors.grey;
      default:
        return Colors.blue;
    }
  }

  void _openCreate(BuildContext context, WidgetRef ref) {
    final titleC = TextEditingController();
    final descC = TextEditingController();
    String priority = 'medium';
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: MediaQuery.of(ctx).viewInsets.bottom + 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('New Complaint', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            TextField(controller: titleC, decoration: const InputDecoration(labelText: 'Title')),
            const SizedBox(height: 8),
            TextField(controller: descC, maxLines: 3, decoration: const InputDecoration(labelText: 'Description')),
            const SizedBox(height: 8),
            StatefulBuilder(builder: (ctx, setSt) {
              return DropdownButtonFormField<String>(
                value: priority,
                decoration: const InputDecoration(labelText: 'Priority'),
                items: const [
                  DropdownMenuItem(value: 'low', child: Text('Low')),
                  DropdownMenuItem(value: 'medium', child: Text('Medium')),
                  DropdownMenuItem(value: 'high', child: Text('High')),
                  DropdownMenuItem(value: 'urgent', child: Text('Urgent')),
                ],
                onChanged: (v) => setSt(() => priority = v ?? 'medium'),
              );
            }),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () async {
                Navigator.pop(ctx);
                await ref.read(complaintListProvider.notifier)
                    .create(title: titleC.text, description: descC.text, priority: priority);
              },
              child: const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }
}
