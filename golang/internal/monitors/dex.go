package monitors

import (
    "math/rand"
    "time"
)

type DexMonitor struct {
    Name       string
    Pairs      []string
    BasePrice  float64
    Volatility float64
    state      map[string]float64
    rng        *rand.Rand
}

func NewDexMonitor(name string, pairs []string) *DexMonitor {
    state := make(map[string]float64)
    for _, pair := range pairs {
        state[pair] = 100.0
    }
    return &DexMonitor{
        Name:       name,
        Pairs:      pairs,
        BasePrice:  100.0,
        Volatility: 0.015,
        state:      state,
        rng:        rand.New(rand.NewSource(time.Now().UnixNano())),
    }
}

func (m *DexMonitor) Snapshot() []PricePoint {
    result := make([]PricePoint, 0, len(m.Pairs))
    for _, pair := range m.Pairs {
        price := m.state[pair]
        change := m.rng.Float64()*2*m.Volatility - m.Volatility
        price = price * (1 + change)
        if price < 0.1 {
            price = 0.1
        }
        m.state[pair] = price
        result = append(result, PricePoint{
            Source:    m.Name,
            Pair:      pair,
            Price:     round(price, 4),
            Timestamp: time.Now().UTC(),
        })
    }
    return result
}
