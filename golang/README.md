# Go Implementation

This folder contains a simplified Go implementation of the crypto arbitrage monitor.

## Commands

```bash
# run monitoring loop
go run ./golang/cmd/app monitor --cycles 3

# run dashboard simulation
go run ./golang/cmd/app dashboard --cycles 2

# run backtest
go run ./golang/cmd/app backtest --start 2024-01-01 --end 2024-01-05
```
