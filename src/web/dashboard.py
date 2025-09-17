"""Helpers to run the dashboard web server."""
from __future__ import annotations

from ..utils.logger import get_logger
from .api import AppState, create_app

logger = get_logger(__name__)


def start_dashboard(state: AppState, host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover - requires uvicorn
    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover - uvicorn optional
        logger.error("uvicorn not available: %s", exc)
        return

    app = create_app(state)
    logger.info("Starting dashboard on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port)


def format_dashboard_snapshot(state: AppState) -> str:
    """Return a human readable snapshot for console based monitoring."""
    lines = ["=== Dashboard Snapshot ==="]
    lines.append(f"Available capital: {state.risk_manager.available_capital:.2f}")
    lines.append(f"Cash balance: {state.risk_manager.portfolio.cash:.2f}")
    lines.append(f"Trades today: {state.risk_manager.trades_today}")
    lines.append(f"Realized PnL: {state.risk_manager.realized_pnl:.2f}")
    lines.append("Opportunities:")
    for opp in state.latest_opportunities:
        lines.append(
            f" - {opp.pair}: buy {opp.buy_exchange} sell {opp.sell_exchange} "
            f"spread {opp.spread:.2f}% profit {opp.expected_profit:.4f}"
        )
    return "\n".join(lines)
