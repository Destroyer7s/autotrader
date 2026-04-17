from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Allocation:
    symbol: str
    dollars: float


class PortfolioAllocator:
    """Simple capital allocator with optional per-symbol weights.

    If no weights are provided, capital is split equally.
    """

    def allocate(
        self,
        symbols: list[str],
        total_capital: float,
        weights: dict[str, float] | None = None,
    ) -> list[Allocation]:
        clean_symbols = [s.strip().upper() for s in symbols if s.strip()]
        if not clean_symbols or total_capital <= 0:
            return []

        unique_symbols = list(dict.fromkeys(clean_symbols))

        if not weights:
            per_symbol = total_capital / len(unique_symbols)
            return [Allocation(symbol=symbol, dollars=per_symbol) for symbol in unique_symbols]

        normalized: dict[str, float] = {}
        total_weight = 0.0
        for symbol in unique_symbols:
            w = max(0.0, float(weights.get(symbol, 0.0)))
            normalized[symbol] = w
            total_weight += w

        if total_weight <= 0:
            per_symbol = total_capital / len(unique_symbols)
            return [Allocation(symbol=symbol, dollars=per_symbol) for symbol in unique_symbols]

        return [
            Allocation(symbol=symbol, dollars=total_capital * (normalized[symbol] / total_weight))
            for symbol in unique_symbols
        ]
