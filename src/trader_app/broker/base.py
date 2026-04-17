from __future__ import annotations

from abc import ABC, abstractmethod

from trader_app.models import Account, OrderRequest, OrderResult, Quote


class BrokerClient(ABC):
    @abstractmethod
    def get_account(self) -> Account:
        raise NotImplementedError

    @abstractmethod
    def get_latest_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    @abstractmethod
    def submit_order(self, request: OrderRequest) -> OrderResult:
        raise NotImplementedError
