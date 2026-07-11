"""complaint workflow and per-user billing

Revision ID: 0004_workflows_billing_roles
Revises: 0003_join_requests
"""
from datetime import date, timedelta

from alembic import op
import sqlalchemy as sa

revision = "0004_workflows_billing_roles"
down_revision = "0003_join_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())
    with op.batch_alter_table("bills") as batch:
        batch.add_column(sa.Column("billed_user_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("billing_year", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("billing_month", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_bills_billed_user", "users", ["billed_user_id"], ["id"], ondelete="CASCADE")
        batch.create_unique_constraint("uq_bill_user_period", ["billed_user_id", "billing_year", "billing_month"])
        batch.create_index("ix_bills_billed_user_id", ["billed_user_id"])

    if "bill_line_items" not in existing_tables:
        op.create_table("bill_line_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bill_id", sa.Integer(), sa.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(40), nullable=False), sa.Column("label", sa.String(120), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False))
        op.create_index("ix_bill_line_items_bill_id", "bill_line_items", ["bill_id"])
    if "payment_attempts" not in existing_tables:
        op.create_table("payment_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bill_id", sa.Integer(), sa.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False), sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False, server_default="razorpay"),
        sa.Column("provider_order_id", sa.String(100), nullable=False, unique=True),
        sa.Column("provider_payment_id", sa.String(100), unique=True), sa.Column("failure_reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_payment_attempts_bill_id", "payment_attempts", ["bill_id"])
        op.create_index("ix_payment_attempts_user_id", "payment_attempts", ["user_id"])
        op.create_index("ix_payment_attempts_status", "payment_attempts", ["status"])
        op.create_index("ix_payment_attempts_provider_order_id", "payment_attempts", ["provider_order_id"])
        op.create_index("ix_payment_attempts_provider_payment_id", "payment_attempts", ["provider_payment_id"])
    if "complaint_events" not in existing_tables:
        op.create_table("complaint_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("complaint_id", sa.Integer(), sa.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_status", sa.String(30)), sa.Column("to_status", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_complaint_events_complaint_id", "complaint_events", ["complaint_id"])

    connection = op.get_bind()
    connection.execute(sa.text("UPDATE complaints SET status='submitted' WHERE status='open'"))
    connection.execute(sa.text("UPDATE complaints SET status='in_progress' WHERE status='escalated'"))
    connection.execute(sa.text("UPDATE complaints SET status='resolved' WHERE status='closed'"))
    connection.execute(sa.text("INSERT INTO complaint_events (complaint_id, actor_id, from_status, to_status, reason, created_at) SELECT id, reporter_id, NULL, status, 'Imported existing complaint', created_at FROM complaints"))

    # This repository contains development/demo dues only. Replace all of them with one explicit current-month example.
    connection.execute(sa.text("DELETE FROM payments"))
    connection.execute(sa.text("DELETE FROM bills"))
    row = connection.execute(sa.text("""
        SELECT u.id AS user_id, u.society_id, r.id AS resident_id, r.flat_id
        FROM users u JOIN residents r ON r.user_id=u.id
        JOIN user_roles ur ON ur.user_id=u.id JOIN roles ro ON ro.id=ur.role_id
        WHERE ro.name='resident' ORDER BY u.id LIMIT 1
    """)).mappings().first()
    if row:
        today = date.today(); due = today + timedelta(days=15); total = 2500.0
        result = connection.execute(sa.text("""
            INSERT INTO bills (society_id, flat_id, resident_id, billed_user_id, billing_year, billing_month,
                bill_number, title, description, amount, late_fee, total_amount, paid_amount, status,
                issue_date, due_date, created_at)
            VALUES (:society, :flat, :resident, :user, :year, :month, :number, :title, :description,
                :amount, 0, :amount, 0, 'pending', :issue, :due, CURRENT_TIMESTAMP)
        """), {"society": row["society_id"], "flat": row["flat_id"], "resident": row["resident_id"],
            "user": row["user_id"], "year": today.year, "month": today.month,
            "number": f"DEMO-{today.year}-{today.month:02d}-001", "title": f"Demo Maintenance {today.strftime('%B %Y')}",
            "description": "Demonstration bill with itemized society charges", "amount": total,
            "issue": today, "due": due})
        bill_id = result.lastrowid
        for code, label, amount in [("maintenance", "Normal Maintenance", 1800.0), ("water", "Water", 400.0), ("electricity", "Electricity", 300.0)]:
            connection.execute(sa.text("INSERT INTO bill_line_items (bill_id, code, label, amount) VALUES (:bill, :code, :label, :amount)"),
                               {"bill": bill_id, "code": code, "label": label, "amount": amount})


def downgrade() -> None:
    op.drop_table("complaint_events")
    op.drop_table("payment_attempts")
    op.drop_table("bill_line_items")
    with op.batch_alter_table("bills") as batch:
        batch.drop_constraint("uq_bill_user_period", type_="unique")
        batch.drop_constraint("fk_bills_billed_user", type_="foreignkey")
        batch.drop_column("billing_month"); batch.drop_column("billing_year"); batch.drop_column("billed_user_id")
