"""Back up and reset only the repository-local SQLite development database."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sys

from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings


def main() -> None:
    url = make_url(settings.DATABASE_URL)
    if url.get_backend_name() != "sqlite" or not url.database or url.database == ":memory:":
        raise RuntimeError("Automatic recovery is available only for the local SQLite development database.")

    backend_root = Path(__file__).resolve().parents[1]
    configured = Path(url.database)
    database = configured.resolve() if configured.is_absolute() else (backend_root / configured).resolve()
    if not database.is_relative_to(backend_root):
        raise RuntimeError(f"Refusing to reset a database outside the backend folder: {database}")

    if not database.exists():
        print(f"[RECOVERY] No SQLite file exists at {database}; retrying a clean migration.")
        return

    backup_dir = backend_root / ".database-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"{database.stem}-before-rebuild-{timestamp}{database.suffix}"
    shutil.copy2(database, backup)

    database.unlink()
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(f"{database}{suffix}")
        if sidecar.exists():
            sidecar.unlink()

    print(f"[RECOVERY] Previous database backed up to: {backup}")
    print("[RECOVERY] Clean SQLite database is ready to be created.")


if __name__ == "__main__":
    main()
