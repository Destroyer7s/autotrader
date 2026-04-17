from __future__ import annotations

import argparse
import logging
import random

from trader_app.broker.alpaca import AlpacaClient
from trader_app.config import load_settings
from trader_app.execution.engine import TradingEngine
from trader_app.risk.manager import RiskManager, RiskPolicy
from trader_app.strategy.adaptive_ensemble import AdaptiveEnsembleStrategy
from trader_app.strategy.mean_reversion import MeanReversionStrategy
from trader_app.strategy.momentum import MomentumStrategy
from trader_app.utils.logging_setup import configure_logging


LOGGER = logging.getLogger(__name__)


def _build_strategy(name: str):
    # Strategy factory kept simple on purpose so new strategies can be registered
    # in one place without touching the trading engine.
    if name == "adaptive_ensemble":
        return AdaptiveEnsembleStrategy()
    if name == "mean_reversion":
        return MeanReversionStrategy()
    return MomentumStrategy()


def _simulate_recent_prices(seed_price: float = 100.0, points: int = 30) -> list[float]:
    # This helper generates synthetic prices for local dry-run checks.
    # It intentionally alternates between mild drift and noise to mimic
    # imperfect market behavior without relying on external data feeds.
    prices = [seed_price]
    for _ in range(points - 1):
        drift = random.uniform(-0.8, 0.8)
        prices.append(max(1.0, prices[-1] + drift))
    return prices


def build_engine() -> TradingEngine:
    # Configuration loading is centralized to keep runtime behavior predictable.
    settings = load_settings()

    broker = AlpacaClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        base_url=settings.alpaca_base_url,
    )

    policy = RiskPolicy(
        # These controls are the hard guardrails for every order decision.
        max_position_pct=settings.max_position_pct,
        max_daily_loss_pct=settings.max_daily_loss_pct,
        max_open_positions=settings.max_open_positions,
        stop_loss_pct=settings.stop_loss_pct,
        take_profit_pct=settings.take_profit_pct,
    )

    return TradingEngine(
        broker=broker,
        risk_manager=RiskManager(policy),
        strategy=_build_strategy(settings.default_strategy),
        require_confirmation=settings.require_confirmation,
        enable_live_trading=settings.enable_live_trading,
    )


def cmd_health() -> int:
    settings = load_settings()
    broker = AlpacaClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        base_url=settings.alpaca_base_url,
    )
    account = broker.get_account()
    print("Account status:", account.status)
    print("Equity:", account.equity)
    print("Cash:", account.cash)
    print("Buying power:", account.buying_power)
    return 0


def cmd_quote(symbol: str) -> int:
    settings = load_settings()
    broker = AlpacaClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        base_url=settings.alpaca_base_url,
    )
    quote = broker.get_latest_quote(symbol)
    print(f"{quote.symbol} bid={quote.bid:.2f} ask={quote.ask:.2f} mid={quote.last:.2f} at {quote.timestamp}")
    return 0


def cmd_run(symbol: str, capital: float, dry_run: bool, confirm: bool, strategy: str | None) -> int:
    settings = load_settings()
    engine = build_engine()

    if strategy:
        # CLI override allows quick strategy A/B testing without changing env vars.
        engine.strategy = _build_strategy(strategy)

    if confirm:
        engine.require_confirmation = True

    prices = _simulate_recent_prices()
    result = engine.evaluate_and_trade(
        symbol=symbol,
        capital_hint=capital,
        recent_prices=prices,
        dry_run=dry_run,
    )

    if result is None:
        mode = "dry run" if (dry_run or not settings.enable_live_trading) else "live"
        print(f"No order sent ({mode}).")
        return 0

    print("Order submitted:", result)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AutoTrader CLI")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Check broker account connectivity")

    quote = sub.add_parser("quote", help="Fetch latest quote")
    quote.add_argument("--symbol", required=True)

    run = sub.add_parser("run", help="Evaluate strategy and optionally place a trade")
    run.add_argument("--symbol", required=True)
    run.add_argument("--capital", required=True, type=float)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--confirm", action="store_true")
    run.add_argument("--strategy", choices=["momentum", "mean_reversion", "adaptive_ensemble"])

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    configure_logging(getattr(logging, args.log_level))

    if args.command == "health":
        return cmd_health()
    if args.command == "quote":
        return cmd_quote(args.symbol)
    if args.command == "run":
        return cmd_run(
            symbol=args.symbol,
            capital=args.capital,
            dry_run=args.dry_run,
            confirm=args.confirm,
            strategy=args.strategy,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
