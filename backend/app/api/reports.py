"""Reports router (Excel exports)."""
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.bill import Bill, BillStatus
from app.models.complaint import Complaint, ComplaintStatus
from app.models.user import User
from app.models.visitor import Visitor
from app.services.report_service import save_excel_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/complaints.xlsx")
def complaints_report(db: Session = Depends(get_db),
                      current=Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"])
    rows = db.execute(select(Complaint).order_by(desc(Complaint.created_at))
                      .limit(500)).scalars().all()
    data = [
        {
            "id": c.id,
            "title": c.title,
            "status": c.status.value,
            "priority": c.priority.value,
            "society_id": c.society_id,
            "flat_id": c.flat_id,
            "reporter_id": c.reporter_id,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "resolved_at": c.resolved_at.isoformat() if c.resolved_at else "",
        }
        for c in rows
    ]
    name = f"complaints-{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    path = save_excel_report(data, list(data[0].keys()) if data else
                             ["id", "title", "status", "priority", "created_at"], name)
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=name)


@router.get("/bills.xlsx")
def bills_report(db: Session = Depends(get_db),
                 current=Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"])
    rows = db.execute(select(Bill).order_by(desc(Bill.created_at)).limit(500)).scalars().all()
    data = [
        {
            "bill_number": b.bill_number,
            "flat_id": b.flat_id,
            "amount": b.amount,
            "late_fee": b.late_fee,
            "total": b.total_amount,
            "paid": b.paid_amount,
            "outstanding": b.outstanding,
            "status": b.status.value,
            "issue_date": b.issue_date.isoformat(),
            "due_date": b.due_date.isoformat(),
        }
        for b in rows
    ]
    name = f"bills-{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    path = save_excel_report(data, list(data[0].keys()) if data else
                             ["bill_number", "flat_id", "amount", "status"], name)
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=name)


@router.get("/visitors.xlsx")
def visitors_report(db: Session = Depends(get_db),
                    current=Depends(get_current_user)):
    require_any_role(current, ["admin", "committee", "security"])
    since = datetime.utcnow() - timedelta(days=30)
    rows = db.execute(select(Visitor).where(Visitor.created_at >= since)
                      .order_by(desc(Visitor.created_at)).limit(500)).scalars().all()
    data = [
        {
            "id": v.id,
            "name": v.name,
            "phone": v.phone or "",
            "purpose": v.purpose or "",
            "vehicle": v.vehicle_number or "",
            "status": v.status.value,
            "created_at": v.created_at.isoformat(),
        }
        for v in rows
    ]
    name = f"visitors-{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    path = save_excel_report(data, list(data[0].keys()) if data else
                             ["id", "name", "status", "created_at"], name)
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=name)
