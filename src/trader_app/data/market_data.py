from __future__ import annotations

from trader_app.broker.alpaca import AlpacaClient
from trader_app.models import Quote


class MarketDataService:
    def __init__(self, broker: AlpacaClient) -> None:
        self.broker = broker

    def latest_quote(self, symbol: str) -> Quote:
        return self.broker.get_latest_quote(symbol)
