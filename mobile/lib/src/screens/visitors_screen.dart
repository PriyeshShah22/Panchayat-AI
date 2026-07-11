import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../services/services.dart';

class VisitorsScreen extends ConsumerWidget {
  const VisitorsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(visitorListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Visitors')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openCreate(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Register'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(visitorListProvider.notifier).refresh(),
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Failed: $e')),
          data: (items) => items.isEmpty
              ? const Center(child: Text('No visitors'))
              : ListView.separated(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final v = items[i];
                    return Card(
                      child: ListTile(
                        leading: CircleAvatar(child: Text(v.name.isNotEmpty ? v.name[0] : '?')),
                        title: Text(v.name),
                        subtitle: Text('${v.purpose ?? ''} · ${DateFormat.yMMMd().add_Hm().format(DateTime.parse(v.createdAt))}'),
                        trailing: PopupMenuButton<String>(
                          onSelected: (kind) async {
                            await ref.read(visitorListProvider.notifier).action(v.id, kind);
                          },
                          itemBuilder: (_) => const [
                            PopupMenuItem(value: 'approve', child: Text('Approve')),
                            PopupMenuItem(value: 'reject', child: Text('Reject')),
                            PopupMenuItem(value: 'check_in', child: Text('Check in')),
                            PopupMenuItem(value: 'check_out', child: Text('Check out')),
                          ],
                          child: Chip(label: Text(v.status)),
                        ),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }

  void _openCreate(BuildContext context, WidgetRef ref) {
    final nameC = TextEditingController();
    final phoneC = TextEditingController();
    final purposeC = TextEditingController();
    final vehicleC = TextEditingController();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: MediaQuery.of(ctx).viewInsets.bottom + 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Register Visitor', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            TextField(controller: nameC, decoration: const InputDecoration(labelText: 'Name')),
            const SizedBox(height: 8),
            TextField(controller: phoneC, decoration: const InputDecoration(labelText: 'Phone')),
            const SizedBox(height: 8),
            TextField(controller: purposeC, decoration: const InputDecoration(labelText: 'Purpose')),
            const SizedBox(height: 8),
            TextField(controller: vehicleC, decoration: const InputDecoration(labelText: 'Vehicle (optional)')),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () async {
                Navigator.pop(ctx);
                await ref.read(visitorListProvider.notifier).register(
                      name: nameC.text,
                      phone: phoneC.text.isEmpty ? null : phoneC.text,
                      purpose: purposeC.text.isEmpty ? null : purposeC.text,
                      vehicle: vehicleC.text.isEmpty ? null : vehicleC.text,
                    );
              },
              child: const Text('Register'),
            ),
          ],
        ),
      ),
    );
  }
}
