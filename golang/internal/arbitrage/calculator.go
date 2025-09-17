package arbitrage

type ProfitBreakdown struct {
    GrossProfit   float64
    NetProfit     float64
    Fees          float64
    SlippageCost  float64
}

type Calculator struct {
    FeeRate  float64
    Slippage float64
}

func NewCalculator() *Calculator {
    return &Calculator{FeeRate: 0.001, Slippage: 0.0005}
}

func (c *Calculator) Evaluate(buyPrice, sellPrice, amount float64) ProfitBreakdown {
    gross := (sellPrice - buyPrice) * amount
    notional := (sellPrice + buyPrice) * amount
    fees := notional * c.FeeRate
    slippage := notional * c.Slippage
    net := gross - fees - slippage
    return ProfitBreakdown{
        GrossProfit:  round(gross, 4),
        NetProfit:    round(net, 4),
        Fees:         round(fees, 4),
        SlippageCost: round(slippage, 4),
    }
}
