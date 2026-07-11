"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "societies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("address", sa.Text, nullable=False),
        sa.Column("city", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("pincode", sa.String(20)),
        sa.Column("registration_no", sa.String(100), unique=True),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("contact_phone", sa.String(20)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("floors", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index("ix_blocks_society_id", "blocks", ["society_id"])

    op.create_table(
        "flats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("block_id", sa.Integer, sa.ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("floor", sa.Integer, nullable=False, server_default="0"),
        sa.Column("area_sqft", sa.Integer),
        sa.Column("bedrooms", sa.Integer, nullable=False, server_default="1"),
        sa.Column("bathrooms", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index("ix_flats_society_id", "flats", ["society_id"])
    op.create_index("ix_flats_block_id", "flats", ["block_id"])
    op.create_index("ix_flats_number", "flats", ["number"])

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.Integer, sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), unique=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime),
    )
    op.create_index("ix_users_society_id", "users", ["society_id"])
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "residents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("flat_id", sa.Integer, sa.ForeignKey("flats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occupation", sa.String(100)),
        sa.Column("emergency_contact_name", sa.String(120)),
        sa.Column("emergency_contact_phone", sa.String(20)),
        sa.Column("date_of_birth", sa.Date),
        sa.Column("ownership", sa.String(20), nullable=False, server_default="owner"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_residents_user_id", "residents", ["user_id"])
    op.create_index("ix_residents_flat_id", "residents", ["flat_id"])

    op.create_table(
        "complaint_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text),
        sa.Column("color", sa.String(7), server_default="#1976d2"),
    )

    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("flat_id", sa.Integer, sa.ForeignKey("flats.id", ondelete="SET NULL")),
        sa.Column("reporter_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignee_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("complaint_categories.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("photo_url", sa.String(500)),
        sa.Column("ai_suggested_category", sa.String(100)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime),
    )
    op.create_index("ix_complaints_society_id", "complaints", ["society_id"])
    op.create_index("ix_complaints_reporter_id", "complaints", ["reporter_id"])
    op.create_index("ix_complaints_status", "complaints", ["status"])

    op.create_table(
        "complaint_comments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("complaint_id", sa.Integer, sa.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("comment", sa.Text, nullable=False),
        sa.Column("is_internal", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_comments_complaint_id", "complaint_comments", ["complaint_id"])

    op.create_table(
        "visitors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("flat_id", sa.Integer, sa.ForeignKey("flats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("host_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("purpose", sa.String(200)),
        sa.Column("id_proof_type", sa.String(50)),
        sa.Column("id_proof_number", sa.String(100)),
        sa.Column("photo_url", sa.String(500)),
        sa.Column("vehicle_number", sa.String(50)),
        sa.Column("qr_code", sa.String(255), unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expected_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_visitors_society_id", "visitors", ["society_id"])
    op.create_index("ix_visitors_host_id", "visitors", ["host_id"])
    op.create_index("ix_visitors_status", "visitors", ["status"])

    op.create_table(
        "visitor_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("visitor_id", sa.Integer, sa.ForeignKey("visitors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_visitor_logs_visitor_id", "visitor_logs", ["visitor_id"])

    op.create_table(
        "bills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("flat_id", sa.Integer, sa.ForeignKey("flats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resident_id", sa.Integer, sa.ForeignKey("residents.id", ondelete="SET NULL")),
        sa.Column("bill_number", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("late_fee", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Float, nullable=False),
        sa.Column("paid_amount", sa.Float, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("issue_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("paid_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_bills_society_id", "bills", ["society_id"])
    op.create_index("ix_bills_flat_id", "bills", ["flat_id"])
    op.create_index("ix_bills_status", "bills", ["status"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("bill_id", sa.Integer, sa.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("method", sa.String(20), nullable=False, server_default="upi"),
        sa.Column("transaction_ref", sa.String(200)),
        sa.Column("received_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("paid_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("notes", sa.Text),
    )
    op.create_index("ix_payments_bill_id", "payments", ["bill_id"])

    op.create_table(
        "notices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("society_id", sa.Integer, sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("is_pinned", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("audience", sa.String(50), nullable=False, server_default="all"),
        sa.Column("published_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", sa.Integer),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("user_agent", sa.String(255)),
        sa.Column("details", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_action", "audit_logs", ["action"])
    op.create_index("ix_audit_entity", "audit_logs", ["entity_type", "entity_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("intent", sa.String(80)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_chat_user_id", "chat_messages", ["user_id"])


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("audit_logs")
    op.drop_table("notices")
    op.drop_table("payments")
    op.drop_table("bills")
    op.drop_table("visitor_logs")
    op.drop_table("visitors")
    op.drop_table("complaint_comments")
    op.drop_table("complaints")
    op.drop_table("complaint_categories")
    op.drop_table("residents")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_table("flats")
    op.drop_table("blocks")
    op.drop_table("societies")
