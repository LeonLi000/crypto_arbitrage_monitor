package trading

import (
    "errors"

    "github.com/example/crypto_arbitrage_monitor/golang/internal/arbitrage"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/monitors"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/risk"
    "github.com/example/crypto_arbitrage_monitor/golang/internal/utils"
)

type DexTrader struct {
    Name string
    Fee  float64
}

type CexTrader struct {
    Name string
    Fee  float64
}

type Executor struct {
    Calculator   *arbitrage.Calculator
    DexTrader    DexTrader
    CexTrader    CexTrader
    RiskManager  *risk.Manager
    DexExchanges map[string]struct{}
    CexExchanges map[string]struct{}
}

type TradeResult struct {
    Opportunity arbitrage.Opportunity
    Amount      float64
    Profit      float64
    Status      string
}

func (t DexTrader) Buy(amount, price float64) float64 {
    return amount * price * (1 + t.Fee)
}

func (t DexTrader) Sell(amount, price float64) float64 {
    return amount * price * (1 - t.Fee)
}

func (t CexTrader) Buy(amount, price float64) float64 {
    return amount * price * (1 + t.Fee)
}

func (t CexTrader) Sell(amount, price float64) float64 {
    return amount * price * (1 - t.Fee)
}

func (e *Executor) Execute(opportunity arbitrage.Opportunity, priceMap map[string]monitors.PricePoint) (*TradeResult, error) {
    buyPoint, ok := priceMap[opportunity.BuyExchange]
    if !ok {
        return nil, errors.New("missing buy price")
    }
    sellPoint, ok := priceMap[opportunity.SellExchange]
    if !ok {
        return nil, errors.New("missing sell price")
    }

    available := e.RiskManager.AvailableCapital()
    amount := available * opportunity.Confidence
    if amount <= 0 {
        return nil, errors.New("no available capital")
    }
    if !e.RiskManager.Allocate(opportunity.ID, amount) {
        return nil, errors.New("risk manager rejected trade")
    }

    breakdown := e.Calculator.Evaluate(buyPoint.Price, sellPoint.Price, amount)
    if breakdown.NetProfit <= 0 {
        e.RiskManager.Release(opportunity.ID, amount, 0)
        return nil, errors.New("negative profit")
    }

    cost, err := e.executeBuy(opportunity.BuyExchange, amount, buyPoint.Price)
    if err != nil {
        e.RiskManager.Release(opportunity.ID, amount, 0)
        return nil, err
    }
    revenue, err := e.executeSell(opportunity.SellExchange, amount, sellPoint.Price)
    if err != nil {
        e.RiskManager.Release(opportunity.ID, amount, 0)
        return nil, err
    }
    profit := revenue - cost
    e.RiskManager.Record(opportunity.ID, amount, profit)
    utils.Logger().Printf("Executed %s profit %.4f", opportunity.Pair, profit)
    return &TradeResult{Opportunity: opportunity, Amount: amount, Profit: profit, Status: "executed"}, nil
}

func (e *Executor) executeBuy(exchange string, amount, price float64) (float64, error) {
    if _, ok := e.DexExchanges[exchange]; ok {
        return e.DexTrader.Buy(amount, price), nil
    }
    if _, ok := e.CexExchanges[exchange]; ok {
        return e.CexTrader.Buy(amount, price), nil
    }
    return 0, errors.New("unknown exchange")
}

func (e *Executor) executeSell(exchange string, amount, price float64) (float64, error) {
    if _, ok := e.DexExchanges[exchange]; ok {
        return e.DexTrader.Sell(amount, price), nil
    }
    if _, ok := e.CexExchanges[exchange]; ok {
        return e.CexTrader.Sell(amount, price), nil
    }
    return 0, errors.New("unknown exchange")
}
