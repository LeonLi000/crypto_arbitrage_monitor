package risk

type Limits struct {
    MaxPosition float64
    MaxTrades   int
    StopLoss    float64
}

type Manager struct {
    Limits      Limits
    Portfolio   *Portfolio
    TradesToday int
    RealizedPnL float64
}

func NewManager(limits Limits, portfolio *Portfolio) *Manager {
    return &Manager{Limits: limits, Portfolio: portfolio}
}

func (m *Manager) AvailableCapital() float64 {
    if m.Portfolio.Cash < m.Limits.MaxPosition {
        return m.Portfolio.Cash
    }
    return m.Limits.MaxPosition
}

func (m *Manager) Allocate(id string, amount float64) bool {
    if amount <= 0 {
        return false
    }
    if amount > m.Limits.MaxPosition {
        return false
    }
    if m.TradesToday >= m.Limits.MaxTrades {
        return false
    }
    if m.Portfolio.Cash < amount {
        return false
    }
    if m.hitStopLoss() {
        return false
    }
    if !m.Portfolio.Allocate(id, amount) {
        return false
    }
    return true
}

func (m *Manager) Release(id string, amount, pnl float64) {
    m.Portfolio.Release(id, amount, pnl)
}

func (m *Manager) Record(id string, amount, profit float64) {
    m.TradesToday++
    m.RealizedPnL += profit
    m.Portfolio.Release(id, amount, profit)
}

func (m *Manager) hitStopLoss() bool {
    drawdown := (m.RealizedPnL / m.Portfolio.InitialCapital) * 100
    return drawdown <= -m.Limits.StopLoss
}
