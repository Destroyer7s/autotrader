from trader_app.strategy.mean_reversion import MeanReversionStrategy
from trader_app.strategy.momentum import MomentumStrategy


def test_momentum_buy_signal() -> None:
    strategy = MomentumStrategy(lookback=3, threshold=0.01)
    prices = [100.0, 101.0, 102.0, 104.0]
    assert strategy.signal(prices) == "buy"


def test_mean_reversion_sell_signal() -> None:
    strategy = MeanReversionStrategy(window=4, band=0.01)
    prices = [100.0, 100.0, 100.0, 103.0]
    assert strategy.signal(prices) == "sell"
