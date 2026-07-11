import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../services/auth_service.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authControllerProvider).user;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: ListTile(
                leading: const CircleAvatar(child: Icon(Icons.person)),
                title: Text(user?.fullName ?? 'Guest'),
                subtitle: Text(user?.email ?? ''),
              ),
            ),
            const SizedBox(height: 12),
            if (user != null)
              Card(
                child: ListTile(
                  leading: const Icon(Icons.badge),
                  title: const Text('Roles'),
                  subtitle: Text(user.roles.join(', ')),
                ),
              ),
            const SizedBox(height: 16),
            FilledButton.tonal(
              onPressed: () {
                ref.read(authControllerProvider.notifier).logout();
                context.go('/login');
              },
              child: const Text('Sign out'),
            ),
          ],
        ),
      ),
    );
  }
}
