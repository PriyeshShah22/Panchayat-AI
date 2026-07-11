import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'storage.dart';

/// Configured Dio instance. Auth interceptor + automatic refresh on 401.
class ApiClient {
  ApiClient(this.storage) {
    dio = Dio(BaseOptions(
      baseUrl: storage.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Accept': 'application/json'},
      responseType: ResponseType.json,
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (storage.accessToken != null) {
          options.headers['Authorization'] = 'Bearer ${storage.accessToken!}';
        }
        handler.next(options);
      },
      onError: (err, handler) async {
        if (err.response?.statusCode == 401 && storage.refreshToken != null) {
          final ok = await _refresh();
          if (ok) {
            // Retry original request once with new token.
            final req = err.requestOptions;
            req.headers['Authorization'] = 'Bearer ${storage.accessToken!}';
            try {
              final retried = await dio.fetch(req);
              return handler.resolve(retried);
            } catch (e) {
              // fallthrough
            }
          }
        }
        handler.next(err);
      },
    ));
  }

  final Storage storage;
  late final Dio dio;

  Future<bool> _refresh() async {
    try {
      final res = await Dio(BaseOptions(baseUrl: storage.baseUrl))
          .post('/auth/refresh', data: {'refresh_token': storage.refreshToken});
      storage.accessToken = res.data['access_token'] as String?;
      storage.refreshToken = res.data['refresh_token'] as String?;
      return storage.accessToken != null;
    } catch (_) {
      storage.accessToken = null;
      storage.refreshToken = null;
      return false;
    }
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  final s = ref.watch(storageProvider);
  return ApiClient(s);
});
