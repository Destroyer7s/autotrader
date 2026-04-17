from __future__ import annotations

from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def signal(self, prices: list[float]) -> str:
        """Return one of: buy, sell, hold."""
        raise NotImplementedError
