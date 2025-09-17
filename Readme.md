# 加密货币套利监控系统

一个全面的加密货币套利机会监控和自动交易系统，支持链上DEX和中心化交易所之间的价格差异监控。

## 功能特性

### 🔍 价格监控
- **链上价格监控**: 实时监控Uniswap、SushiSwap、PancakeSwap等DEX价格
- **交易所价格监控**: 支持Binance、Coinbase、Kraken等主流CEX
- **多链支持**: Ethereum、BSC、Polygon、Arbitrum等
- **实时WebSocket连接**: 毫秒级价格更新

### 💰 套利识别
- **智能套利算法**: 自动识别有利可图的套利机会
- **手续费计算**: 精确计算交易成本和滑点
- **最小利润阈值**: 可配置的最小利润要求
- **风险评估**: 实时风险分析和资金管理

### 🤖 自动交易
- **自动执行**: 发现套利机会时自动执行交易
- **多策略支持**: 支持不同的套利策略
- **资金管理**: 智能资金分配和风险控制
- **交易限制**: 可配置的交易频率和金额限制

### 📊 监控和分析
- **实时仪表板**: Web界面显示实时数据
- **历史数据分析**: 套利机会历史统计
- **性能指标**: 收益率、成功率等关键指标
- **告警系统**: 重要事件实时通知

## 项目结构

```
crypto_arbitrage_monitor/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 主程序入口
│   ├── monitors/               # 价格监控模块
│   │   ├── __init__.py
│   │   ├── dex_monitor.py      # DEX价格监控
│   │   ├── cex_monitor.py      # CEX价格监控
│   │   └── price_aggregator.py # 价格聚合器
│   ├── arbitrage/              # 套利模块
│   │   ├── __init__.py
│   │   ├── detector.py         # 套利机会检测
│   │   ├── calculator.py       # 利润计算
│   │   └── strategies.py       # 套利策略
│   ├── trading/                # 交易执行模块
│   │   ├── __init__.py
│   │   ├── executor.py         # 交易执行器
│   │   ├── dex_trader.py       # DEX交易
│   │   └── cex_trader.py       # CEX交易
│   ├── risk/                   # 风险管理模块
│   │   ├── __init__.py
│   │   ├── manager.py          # 风险管理器
│   │   └── portfolio.py        # 资金组合管理
│   ├── utils/                  # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志工具
│   │   ├── database.py         # 数据库工具
│   │   └── notifications.py    # 通知工具
│   └── web/                    # Web界面
│       ├── __init__.py
│       ├── dashboard.py        # 仪表板
│       └── api.py              # API接口
├── config/                     # 配置文件目录
│   ├── config.yaml             # 主配置文件
│   ├── exchanges.yaml          # 交易所配置
│   ├── strategies.yaml         # 策略配置
│   └── .env.example            # 环境变量示例
├── data/                       # 数据存储目录
│   ├── raw/                    # 原始数据
│   ├── processed/              # 处理后数据
│   └── logs/                   # 日志文件
├── tests/                      # 测试目录
├── docs/                       # 文档目录
├── scripts/                    # 脚本目录
├── requirements.txt            # 依赖包列表
├── setup.py                    # 安装脚本
└── README.md                   # 项目说明
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd crypto_arbitrage_monitor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

```bash
# 复制环境变量配置
cp config/.env.example .env

# 编辑配置文件，添加API密钥等信息
vim .env
```

### 3. 运行系统

```bash
# 启动监控系统
python -m src.main monitor

# 启动Web仪表板
python -m src.main dashboard

# 运行回测
python -m src.main backtest --start-date 2024-01-01 --end-date 2024-01-31
```

## 配置说明

### 主配置文件 (config/config.yaml)

```yaml
# 基础设置
app:
  name: "Crypto Arbitrage Monitor"
  version: "1.0.0"
  debug: false

# 监控设置
monitoring:
  update_interval: 1  # 价格更新间隔(秒)
  min_profit_threshold: 0.5  # 最小利润阈值(%)
  max_slippage: 0.3  # 最大滑点(%)

# 风险管理
risk:
  max_position_size: 10000  # 最大仓位(USD)
  max_daily_trades: 50      # 每日最大交易次数
  stop_loss: 2.0            # 止损阈值(%)

# 数据库设置
database:
  url: "postgresql://user:pass@localhost/arbitrage"
  pool_size: 10

# 通知设置
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

## 命令行用法

项目包含Python和Go两套实现，均通过命令行进行演示。Python版本提供更丰富的模块化结构，而Go版本展示了如何在强类型语言中实现同样的流程。

### Python

```bash
# 运行监控循环
python -m src.main monitor --cycles 5

# 运行仪表板（终端输出摘要）
python -m src.main dashboard --cycles 3

# 运行简化回测
python -m src.main backtest --start-date 2024-01-01 --end-date 2024-01-10
```

### Go

```bash
cd golang

# 运行监控循环
go run ./cmd/app monitor --cycles 5

# 运行仪表板演示
go run ./cmd/app dashboard --cycles 3

# 运行简化回测
go run ./cmd/app backtest --start 2024-01-01 --end 2024-01-10

cd ..
```

## 安全注意事项

⚠️ **重要提醒**:
- 请妥善保管API密钥和私钥
- 建议先在测试网络上运行
- 设置合理的风险控制参数
- 定期备份重要数据
- 监控系统运行状态

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request来改进项目！

## 联系方式

- 项目主页: https://github.com/crypto-arbitrage/monitor
- 问题反馈: https://github.com/crypto-arbitrage/monitor/issues
- 邮箱: team@cryptoarbitrage.com
