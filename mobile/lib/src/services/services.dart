import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api_client.dart';
import '../models/models.dart';

/// Generic list providers for the entity pages.
class ComplaintListController extends StateNotifier<AsyncValue<List<Complaint>>> {
  ComplaintListController(this.ref) : super(const AsyncValue.loading()) {
    refresh();
  }
  final Ref ref;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final res = await ref.read(apiClientProvider).dio.get('/complaints/?limit=100');
      final list = (res.data as List).map((j) => Complaint.fromJson(j as Map<String, dynamic>)).toList();
      state = AsyncValue.data(list);
    } catch (e, s) {
      state = AsyncValue.error(e, s);
    }
  }

  Future<bool> create({required String title, required String description, required String priority}) async {
    try {
      final res = await ref.read(apiClientProvider).dio.post('/complaints/', data: {
        'title': title,
        'description': description,
        'society_id': 1,
        'priority': priority,
      });
      if ((res.statusCode ?? 0) >= 200 && (res.statusCode ?? 0) < 300) {
        await refresh();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }
}

final complaintListProvider = StateNotifierProvider<ComplaintListController, AsyncValue<List<Complaint>>>(
  (ref) => ComplaintListController(ref),
);

class BillListController extends StateNotifier<AsyncValue<List<Bill>>> {
  BillListController(this.ref) : super(const AsyncValue.loading()) {
    refresh();
  }
  final Ref ref;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final res = await ref.read(apiClientProvider).dio.get('/bills/?limit=100');
      final list = (res.data as List).map((j) => Bill.fromJson(j as Map<String, dynamic>)).toList();
      state = AsyncValue.data(list);
    } catch (e, s) {
      state = AsyncValue.error(e, s);
    }
  }

  Future<bool> pay(int billId, double amount, String method) async {
    try {
      final res = await ref.read(apiClientProvider).dio.post('/bills/$billId/pay', data: {
        'amount': amount,
        'method': method,
        'transaction_ref': null,
      });
      if ((res.statusCode ?? 0) >= 200 && (res.statusCode ?? 0) < 300) {
        await refresh();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }
}

final billListProvider = StateNotifierProvider<BillListController, AsyncValue<List<Bill>>>(
  (ref) => BillListController(ref),
);

class NoticeListController extends StateNotifier<AsyncValue<List<Notice>>> {
  NoticeListController(this.ref) : super(const AsyncValue.loading()) {
    refresh();
  }
  final Ref ref;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final res = await ref.read(apiClientProvider).dio.get('/notices/');
      final list = (res.data as List).map((j) => Notice.fromJson(j as Map<String, dynamic>)).toList();
      state = AsyncValue.data(list);
    } catch (e, s) {
      state = AsyncValue.error(e, s);
    }
  }
}

final noticeListProvider = StateNotifierProvider<NoticeListController, AsyncValue<List<Notice>>>(
  (ref) => NoticeListController(ref),
);

class VisitorListController extends StateNotifier<AsyncValue<List<Visitor>>> {
  VisitorListController(this.ref) : super(const AsyncValue.loading()) {
    refresh();
  }
  final Ref ref;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final res = await ref.read(apiClientProvider).dio.get('/visitors/?limit=100');
      final list = (res.data as List).map((j) => Visitor.fromJson(j as Map<String, dynamic>)).toList();
      state = AsyncValue.data(list);
    } catch (e, s) {
      state = AsyncValue.error(e, s);
    }
  }

  Future<bool> register({required String name, String? phone, String? purpose, String? vehicle}) async {
    try {
      final res = await ref.read(apiClientProvider).dio.post('/visitors/', data: {
        'society_id': 1,
        'flat_id': 1,
        'name': name,
        'phone': phone,
        'purpose': purpose,
        'vehicle_number': vehicle,
      });
      if ((res.statusCode ?? 0) >= 200 && (res.statusCode ?? 0) < 300) {
        await refresh();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<bool> action(int visitorId, String kind) async {
    try {
      final res = await ref.read(apiClientProvider).dio.post('/visitors/$visitorId/action', data: {
        'action': kind,
      });
      if ((res.statusCode ?? 0) >= 200 && (res.statusCode ?? 0) < 300) {
        await refresh();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }
}

final visitorListProvider = StateNotifierProvider<VisitorListController, AsyncValue<List<Visitor>>>(
  (ref) => VisitorListController(ref),
);
