"""Command line entry point for the crypto arbitrage monitor demo."""
from __future__ import annotations

import argparse
import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .arbitrage.calculator import OpportunityCalculator
from .arbitrage.detector import ArbitrageDetector
from .arbitrage.strategies import ConfidenceWeightedStrategy
from .monitors.cex_monitor import CexMonitor
from .monitors.dex_monitor import DexMonitor
from .monitors.price_aggregator import PriceAggregator
from .risk.manager import RiskLimits, RiskManager
from .risk.portfolio import Portfolio
from .trading.cex_trader import CexTrader
from .trading.dex_trader import DexTrader
from .trading.executor import TradeExecutor
from .utils import config as config_utils
from .utils.database import InMemoryDatabase, StoredOpportunity
from .utils.logger import get_logger, setup_logging
from .utils.models import PricePoint
from .utils.notifications import Notifier
from .web.api import AppState
from .web.dashboard import format_dashboard_snapshot

logger = get_logger(__name__)

CONFIG_PATH = Path("config/config.yaml")


@dataclass
class AppContext:
    config: config_utils.AppConfig
    monitors: List
    aggregator: PriceAggregator
    detector: ArbitrageDetector
    calculator: OpportunityCalculator
    risk_manager: RiskManager
    notifier: Notifier
    database: InMemoryDatabase
    executor: TradeExecutor
    state: AppState


def build_context() -> AppContext:
    setup_logging()
    config = config_utils.load_config(CONFIG_PATH)

    trading_pairs = ["ETH/USDT", "BTC/USDT", "SOL/USDT"]
    dex_names = {"Uniswap", "SushiSwap", "PancakeSwap"}
    cex_names = {"Binance", "Coinbase", "Kraken"}

    monitors = [
        DexMonitor(name=name, trading_pairs=trading_pairs, update_interval=1.0)
        for name in dex_names
    ] + [
        CexMonitor(name=name, trading_pairs=trading_pairs, update_interval=1.0)
        for name in cex_names
    ]

    aggregator = PriceAggregator(monitors)
    detector = ArbitrageDetector(
        min_profit_threshold=config.monitoring.get("min_profit_threshold", 0.5)
    )
    calculator = OpportunityCalculator()
    portfolio = Portfolio.with_capital(config.risk.get("max_position_size", 10_000) * 2)
    risk_limits = RiskLimits(
        max_position_size=config.risk.get("max_position_size", 10_000),
        max_daily_trades=config.risk.get("max_daily_trades", 50),
        stop_loss=config.risk.get("stop_loss", 2.0),
    )
    risk_manager = RiskManager(risk_limits, portfolio)
    notifier = Notifier()
    database = InMemoryDatabase()
    strategy = ConfidenceWeightedStrategy(max_trade_size=risk_limits.max_position_size)
    executor = TradeExecutor(
        calculator=calculator,
        dex_trader=DexTrader("dex"),
        cex_trader=CexTrader("cex"),
        risk_manager=risk_manager,
        notifier=notifier,
        database=database,
        strategy=strategy,
        dex_exchanges=dex_names,
        cex_exchanges=cex_names,
    )
    state = AppState(database=database, risk_manager=risk_manager, latest_opportunities=[])
    return AppContext(
        config=config,
        monitors=monitors,
        aggregator=aggregator,
        detector=detector,
        calculator=calculator,
        risk_manager=risk_manager,
        notifier=notifier,
        database=database,
        executor=executor,
        state=state,
    )


async def run_monitor(context: AppContext, cycles: int | None = 5) -> None:
    async for prices in context.aggregator.stream(cycles=cycles):
        opportunities = context.detector.detect(prices)
        context.state.latest_opportunities = opportunities
        for opp in opportunities:
            context.database.save_opportunity(
                StoredOpportunity(
                    identifier=opp.identifier,
                    pair=opp.pair,
                    source=opp.buy_exchange,
                    target=opp.sell_exchange,
                    expected_profit=opp.expected_profit,
                    confidence=opp.confidence,
                )
            )
            context.executor.execute(opp, prices[opp.pair])
        snapshot = format_dashboard_snapshot(context.state)
        logger.info("\n%s", snapshot)


async def run_dashboard(context: AppContext, cycles: int) -> None:
    # Provide a simple textual dashboard update loop for demonstration.
    await run_monitor(context, cycles=cycles)


async def run_backtest(context: AppContext, start: str, end: str) -> None:
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    rng = random.Random(42)
    trading_pairs = ["ETH/USDT", "BTC/USDT", "SOL/USDT"]
    exchanges = list(context.executor.dex_exchanges | context.executor.cex_exchanges)
    current = start_dt
    total_opportunities = 0
    while current <= end_dt:
        synthetic_prices = {}
        for pair in trading_pairs:
            base_price = 100 + rng.random() * 50
            synthetic_prices[pair] = {}
            for exchange in exchanges:
                drift = rng.uniform(-0.02, 0.02)
                price = base_price * (1 + drift)
                synthetic_prices[pair][exchange] = PricePoint(
                    source=exchange,
                    pair=pair,
                    price=round(price, 2),
                    timestamp=current,
                )
        opportunities = context.detector.detect(synthetic_prices)
        total_opportunities += len(opportunities)
        logger.info(
            "Backtest %s detected %d opportunities",
            current.date(),
            len(opportunities),
        )
        current += timedelta(days=1)
    logger.info(
        "Backtest summary %s-%s total opportunities %d",
        start,
        end,
        total_opportunities,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crypto arbitrage monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor_parser = subparsers.add_parser("monitor", help="Run live monitoring loop")
    monitor_parser.add_argument("--cycles", type=int, default=5, help="Number of cycles to run")

    dashboard_parser = subparsers.add_parser("dashboard", help="Run dashboard demo")
    dashboard_parser.add_argument("--cycles", type=int, default=3, help="Number of update cycles")

    backtest_parser = subparsers.add_parser("backtest", help="Run a toy backtest")
    backtest_parser.add_argument("--start-date", required=True)
    backtest_parser.add_argument("--end-date", required=True)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    context = build_context()

    if args.command == "monitor":
        asyncio.run(run_monitor(context, cycles=args.cycles))
    elif args.command == "dashboard":
        asyncio.run(run_dashboard(context, cycles=args.cycles))
    elif args.command == "backtest":
        asyncio.run(run_backtest(context, args.start_date, args.end_date))
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unknown command {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
