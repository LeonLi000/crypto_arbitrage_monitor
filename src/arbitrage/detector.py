"""Identify profitable arbitrage opportunities from aggregated prices."""
from __future__ import annotations

import uuid
from typing import Dict, Iterable, List

from ..utils.logger import get_logger
from ..utils.models import ArbitrageOpportunity, PricePoint

logger = get_logger(__name__)


class ArbitrageDetector:
    def __init__(self, min_profit_threshold: float = 0.3) -> None:
        self.min_profit_threshold = min_profit_threshold

    def detect(self, prices: Dict[str, Dict[str, PricePoint]]) -> List[ArbitrageOpportunity]:
        opportunities: List[ArbitrageOpportunity] = []
        for pair, by_exchange in prices.items():
            if len(by_exchange) < 2:
                continue
            cheapest = min(by_exchange.values(), key=lambda p: p.price)
            most_expensive = max(by_exchange.values(), key=lambda p: p.price)
            if cheapest.source == most_expensive.source:
                continue

            spread_pct = ((most_expensive.price - cheapest.price) / cheapest.price) * 100
            if spread_pct < self.min_profit_threshold:
                logger.debug(
                    "Pair %s spread %.4f below threshold %.4f",
                    pair,
                    spread_pct,
                    self.min_profit_threshold,
                )
                continue

            opportunity = ArbitrageOpportunity(
                identifier=str(uuid.uuid4()),
                pair=pair,
                buy_exchange=cheapest.source,
                sell_exchange=most_expensive.source,
                spread=round(spread_pct, 4),
                expected_profit=round(most_expensive.price - cheapest.price, 4),
                confidence=round(min(spread_pct / 10, 0.99), 4),
            )
            opportunities.append(opportunity)
            logger.info(
                "Detected opportunity %s buy on %s sell on %s spread %.4f%%",
                opportunity.identifier,
                opportunity.buy_exchange,
                opportunity.sell_exchange,
                opportunity.spread,
            )
        return opportunities

    @staticmethod
    def top_opportunities(opportunities: Iterable[ArbitrageOpportunity], limit: int = 5) -> List[ArbitrageOpportunity]:
        return sorted(opportunities, key=lambda opp: opp.spread, reverse=True)[:limit]
