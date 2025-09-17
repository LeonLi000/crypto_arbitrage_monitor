"""Simulated DEX trade execution."""
from __future__ import annotations

from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DexTrader:
    name: str
    fee: float = 0.003

    def buy(self, pair: str, amount: float, price: float) -> float:
        cost = amount * price * (1 + self.fee)
        logger.debug(
            "DEX %s buy %s amount %.4f price %.4f cost %.4f",
            self.name,
            pair,
            amount,
            price,
            cost,
        )
        return cost

    def sell(self, pair: str, amount: float, price: float) -> float:
        revenue = amount * price * (1 - self.fee)
        logger.debug(
            "DEX %s sell %s amount %.4f price %.4f revenue %.4f",
            self.name,
            pair,
            amount,
            price,
            revenue,
        )
        return revenue
