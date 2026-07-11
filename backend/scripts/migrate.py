"""Upgrade both legacy create_all databases and Alembic-managed databases."""
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.db.base import engine


def run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "alembic", *args], check=True)


tables = set(inspect(engine).get_table_names())
has_version = False
if "alembic_version" in tables:
    with engine.connect() as connection:
        has_version = connection.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).first() is not None
if not has_version and "users" in tables:
    # Existing clones were bootstrapped with Base.metadata.create_all through revision 0003.
    run("stamp", "0003_join_requests")
run("upgrade", "head")
