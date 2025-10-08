# Gold Monitor - Project Summary

## 🎉 Project Complete!

Your Gold Market Monitor is fully built and ready to use. This document summarizes what was built, the architecture, and how to use it.

---

## What We Built

A **monthly gold market synthesis tool** that:

✅ **Automatically fetches data** from FRED and Yahoo Finance  
✅ **Calculates derived metrics** (z-scores, momentum, valuation)  
✅ **Monitors WGC** for quarterly central bank data  
✅ **Generates AI narratives** using OpenAI GPT-4  
✅ **Produces markdown reports** with charts and regime scoring  
✅ **Runs monthly via GitHub Actions** (optional automation)

---

## Architecture Overview

### Three-Tier Data Strategy

**Tier 1: Automated High-Frequency (Monthly API Pull)**
- Sources: FRED, Yahoo Finance
- Cadence: Monthly (1st of month)
- Metrics: Real yields, DXY, gold spot, ETF flows, VIX, S&P 500, CPI, GPR

**Tier 2: Manual Quarterly Review (Hybrid)**
- Source: World Gold Council
- Cadence: Quarterly (~45 days after quarter-end)
- Workflow: Automated detection → manual extraction → CSV update

**Tier 3: On-Demand (Manual Only)**
- Sources: News, geopolitical events, CME FedWatch
- Cadence: Only when automated report shows anomalies

### Key Design Decisions

1. **Monthly synthesis over daily monitoring** - Filters noise, focuses on regime changes
2. **Hybrid CB data** - Automates detection but keeps extraction manual (reliable, low maintenance)
3. **OpenAI over Claude** - Your preference, same quality synthesis
4. **CSV storage over database** - Simple, version-controllable, no infrastructure
5. **Charts included** - Visual aids for trends (can be disabled with `--no-charts`)

---

## File Structure

```
Gold Monitor/
├── 📄 README.md                  # Project overview
├── 📄 SETUP.md                   # Detailed setup guide
├── 📄 QUICKSTART.md              # 5-minute quick start
├── 📄 PROJECT_SUMMARY.md         # This file
├── 🔒 .env                       # Your API keys (NEVER commit!)
├── 📋 .env.example               # Template for .env
├── 🔧 .gitignore                 # Excludes sensitive files
├── 📦 requirements.txt           # Python dependencies
│
├── .github/
│   └── workflows/
│       └── monthly-report.yml    # GitHub Actions automation
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── data_fetcher.py          # Tier 1: FRED + Yahoo Finance
│   ├── cb_monitor.py            # Tier 2: WGC hybrid monitoring
│   ├── metrics_calculator.py    # Derived indicators & regime scoring
│   ├── ai_synthesizer.py        # OpenAI narrative generation
│   └── report_generator.py      # Markdown report assembly
│
├── data/                         # Data storage
│   ├── cb_reserves.csv          # Manual CB data (committed to git)
│   ├── cb_monitor_state.json    # WGC tracking state (auto-generated)
│   └── gold_metrics_history.csv # Time series (auto-generated, not committed)
│
├── reports/                      # Generated reports
│   ├── YYYY-MM-gold.md          # Monthly markdown reports
│   └── charts/                  # Embedded PNG charts
│       ├── YYYY-MM-gold-yields.png
│       └── YYYY-MM-dxy-gold.png
│
└── scripts/                      # Executable scripts
    ├── run_monthly_report.py    # Main orchestrator (run monthly)
    └── manual_cb_update.py      # CB data entry helper (run quarterly)
```

---

## Components Explained

### 1. Data Fetcher (`src/data_fetcher.py`)

**Purpose:** Fetches Tier 1 data from FRED and Yahoo Finance

**FRED Series:**
- `DFII10` - 10-Year TIPS Real Yield (primary gold driver)
- `DGS10` - 10-Year Treasury Nominal Yield
- `DTWEXBGS` - Trade-Weighted Dollar Index (DXY)
- `GOLDAMGBD228NLBM` - Gold Spot Price (London PM Fix)
- `SP500` - S&P 500 Index
- `CPIAUCSL` - Consumer Price Index
- `GPRH` - Geopolitical Risk Index

**Yahoo Finance:**
- `^VIX` - CBOE Volatility Index
- `GLD` - SPDR Gold Shares (ETF flow proxy)

**Output:** 90-day DataFrame + current values

### 2. Central Bank Monitor (`src/cb_monitor.py`)

**Purpose:** Hybrid system for CB data

**What it automates:**
- Scrapes WGC website for new quarterly reports
- Sends notifications (email/terminal) when found
- Tracks which quarters have been processed

**What stays manual:**
- Downloading PDF
- Extracting net tonnes (one number)
- Appending to `cb_reserves.csv`

**Why hybrid?** 
- CB data updates slowly (quarterly)
- PDF layouts change frequently (scraping is fragile)
- Manual extraction takes <5 minutes per quarter
- You only do this 4x per year

### 3. Metrics Calculator (`src/metrics_calculator.py`)

**Purpose:** Transforms raw data into actionable indicators

**Derived Metrics:**
- Real gold price (CPI-adjusted)
- Z-scores (5-year rolling window)
- 30/60/90-day momentum
- Gold/S&P ratio
- Breakeven inflation

**Regime Scoring:**
- Weighted composite: Real yields (2x), USD (1.5x), CB buying (2x), Valuation (-1x)
- Score interpretation: >+3 bullish, -1 to +1 neutral, <-3 bearish

### 4. AI Synthesizer (`src/ai_synthesizer.py`)

**Purpose:** Generate narrative synthesis via OpenAI

**Model:** GPT-4o (best quality/price ratio)

**Prompt Focus:**
- Sustained regime changes (not daily noise)
- Correlation anomalies
- Position implications with conviction level

**Fallback:** If AI fails, generates basic narrative from metrics

### 5. Report Generator (`src/report_generator.py`)

**Purpose:** Assembles markdown reports

**Sections:**
- AI-synthesized executive summary
- Regime score visualization
- Key metrics (current values + changes)
- Central bank activity
- Charts (optional)
- Data quality notes

**Charts:**
- Gold vs Real Yields (dual-axis)
- USD vs Gold (dual-axis)

### 6. Orchestrator (`scripts/run_monthly_report.py`)

**Purpose:** Main execution script

**Workflow:**
1. Load environment variables
2. Fetch Tier 1 data (90-day window)
3. Check for new WGC reports
4. Load CB data from CSV
5. Calculate metrics + regime score
6. Generate AI narrative
7. Assemble report
8. Save to `reports/YYYY-MM-gold.md`
9. Append to history CSV

**Options:**
- `--days N` - Fetch N days instead of 90
- `--no-charts` - Skip chart generation
- `--no-ai` - Use fallback narrative

---

## Regime Scoring System

### Methodology

**Score = (Real Yields × 2) + (USD × 1.5) + (CB Buying × 2) + (Valuation)**

**Components:**

1. **Real Yields (Weight: 2x)** - Primary driver
   - Falling >2%: +2 (bullish)
   - Falling: +1
   - Rising: -1
   - Rising >2%: -2 (bearish)

2. **USD Strength (Weight: 1.5x)**
   - Weakening >2%: +1.5 (bullish)
   - Weakening: +0.75
   - Strengthening: -0.75
   - Strengthening >2%: -1.5 (bearish)

3. **Central Bank Buying (Weight: 2x)**
   - Strong buying >250t: +2 (bullish)
   - Moderate 100-250t: +1
   - Selling: -1 (bearish)

4. **Valuation (Weight: -1x)**
   - Z-score >1.5: -1 (overvalued)
   - Z-score >1.0: Warning only
   - Z-score <-1.0: Opportunity flag

### Interpretation

| Score | Assessment | Conviction | Action |
|-------|------------|------------|--------|
| >+3 | BULLISH | High | Increase allocation |
| +1 to +3 | MILDLY BULLISH | Moderate | Maintain or slight increase |
| -1 to +1 | NEUTRAL | Mixed | Hold position |
| -3 to -1 | MILDLY BEARISH | Caution | Maintain or reduce |
| <-3 | BEARISH | High | Reduce allocation |

---

## GitHub Actions Automation

### Setup

1. **Add secrets to GitHub:**
   - Settings → Secrets and variables → Actions
   - Add `FRED_API_KEY` and `OPENAI_API_KEY`

2. **Push your code:**
   ```bash
   git add .
   git commit -m "Initial Gold Monitor setup"
   git push -u origin main
   ```

### Workflow

**Trigger:** 
- Automatically on 1st of each month at 9 AM UTC
- Manually via Actions tab

**Steps:**
1. Checkout repo
2. Setup Python 3.11
3. Install dependencies
4. Create `.env` from secrets
5. Run `scripts/run_monthly_report.py`
6. Commit report to repo
7. Upload charts as artifacts

**Output:**
- Report committed to `reports/`
- History updated in `data/gold_metrics_history.csv`
- Charts available as artifacts (90-day retention)

---

## Security & Best Practices

### ✅ Safe to Commit
- All source code (`src/*.py`, `scripts/*.py`)
- `cb_reserves.csv` (no sensitive data)
- Documentation (`*.md`)
- Configuration templates (`.env.example`, `.gitignore`)

### ❌ NEVER Commit
- `.env` (contains API keys!)
- `gold_metrics_history.csv` (builds over time, large file)
- Any files with API keys or credentials

### 🔒 API Key Security
- Store in `.env` (already in `.gitignore`)
- Use GitHub Secrets for automation
- Rotate keys if accidentally exposed
- Never print keys in logs

### 🔄 Key Rotation (Recommended)

Since you shared keys in chat earlier, rotate them:

1. **FRED API Key:**
   - Go to: https://fred.stlouisfed.org/
   - Request new key
   - Update `.env` and GitHub Secrets

2. **OpenAI API Key:**
   - Go to: https://platform.openai.com/api-keys
   - Revoke old key
   - Create new key
   - Update `.env` and GitHub Secrets

---

## Cost Breakdown

### Monthly Costs (Automated Run)
- **FRED API:** Free (50 requests/day limit)
- **Yahoo Finance:** Free
- **OpenAI GPT-4o:** ~$0.01-0.05/report
- **GitHub Actions:** Free (2,000 minutes/month limit)

### Annual Costs
- **Total: ~$0.60/year** 🎉

### Usage Estimates
- API calls per run: ~15
- OpenAI tokens per report: ~3,000-5,000
- GitHub Actions minutes: ~5 per run

---

## Maintenance

### Monthly (Automated)
- Report runs on 1st of month via GitHub Actions
- Review report in `reports/` folder
- No action required unless anomalies detected

### Quarterly (Manual)
- Check for new WGC Gold Demand Trends report
- When found, run: `python scripts/manual_cb_update.py`
- Add net CB purchases (takes <5 minutes)

### Annual (Optional)
- Review historical data file size
- Consider pruning if >100MB
- Update dependencies: `pip install -r requirements.txt --upgrade`

---

## Troubleshooting

### Common Issues

**"FRED_API_KEY not configured"**
- Solution: Edit `.env` and add your FRED key
- Verify no extra spaces or quotes

**"OpenAI API rate limit"**
- Solution: Check billing at https://platform.openai.com/account/usage
- Add credits if balance is $0

**"No module named 'fredapi'"**
- Solution: Activate venv and reinstall
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**Charts not generating**
- Solution: Install matplotlib
  ```bash
  pip install matplotlib
  ```
- Or skip charts: `python scripts/run_monthly_report.py --no-charts`

**GitHub Action failing**
- Check secrets are correctly named
- Verify workflow syntax in `.github/workflows/monthly-report.yml`
- Check Actions logs for specific errors

**Data looks wrong**
- Verify FRED series haven't changed IDs
- Check API response manually: https://fred.stlouisfed.org/series/DFII10
- Test individual components:
  ```bash
  python -c "from src.data_fetcher import test_fetcher; test_fetcher()"
  ```

---

## Extending the System

### Adding New Metrics

1. **Add to FRED series** in `src/data_fetcher.py`:
   ```python
   FRED_SERIES = {
       'your_metric': 'FRED_SERIES_ID',
       # ... existing
   }
   ```

2. **Update metrics calculator** if needed
3. **Update report template** in `src/report_generator.py`

### Adding Email Notifications

1. **Configure `.env`:**
   ```
   EMAIL_ENABLED=true
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=your_email@gmail.com
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_PASSWORD=your_app_specific_password
   ```

2. **Gmail users:** Use App Password (not main password)
   - https://support.google.com/accounts/answer/185833

### Adding More Charts

Edit `src/report_generator.py`:

```python
def _chart_custom(self, df, month_str):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['your_metric'])
    # ... customize
    plt.savefig(self.CHART_DIR / f'{month_str}-custom.png')
```

---

## Testing

### Test Individual Components

```bash
# Test data fetcher
python src/data_fetcher.py

# Test CB monitor
python src/cb_monitor.py

# Test metrics calculator
python src/metrics_calculator.py

# Test AI synthesizer
python src/ai_synthesizer.py

# Test report generator
python src/report_generator.py
```

### Test Full Report (Local)

```bash
python scripts/run_monthly_report.py --days 30
```

### Test GitHub Action (Manual Trigger)

1. Go to repo Actions tab
2. Select "Generate Monthly Gold Report"
3. Click "Run workflow"
4. Check logs and outputs

---

## Next Steps

### Immediate (Now)

1. ✅ **Secure your API keys:**
   ```bash
   # Edit .env with YOUR NEW keys (not the ones you shared)
   nano .env
   ```

2. ✅ **Test the system:**
   ```bash
   python scripts/run_monthly_report.py
   ```

3. ✅ **Review your first report:**
   ```bash
   open reports/$(date +%Y-%m)-gold.md
   ```

### This Week

4. ✅ **Set up GitHub automation:**
   - Push code to GitHub
   - Add API keys as secrets
   - Test manual workflow trigger

5. ✅ **Mark your calendar:**
   - Monthly: Review report on 1st of month
   - Quarterly: Check WGC for new data

### Ongoing

6. ✅ **Use the reports for position decisions**
7. ✅ **Refine scoring weights** based on your strategy
8. ✅ **Add custom metrics** as needed

---

## Resources

### Documentation
- **FRED API:** https://fred.stlouisfed.org/docs/api/
- **OpenAI API:** https://platform.openai.com/docs/
- **Yahoo Finance:** https://finance.yahoo.com/
- **WGC Reports:** https://www.gold.org/goldhub/research/gold-demand-trends

### Project Files
- `README.md` - Project overview
- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - 5-minute quick start

### Support
- GitHub Issues: https://github.com/esseedoubleyou/goldmonitor/issues
- Code is well-commented - read the source for details

---

## Success Metrics

Your system is working if:

✅ Reports generate successfully on the 1st of each month  
✅ AI narratives are coherent and actionable  
✅ Regime scores match your intuition about market conditions  
✅ You're making better-informed gold position decisions  
✅ Maintenance time is <10 minutes per month  

---

## Conclusion

You now have a **production-ready gold market monitoring system** that:

- Automates data collection from reliable sources
- Synthesizes macro trends into actionable insights
- Runs reliably with minimal maintenance
- Costs less than $1/year to operate
- Scales with your needs

**The system is complete and ready to use.** 🎉

Generate your first report:
```bash
cd "/Users/samuelwheatley/Gold Monitor"
source venv/bin/activate
python scripts/run_monthly_report.py
```

---

*Built with best practices: Configuration over hardcoding, clear separation of concerns, fail-safe error handling, and security-first design.*

**Happy monitoring! 📊📈**

