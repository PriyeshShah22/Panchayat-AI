// Lightweight model classes for the mobile app.
// Each model has `fromJson` so the REST layer can populate them.

class AppUser {
  final int id;
  final String email;
  final String fullName;
  final bool isSuperuser;
  final int? societyId;
  final List<String> roles;
  AppUser({
    required this.id,
    required this.email,
    required this.fullName,
    required this.isSuperuser,
    required this.societyId,
    required this.roles,
  });
  factory AppUser.fromJson(Map<String, dynamic> j) => AppUser(
        id: j['id'] as int,
        email: j['email'] as String,
        fullName: j['full_name'] as String,
        isSuperuser: j['is_superuser'] == true,
        societyId: j['society_id'] as int?,
        roles: ((j['roles'] as List?) ?? [])
            .map((r) => (r as Map)['name']?.toString() ?? '')
            .where((s) => s.isNotEmpty)
            .toList(),
      );
}

class Complaint {
  final int id;
  final String title;
  final String description;
  final String status;
  final String priority;
  final String? aiCategory;
  final String createdAt;
  Complaint({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.priority,
    required this.aiCategory,
    required this.createdAt,
  });
  factory Complaint.fromJson(Map<String, dynamic> j) => Complaint(
        id: j['id'] as int,
        title: j['title'] as String,
        description: j['description'] as String,
        status: (j['status'] as String).toUpperCase(),
        priority: (j['priority'] as String).toUpperCase(),
        aiCategory: j['ai_suggested_category'] as String?,
        createdAt: j['created_at'] as String,
      );
}

class Bill {
  final int id;
  final String billNumber;
  final String title;
  final double amount;
  final double totalAmount;
  final double paidAmount;
  final String status;
  final String dueDate;
  Bill({
    required this.id,
    required this.billNumber,
    required this.title,
    required this.amount,
    required this.totalAmount,
    required this.paidAmount,
    required this.status,
    required this.dueDate,
  });
  double get outstanding => totalAmount - paidAmount;
  factory Bill.fromJson(Map<String, dynamic> j) => Bill(
        id: j['id'] as int,
        billNumber: j['bill_number'] as String,
        title: j['title'] as String,
        amount: (j['amount'] as num).toDouble(),
        totalAmount: (j['total_amount'] as num).toDouble(),
        paidAmount: (j['paid_amount'] as num).toDouble(),
        status: (j['status'] as String).toUpperCase(),
        dueDate: j['due_date'] as String,
      );
}

class Visitor {
  final int id;
  final String name;
  final String? phone;
  final String? purpose;
  final String? vehicle;
  final String status;
  final String createdAt;
  Visitor({
    required this.id,
    required this.name,
    required this.phone,
    required this.purpose,
    required this.vehicle,
    required this.status,
    required this.createdAt,
  });
  factory Visitor.fromJson(Map<String, dynamic> j) => Visitor(
        id: j['id'] as int,
        name: j['name'] as String,
        phone: j['phone'] as String?,
        purpose: j['purpose'] as String?,
        vehicle: j['vehicle_number'] as String?,
        status: (j['status'] as String).toUpperCase(),
        createdAt: j['created_at'] as String,
      );
}

class Notice {
  final int id;
  final String title;
  final String body;
  final bool isPinned;
  final String audience;
  final String publishedAt;
  Notice({
    required this.id,
    required this.title,
    required this.body,
    required this.isPinned,
    required this.audience,
    required this.publishedAt,
  });
  factory Notice.fromJson(Map<String, dynamic> j) => Notice(
        id: j['id'] as int,
        title: j['title'] as String,
        body: j['body'] as String,
        isPinned: j['is_pinned'] == true,
        audience: j['audience'] as String,
        publishedAt: j['published_at'] as String,
      );
}
