package config

import (
    "bufio"
    "os"
    "strconv"
    "strings"
)

type App struct {
    Name    string
    Version string
    Debug   bool
}

type Monitoring struct {
    UpdateInterval     int
    MinProfitThreshold float64
    MaxSlippage        float64
}

type Risk struct {
    MaxPositionSize float64
    MaxDailyTrades  int
    StopLoss        float64
}

type Config struct {
    App        App
    Monitoring Monitoring
    Risk       Risk
}

func Load(path string) (Config, error) {
    file, err := os.Open(path)
    if err != nil {
        return Config{}, err
    }
    defer file.Close()

    cfg := Config{}
    currentSection := ""
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        raw := scanner.Text()
        trimmed := strings.TrimSpace(raw)
        if trimmed == "" || strings.HasPrefix(trimmed, "#") {
            continue
        }
        indent := len(raw) - len(strings.TrimLeft(raw, " "))
        if strings.HasSuffix(trimmed, ":") {
            if indent == 0 {
                currentSection = strings.TrimSuffix(trimmed, ":")
            }
            continue
        }
        parts := strings.SplitN(trimmed, ":", 2)
        if len(parts) != 2 {
            continue
        }
        key := strings.TrimSpace(parts[0])
        value := strings.TrimSpace(parts[1])
        switch currentSection {
        case "app":
            assignApp(&cfg.App, key, value)
        case "monitoring":
            assignMonitoring(&cfg.Monitoring, key, value)
        case "risk":
            assignRisk(&cfg.Risk, key, value)
        }
    }
    if err := scanner.Err(); err != nil {
        return Config{}, err
    }
    return cfg, nil
}

func assignApp(app *App, key, value string) {
    switch key {
    case "name":
        app.Name = trimQuotes(value)
    case "version":
        app.Version = trimQuotes(value)
    case "debug":
        app.Debug = parseBool(value)
    }
}

func assignMonitoring(mon *Monitoring, key, value string) {
    switch key {
    case "update_interval":
        mon.UpdateInterval = parseInt(value)
    case "min_profit_threshold":
        mon.MinProfitThreshold = parseFloat(value)
    case "max_slippage":
        mon.MaxSlippage = parseFloat(value)
    }
}

func assignRisk(r *Risk, key, value string) {
    switch key {
    case "max_position_size":
        r.MaxPositionSize = parseFloat(value)
    case "max_daily_trades":
        r.MaxDailyTrades = parseInt(value)
    case "stop_loss":
        r.StopLoss = parseFloat(value)
    }
}

func trimQuotes(value string) string {
    return strings.Trim(value, "\"")
}

func parseBool(value string) bool {
    value = strings.ToLower(value)
    return value == "true" || value == "yes" || value == "1"
}

func parseInt(value string) int {
    i, err := strconv.Atoi(strings.Split(value, "#")[0])
    if err != nil {
        return 0
    }
    return i
}

func parseFloat(value string) float64 {
    cleaned := strings.Split(value, "#")[0]
    f, err := strconv.ParseFloat(strings.TrimSpace(cleaned), 64)
    if err != nil {
        return 0
    }
    return f
}
