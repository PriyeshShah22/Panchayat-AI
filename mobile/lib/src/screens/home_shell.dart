import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final tabs = ['/', '/complaints', '/bills', '/visitors', '/notices', '/ai', '/profile'];
final labels = ['Home', 'Complaints', 'Bills', 'Visitors', 'Notices', 'AI', 'Profile'];
final icons = [
  Icons.dashboard,
  Icons.report_problem,
  Icons.receipt_long,
  Icons.login,
  Icons.campaign,
  Icons.smart_toy,
  Icons.person,
];

class HomeShell extends ConsumerWidget {
  const HomeShell({super.key, required this.child});
  final Widget child;

  int _indexFromLocation(String loc) {
    for (var i = 0; i < tabs.length; i++) {
      if (loc == tabs[i] || loc.startsWith('${tabs[i]}/')) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loc = GoRouter.of(context).routerDelegate.currentConfiguration.uri.toString();
    final i = _indexFromLocation(loc);
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: i,
        onDestinationSelected: (idx) => context.go(tabs[idx]),
        destinations: [
          for (var k = 0; k < tabs.length; k++)
            NavigationDestination(icon: Icon(icons[k]), label: labels[k]),
        ],
      ),
    );
  }
}
