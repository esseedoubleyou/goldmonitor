# Gold Monitor - Quick Start

Get your first report in 5 minutes! ⏱️

## 1. Install Dependencies (1 minute)

```bash
cd "/Users/samuelwheatley/Gold Monitor"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Add Your API Keys (2 minutes)

Edit `.env` and replace the placeholder values:

```bash
nano .env  # or use any text editor
```

**Replace these lines:**
```
FRED_API_KEY=your_fred_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**With your actual keys:**
```
FRED_API_KEY=cc51675bebcb60bc0cce24e1d3413b76
OPENAI_API_KEY=sk-proj-V-CPl_7v...
```

⚠️ **SECURITY WARNING:** 
- **NEVER commit `.env` to git** (it's already in `.gitignore`)
- **Rotate the keys you shared earlier** - they were exposed in chat
- Get new keys:
  - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
  - OpenAI: https://platform.openai.com/api-keys

## 3. Generate Your First Report (2 minutes)

```bash
python scripts/run_monthly_report.py
```

This will:
1. ✅ Fetch 90 days of market data from FRED & Yahoo Finance
2. ✅ Check for new WGC reports
3. ✅ Calculate derived metrics & regime score
4. ✅ Generate AI-synthesized narrative via OpenAI
5. ✅ Create markdown report with charts
6. ✅ Save to `reports/YYYY-MM-gold.md`

## 4. View Your Report

```bash
# Find the report
ls reports/

# Open it
open reports/$(date +%Y-%m)-gold.md

# Or read in terminal
cat reports/$(date +%Y-%m)-gold.md
```

---

## What You Should See

```
🏆 GOLD MARKET MONITOR - Monthly Report Generator
======================================================================

STEP 1: Fetching market data (FRED + Yahoo Finance)
----------------------------------------------------------------------
✅ Fetched real_yield (DFII10): 63 observations
✅ Fetched nominal_yield (DGS10): 63 observations
...

STEP 4: Calculating derived metrics
----------------------------------------------------------------------
✅ Calculated 45 metrics
   Real gold price: $2,145.32
   Gold spot: $2,654.20

STEP 5: Calculating regime score
----------------------------------------------------------------------
✅ Regime Score: 2.8
   Assessment: MILDLY BULLISH
   Action: Maintain or slightly increase position

✅ REPORT GENERATION COMPLETE!
======================================================================

📄 Report: reports/2025-10-gold.md
```

---

## Next Steps

### Monthly Usage (Automated)

**Option A: GitHub Actions (Recommended)**
1. Push your code to GitHub (see SETUP.md)
2. Add API keys as GitHub Secrets
3. Reports run automatically on 1st of each month

**Option B: Manual Run**
```bash
# Run on the 1st of each month
python scripts/run_monthly_report.py
```

### Quarterly: Update Central Bank Data

When you see a notification about a new WGC report:

```bash
python scripts/manual_cb_update.py
```

Follow the prompts to add the latest quarterly data.

---

## Troubleshooting

### Error: "FRED_API_KEY not configured"
- Check your `.env` file exists
- Verify no typos in the key
- Ensure no extra spaces or quotes

### Error: "OpenAI API rate limit"
- Check your OpenAI billing: https://platform.openai.com/account/usage
- Add credits if balance is $0
- Each report costs ~$0.01-0.05

### Error: "No module named 'fredapi'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Charts not showing
- Install matplotlib: `pip install matplotlib`
- Or skip charts: `python scripts/run_monthly_report.py --no-charts`

---

## File Structure

```
Gold Monitor/
├── reports/
│   └── 2025-10-gold.md          ← Your report is here!
├── data/
│   ├── cb_reserves.csv           ← Update quarterly
│   └── gold_metrics_history.csv  ← Builds over time
├── scripts/
│   ├── run_monthly_report.py     ← Run this monthly
│   └── manual_cb_update.py       ← Run when WGC updates
└── .env                          ← Your API keys (secret!)
```

---

## Cost

- **FRED API:** Free
- **Yahoo Finance:** Free  
- **OpenAI GPT-4o:** ~$0.05/report = ~$0.60/year
- **GitHub Actions:** Free

**Total: < $1/year** 🎉

---

## Help

- 📖 Full setup guide: `SETUP.md`
- 📚 Project overview: `README.md`
- 🐛 Found a bug? Open an issue on GitHub

---

**That's it! You're all set.** 🚀

Your first report is in `reports/` - review it and start tracking gold's macro environment!

