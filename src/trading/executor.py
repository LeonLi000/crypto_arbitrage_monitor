"""Trade execution orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..arbitrage.calculator import OpportunityCalculator
from ..arbitrage.strategies import Strategy
from ..risk.manager import RiskManager
from ..utils.database import InMemoryDatabase, StoredTrade
from ..utils.logger import get_logger
from ..utils.models import ArbitrageOpportunity, PricePoint, TradeResult
from ..utils.notifications import Notifier
from .cex_trader import CexTrader
from .dex_trader import DexTrader

logger = get_logger(__name__)


@dataclass
class TradeExecutor:
    calculator: OpportunityCalculator
    dex_trader: DexTrader
    cex_trader: CexTrader
    risk_manager: RiskManager
    notifier: Notifier
    database: InMemoryDatabase
    strategy: Strategy
    dex_exchanges: set[str]
    cex_exchanges: set[str]

    def execute(self, opportunity: ArbitrageOpportunity, price_map: Dict[str, PricePoint]) -> TradeResult | None:
        buy_point = price_map.get(opportunity.buy_exchange)
        sell_point = price_map.get(opportunity.sell_exchange)
        if not buy_point or not sell_point:
            logger.debug("Missing prices for opportunity %s", opportunity.identifier)
            return None

        available_capital = self.risk_manager.available_capital
        trade_amount = self.strategy.plan_trade(opportunity, available_capital)
        if trade_amount <= 0:
            logger.debug("Strategy returned zero trade size for %s", opportunity.identifier)
            return None
        if not self.risk_manager.allocate(opportunity.identifier, trade_amount):
            return None

        breakdown = self.calculator.evaluate(buy_point.price, sell_point.price, trade_amount)
        if breakdown.net_profit <= 0:
            logger.info("Opportunity %s rejected due to negative net profit", opportunity.identifier)
            self.risk_manager.portfolio.release(opportunity.identifier, trade_amount, 0.0)
            return None

        buy_cost = self._execute_buy(opportunity.buy_exchange, opportunity.pair, trade_amount, buy_point.price)
        sell_revenue = self._execute_sell(opportunity.sell_exchange, opportunity.pair, trade_amount, sell_point.price)
        realized_profit = sell_revenue - buy_cost

        trade = TradeResult(
            opportunity_id=opportunity.identifier,
            executed_amount=trade_amount,
            realized_profit=round(realized_profit, 4),
            status="executed" if realized_profit > 0 else "breakeven",
        )
        self.risk_manager.register_trade(opportunity.identifier, trade_amount, realized_profit)
        self.database.add_trade(
            StoredTrade(
                opportunity_id=trade.opportunity_id,
                amount=trade.executed_amount,
                realized_profit=trade.realized_profit,
                status=trade.status,
            )
        )
        self.notifier.notify(
            f"Executed arbitrage {opportunity.pair} profit {trade.realized_profit:.4f}"
        )
        return trade

    def _execute_buy(self, exchange: str, pair: str, amount: float, price: float) -> float:
        if exchange in self.dex_exchanges:
            return self.dex_trader.buy(pair, amount, price)
        if exchange in self.cex_exchanges:
            return self.cex_trader.buy(pair, amount, price)
        raise ValueError(f"Unknown exchange for buy: {exchange}")

    def _execute_sell(self, exchange: str, pair: str, amount: float, price: float) -> float:
        if exchange in self.dex_exchanges:
            return self.dex_trader.sell(pair, amount, price)
        if exchange in self.cex_exchanges:
            return self.cex_trader.sell(pair, amount, price)
        raise ValueError(f"Unknown exchange for sell: {exchange}")
