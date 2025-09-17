package risk

type Portfolio struct {
    InitialCapital float64
    Cash           float64
    Positions      map[string]float64
}

func NewPortfolio(capital float64) *Portfolio {
    return &Portfolio{
        InitialCapital: capital,
        Cash:           capital,
        Positions:      make(map[string]float64),
    }
}

func (p *Portfolio) Allocate(id string, amount float64) bool {
    if amount > p.Cash {
        return false
    }
    p.Cash -= amount
    p.Positions[id] += amount
    return true
}

func (p *Portfolio) Release(id string, amount, pnl float64) {
    exposure := p.Positions[id]
    if amount > exposure {
        amount = exposure
    }
    delete(p.Positions, id)
    p.Cash += amount + pnl
}
