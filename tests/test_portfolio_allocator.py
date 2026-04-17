from trader_app.execution.portfolio import PortfolioAllocator


def test_equal_allocation_for_symbols() -> None:
    allocator = PortfolioAllocator()
    allocations = allocator.allocate(["AAPL", "MSFT", "NVDA"], 3000)

    assert len(allocations) == 3
    assert all(item.dollars == 1000 for item in allocations)


def test_weighted_allocation() -> None:
    allocator = PortfolioAllocator()
    allocations = allocator.allocate(
        ["AAPL", "MSFT"],
        3000,
        weights={"AAPL": 2, "MSFT": 1},
    )

    by_symbol = {item.symbol: item.dollars for item in allocations}
    assert by_symbol["AAPL"] == 2000
    assert by_symbol["MSFT"] == 1000
