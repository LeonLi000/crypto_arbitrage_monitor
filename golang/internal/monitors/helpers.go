package monitors

import "math"

func round(value float64, precision int) float64 {
    scale := math.Pow(10, float64(precision))
    return math.Round(value*scale) / scale
}
