package arbitrage

import (
    "sort"

    "github.com/example/crypto_arbitrage_monitor/golang/internal/monitors"
)

type Opportunity struct {
    ID            string
    Pair          string
    BuyExchange   string
    SellExchange  string
    Spread        float64
    ExpectedProfit float64
    Confidence    float64
}

type Detector struct {
    MinSpread float64
}

func NewDetector(minSpread float64) *Detector {
    return &Detector{MinSpread: minSpread}
}

func (d *Detector) Detect(prices map[string]map[string]monitors.PricePoint) []Opportunity {
    opportunities := make([]Opportunity, 0)
    for pair, entries := range prices {
        if len(entries) < 2 {
            continue
        }
        points := make([]monitors.PricePoint, 0, len(entries))
        for _, point := range entries {
            points = append(points, point)
        }
        sort.Slice(points, func(i, j int) bool { return points[i].Price < points[j].Price })
        buy := points[0]
        sell := points[len(points)-1]
        if buy.Source == sell.Source {
            continue
        }
        spread := ((sell.Price - buy.Price) / buy.Price) * 100
        if spread < d.MinSpread {
            continue
        }
        opportunity := Opportunity{
            ID:             buy.Pair + "-" + buy.Source + "-" + sell.Source,
            Pair:           pair,
            BuyExchange:    buy.Source,
            SellExchange:   sell.Source,
            Spread:         round(spread, 4),
            ExpectedProfit: round(sell.Price-buy.Price, 4),
            Confidence:     round(min(spread/10, 0.99), 4),
        }
        opportunities = append(opportunities, opportunity)
    }
    return opportunities
}

func min(a, b float64) float64 {
    if a < b {
        return a
    }
    return b
}
