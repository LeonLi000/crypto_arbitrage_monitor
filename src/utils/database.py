"""Simplified in-memory storage utilities used by the monitoring service."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class StoredOpportunity:
    """Persisted representation of an arbitrage opportunity."""

    identifier: str
    pair: str
    source: str
    target: str
    expected_profit: float
    confidence: float


@dataclass
class StoredTrade:
    """Record describing a simulated trade execution."""

    opportunity_id: str
    amount: float
    realized_profit: float
    status: str


@dataclass
class InMemoryDatabase:
    """Very small persistence layer used for demos and tests."""

    opportunities: Dict[str, StoredOpportunity] = field(default_factory=dict)
    trades: List[StoredTrade] = field(default_factory=list)

    def save_opportunity(self, opportunity: StoredOpportunity) -> None:
        logger.debug("Persisting opportunity %s", opportunity.identifier)
        self.opportunities[opportunity.identifier] = opportunity

    def get_opportunity(self, identifier: str) -> Optional[StoredOpportunity]:
        return self.opportunities.get(identifier)

    def list_opportunities(self) -> List[StoredOpportunity]:
        return list(self.opportunities.values())

    def add_trade(self, trade: StoredTrade) -> None:
        logger.debug("Persisting trade for opportunity %s", trade.opportunity_id)
        self.trades.append(trade)

    def list_trades(self) -> List[StoredTrade]:
        return list(self.trades)
