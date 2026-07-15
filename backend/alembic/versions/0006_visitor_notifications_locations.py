"""visitor notifications and canonical A-D society layout

Revision ID: 0006_visitor_notifications
Revises: 0005_maintenance_location
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_visitor_notifications"
down_revision = "0005_maintenance_location"
branch_labels = None
depends_on = None

WINGS = ("A", "B", "C", "D")
VALID_FLATS = tuple(f"{floor}0{unit}" for floor in range(1, 5) for unit in range(1, 5))


def upgrade() -> None:
    op.create_table(
        "user_notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("society_id", sa.Integer(), sa.ForeignKey("societies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(60), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("read_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_user_notifications_society_id", "user_notifications", ["society_id"])
    op.create_index("ix_user_notifications_user_id", "user_notifications", ["user_id"])
    op.create_index("ix_user_notifications_kind", "user_notifications", ["kind"])
    op.create_index("ix_user_notifications_created_at", "user_notifications", ["created_at"])

    bind = op.get_bind()
    societies = bind.execute(sa.text("SELECT id FROM societies")).all()
    valid_set = set(VALID_FLATS)
    for (society_id,) in societies:
        block_ids: dict[str, int] = {}
        for wing in WINGS:
            row = bind.execute(sa.text(
                "SELECT id FROM blocks WHERE society_id=:society_id AND upper(name)=:wing ORDER BY id LIMIT 1"
            ), {"society_id": society_id, "wing": wing}).first()
            if row:
                block_id = row[0]
                bind.execute(sa.text("UPDATE blocks SET name=:wing, floors=4 WHERE id=:id"), {"wing": wing, "id": block_id})
            else:
                bind.execute(sa.text(
                    "INSERT INTO blocks (society_id, name, floors) VALUES (:society_id, :wing, 4)"
                ), {"society_id": society_id, "wing": wing})
                block_id = bind.execute(sa.text(
                    "SELECT id FROM blocks WHERE society_id=:society_id AND name=:wing ORDER BY id DESC LIMIT 1"
                ), {"society_id": society_id, "wing": wing}).scalar_one()
            block_ids[wing] = block_id

            for number in VALID_FLATS:
                exists = bind.execute(sa.text(
                    "SELECT id FROM flats WHERE block_id=:block_id AND number=:number LIMIT 1"
                ), {"block_id": block_id, "number": number}).first()
                if not exists:
                    bind.execute(sa.text(
                        "INSERT INTO flats (society_id, block_id, number, floor, area_sqft, bedrooms, bathrooms) "
                        "VALUES (:society_id, :block_id, :number, :floor, 1000, 2, 2)"
                    ), {"society_id": society_id, "block_id": block_id, "number": number, "floor": int(number[0])})

        legacy = bind.execute(sa.text(
            "SELECT f.id, f.number, f.floor, upper(b.name) "
            "FROM flats f JOIN blocks b ON b.id=f.block_id WHERE f.society_id=:society_id"
        ), {"society_id": society_id}).all()
        for old_id, number, floor, wing in legacy:
            if wing in WINGS and str(number) in valid_set:
                continue
            target_wing = wing if wing in WINGS else "A"
            safe_floor = int(floor or 1)
            if safe_floor not in range(1, 5):
                safe_floor = 1
            target_number = f"{safe_floor}01"
            target_id = bind.execute(sa.text(
                "SELECT id FROM flats WHERE block_id=:block_id AND number=:number LIMIT 1"
            ), {"block_id": block_ids[target_wing], "number": target_number}).scalar_one()
            for table in ("residents", "complaints", "visitors", "bills"):
                bind.execute(sa.text(f"UPDATE {table} SET flat_id=:target WHERE flat_id=:old"), {"target": target_id, "old": old_id})
            bind.execute(sa.text("DELETE FROM flats WHERE id=:id"), {"id": old_id})

        bind.execute(sa.text(
            "DELETE FROM blocks WHERE society_id=:society_id AND upper(name) NOT IN ('A','B','C','D')"
        ), {"society_id": society_id})

    op.create_index("uq_blocks_society_wing", "blocks", ["society_id", "name"], unique=True)
    op.create_index("uq_flats_block_number", "flats", ["block_id", "number"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_flats_block_number", table_name="flats")
    op.drop_index("uq_blocks_society_wing", table_name="blocks")
    op.drop_table("user_notifications")
