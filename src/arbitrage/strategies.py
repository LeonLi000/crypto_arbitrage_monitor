"""Strategy abstractions controlling how opportunities become trades."""
from __future__ import annotations

from dataclasses import dataclass

from ..utils.logger import get_logger
from ..utils.models import ArbitrageOpportunity

logger = get_logger(__name__)


class Strategy:
    """Base strategy with simple sizing rules."""

    def plan_trade(self, opportunity: ArbitrageOpportunity, capital: float) -> float:
        raise NotImplementedError


@dataclass
class FixedFractionStrategy(Strategy):
    fraction: float = 0.1
    max_trade_size: float = 2_000.0

    def plan_trade(self, opportunity: ArbitrageOpportunity, capital: float) -> float:
        amount = min(capital * self.fraction, self.max_trade_size)
        logger.debug(
            "Strategy sized trade for %s amount %.4f", opportunity.identifier, amount
        )
        return round(max(amount, 0.0), 4)


@dataclass
class ConfidenceWeightedStrategy(Strategy):
    max_trade_size: float = 5_000.0

    def plan_trade(self, opportunity: ArbitrageOpportunity, capital: float) -> float:
        amount = capital * opportunity.confidence
        amount = min(amount, self.max_trade_size)
        logger.debug(
            "Confidence strategy sized trade for %s amount %.4f",
            opportunity.identifier,
            amount,
        )
        return round(max(amount, 0.0), 4)
