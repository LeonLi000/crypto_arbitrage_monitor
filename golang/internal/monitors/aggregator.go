package monitors

import "context"

type SnapshotProvider interface {
    Snapshot() []PricePoint
}

type Aggregator struct {
    Providers []SnapshotProvider
}

func NewAggregator(providers []SnapshotProvider) *Aggregator {
    return &Aggregator{Providers: providers}
}

func (a *Aggregator) Collect(ctx context.Context) map[string]map[string]PricePoint {
    result := make(map[string]map[string]PricePoint)
    for _, provider := range a.Providers {
        select {
        case <-ctx.Done():
            return result
        default:
        }
        for _, point := range provider.Snapshot() {
            if _, ok := result[point.Pair]; !ok {
                result[point.Pair] = make(map[string]PricePoint)
            }
            result[point.Pair][point.Source] = point
        }
    }
    return result
}
