"""Portfolio tracking utilities used by the risk manager."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Portfolio:
    initial_capital: float
    cash: float
    positions: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def with_capital(cls, capital: float) -> "Portfolio":
        return cls(initial_capital=capital, cash=capital)

    def allocate(self, opportunity_id: str, amount: float) -> bool:
        if amount > self.cash:
            logger.warning(
                "Insufficient cash for trade %.2f required %.2f available", amount, self.cash
            )
            return False
        self.cash -= amount
        self.positions[opportunity_id] = self.positions.get(opportunity_id, 0.0) + amount
        logger.debug(
            "Allocated %.2f to %s remaining cash %.2f",
            amount,
            opportunity_id,
            self.cash,
        )
        return True

    def release(self, opportunity_id: str, amount: float, pnl: float) -> None:
        exposure = self.positions.pop(opportunity_id, 0.0)
        if exposure:
            amount = min(amount, exposure)
        self.cash += amount + pnl
        logger.debug(
            "Released %.2f from %s pnl %.2f new cash %.2f",
            amount,
            opportunity_id,
            pnl,
            self.cash,
        )
