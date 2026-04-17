from __future__ import annotations

from statistics import mean

from trader_app.strategy.base import Strategy


class MeanReversionStrategy(Strategy):
    def __init__(self, window: int = 10, band: float = 0.015) -> None:
        self.window = window
        self.band = band

    def signal(self, prices: list[float]) -> str:
        if len(prices) < self.window:
            return "hold"

        window_prices = prices[-self.window :]
        avg = mean(window_prices)
        current = window_prices[-1]

        if avg <= 0:
            return "hold"

        dev = (current - avg) / avg
        if dev <= -self.band:
            return "buy"
        if dev >= self.band:
            return "sell"
        return "hold"
