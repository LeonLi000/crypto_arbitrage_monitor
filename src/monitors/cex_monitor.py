"""Simulated centralised exchange price monitor."""
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Dict, Iterable, List

from ..utils.logger import get_logger
from ..utils.models import PricePoint

logger = get_logger(__name__)


@dataclass
class CexMonitor:
    """Track order book mid prices from a simulated CEX."""

    name: str
    trading_pairs: Iterable[str]
    update_interval: float = 1.0
    base_price: float = 100.0
    volatility: float = 0.01
    fee: float = 0.001
    _state: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._state = {pair: self.base_price * random.uniform(0.98, 1.02) for pair in self.trading_pairs}

    async def fetch_snapshot(self) -> List[PricePoint]:
        await asyncio.sleep(self.update_interval)
        return [self._next_price(pair) for pair in self._state]

    async def stream_prices(self) -> AsyncIterator[PricePoint]:
        while True:
            for pair in list(self._state):
                yield self._next_price(pair)
            await asyncio.sleep(self.update_interval)

    def _next_price(self, pair: str) -> PricePoint:
        price = self._state[pair]
        change = random.gauss(0, self.volatility)
        price *= 1 + change
        price = max(price, 0.1)
        self._state[pair] = price
        point = PricePoint(
            source=self.name,
            pair=pair,
            price=round(price * (1 - self.fee), 4),
            timestamp=datetime.utcnow(),
        )
        logger.debug("CEX %s price for %s: %s", self.name, pair, point.price)
        return point
