"""Seed the database with sample data for development."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta

from app.core.security import hash_password
from app.db.base import SessionLocal, create_all
from app.models.bill import Bill, BillStatus, Payment, PaymentMethod
from app.models.complaint import Complaint, ComplaintCategory, ComplaintPriority, ComplaintStatus
from app.models.notice import Notice
from app.models.resident import Resident
from app.models.society import Block, Flat, Society
from app.models.user import Permission, Role, User, UserStatus
from app.models.visitor import Visitor, VisitorStatus
from app.services.billing_service import create_user_bill


def upsert_role(db, name: str, description: str = "") -> Role:
    role = db.query(Role).filter_by(name=name).one_or_none()
    if role:
        return role
    role = Role(name=name, description=description)
    db.add(role)
    db.flush()
    return role


def upsert_user(db, *, email: str, name: str, password: str,
                society_id: int | None, roles: list[str], is_super: bool = False,
                phone: str | None = None) -> User:
    u = db.query(User).filter_by(email=email).one_or_none()
    if u:
        return u
    u = User(email=email, full_name=name, hashed_password=hash_password(password),
             society_id=society_id, is_superuser=is_super, status=UserStatus.active,
             phone=phone)
    for r in roles:
        u.roles.append(upsert_role(db, r))
    db.add(u)
    db.flush()
    return u


def upsert_permission(db, code: str, name: str) -> Permission:
    p = db.query(Permission).filter_by(code=code).one_or_none()
    if p:
        return p
    p = Permission(code=code, name=name)
    db.add(p)
    db.flush()
    return p


def main() -> None:
    create_all()
    db = SessionLocal()
    try:
        print("Seeding...")
        # Permissions
        admin_perms = [
            ("users.manage", "Manage users"),
            ("societies.manage", "Manage societies"),
            ("reports.view", "View reports"),
            ("settings.manage", "Manage settings"),
        ]
        committee_perms = [
            ("bills.manage", "Manage bills"),
            ("complaints.manage", "Manage complaints"),
            ("notices.publish", "Publish notices"),
            ("reports.view", "View reports"),
        ]
        security_perms = [
            ("visitors.checkin", "Process visitor check-in/out"),
        ]

        # Society
        soc = db.query(Society).filter_by(name="Green Park Residency").one_or_none()
        if not soc:
            soc = Society(name="Green Park Residency",
                          address="21 MG Road, Sector 5",
                          city="Pune", state="MH", pincode="411014",
                          registration_no="GPR-2018-0142",
                          contact_email="office@greenpark.com",
                          contact_phone="+91-9876543210")
            db.add(soc)
            db.flush()
        print("  society:", soc.name)

        # Four wings, four floors, four flats on every floor.
        flats_by_key = {}
        for wing in ("A", "B", "C", "D"):
            block = db.query(Block).filter_by(society_id=soc.id, name=wing).one_or_none()
            if not block:
                block = Block(society_id=soc.id, name=wing, floors=4)
                db.add(block)
                db.flush()
            else:
                block.floors = 4
            for floor in range(1, 5):
                for unit in range(1, 5):
                    number = f"{floor}0{unit}"
                    flat = db.query(Flat).filter_by(block_id=block.id, number=number).one_or_none()
                    if not flat:
                        flat = Flat(society_id=soc.id, block_id=block.id, number=number,
                                    floor=floor, area_sqft=1000, bedrooms=2, bathrooms=2)
                        db.add(flat)
                        db.flush()
                    flats_by_key[(wing, number)] = flat
        print(f"  flats: {len(flats_by_key)}")

        # Roles + Permissions
        admin = upsert_role(db, "admin", "Society administrator")
        committee = upsert_role(db, "committee", "Managing committee member")
        resident = upsert_role(db, "resident", "Resident / owner")
        security = upsert_role(db, "security", "Security staff")

        for code, name in admin_perms:
            permission = upsert_permission(db, code, name)
            if permission not in admin.permissions:
                admin.permissions.append(permission)
        for code, name in committee_perms:
            permission = upsert_permission(db, code, name)
            if permission not in committee.permissions:
                committee.permissions.append(permission)
        for code, name in security_perms:
            permission = upsert_permission(db, code, name)
            if permission not in security.permissions:
                security.permissions.append(permission)
        db.flush()

        # Users
        superuser = upsert_user(db, email="admin@greenpark.com", name="Site Admin",
                                password="Admin@12345", society_id=soc.id,
                                roles=["admin"], is_super=True)
        committee_user = upsert_user(db, email="committee@greenpark.com", name="Priya Committee",
                                     password="Committee@123", society_id=soc.id,
                                     roles=["committee"])
        security_user = upsert_user(db, email="security@greenpark.com", name="Ram Security",
                                    password="Security@123", society_id=soc.id,
                                    roles=["security"])
        resident_admin = upsert_user(db, email="resident@greenpark.com", name="Asha Resident",
                                     password="Resident@123", society_id=soc.id,
                                     roles=["resident", "committee"])
        # A second resident for visitor demos
        ravi = upsert_user(db, email="ravi@greenpark.com", name="Ravi Kumar",
                           password="Ravi@12345", society_id=soc.id,
                           roles=["resident"], phone="+91-9000000001")

        # Resident profiles
        for user_obj, flat in [(resident_admin, flats_by_key[("A", "101")]), (ravi, flats_by_key[("B", "101")])]:
            existing = db.query(Resident).filter_by(user_id=user_obj.id).one_or_none()
            if not existing:
                db.add(Resident(user_id=user_obj.id, flat_id=flat.id, ownership="owner",
                                 emergency_contact_name="Friend",
                                 emergency_contact_phone="+91-9999999999"))
        db.flush()

        # Complaint categories
        cats = ["Plumbing", "Electrical", "Cleaning", "Security", "Parking", "Lift", "Pest Control", "Noise"]
        for c in cats:
            if not db.query(ComplaintCategory).filter_by(name=c).one_or_none():
                db.add(ComplaintCategory(name=c, color="#1976d2"))
        db.flush()

        # Sample complaints
        if not db.query(Complaint).first():
            plumbing = db.query(ComplaintCategory).filter_by(name="Plumbing").one()
            db.add(Complaint(
                title="Leakage in kitchen sink",
                description="The kitchen sink pipe is leaking continuously.",
                society_id=soc.id, flat_id=flats_by_key[("A", "101")].id,
                reporter_id=resident_admin.id, category_id=plumbing.id,
                status=ComplaintStatus.in_progress,
                priority=ComplaintPriority.high,
            ))
            db.add(Complaint(
                title="Lift not working in Block B",
                description="Lift has been stuck on 3rd floor since morning.",
                society_id=soc.id, flat_id=flats_by_key[("B", "201")].id,
                reporter_id=ravi.id,
                status=ComplaintStatus.submitted,
                priority=ComplaintPriority.urgent,
            ))

        # Notices
        if not db.query(Notice).first():
            db.add(Notice(society_id=soc.id, author_id=committee_user.id,
                          title="Water supply shutdown — Sunday",
                          body="Water supply will be unavailable 9 AM to 1 PM this Sunday for tank cleaning.",
                          is_pinned=True, audience="all"))
            db.add(Notice(society_id=soc.id, author_id=committee_user.id,
                          title="Annual general meeting",
                          body="AGM scheduled for 25th at the clubhouse. Attendance is appreciated."))

        # Visitors
        if not db.query(Visitor).first():
            db.add(Visitor(society_id=soc.id, flat_id=flats_by_key[("A", "101")].id, host_id=resident_admin.id,
                           name="Delivery — Amazon", phone="+91-8000000001",
                           purpose="Parcel delivery", status=VisitorStatus.checked_in))
            db.add(Visitor(society_id=soc.id, flat_id=flats_by_key[("B", "101")].id, host_id=ravi.id,
                           name="Friend — Ajay", phone="+91-8000000002",
                           purpose="Personal visit", vehicle_number="MH12AB1234",
                           status=VisitorStatus.approved))

        # One idempotent maintenance-only demo bill. Admins normally bill every resident in one action.
        if not db.query(Bill).first():
            create_user_bill(db, society_id=soc.id, billed_user=resident_admin,
                billing_year=date.today().year, billing_month=date.today().month,
                due_date=date.today() + timedelta(days=15), maintenance_amount=2500,
                description="Demonstration monthly society maintenance")

        db.commit()
        # Keep console output compatible with the default Windows code page.
        print("[OK] Seed complete")
        print("\nLogin credentials (all in society: Green Park Residency):")
        print("  admin@greenpark.com     / Admin@12345     (superuser + admin)")
        print("  committee@greenpark.com / Committee@123   (committee)")
        print("  security@greenpark.com  / Security@123    (security)")
        print("  resident@greenpark.com  / Resident@123    (resident + committee)")
        print("  ravi@greenpark.com      / Ravi@12345      (resident)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
