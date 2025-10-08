# IMF Gold Data - Analysis & Recommendation

## 📊 What You Have

**IMF International Liquidity Dataset:**
- **9,557 rows** of gold reserve data
- **1,372 time periods** (1945 to Sep 2025)
- **Quarterly data available** through Q2 2025
- **Coverage:** World-level aggregates

### Key Series Available:

1. **Gold reserves (volume)** - Fine troy ounces, Quarterly
   - Latest: Q2 2025 data available
   
2. **Gold reserves at market value** - USD/SDR, Quarterly
   - Q2 2025: $17.36 trillion (world total)
   - Q1 2025: $16.76 trillion
   - Q4 2024: $16.07 trillion
   - Q3 2024: $16.51 trillion

---

## 🎯 Critical Difference: Levels vs. Flows

### What Your System Needs:
```csv
quarter,cb_net_tonnes,source,validated_date
Q1_2025,290,WGC,2025-05-20
```
**This is NET PURCHASES (tonnes bought/sold)**

### What IMF Provides:
```csv
Q1_2025: 2.66 trillion SDR (total reserve level)
Q4_2024: 2.30 trillion SDR (total reserve level)
```
**This is TOTAL RESERVE LEVELS (at market value)**

---

## ⚠️ The Problem

**IMF reserve levels change due to TWO factors:**

1. **Physical purchases/sales** ✅ (What you want)
2. **Gold price changes** ❌ (Distorts the signal)

### Example:
- Q4 2024: Gold reserves worth $16.07T
- Q1 2025: Gold reserves worth $16.76T
- **Change: +$0.69T**

**BUT:**  this could be due to:
- Central banks buying gold ✅
- Gold price rising 📈 ❌
- OR BOTH

**You can't separate these effects from reserve levels alone.**

---

## 💡 WGC vs. IMF Methodology

### WGC (What your system was designed for):
- Reports **actual purchases in tonnes**
- Removes price effects
- Shows **physical flow**
- Example: "Central banks bought 290 tonnes in Q1"

### IMF (What you have):
- Reports **total reserve value**
- Includes price effects
- Shows **level at market value**
- Example: "Central banks held $16.76T in Q1"

---

## 🤔 Can We Use Your IMF Data?

### Option A: Calculate Volume Changes (Partial Solution)

**What we can do:**
```python
Q1_2025_ounces = 1,234,567,890  # From IMF volume series
Q4_2024_ounces = 1,220,000,000  
Change = 14,567,890 troy ounces = ~453 tonnes
```

**Pros:**
- Removes price effects (uses volume, not value)
- Historical backfill possible
- Quarterly granularity

**Cons:**
- IMF data lags (Q2 2025 is latest, we're in Q4)
- Less timely than WGC (WGC publishes ~45 days after quarter)
- May include methodology differences vs. WGC

### Option B: Keep WGC Manual Entry (Current Design)

**Pros:**
- Exact methodology match (tonnes purchased)
- Industry-standard source
- Only 5 min per quarter
- More timely than IMF

**Cons:**
- Manual work (4x per year)

---

## 📋 My Recommendations

### For Historical Data (2020-2024): ✅ YES, Use IMF

**Value:** Backfill your `cb_reserves.csv` with 5 years of history

**How:**
1. Extract quarterly volume data (troy ounces)
2. Calculate quarter-over-quarter changes
3. Convert to tonnes
4. Import into your system

**I'll build you an importer script for this.**

### For Ongoing Updates (2025+): ⚠️ MAYBE

**Decision factors:**

| Factor | WGC Manual | IMF Automated |
|--------|------------|---------------|
| **Effort** | 5 min/quarter | 0 min (automated) |
| **Timeliness** | ~45 days lag | ~60-90 days lag |
| **Methodology** | Purchase flow | Volume change |
| **Reliability** | Very high | High |

**Recommendation:**
1. **Start with WGC manual** (as designed)
2. **Test IMF automated** for 2-3 quarters
3. **Compare results** - if within 10%, switch to IMF
4. **Keep WGC as validation** check

---

## 🚀 Next Steps

### Immediate: Backfill Historical Data

I'll create a script to:
1. Extract IMF quarterly volume data (2020-2025)
2. Calculate net changes in tonnes
3. Generate a CSV ready to import

**This gives you 5 years of history immediately.**

### Medium-term: Hybrid Approach

1. Use IMF historical (2020-2024) ✅
2. Use WGC manual going forward ✅
3. Cross-validate both sources

### Long-term: Evaluate Automation

After 3 months of both:
- If IMF matches WGC within 10% → automate
- If IMF lags too much → stick with WGC
- If IMF diverges → keep WGC (gold standard)

---

## 📊 Summary

**Your IMF data is EXCELLENT for historical backfill** but has trade-offs for ongoing use.

**Recommended hybrid strategy:**
```
Historical (2020-2024):  IMF automated  ✅
Current (2025+):         WGC manual     ✅  
Validation:              Compare both   ✅
```

This gives you:
- Rich historical context
- Reliable current data
- Cross-validation capability

---

## ⚡ Ready to Proceed?

**Say "yes" and I'll create the IMF importer script that:**
1. Extracts quarterly volume changes
2. Converts to tonnes
3. Generates CSV for your system
4. Backfills 2020-2025 data

**This will give you 5 years of historical CB data immediately!**

