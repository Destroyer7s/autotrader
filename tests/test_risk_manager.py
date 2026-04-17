from trader_app.risk.manager import RiskManager, RiskPolicy


def test_calculate_order_qty_respects_max_position_pct() -> None:
    policy = RiskPolicy(
        max_position_pct=0.10,
        max_daily_loss_pct=0.03,
        max_open_positions=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.05,
    )
    manager = RiskManager(policy)

    qty = manager.calculate_order_qty(equity=10000, price=100, available_cash=5000)
    assert qty == 10


def test_bracket_levels() -> None:
    policy = RiskPolicy(
        max_position_pct=0.10,
        max_daily_loss_pct=0.03,
        max_open_positions=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.05,
    )
    manager = RiskManager(policy)

    stop, take = manager.bracket_levels(100)
    assert stop == 98.0
    assert take == 105.0
