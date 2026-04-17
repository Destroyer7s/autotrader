from __future__ import annotations

import logging
from typing import Any

import requests

from trader_app.models import Account, OrderRequest, OrderResult, Quote

LOGGER = logging.getLogger(__name__)


class AlpacaClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": secret_key,
                "Content-Type": "application/json",
            }
        )

    def _get(self, path: str) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}{path}", timeout=20)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(f"{self.base_url}{path}", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    def get_account(self) -> Account:
        data = self._get("/v2/account")
        return Account(
            equity=float(data["equity"]),
            cash=float(data["cash"]),
            buying_power=float(data["buying_power"]),
            daytrade_count=int(data.get("daytrade_count", 0)),
            status=data.get("status", "unknown"),
        )

    def get_latest_quote(self, symbol: str) -> Quote:
        data = self._get(f"/v2/stocks/{symbol}/quotes/latest")
        quote = data["quote"]
        return Quote(
            symbol=symbol,
            bid=float(quote["bp"]),
            ask=float(quote["ap"]),
            last=float((quote["bp"] + quote["ap"]) / 2),
            timestamp=quote["t"],
        )

    def submit_order(self, request: OrderRequest) -> OrderResult:
        payload: dict[str, Any] = {
            "symbol": request.symbol,
            "qty": request.qty,
            "side": request.side,
            "type": request.order_type,
            "time_in_force": request.time_in_force,
        }

        if request.stop_loss is not None:
            payload["stop_loss"] = {"stop_price": str(request.stop_loss)}
        if request.take_profit is not None:
            payload["take_profit"] = {"limit_price": str(request.take_profit)}

        LOGGER.info("Submitting order: %s", payload)
        data = self._post("/v2/orders", payload)
        return OrderResult(
            id=data["id"],
            symbol=data["symbol"],
            qty=int(float(data["qty"])),
            side=data["side"],
            status=data.get("status", "accepted"),
        )
