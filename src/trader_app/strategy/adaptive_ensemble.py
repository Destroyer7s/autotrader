from __future__ import annotations

from trader_app.strategy.base import Strategy
from trader_app.strategy.indicators import annualized_volatility, pct_return, rsi, sma, zscore


class AdaptiveEnsembleStrategy(Strategy):
    """A multi-factor strategy that blends trend, momentum, and mean reversion signals.

    Design goals:
    - Avoid one-dimensional decisions.
    - Trade only when multiple signals agree.
    - Stay defensive in high-volatility regimes.
    """

    def __init__(
        self,
        short_window: int = 5,
        long_window: int = 20,
        momentum_lookback: int = 5,
        momentum_threshold: float = 0.004,
        rsi_window: int = 14,
        mean_reversion_band: float = 1.0,
        min_score_low_vol: int = 2,
        min_score_high_vol: int = 3,
        high_vol_threshold: float = 0.55,
    ) -> None:
        # These parameters are intentionally exposed so you can tune behavior per symbol.
        self.short_window = short_window
        self.long_window = long_window
        self.momentum_lookback = momentum_lookback
        self.momentum_threshold = momentum_threshold
        self.rsi_window = rsi_window
        self.mean_reversion_band = mean_reversion_band
        self.min_score_low_vol = min_score_low_vol
        self.min_score_high_vol = min_score_high_vol
        self.high_vol_threshold = high_vol_threshold

    def signal(self, prices: list[float]) -> str:
        # We need enough bars for every indicator before making a decision.
        minimum_bars = max(self.long_window + 1, self.rsi_window + 1, self.momentum_lookback + 1)
        if len(prices) < minimum_bars:
            return "hold"

        # Factor 1: Trend direction via moving-average crossover.
        short_ma = sma(prices, self.short_window)
        long_ma = sma(prices, self.long_window)
        trend_vote = 1 if short_ma > long_ma else -1

        # Factor 2: Momentum over a short horizon.
        momentum = pct_return(prices[-self.momentum_lookback - 1], prices[-1])
        if momentum > self.momentum_threshold:
            momentum_vote = 1
        elif momentum < -self.momentum_threshold:
            momentum_vote = -1
        else:
            momentum_vote = 0

        # Factor 3: RSI extremes as a contrarian stabilizer.
        current_rsi = rsi(prices, self.rsi_window)
        if current_rsi < 35:
            rsi_vote = 1
        elif current_rsi > 70:
            rsi_vote = -1
        else:
            rsi_vote = 0

        # Factor 4: Mean-reversion pressure using z-score on recent prices.
        recent = prices[-self.long_window:]
        distance = zscore(recent)
        if distance <= -self.mean_reversion_band:
            reversion_vote = 1
        elif distance >= self.mean_reversion_band:
            reversion_vote = -1
        else:
            reversion_vote = 0

        # Ensemble score: positive supports buy, negative supports sell.
        score = trend_vote + momentum_vote + rsi_vote + reversion_vote

        # Regime filter: in high volatility, require stronger agreement before trading.
        vol = annualized_volatility(prices, window=min(20, len(prices) - 1))
        required_score = self.min_score_high_vol if vol >= self.high_vol_threshold else self.min_score_low_vol

        if score >= required_score:
            return "buy"
        if score <= -required_score:
            return "sell"
        return "hold"
