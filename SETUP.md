# Gold Monitor - Setup Guide

Complete step-by-step setup instructions.

## Prerequisites

- **Python 3.10+** installed
- **Git** installed
- **FRED API key** (free from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html))
- **OpenAI API key** (from [OpenAI Platform](https://platform.openai.com/api-keys))

---

## Step 1: Clone or Initialize Repository

If you haven't already:

```bash
cd "/Users/samuelwheatley/Gold Monitor"
git init
git remote add origin https://github.com/esseedoubleyou/goldmonitor.git
```

---

## Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Configure API Keys

### 🚨 IMPORTANT: Never commit your API keys!

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual keys
nano .env  # or use your favorite editor
```

Your `.env` file should look like:

```
FRED_API_KEY=your_actual_fred_key_here
OPENAI_API_KEY=your_actual_openai_key_here
EMAIL_ENABLED=false
```

**Getting API Keys:**

1. **FRED API Key** (free, instant):
   - Go to: https://fred.stlouisfed.org/docs/api/api_key.html
   - Click "Request API Key"
   - Copy the key to `.env`

2. **OpenAI API Key** (requires payment setup):
   - Go to: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy to `.env`
   - Note: You'll need credits ($5-10 should last many months)

---

## Step 4: Test Your Setup

Run a test report with the current data:

```bash
python scripts/run_monthly_report.py
```

This should:
- ✅ Fetch 90 days of market data
- ✅ Check for WGC reports
- ✅ Calculate metrics
- ✅ Generate AI narrative
- ✅ Create report in `reports/`

**If you see errors:**
- `FRED_API_KEY not configured` → Check your `.env` file
- `OpenAI API rate limit` → Check your OpenAI billing/credits
- `Module not found` → Run `pip install -r requirements.txt` again

---

## Step 5: Set Up GitHub Automation (Optional)

To run reports automatically on the 1st of each month:

### A. Add Secrets to GitHub

1. Go to your repo: https://github.com/esseedoubleyou/goldmonitor
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add two secrets:
   - Name: `FRED_API_KEY`, Value: your FRED key
   - Name: `OPENAI_API_KEY`, Value: your OpenAI key

### B. Push Your Code

```bash
git add .
git commit -m "Initial Gold Monitor setup"
git push -u origin main
```

### C. Verify Workflow

- Go to Actions tab in GitHub
- You should see "Generate Monthly Gold Report" workflow
- Click "Run workflow" to test manually

**The workflow will:**
- Run automatically on the 1st of each month at 9 AM UTC
- Commit the report to your repo
- Upload charts as artifacts

---

## Step 6: Update Central Bank Data (Quarterly)

Central bank data is updated manually each quarter:

```bash
# When you receive notification of new WGC report:
python scripts/manual_cb_update.py

# Follow the prompts to add:
# - Quarter (e.g., Q1_2025)
# - Net tonnes purchased
# - Source (default: WGC)
```

**WGC reports typically publish:**
- Q1 report: Late May
- Q2 report: Late August
- Q3 report: Late November
- Q4 report: Late February

Check: https://www.gold.org/goldhub/research/gold-demand-trends

---

## Daily Usage

### Generate a Report Manually

```bash
# Standard 90-day report with charts
python scripts/run_monthly_report.py

# Quick report without charts
python scripts/run_monthly_report.py --no-charts

# Without AI (uses fallback narrative)
python scripts/run_monthly_report.py --no-ai
```

### View Your Reports

Reports are saved in `reports/YYYY-MM-gold.md`

```bash
# Open latest report
open reports/$(date +%Y-%m)-gold.md

# Or view in terminal
cat reports/$(date +%Y-%m)-gold.md
```

### Update Central Bank Data

```bash
# Interactive update
python scripts/manual_cb_update.py

# View current data
python scripts/manual_cb_update.py --show
```

---

## Troubleshooting

### "FRED API key invalid"
- Verify key in `.env` (no spaces, no quotes)
- Activate key on FRED website
- Check API request limits (50 requests/minute)

### "OpenAI API rate limit"
- Check usage: https://platform.openai.com/account/usage
- Add credits: https://platform.openai.com/account/billing
- GPT-4o costs ~$0.01-0.05 per report

### "Module not found"
```bash
pip install -r requirements.txt
```

### Charts not generating
```bash
pip install matplotlib
```

### GitHub Action failing
- Check secrets are set correctly
- Verify workflow syntax
- Check Actions logs for errors

---

## Project Structure

```
gold-monitor/
├── .env                          # Your API keys (NEVER commit!)
├── .env.example                  # Template for .env
├── .github/workflows/            # GitHub Actions automation
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview
├── SETUP.md                      # This file
├── src/                          # Source code
│   ├── data_fetcher.py          # FRED + Yahoo Finance
│   ├── cb_monitor.py            # WGC monitoring
│   ├── metrics_calculator.py    # Indicators & scoring
│   ├── ai_synthesizer.py        # OpenAI narrative
│   └── report_generator.py      # Markdown assembly
├── data/                         # Data storage
│   ├── cb_reserves.csv          # Manual CB data (committed)
│   ├── cb_monitor_state.json    # WGC tracking (auto)
│   └── gold_metrics_history.csv # Time series (auto)
├── reports/                      # Generated reports
│   ├── YYYY-MM-gold.md          # Monthly reports
│   └── charts/                  # Embedded charts
└── scripts/                      # Executable scripts
    ├── run_monthly_report.py    # Main script
    └── manual_cb_update.py      # CB data helper
```

---

## Security Notes

### ✅ Safe to Commit
- Code files (`*.py`)
- `cb_reserves.csv` (no sensitive data)
- `README.md`, `SETUP.md`
- `.gitignore`, `requirements.txt`

### ❌ NEVER Commit
- `.env` (contains API keys!)
- `gold_metrics_history.csv` (large, builds over time)
- Personal notes or credentials

### 🔒 GitHub Secrets
- Store API keys as repository secrets
- Never print secrets in logs
- Rotate keys if accidentally exposed

---

## Cost Estimate

### Monthly Costs
- **FRED API:** Free
- **Yahoo Finance:** Free
- **OpenAI (GPT-4o):** ~$0.01-0.05 per report (~$0.60/year)
- **GitHub Actions:** Free (< 2,000 minutes/month)

**Total: < $1/year** 🎉

---

## Next Steps

1. ✅ Run your first report: `python scripts/run_monthly_report.py`
2. ✅ Review the output in `reports/`
3. ✅ Set up GitHub automation (push your code)
4. 📅 Mark calendar for next month's run
5. 📅 Mark calendar for quarterly WGC checks

---

## Need Help?

- **Issues:** https://github.com/esseedoubleyou/goldmonitor/issues
- **FRED API Docs:** https://fred.stlouisfed.org/docs/api/
- **OpenAI API Docs:** https://platform.openai.com/docs/

---

**Ready to go! 🚀**

Generate your first report:
```bash
python scripts/run_monthly_report.py
```

