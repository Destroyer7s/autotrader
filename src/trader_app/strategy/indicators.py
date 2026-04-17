from __future__ import annotations

from math import sqrt
from statistics import mean, stdev


def sma(values: list[float], window: int) -> float:
    """Simple moving average over the last `window` values."""
    if window <= 0 or len(values) < window:
        raise ValueError("window must be > 0 and <= len(values)")
    return mean(values[-window:])


def pct_return(start: float, end: float) -> float:
    """Percent return as a decimal (0.01 = 1%)."""
    if start <= 0:
        return 0.0
    return (end - start) / start


def annualized_volatility(prices: list[float], window: int = 20) -> float:
    """Estimate annualized volatility from simple daily returns.

    The value is approximate and intended for strategy gating, not risk reporting.
    """
    if len(prices) < window + 1:
        return 0.0

    sampled = prices[-(window + 1) :]
    returns: list[float] = []
    for idx in range(1, len(sampled)):
        prev = sampled[idx - 1]
        curr = sampled[idx]
        if prev <= 0:
            continue
        returns.append((curr - prev) / prev)

    if len(returns) < 2:
        return 0.0

    return stdev(returns) * sqrt(252)


def rsi(prices: list[float], window: int = 14) -> float:
    """Classic Wilder-style RSI approximation.

    Returns a value in [0, 100].
    """
    if len(prices) < window + 1:
        return 50.0

    gains: list[float] = []
    losses: list[float] = []

    for idx in range(-window, 0):
        delta = prices[idx] - prices[idx - 1]
        if delta >= 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(-delta)

    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def zscore(values: list[float]) -> float:
    """Z-score of the last value relative to the full sequence."""
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    sigma = stdev(values)
    if sigma == 0:
        return 0.0
    return (values[-1] - mu) / sigma
