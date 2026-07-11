"""Service layer initialization. Re-export common services."""
from .ai_service import chat, classify_complaint
from .notification_service import send_email, send_telegram
from .ocr_service import ocr_extract
from .report_service import generate_bill_pdf, generate_excel_report
from .billing_service import generate_monthly_bills

__all__ = [
    "chat", "classify_complaint",
    "send_email", "send_telegram",
    "ocr_extract",
    "generate_bill_pdf", "generate_excel_report",
    "generate_monthly_bills",
]
