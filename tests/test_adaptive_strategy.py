from trader_app.strategy.adaptive_ensemble import AdaptiveEnsembleStrategy


def test_adaptive_strategy_holds_with_insufficient_data() -> None:
    strategy = AdaptiveEnsembleStrategy()
    prices = [100.0, 100.5, 101.0]
    assert strategy.signal(prices) == "hold"


def test_adaptive_strategy_returns_valid_signal() -> None:
    strategy = AdaptiveEnsembleStrategy()

    # Moderately trending synthetic path with noise.
    prices = [
        100.0,
        100.2,
        100.4,
        100.7,
        101.0,
        101.3,
        101.1,
        101.5,
        101.8,
        102.1,
        102.4,
        102.2,
        102.6,
        102.9,
        103.1,
        103.4,
        103.0,
        103.3,
        103.7,
        104.1,
        104.4,
        104.7,
        104.5,
        104.9,
        105.2,
    ]

    signal = strategy.signal(prices)
    assert signal in {"buy", "sell", "hold"}
