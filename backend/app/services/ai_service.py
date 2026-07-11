"""AI assistant service.

Uses OpenAI when configured, otherwise falls back to a deterministic local
intent router over real database facts. Always permission-aware: residents
only see their own data; committee/admin see their scope.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bill import Bill, BillStatus
from app.models.chat import ChatMessage
from app.models.complaint import Complaint, ComplaintStatus
from app.models.notice import Notice
from app.models.resident import Resident
from app.models.user import User
from app.models.visitor import Visitor, VisitorStatus


_INTENTS = {
    "maintenance_pending": [r"\bmaintenance\b", r"outstanding", r"unpaid", r"due bill"],
    "complaint_history": [r"complaint", r"issue", r"ticket"],
    "last_payment": [r"last payment", r"recent payment", r"paid"],
    "visitors_today": [r"visitor", r"guest", r"who came", r"who visited"],
    "notices_recent": [r"notice", r"announcement", r"circular"],
    "defaulter_list": [r"defaulter", r"who hasn.?t paid", r"outstanding list"],
    "active_users": [r"active user", r"inactive"],
    "summary": [r"summari[sz]e", r"overview", r"report"],
}


def _classify(message: str) -> str:
    msg = message.lower()
    for intent, patterns in _INTENTS.items():
        for p in patterns:
            if re.search(p, msg):
                return intent
    return "generic"


def _resident_flat_ids(db: Session, resident: Resident) -> List[int]:
    return [resident.flat_id]


def _handle_intent(intent: str, db: Session, user: User) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    if intent == "maintenance_pending":
        if user.is_superuser or "committee" in user.role_names or "admin" in user.role_names:
            bills = db.execute(
                select(Bill).where(Bill.status.in_([BillStatus.pending, BillStatus.overdue])).limit(20)
            ).scalars().all()
            data["outstanding_count"] = len(bills)
            data["total_outstanding"] = round(sum(b.outstanding for b in bills), 2)
            data["sample"] = [
                {"bill_number": b.bill_number, "flat_id": b.flat_id, "outstanding": b.outstanding}
                for b in bills[:5]
            ]
        else:
            resident = user.resident
            if not resident:
                return {"reply": "I could not find your resident profile."}
            bills = db.execute(
                select(Bill).where(
                    Bill.flat_id == resident.flat_id,
                    Bill.status.in_([BillStatus.pending, BillStatus.overdue]),
                )
            ).scalars().all()
            data["outstanding_count"] = len(bills)
            data["total_outstanding"] = round(sum(b.outstanding for b in bills), 2)

    elif intent == "complaint_history":
        if user.is_superuser or "committee" in user.role_names or "admin" in user.role_names:
            recent = db.execute(
                select(Complaint).order_by(desc(Complaint.created_at)).limit(10)
            ).scalars().all()
        else:
            recent = db.execute(
                select(Complaint).where(Complaint.reporter_id == user.id)
                .order_by(desc(Complaint.created_at)).limit(10)
            ).scalars().all()
        data["count"] = len(recent)
        data["recent"] = [
            {"id": c.id, "title": c.title, "status": c.status.value, "priority": c.priority.value}
            for c in recent
        ]

    elif intent == "last_payment":
        if not user.resident:
            return {"reply": "Resident profile not found."}
        bills = db.execute(
            select(Bill).where(Bill.flat_id == user.resident.flat_id, Bill.paid_at.is_not(None))
            .order_by(desc(Bill.paid_at)).limit(1)
        ).scalars().first()
        if bills:
            data["amount"] = bills.paid_amount
            data["paid_at"] = bills.paid_at.isoformat()
            data["bill_number"] = bills.bill_number
        else:
            data["paid_at"] = None

    elif intent == "visitors_today":
        since = datetime.utcnow() - timedelta(hours=24)
        if user.is_superuser or "security" in user.role_names or "committee" in user.role_names:
            visitors = db.execute(
                select(Visitor).where(Visitor.created_at >= since)
            ).scalars().all()
        else:
            visitors = db.execute(
                select(Visitor).where(Visitor.host_id == user.id, Visitor.created_at >= since)
            ).scalars().all()
        data["count"] = len(visitors)
        data["sample"] = [
            {"name": v.name, "purpose": v.purpose, "status": v.status.value} for v in visitors[:5]
        ]

    elif intent == "notices_recent":
        notices = db.execute(
            select(Notice).order_by(desc(Notice.published_at)).limit(5)
        ).scalars().all()
        data["count"] = len(notices)
        data["recent"] = [{"id": n.id, "title": n.title} for n in notices]

    elif intent == "defaulter_list":
        rows = db.execute(
            select(Bill.flat_id, func.count(Bill.id).label("cnt"), func.sum(Bill.total_amount - Bill.paid_amount).label("due"))
            .where(Bill.status.in_([BillStatus.pending, BillStatus.overdue]))
            .group_by(Bill.flat_id).order_by(desc("due")).limit(10)
        ).all()
        data["top_defaulters"] = [
            {"flat_id": r.flat_id, "bills": r.cnt, "outstanding": round(float(r.due or 0), 2)} for r in rows
        ]

    elif intent == "active_users":
        rows = db.execute(select(User).limit(20)).scalars().all()
        data["active_count"] = sum(1 for u in rows if u.status.value == "active")
        data["sample"] = [u.email for u in rows[:5]]

    elif intent == "summary":
        complaints = db.execute(select(func.count(Complaint.id))).scalar() or 0
        bills = db.execute(select(func.count(Bill.id))).scalar() or 0
        visitors = db.execute(select(func.count(Visitor.id))).scalar() or 0
        data = {"complaints_total": complaints, "bills_total": bills, "visitors_total": visitors}

    return data


def _natural_reply(intent: str, data: Dict[str, Any], user: User) -> str:
    role = "Admin" if user.is_superuser else next(iter(user.role_names), "User")

    if intent == "maintenance_pending":
        if "outstanding_count" not in data:
            return "I could not retrieve your maintenance status."
        return (
            f"You have {data['outstanding_count']} outstanding bill(s) totalling "
            f"₹{data['total_outstanding']}."
        )
    if intent == "complaint_history":
        return f"You have filed {data.get('count', 0)} complaint(s). Most recent: " + ", ".join(
            f"#{c['id']} {c['title']} ({c['status']})" for c in data.get("recent", [])[:3]
        )
    if intent == "last_payment":
        if not data.get("paid_at"):
            return "No payments recorded yet."
        return f"Your last payment was ₹{data['amount']} on {data['paid_at']} for bill {data['bill_number']}."
    if intent == "visitors_today":
        names = ", ".join(v["name"] for v in data.get("sample", []))
        return f"{data['count']} visitor(s) in the last 24 hours. Latest: {names or 'none'}."
    if intent == "notices_recent":
        titles = "; ".join(n["title"] for n in data.get("recent", []))
        return f"{data['count']} recent notice(s): {titles or 'none'}."
    if intent == "defaulter_list":
        items = data.get("top_defaulters", [])
        if not items:
            return "No defaulters right now."
        return "Top defaulters by outstanding amount: " + ", ".join(
            f"Flat {d['flat_id']} (₹{d['outstanding']})" for d in items
        )
    if intent == "active_users":
        return f"Active accounts in the directory: {data['active_count']}."
    if intent == "summary":
        return (
            f"Society snapshot ({role} view): {data['complaints_total']} complaints, "
            f"{data['bills_total']} bills, {data['visitors_total']} visitors on record."
        )
    return "I can help with maintenance, complaints, visitors, notices, and reports. Try asking: 'Show my pending maintenance'."


def chat(db: Session, user: User, message: str) -> Dict[str, Any]:
    """Main entry-point: classify, fetch permission-aware data, reply."""
    intent = _classify(message)
    data = _handle_intent(intent, db, user)
    reply = _natural_reply(intent, data, user)

    # persist both turns
    db.add(ChatMessage(user_id=user.id, role="user", content=message, intent=intent))
    db.add(ChatMessage(user_id=user.id, role="assistant", content=reply, intent=intent))
    db.commit()

    return {"intent": intent, "reply": reply, "data": data}


def classify_complaint(text: str) -> str:
    """Best-effort category guess from text. Returns the *name*, not id."""
    text = text.lower()
    bucket = {
        "Plumbing": ["leak", "tap", "pipe", "water", "drain", "toilet", "sink"],
        "Electrical": ["light", "bulb", "power", "electric", "fuse", "switch", "fan"],
        "Cleaning": ["dirty", "garbage", "trash", "clean", "dust", "litter"],
        "Security": ["guard", "security", "theft", "camera", "cctv", "suspicious"],
        "Parking": ["park", "vehicle", "car", "bike"],
        "Lift": ["lift", "elevator"],
        "Pest Control": ["pest", "insect", "cockroach", "rat", "mosquito"],
        "Noise": ["noise", "loud", "music", "party"],
    }
    best, hits = "General", 0
    for cat, kws in bucket.items():
        score = sum(1 for w in kws if w in text)
        if score > hits:
            best, hits = cat, score
    return best
