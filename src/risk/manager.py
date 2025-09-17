"""Risk controls for the arbitrage system."""
from __future__ import annotations

from dataclasses import dataclass

from ..utils.logger import get_logger
from .portfolio import Portfolio

logger = get_logger(__name__)


@dataclass
class RiskLimits:
    max_position_size: float
    max_daily_trades: int
    stop_loss: float  # percent drawdown permitted


class RiskManager:
    def __init__(self, limits: RiskLimits, portfolio: Portfolio) -> None:
        self.limits = limits
        self.portfolio = portfolio
        self.trades_today = 0
        self.realized_pnl = 0.0

    @property
    def available_capital(self) -> float:
        return min(self.portfolio.cash, self.limits.max_position_size)

    def can_execute(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if amount > self.limits.max_position_size:
            logger.warning("Trade %.2f exceeds position limit %.2f", amount, self.limits.max_position_size)
            return False
        if self.trades_today >= self.limits.max_daily_trades:
            logger.warning("Daily trade limit reached (%d)", self.limits.max_daily_trades)
            return False
        if amount > self.portfolio.cash:
            logger.warning("Insufficient portfolio cash %.2f for trade %.2f", self.portfolio.cash, amount)
            return False
        if self._reached_stop_loss():
            logger.warning("Stop loss triggered; trade blocked")
            return False
        return True

    def register_trade(self, opportunity_id: str, amount: float, profit: float) -> None:
        self.trades_today += 1
        self.realized_pnl += profit
        self.portfolio.release(opportunity_id, amount, profit)
        logger.info(
            "Registered trade %s amount %.2f profit %.2f total pnl %.2f",
            opportunity_id,
            amount,
            profit,
            self.realized_pnl,
        )

    def allocate(self, opportunity_id: str, amount: float) -> bool:
        if not self.can_execute(amount):
            return False
        return self.portfolio.allocate(opportunity_id, amount)

    def _reached_stop_loss(self) -> bool:
        drawdown_pct = (self.realized_pnl / self.portfolio.initial_capital) * 100
        return drawdown_pct <= -abs(self.limits.stop_loss)
