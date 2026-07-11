import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../services/services.dart';

class BillsScreen extends ConsumerWidget {
  const BillsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(billListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Bills & Maintenance')),
      body: RefreshIndicator(
        onRefresh: () => ref.read(billListProvider.notifier).refresh(),
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Failed: $e')),
          data: (items) => items.isEmpty
              ? const Center(child: Text('No bills'))
              : ListView.separated(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final b = items[i];
                    return Card(
                      child: ListTile(
                        title: Text('${b.billNumber} · ${b.title}'),
                        subtitle: Text(
                          'Due ${DateFormat.yMMMd().format(DateTime.parse(b.dueDate))}\n'
                          'Total ₹${b.totalAmount.toStringAsFixed(0)} · Paid ₹${b.paidAmount.toStringAsFixed(0)} · Outstanding ₹${b.outstanding.toStringAsFixed(0)}',
                        ),
                        isThreeLine: true,
                        trailing: b.outstanding > 0
                            ? FilledButton(
                                onPressed: () async {
                                  final ok = await ref.read(billListProvider.notifier)
                                      .pay(b.id, b.outstanding, 'upi');
                                  if (!context.mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text(ok ? 'Payment recorded' : 'Failed')),
                                  );
                                },
                                child: const Text('Pay'),
                              )
                            : const Chip(label: Text('PAID'), backgroundColor: Colors.green),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
