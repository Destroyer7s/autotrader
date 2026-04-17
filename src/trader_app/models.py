from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    timestamp: str


@dataclass
class Account:
    equity: float
    cash: float
    buying_power: float
    daytrade_count: int
    status: str


@dataclass
class OrderRequest:
    symbol: str
    qty: int
    side: str
    order_type: str = "market"
    time_in_force: str = "day"
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class OrderResult:
    id: str
    symbol: str
    qty: int
    side: str
    status: str
