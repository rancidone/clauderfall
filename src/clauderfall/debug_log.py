"""Debug logger for the Clauderfall MCP server.

Enable by setting CLAUDERFALL_DEBUG=1 in the environment.

Call configure(db_path) once at startup to persist logs to the clauderfall.db
SQLite database in a `logs` table. No extra runtime setup required.

Rotation is row-count-based: when the table exceeds MAX_LOG_ROWS, the oldest
rows are deleted to bring it back to ROTATION_KEEP_ROWS. Both are configurable
via CLAUDERFALL_LOG_MAX_ROWS and CLAUDERFALL_LOG_KEEP_ROWS env vars.

Output never goes to stdout, which is reserved for the MCP transport.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path


_ENABLED = os.environ.get("CLAUDERFALL_DEBUG", "").strip() in {"1", "true", "yes"}

# Rotation defaults: keep the most recent 5 000 rows, rotate when 10 000 are exceeded.
_MAX_LOG_ROWS = int(os.environ.get("CLAUDERFALL_LOG_MAX_ROWS", "10000"))
_ROTATION_KEEP_ROWS = int(os.environ.get("CLAUDERFALL_LOG_KEEP_ROWS", "5000"))

_logger = logging.getLogger("clauderfall.mcp")
_logger.setLevel(logging.DEBUG if _ENABLED else logging.CRITICAL)

_stderr_handler = logging.StreamHandler(sys.stderr)
_stderr_handler.setFormatter(logging.Formatter("[clauderfall] %(levelname)s %(message)s"))
_logger.addHandler(_stderr_handler if _ENABLED else logging.NullHandler())


_CREATE_LOGS = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,
    level TEXT NOT NULL,
    logger TEXT NOT NULL,
    message TEXT NOT NULL
);
"""

_ROTATION_INTERVAL = 100  # check row count every N emissions to avoid per-row COUNT queries


class _SQLiteHandler(logging.Handler):
    """Appends log rows to the clauderfall.db `logs` table with row-count rotation."""

    def __init__(self, db_path: Path) -> None:
        super().__init__()
        self._db_path = db_path
        self._emit_count = 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            conn = sqlite3.connect(self._db_path, timeout=2)
            try:
                conn.execute(
                    "INSERT INTO logs (logged_at, level, logger, message) VALUES (?, ?, ?, ?)",
                    (
                        datetime.now(UTC).isoformat(),
                        record.levelname,
                        record.name,
                        msg,
                    ),
                )
                conn.commit()
                self._emit_count += 1
                if self._emit_count % _ROTATION_INTERVAL == 0:
                    _rotate(conn)
            finally:
                conn.close()
        except Exception:  # noqa: BLE001
            # Never let a logging failure propagate — stderr is last resort.
            try:
                print(f"[clauderfall] logging error: {traceback.format_exc()}", file=sys.stderr)
            except Exception:  # noqa: BLE001
                pass


def _rotate(conn: sqlite3.Connection) -> None:
    """Delete oldest rows if the table exceeds MAX_LOG_ROWS, keeping ROTATION_KEEP_ROWS."""
    try:
        (count,) = conn.execute("SELECT COUNT(*) FROM logs").fetchone()
        if count > _MAX_LOG_ROWS:
            excess = count - _ROTATION_KEEP_ROWS
            conn.execute(
                "DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY id ASC LIMIT ?)",
                (excess,),
            )
            conn.commit()
    except Exception:  # noqa: BLE001
        pass


def configure(db_path: Path) -> None:
    """Install the SQLite log handler and create the logs table. Idempotent."""
    if not _ENABLED:
        return
    for handler in _logger.handlers:
        if isinstance(handler, _SQLiteHandler) and handler._db_path == db_path:
            return
    try:
        conn = sqlite3.connect(db_path, timeout=2)
        try:
            conn.execute(_CREATE_LOGS)
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return
    _logger.addHandler(_SQLiteHandler(db_path))


def debug(msg: str, *args: object) -> None:
    _logger.debug(msg, *args)


def info(msg: str, *args: object) -> None:
    _logger.info(msg, *args)


def warning(msg: str, *args: object) -> None:
    _logger.warning(msg, *args)


def error(msg: str, *args: object) -> None:
    _logger.error(msg, *args)


def exception(msg: str, *args: object) -> None:
    """Log an error message with the current exception traceback attached."""
    _logger.exception(msg, *args)
