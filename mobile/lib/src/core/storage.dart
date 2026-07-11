import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Thin wrapper around SharedPreferences for token + theme persistence.
class Storage {
  Storage(this._prefs);
  final SharedPreferences _prefs;
  static const _kAccess = 'access_token';
  static const _kRefresh = 'refresh_token';
  static const _kBaseUrl = 'api_base_url';

  String? get accessToken => _prefs.getString(_kAccess);
  String? get refreshToken => _prefs.getString(_kRefresh);
  String get baseUrl => _prefs.getString(_kBaseUrl) ?? _defaultBase;

  set accessToken(String? value) =>
      value == null ? _prefs.remove(_kAccess) : _prefs.setString(_kAccess, value);
  set refreshToken(String? value) =>
      value == null ? _prefs.remove(_kRefresh) : _prefs.setString(_kRefresh, value);
  set baseUrl(String value) => _prefs.setString(_kBaseUrl, value);

  bool get hasToken => accessToken != null && accessToken!.isNotEmpty;
}

const String _defaultBase = 'http://10.0.2.2:8000/api/v1';

final storageProvider = Provider<Storage>((ref) {
  throw UnimplementedError('storageProvider must be overridden in main()');
});
