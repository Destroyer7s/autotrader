from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    # Optional dependency fallback keeps runtime resilient.
    def load_dotenv() -> None:
        return None


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    return float(raw)


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw)


@dataclass(frozen=True)
class Settings:
    trader_env: str
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_base_url: str
    default_strategy: str
    require_confirmation: bool
    enable_live_trading: bool
    max_position_pct: float
    max_daily_loss_pct: float
    max_open_positions: int
    stop_loss_pct: float
    take_profit_pct: float
    journal_db_path: str
    discord_webhook_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    alert_to_email: str
    alert_from_email: str



def load_settings() -> Settings:
    # Load environment variables from .env for local development convenience.
    load_dotenv()
    return Settings(
        trader_env=os.getenv("TRADER_ENV", "dev"),
        alpaca_api_key=os.getenv("ALPACA_API_KEY", ""),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
        alpaca_base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        default_strategy=os.getenv("DEFAULT_STRATEGY", "momentum"),
        require_confirmation=_get_bool("REQUIRE_CONFIRMATION", True),
        enable_live_trading=_get_bool("ENABLE_LIVE_TRADING", False),
        max_position_pct=_get_float("MAX_POSITION_PCT", 0.10),
        max_daily_loss_pct=_get_float("MAX_DAILY_LOSS_PCT", 0.03),
        max_open_positions=_get_int("MAX_OPEN_POSITIONS", 5),
        stop_loss_pct=_get_float("STOP_LOSS_PCT", 0.02),
        take_profit_pct=_get_float("TAKE_PROFIT_PCT", 0.05),
        journal_db_path=os.getenv("JOURNAL_DB_PATH", "logs/trade_journal.db"),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=_get_int("SMTP_PORT", 587),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        alert_to_email=os.getenv("ALERT_TO_EMAIL", ""),
        alert_from_email=os.getenv("ALERT_FROM_EMAIL", ""),
    )
