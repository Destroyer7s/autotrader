from __future__ import annotations

import logging

from trader_app.broker.alpaca import AlpacaClient
from trader_app.models import OrderRequest, OrderResult
from trader_app.risk.manager import RiskManager
from trader_app.strategy.base import Strategy

LOGGER = logging.getLogger(__name__)


class TradingEngine:
    def __init__(
        self,
        broker: AlpacaClient,
        risk_manager: RiskManager,
        strategy: Strategy,
        require_confirmation: bool,
        enable_live_trading: bool,
    ) -> None:
        self.broker = broker
        self.risk_manager = risk_manager
        self.strategy = strategy
        self.require_confirmation = require_confirmation
        self.enable_live_trading = enable_live_trading

    def evaluate_and_trade(
        self,
        symbol: str,
        capital_hint: float,
        recent_prices: list[float],
        dry_run: bool,
    ) -> OrderResult | None:
        # Pull account first because every downstream decision depends on
        # real account constraints (equity, buying power, and broker status).
        account = self.broker.get_account()

        # NOTE: this scaffold currently uses account.equity as both baseline and
        # current equity, so this check is effectively a structural placeholder.
        # In production, pass in start-of-day equity from a persisted ledger.
        if self.risk_manager.should_halt_for_daily_loss(
            equity_start_of_day=account.equity,
            equity_now=account.equity,
        ):
            LOGGER.warning("Risk halt active. Daily loss threshold reached or invalid baseline.")
            return None

        # Ask the strategy for directional intent using recent market history.
        signal = self.strategy.signal(recent_prices)
        LOGGER.info("Strategy signal for %s: %s", symbol, signal)
        if signal not in {"buy", "sell"}:
            return None

        # Use live quote for sizing and order construction.
        quote = self.broker.get_latest_quote(symbol)
        price = quote.last

        # Honor both operator intent (`capital_hint`) and broker constraints.
        budget = min(capital_hint, account.buying_power)
        qty = self.risk_manager.calculate_order_qty(
            equity=account.equity,
            price=price,
            available_cash=budget,
        )
        if qty <= 0:
            LOGGER.warning("Calculated qty is 0. No trade sent.")
            return None

        # Build protective bracket targets before sending the order.
        stop, take = self.risk_manager.bracket_levels(price)
        request = OrderRequest(
            symbol=symbol,
            qty=qty,
            side=signal,
            stop_loss=stop,
            take_profit=take,
        )

        # Dry-run mode is mandatory for safe local iteration.
        if dry_run or not self.enable_live_trading:
            LOGGER.info("Dry run only. Proposed order: %s", request)
            return None

        # Human-in-the-loop confirmation is highly recommended for live trading.
        if self.require_confirmation and not self._confirm_request(request, price):
            LOGGER.info("Order canceled by operator.")
            return None

        return self.broker.submit_order(request)

    def _confirm_request(self, request: OrderRequest, price: float) -> bool:
        total = request.qty * price
        prompt = (
            f"Confirm {request.side.upper()} {request.qty} {request.symbol} at ~{price:.2f} "
            f"(notional {total:.2f})? Type YES to continue: "
        )
        user_input = input(prompt).strip()
        return user_input == "YES"
