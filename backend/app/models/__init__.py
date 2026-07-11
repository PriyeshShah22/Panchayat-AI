"""Re-export every model so Base.metadata sees all tables.

Both `from app.models.user import User` and `from app.models import user`
work — Alembic's env.py and db.base's create_all() use both styles.
"""
# Submodules (for Alembic env.py auto-discovery)
from . import user, society, resident, complaint, visitor, bill, notice, audit, chat, ai_action, join_request  # noqa: F401

# Classes (for explicit imports elsewhere)
from .user import User, Role, Permission, UserRole  # noqa: F401
from .society import Society, Block, Flat  # noqa: F401
from .resident import Resident  # noqa: F401
from .complaint import Complaint, ComplaintCategory, ComplaintComment, ComplaintEvent  # noqa: F401
from .visitor import Visitor, VisitorLog  # noqa: F401
from .bill import Bill, BillLineItem, Payment, PaymentAttempt  # noqa: F401
from .notice import Notice  # noqa: F401
from .audit import AuditLog  # noqa: F401
from .chat import ChatMessage  # noqa: F401
from .ai_action import AIAction  # noqa: F401
from .join_request import JoinRequest  # noqa: F401
