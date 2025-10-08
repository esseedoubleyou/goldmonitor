# Gold Market Monitor

An automated monthly reporting system that tracks gold's macro environment to inform position decisions.

## Overview

This tool generates monthly markdown reports analyzing:
- Real interest rates (TIPS yields)
- US Dollar strength (DXY)
- Investment flows (ETF holdings)
- Market sentiment (VIX, geopolitical risk)
- Central bank activity
- Valuation metrics (real gold price, gold/S&P ratio)

**Key Principle:** This is a *monthly synthesis tool*, not a real-time trading system. We prioritize actionable insights over data volume and reliability over complexity.

## Setup

### 1. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys:
# - FRED_API_KEY: Get from https://fred.stlouisfed.org/docs/api/api_key.html
# - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
```

**⚠️ NEVER commit .env to git! It contains sensitive API keys.**

### 3. Initialize Data Files

```bash
# Create initial central bank data file
python scripts/manual_cb_update.py --init
```

This creates `data/cb_reserves.csv` with sample data. You'll update this manually each quarter.

## Usage

### Generate Monthly Report

```bash
python scripts/run_monthly_report.py
```

This will:
1. Fetch 90 days of data from FRED and Yahoo Finance
2. Check for new WGC quarterly reports
3. Calculate derived metrics (z-scores, momentum, flows)
4. Generate AI-synthesized narrative via OpenAI
5. Save report to `reports/YYYY-MM-gold.md`
6. Append raw data to `data/gold_metrics_history.csv`

### Update Central Bank Data (Quarterly)

When you receive notification of a new WGC report:

```bash
python scripts/manual_cb_update.py
```

Follow the prompts to add the latest quarterly central bank purchase data.

## Data Architecture

### Tier 1: Automated High-Frequency (Monthly Pull)
- **Sources:** FRED, Yahoo Finance
- **Cadence:** Monthly (1st of month via GitHub Actions)
- **Metrics:** Real yields, DXY, gold spot, ETF flows, VIX, S&P 500, CPI, geopolitical risk

### Tier 2: Manual Quarterly Review (Hybrid)
- **Sources:** World Gold Council
- **Cadence:** Quarterly (~45 days after quarter-end)
- **Workflow:** Automated detection → manual extraction → CSV update

### Tier 3: On-Demand (Manual Only)
- **Sources:** News, geopolitical events, CME FedWatch
- **Cadence:** Only when automated report shows anomalies

## Project Structure

```
gold-monitor/
├── .env                          # API keys (never commit!)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── src/
│   ├── data_fetcher.py          # Tier 1: FRED + Yahoo Finance
│   ├── cb_monitor.py            # Tier 2: WGC detection + manual assist
│   ├── metrics_calculator.py    # Derived indicators
│   ├── report_generator.py      # Markdown report assembly
│   └── ai_synthesizer.py        # OpenAI narrative generation
├── data/
│   ├── gold_metrics_history.csv # Time series (auto-generated)
│   ├── cb_reserves.csv          # Manual CB data entry
│   └── cb_monitor_state.json    # Tracks processed WGC reports
├── reports/
│   └── YYYY-MM-gold.md          # Generated monthly reports
└── scripts/
    ├── run_monthly_report.py    # Main orchestrator
    └── manual_cb_update.py      # CB data entry helper
```

## Automation (GitHub Actions)

The system runs automatically on the 1st of each month via GitHub Actions.

To enable:
1. Add your API keys as GitHub Secrets:
   - `FRED_API_KEY`
   - `OPENAI_API_KEY`
2. Push the `.github/workflows/monthly-report.yml` file
3. Reports will be committed automatically to the repo

## Regime Scoring

The report includes a **Regime Score** based on:

- **Real yields** (weight: 2x) - Primary driver
- **USD strength** (weight: 1.5x)
- **Central bank buying** (weight: 2x)
- **Valuation** (weight: -1 if overextended)

**Interpretation:**
- Score > +3: High conviction bullish
- Score -1 to +1: Neutral
- Score < -3: Bearish

## FAQ

### How often should I run this?

**Once per month** (automated on 1st). Gold macro trends are slow-moving—daily checks add noise, not signal.

### What if central bank data is stale?

The report will warn you if CB data is >90 days old. Check the [WGC Gold Demand Trends](https://www.gold.org/goldhub/research/gold-demand-trends) page for new quarterly reports.

### Can I backfill historical data?

Yes. FRED and Yahoo Finance support historical queries. Modify `data_fetcher.py` to pull longer time periods and run once to populate history.

### Why not use real-time data?

This is a **positioning tool** for monthly rebalancing, not a **trading system**. Monthly synthesis filters noise and focuses on durable regime shifts.

## Troubleshooting

### "FRED API key invalid"
- Verify your key in `.env`
- Check you've activated it on FRED's website
- Ensure no extra spaces in the `.env` file

### "OpenAI API rate limit"
- You may have hit usage limits
- Check your billing at https://platform.openai.com/account/usage
- The script uses GPT-4o which requires paid credits

### "No data returned from FRED"
- Some series update with delays (e.g., CPI is monthly)
- Check series is still active: https://fred.stlouisfed.org/series/[SERIES_ID]

## Security

- **Never commit `.env`** - it contains sensitive API keys
- **Rotate API keys** if accidentally exposed
- **Use environment variables** for all secrets
- **Review** `.gitignore` to ensure data privacy

## Contributing

This is a personal tool, but suggestions welcome:
1. Open an issue describing the enhancement
2. Fork and create a feature branch
3. Submit a pull request

## License

MIT License - Use freely, no warranty provided.

---

**Questions?** Review the project specification document or check the inline code documentation.

