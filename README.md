# AutoTrader

A production-oriented Python trading system scaffold for real broker execution with strong risk controls.

## What this includes

- Broker API client (Alpaca implementation)
- Strategy framework (adaptive ensemble, momentum, mean reversion)
- Multi-symbol portfolio allocation runner
- Risk manager with hard limits
- Trading engine with optional order confirmation
- CLI commands for account checks, dry runs, and live execution
- Unit tests for risk and strategy logic
- Append-only JSONL trade journal for auditability
- SQLite trade journal with analytics summary command
- Scheduler command with Discord/email alerts
- GitHub Actions CI for Python 3.9 to 3.12

## Important safety notes

- This project is for educational and operational tooling purposes.
- Live trading is risky and can cause significant losses.
- Use strict risk settings and start with very small allocations.
- Use broker APIs only. Do not automate bank website logins.

## Quick start

1. Create and activate a virtual environment.
2. Install package in editable mode.
3. Copy `.env.example` to `.env` and fill values.
4. Run account check, then dry run, then small live run.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
trader-cli health
trader-cli run --symbol AAPL --capital 500 --confirm
```

## CLI examples

```bash
# Validate broker connectivity and account details
trader-cli health

# Get latest quote
trader-cli quote --symbol MSFT

# Dry run (no order sent)
trader-cli run --symbol AAPL --capital 1000 --dry-run

# Live run with manual confirmation prompt
trader-cli run --symbol AAPL --capital 1000 --confirm

# Explicitly choose the adaptive ensemble strategy
trader-cli run --symbol AAPL --capital 1000 --dry-run --strategy adaptive_ensemble

# Run across multiple symbols with automatic capital allocation
trader-cli run-portfolio --symbols AAPL,MSFT,NVDA --capital 3000 --dry-run

# View persisted analytics from the SQLite journal
trader-cli analytics --limit 200

# Schedule repeated cycles with optional alerts
trader-cli schedule --symbols AAPL,MSFT --capital 2000 --interval-seconds 300 --iterations 4 --dry-run
```

## Architecture

- `src/trader_app/config.py`: environment configuration
- `src/trader_app/broker/`: broker interface + Alpaca client
- `src/trader_app/data/`: market data wrapper
- `src/trader_app/strategy/`: strategy interfaces and implementations
	- Includes `AdaptiveEnsembleStrategy` with trend, momentum, RSI, mean-reversion, and volatility gating
- `src/trader_app/risk/`: risk policy and position sizing
- `src/trader_app/execution/`: trading engine orchestration
- `src/trader_app/execution/portfolio.py`: multi-symbol capital allocator
- `src/trader_app/cli.py`: command line interface
- `src/trader_app/utils/trade_journal.py`: structured trade and decision audit log
- `src/trader_app/utils/sqlite_journal.py`: durable SQLite journal used by analytics
- `src/trader_app/analytics/performance.py`: event analytics summaries
- `src/trader_app/alerts/notifier.py`: Discord/email notification adapters

## Suggested next upgrades

- Add persistent trade journal storage (PostgreSQL)
- Add portfolio-level risk constraints across symbols
- Add async stream handling for real-time bars
- Add scheduled runs and alerting
- Add broker abstraction for Interactive Brokers/Tradier

## Repo hygiene

- CI workflow: .github/workflows/ci.yml
- Contribution guide: CONTRIBUTING.md
- Security policy: SECURITY.md
