from pathlib import Path

from trader_app.analytics.performance import PerformanceAnalytics
from trader_app.utils.sqlite_journal import SqliteTradeJournal


def test_analytics_summary_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "journal.db"
    journal = SqliteTradeJournal(str(db_path))

    journal.append_event("strategy_signal", {"symbol": "AAPL", "signal": "buy"})
    journal.append_event("proposed_order", {"symbol": "AAPL"})
    journal.append_event("order_submitted", {"symbol": "AAPL"})

    analytics = PerformanceAnalytics(journal)
    report = analytics.summary(limit=50)

    assert report["events_analyzed"] == 3
    assert report["orders_submitted"] == 1
    assert report["orders_proposed_dryrun"] == 1
    assert report["event_counts"]["strategy_signal"] == 1
