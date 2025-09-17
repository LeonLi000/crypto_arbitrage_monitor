package monitors

import (
    "math/rand"
    "time"
)

type CexMonitor struct {
    Name       string
    Pairs      []string
    BasePrice  float64
    Volatility float64
    Fee        float64
    state      map[string]float64
    rng        *rand.Rand
}

func NewCexMonitor(name string, pairs []string) *CexMonitor {
    state := make(map[string]float64)
    src := rand.NewSource(time.Now().UnixNano())
    rng := rand.New(src)
    for _, pair := range pairs {
        state[pair] = 100.0 * (0.98 + rng.Float64()*0.04)
    }
    return &CexMonitor{
        Name:       name,
        Pairs:      pairs,
        BasePrice:  100.0,
        Volatility: 0.01,
        Fee:        0.001,
        state:      state,
        rng:        rng,
    }
}

func (m *CexMonitor) Snapshot() []PricePoint {
    result := make([]PricePoint, 0, len(m.Pairs))
    for _, pair := range m.Pairs {
        price := m.state[pair]
        change := m.rng.NormFloat64() * m.Volatility
        price = price * (1 + change)
        if price < 0.1 {
            price = 0.1
        }
        m.state[pair] = price
        result = append(result, PricePoint{
            Source:    m.Name,
            Pair:      pair,
            Price:     round(price*(1-m.Fee), 4),
            Timestamp: time.Now().UTC(),
        })
    }
    return result
}
