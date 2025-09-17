package main

import (
    "context"
    "flag"
    "fmt"
    "os"
    "time"

    "github.com/example/crypto_arbitrage_monitor/golang/internal/arbitrage"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/config"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/monitors"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/risk"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/trading"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/utils"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/web"
)

var configPath = "../config/config.yaml"

func main() {
    if len(os.Args) < 2 {
        fmt.Println("usage: goapp <command> [options]")
        return
    }
    command := os.Args[1]
    switch command {
    case "monitor":
        monitorFlags := flag.NewFlagSet("monitor", flag.ExitOnError)
        cycles := monitorFlags.Int("cycles", 5, "number of cycles")
        _ = monitorFlags.Parse(os.Args[2:])
        runMonitor(*cycles)
    case "dashboard":
        dashFlags := flag.NewFlagSet("dashboard", flag.ExitOnError)
        cycles := dashFlags.Int("cycles", 3, "number of cycles")
        _ = dashFlags.Parse(os.Args[2:])
        runMonitor(*cycles)
    case "backtest":
        backtestFlags := flag.NewFlagSet("backtest", flag.ExitOnError)
        start := backtestFlags.String("start", "2024-01-01", "start date")
        end := backtestFlags.String("end", "2024-01-10", "end date")
        _ = backtestFlags.Parse(os.Args[2:])
        runBacktest(*start, *end)
    default:
        fmt.Println("unknown command", command)
    }
}

func buildContext() (*config.Config, *monitors.Aggregator, *arbitrage.Detector, *trading.Executor, *risk.Manager) {
    cfg, err := config.Load(configPath)
    if err != nil {
        panic(err)
    }
    pairs := []string{"ETH/USDT", "BTC/USDT", "SOL/USDT"}
    dexNames := []string{"Uniswap", "SushiSwap", "PancakeSwap"}
    cexNames := []string{"Binance", "Coinbase", "Kraken"}

    providers := make([]monitors.SnapshotProvider, 0)
    dexSet := make(map[string]struct{})
    cexSet := make(map[string]struct{})
    for _, name := range dexNames {
        providers = append(providers, monitors.NewDexMonitor(name, pairs))
        dexSet[name] = struct{}{}
    }
    for _, name := range cexNames {
        providers = append(providers, monitors.NewCexMonitor(name, pairs))
        cexSet[name] = struct{}{}
    }

    aggregator := monitors.NewAggregator(providers)
    detector := arbitrage.NewDetector(cfg.Monitoring.MinProfitThreshold)
    portfolio := risk.NewPortfolio(cfg.Risk.MaxPositionSize * 2)
    limits := risk.Limits{MaxPosition: cfg.Risk.MaxPositionSize, MaxTrades: cfg.Risk.MaxDailyTrades, StopLoss: cfg.Risk.StopLoss}
    manager := risk.NewManager(limits, portfolio)
    executor := &trading.Executor{
        Calculator:   arbitrage.NewCalculator(),
        DexTrader:    trading.DexTrader{Name: "dex", Fee: 0.003},
        CexTrader:    trading.CexTrader{Name: "cex", Fee: 0.001},
        RiskManager:  manager,
        DexExchanges: dexSet,
        CexExchanges: cexSet,
    }
    return &cfg, aggregator, detector, executor, manager
}

func runMonitor(cycles int) {
    cfg, aggregator, detector, executor, manager := buildContext()
    ctx := context.Background()
    for i := 0; i < cycles; i++ {
        priceMap := aggregator.Collect(ctx)
        opportunities := detector.Detect(priceMap)
        for _, opp := range opportunities {
            if pairPrices, ok := priceMap[opp.Pair]; ok {
                _, err := executor.Execute(opp, pairPrices)
                if err != nil {
                    utils.Logger().Println("trade skipped:", err)
                }
            }
        }
        snapshot := web.Snapshot{Opportunities: opportunities, Risk: manager}
        fmt.Println(web.Render(snapshot))
        time.Sleep(time.Second)
    }
    utils.Logger().Printf("Completed monitor cycles using version %s", cfg.App.Version)
}

func runBacktest(start, end string) {
    _, aggregator, detector, _, manager := buildContext()
    pairs := []string{"ETH/USDT", "BTC/USDT", "SOL/USDT"}
    ctx := context.Background()
    startTime, _ := time.Parse("2006-01-02", start)
    endTime, _ := time.Parse("2006-01-02", end)
    current := startTime
    total := 0
    for !current.After(endTime) {
        priceMap := aggregator.Collect(ctx)
        opportunities := detector.Detect(priceMap)
        total += len(opportunities)
        snapshot := web.Snapshot{Opportunities: opportunities, Risk: manager}
        fmt.Printf("Backtest %s opportunities %d\n", current.Format("2006-01-02"), len(opportunities))
        fmt.Println(web.Render(snapshot))
        current = current.Add(24 * time.Hour)
    }
    fmt.Printf("Backtest summary %s-%s total opps %d for %d pairs\n", start, end, total, len(pairs))
}
