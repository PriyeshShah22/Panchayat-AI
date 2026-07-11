import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/home_shell.dart';
import '../screens/dashboard_screen.dart';
import '../screens/complaints_screen.dart';
import '../screens/bills_screen.dart';
import '../screens/visitors_screen.dart';
import '../screens/notices_screen.dart';
import '../screens/ai_screen.dart';
import '../screens/profile_screen.dart';
import '../services/auth_service.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  // Listen to the auth state to flip the redirect target.
  final authNotifier = _AuthRouterListener(ref);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: authNotifier,
    redirect: (context, state) {
      final auth = ref.read(authControllerProvider);
      final loggingIn = state.matchedLocation == '/login' || state.matchedLocation == '/register';
      if (auth.initializing) return '/splash';
      if (auth.user == null) return loggingIn ? null : '/login';
      if (loggingIn) return '/';
      return null;
    },
    routes: [
      GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      ShellRoute(
        builder: (context, state, child) => HomeShell(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, __) => const DashboardScreen()),
          GoRoute(path: '/complaints', builder: (_, __) => const ComplaintsScreen()),
          GoRoute(path: '/bills', builder: (_, __) => const BillsScreen()),
          GoRoute(path: '/visitors', builder: (_, __) => const VisitorsScreen()),
          GoRoute(path: '/notices', builder: (_, __) => const NoticesScreen()),
          GoRoute(path: '/ai', builder: (_, __) => const AIScreen()),
          GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
        ],
      ),
    ],
  );
});

class _AuthRouterListener extends ChangeNotifier {
  _AuthRouterListener(Ref ref) {
    _sub = ref.listen<AuthState>(
      authControllerProvider,
      (_, __) => notifyListeners(),
      fireImmediately: false,
    );
  }
  late final ProviderSubscription<AuthState> _sub;
  @override
  void dispose() {
    _sub.close();
    super.dispose();
  }
}
