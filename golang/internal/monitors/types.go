package monitors

import "time"

type PricePoint struct {
    Source    string
    Pair      string
    Price     float64
    Timestamp time.Time
}
