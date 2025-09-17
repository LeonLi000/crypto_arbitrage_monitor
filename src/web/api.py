"""Minimal FastAPI application exposing monitoring data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency
    from fastapi import FastAPI
except Exception:  # pragma: no cover - fallback for environments without fastapi
    FastAPI = None  # type: ignore

from ..utils.database import InMemoryDatabase
from ..utils.logger import get_logger
from ..utils.models import ArbitrageOpportunity
from ..risk.manager import RiskManager

logger = get_logger(__name__)


@dataclass
class AppState:
    database: InMemoryDatabase
    risk_manager: RiskManager
    latest_opportunities: List[ArbitrageOpportunity]


def create_app(state: AppState):  # pragma: no cover - requires FastAPI runtime
    if FastAPI is None:
        raise RuntimeError("fastapi is not installed")

    app = FastAPI(title="Crypto Arbitrage Monitor")

    @app.get("/opportunities")
    def list_opportunities() -> List[Dict[str, Any]]:
        return [
            {
                "id": opp.identifier,
                "pair": opp.pair,
                "buy": opp.buy_exchange,
                "sell": opp.sell_exchange,
                "spread": opp.spread,
                "expected_profit": opp.expected_profit,
                "confidence": opp.confidence,
            }
            for opp in state.latest_opportunities
        ]

    @app.get("/trades")
    def list_trades() -> List[Dict[str, Any]]:
        return [
            {
                "opportunity_id": trade.opportunity_id,
                "amount": trade.amount,
                "profit": trade.realized_profit,
                "status": trade.status,
            }
            for trade in state.database.list_trades()
        ]

    @app.get("/metrics")
    def metrics() -> Dict[str, Any]:
        return {
            "available_capital": state.risk_manager.available_capital,
            "cash": state.risk_manager.portfolio.cash,
            "trades_today": state.risk_manager.trades_today,
            "pnl": state.risk_manager.realized_pnl,
        }

    return app
