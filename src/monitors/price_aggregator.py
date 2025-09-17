"""Aggregate price information from multiple monitors."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, Iterable, List, Mapping

from ..utils.logger import get_logger
from ..utils.models import PricePoint

logger = get_logger(__name__)


class PriceAggregator:
    """Coordinate snapshot collection across monitors and expose merged data."""

    def __init__(self, monitors: Iterable) -> None:
        self.monitors = list(monitors)

    async def collect_once(self) -> Dict[str, Dict[str, PricePoint]]:
        """Fetch one set of prices from all monitors."""
        logger.debug("Collecting price snapshot from %d monitors", len(self.monitors))
        results = await asyncio.gather(*[monitor.fetch_snapshot() for monitor in self.monitors])
        prices: Dict[str, Dict[str, PricePoint]] = defaultdict(dict)
        for monitor_prices in results:
            for point in monitor_prices:
                prices[point.pair][point.source] = point
        return prices

    async def stream(self, cycles: int | None = None) -> Iterable[Dict[str, Dict[str, PricePoint]]]:
        count = 0
        while cycles is None or count < cycles:
            yield await self.collect_once()
            count += 1

    @staticmethod
    def flatten(prices: Mapping[str, Mapping[str, PricePoint]]) -> List[PricePoint]:
        """Return the aggregated data as a simple list of price points."""
        return [point for sources in prices.values() for point in sources.values()]
