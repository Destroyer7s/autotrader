from __future__ import annotations

from trader_app.strategy.base import Strategy


class MomentumStrategy(Strategy):
    def __init__(self, lookback: int = 5, threshold: float = 0.002) -> None:
        self.lookback = lookback
        self.threshold = threshold

    def signal(self, prices: list[float]) -> str:
        if len(prices) <= self.lookback:
            return "hold"

        start = prices[-self.lookback - 1]
        end = prices[-1]
        if start <= 0:
            return "hold"

        change = (end - start) / start
        if change >= self.threshold:
            return "buy"
        if change <= -self.threshold:
            return "sell"
        return "hold"
