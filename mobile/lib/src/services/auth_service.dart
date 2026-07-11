import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api_client.dart';
import '../core/storage.dart';
import '../models/models.dart';

class AuthState {
  final AppUser? user;
  final bool initializing;
  final String? error;
  const AuthState({this.user, this.initializing = true, this.error});
  AuthState copyWith({AppUser? user, bool? initializing, String? error, bool clearError = false}) =>
      AuthState(
        user: user ?? this.user,
        initializing: initializing ?? this.initializing,
        error: clearError ? null : (error ?? this.error),
      );
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this.ref) : super(const AuthState());
  final Ref ref;

  ApiClient get _api => ref.read(apiClientProvider);
  Storage get _storage => ref.read(storageProvider);

  Future<void> initialize() async {
    if (!_storage.hasToken) {
      state = const AuthState(initializing: false);
      return;
    }
    try {
      final res = await _api.dio.get('/auth/me');
      state = AuthState(user: AppUser.fromJson(res.data as Map<String, dynamic>), initializing: false);
    } catch (_) {
      state = const AuthState(initializing: false);
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(clearError: true);
    try {
      final res = await _api.dio.post('/auth/login', data: {'email': email, 'password': password});
      final data = res.data as Map<String, dynamic>;
      _storage.accessToken = data['access_token'] as String?;
      _storage.refreshToken = data['refresh_token'] as String?;
      state = AuthState(user: AppUser.fromJson(data['user'] as Map<String, dynamic>));
      return true;
    } catch (e) {
      state = state.copyWith(error: 'Invalid credentials');
      return false;
    }
  }

  Future<bool> register(String fullName, String email, String phone, String password) async {
    state = state.copyWith(clearError: true);
    try {
      final res = await _api.dio.post('/auth/register', data: {
        'full_name': fullName,
        'email': email,
        'phone': phone.isEmpty ? null : phone,
        'password': password,
        'role_names': ['resident'],
      });
      final data = res.data as Map<String, dynamic>;
      _storage.accessToken = data['access_token'] as String?;
      _storage.refreshToken = data['refresh_token'] as String?;
      state = AuthState(user: AppUser.fromJson(data['user'] as Map<String, dynamic>));
      return true;
    } catch (e) {
      state = state.copyWith(error: 'Registration failed');
      return false;
    }
  }

  void logout() {
    _storage.accessToken = null;
    _storage.refreshToken = null;
    state = const AuthState(initializing: false);
  }
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>(
  (ref) => AuthController(ref),
);
