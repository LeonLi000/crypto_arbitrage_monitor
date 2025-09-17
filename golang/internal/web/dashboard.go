package web

import (
    "fmt"
    "strings"

    "github.com/example/crypto_arbitrage_monitor/golang/internal/arbitrage"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/risk"
)

type Snapshot struct {
    Opportunities []arbitrage.Opportunity
    Risk          *risk.Manager
}

func Render(snapshot Snapshot) string {
    var b strings.Builder
    b.WriteString("=== Go Dashboard Snapshot ===\n")
    b.WriteString(fmt.Sprintf("Available capital: %.2f\n", snapshot.Risk.AvailableCapital()))
    b.WriteString(fmt.Sprintf("Cash: %.2f\n", snapshot.Risk.Portfolio.Cash))
    b.WriteString(fmt.Sprintf("Trades today: %d\n", snapshot.Risk.TradesToday))
    b.WriteString(fmt.Sprintf("Realized PnL: %.2f\n", snapshot.Risk.RealizedPnL))
    b.WriteString("Opportunities:\n")
    for _, opp := range snapshot.Opportunities {
        b.WriteString(fmt.Sprintf(" - %s buy %s sell %s spread %.2f%%\n", opp.Pair, opp.BuyExchange, opp.SellExchange, opp.Spread))
    }
    return b.String()
}
