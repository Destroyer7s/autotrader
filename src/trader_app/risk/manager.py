from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskPolicy:
    max_position_pct: float
    max_daily_loss_pct: float
    max_open_positions: int
    stop_loss_pct: float
    take_profit_pct: float


class RiskManager:
    def __init__(self, policy: RiskPolicy) -> None:
        self.policy = policy

    def allowed_position_dollars(self, equity: float) -> float:
        # Max dollars allowed in a single position under current policy.
        return max(0.0, equity * self.policy.max_position_pct)

    def calculate_order_qty(self, equity: float, price: float, available_cash: float) -> int:
        # Defensive guard against invalid market/account inputs.
        if equity <= 0 or price <= 0 or available_cash <= 0:
            return 0

        # Position size is constrained by BOTH policy and available capital.
        cap_by_policy = self.allowed_position_dollars(equity)
        spendable = min(cap_by_policy, available_cash)

        # Integer floor to avoid accidental fractional share assumptions.
        qty = int(spendable // price)
        return max(0, qty)

    def should_halt_for_daily_loss(self, equity_start_of_day: float, equity_now: float) -> bool:
        # Invalid baseline means risk context is unknown; safest option is halt.
        if equity_start_of_day <= 0:
            return True
        loss = (equity_start_of_day - equity_now) / equity_start_of_day
        return loss >= self.policy.max_daily_loss_pct

    def bracket_levels(self, entry_price: float) -> tuple[float, float]:
        # Precompute bracket levels for downstream order adapters.
        stop = entry_price * (1 - self.policy.stop_loss_pct)
        take = entry_price * (1 + self.policy.take_profit_pct)
        return round(stop, 4), round(take, 4)
