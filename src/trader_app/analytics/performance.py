from __future__ import annotations

from collections import Counter
from typing import Any

from trader_app.utils.sqlite_journal import SqliteTradeJournal


class PerformanceAnalytics:
    """Build lightweight operational metrics from persisted journal events."""

    def __init__(self, journal: SqliteTradeJournal) -> None:
        self.journal = journal

    def summary(self, limit: int = 1000) -> dict[str, Any]:
        events = self.journal.recent_events(limit=limit)
        counts = Counter(e["event_type"] for e in events)

        submitted = counts.get("order_submitted", 0)
        canceled = counts.get("order_canceled", 0)
        proposed = counts.get("proposed_order", 0)

        return {
            "events_analyzed": len(events),
            "orders_submitted": submitted,
            "orders_canceled": canceled,
            "orders_proposed_dryrun": proposed,
            "submission_rate": 0.0 if len(events) == 0 else submitted / len(events),
            "event_counts": dict(counts),
        }
