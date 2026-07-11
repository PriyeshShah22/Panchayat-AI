import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../services/auth_service.dart';
import '../services/services.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    final bills = ref.watch(billListProvider);
    final complaints = ref.watch(complaintListProvider);
    final visitors = ref.watch(visitorListProvider);

    final pendingBills = bills.maybeWhen(
      data: (data) => data.where((b) => b.status != 'PAID').length,
      orElse: () => 0,
    );
    final openComplaints = complaints.maybeWhen(
      data: (data) => data.where((c) => c.status != 'RESOLVED' && c.status != 'CLOSED').length,
      orElse: () => 0,
    );
    final todayVisitors = visitors.maybeWhen(
      data: (data) => data.length,
      orElse: () => 0,
    );

    return Scaffold(
      appBar: AppBar(
        title: Text('Hello, ${auth.user?.fullName.split(' ').first ?? 'User'}'),
        actions: [
          IconButton(onPressed: () => context.go('/profile'), icon: const Icon(Icons.person)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.read(billListProvider.notifier).refresh();
          ref.read(complaintListProvider.notifier).refresh();
          ref.read(visitorListProvider.notifier).refresh();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _bigCard(context, 'Outstanding bills', '$pendingBills', Icons.receipt_long, () => context.go('/bills')),
            const SizedBox(height: 12),
            _bigCard(context, 'Open complaints', '$openComplaints', Icons.report_problem, () => context.go('/complaints')),
            const SizedBox(height: 12),
            _bigCard(context, 'Recent visitors', '$todayVisitors', Icons.login, () => context.go('/visitors')),
            const SizedBox(height: 24),
            Text('Recent notices', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ...ref.watch(noticeListProvider).maybeWhen(
                  data: (list) => list.take(3).map((n) => Card(
                        child: ListTile(
                          leading: Icon(n.isPinned ? Icons.push_pin : Icons.campaign),
                          title: Text(n.title),
                          subtitle: Text(DateFormat.yMMMd().add_Hm().format(DateTime.parse(n.publishedAt))),
                        ),
                      )),
                  orElse: () => [const Padding(padding: EdgeInsets.all(16), child: Text('Loading…'))],
                ),
          ],
        ),
      ),
    );
  }

  Widget _bigCard(BuildContext ctx, String title, String value, IconData icon, VoidCallback onTap) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(backgroundColor: Theme.of(ctx).colorScheme.primaryContainer, child: Icon(icon, color: Theme.of(ctx).colorScheme.primary)),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(ctx).textTheme.bodyMedium),
                    Text(value, style: Theme.of(ctx).textTheme.headlineSmall),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
