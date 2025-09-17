"""Profit estimation utilities for potential arbitrage trades."""
from __future__ import annotations

from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProfitBreakdown:
    gross_profit: float
    net_profit: float
    fees: float
    slippage_cost: float


class OpportunityCalculator:
    """Perform simple profit calculations for arbitrage opportunities."""

    def __init__(self, fee_rate: float = 0.001, slippage: float = 0.0005) -> None:
        self.fee_rate = fee_rate
        self.slippage = slippage

    def evaluate(self, buy_price: float, sell_price: float, amount: float) -> ProfitBreakdown:
        logger.debug(
            "Evaluating opportunity buy_price=%s sell_price=%s amount=%s",
            buy_price,
            sell_price,
            amount,
        )
        gross_profit = (sell_price - buy_price) * amount
        notional = (buy_price + sell_price) * amount
        fees = notional * self.fee_rate
        slippage_cost = notional * self.slippage
        net_profit = gross_profit - fees - slippage_cost
        return ProfitBreakdown(
            gross_profit=round(gross_profit, 4),
            net_profit=round(net_profit, 4),
            fees=round(fees, 4),
            slippage_cost=round(slippage_cost, 4),
        )
