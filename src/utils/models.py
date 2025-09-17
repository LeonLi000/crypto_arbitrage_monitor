"""Dataclass models shared across the project."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class PricePoint:
    source: str
    pair: str
    price: float
    timestamp: datetime


@dataclass(slots=True)
class ArbitrageOpportunity:
    identifier: str
    pair: str
    buy_exchange: str
    sell_exchange: str
    spread: float
    expected_profit: float
    confidence: float


@dataclass(slots=True)
class TradeResult:
    opportunity_id: str
    executed_amount: float
    realized_profit: float
    status: str
