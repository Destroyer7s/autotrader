from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SqliteTradeJournal:
    """SQLite-backed event journal for durable trade and decision logs."""

    def __init__(self, db_path: str = "logs/trade_journal.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO journal_events (ts, event_type, payload_json) VALUES (?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    event_type,
                    json.dumps(payload, sort_keys=True),
                ),
            )
            conn.commit()

    def recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, ts, event_type, payload_json
                FROM journal_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        events: list[dict[str, Any]] = []
        for row in rows:
            payload = json.loads(row[3]) if row[3] else {}
            events.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "event_type": row[2],
                    "payload": payload,
                }
            )
        return events
