"""
Report Generator: Markdown Report Assembly

Generates monthly markdown reports with:
- AI-synthesized narrative
- Key metrics and trends
- Regime score and interpretation
- Optional charts
- Data quality notes
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


class ReportGenerator:
    """Generates markdown reports from metrics."""
    
    REPORT_DIR = Path('reports')
    CHART_DIR = REPORT_DIR / 'charts'
    
    def __init__(self, include_charts: bool = True):
        """
        Initialize generator.
        
        Args:
            include_charts: Whether to generate embedded charts
        """
        self.include_charts = include_charts
        self.REPORT_DIR.mkdir(exist_ok=True)
        
        if include_charts:
            self.CHART_DIR.mkdir(exist_ok=True)
    
    def generate_report(
        self, 
        metrics: Dict, 
        regime_score: Dict,
        cb_data: Dict,
        ai_narrative: str,
        df: pd.DataFrame
    ) -> str:
        """
        Generate monthly markdown report.
        
        Args:
            metrics: Calculated metrics
            regime_score: Regime scoring results
            cb_data: Central bank data
            ai_narrative: AI-generated narrative
            df: Recent data DataFrame
            
        Returns:
            Complete report as markdown string
        """
        report_date = datetime.now()
        month_str = report_date.strftime('%B %Y')
        
        # Generate charts if enabled
        chart_references = ""
        if self.include_charts:
            chart_references = self._generate_charts(df, metrics, report_date)
        
        # Build report sections
        report = self._build_header(report_date, month_str)
        report += self._build_ai_narrative(ai_narrative)
        report += self._build_regime_section(regime_score)
        report += self._build_metrics_section(metrics)
        report += self._build_cb_section(cb_data)
        report += chart_references
        report += self._build_data_quality_section(metrics)
        report += self._build_footer()
        
        return report
    
    def _build_header(self, report_date: datetime, month_str: str) -> str:
        """Generate report header."""
        return f"""# Gold Market Monitor - {month_str}

*Generated: {report_date.strftime('%Y-%m-%d %H:%M:%S')}*

---

"""
    
    def _build_ai_narrative(self, narrative: str) -> str:
        """Format AI narrative section."""
        return f"""## Executive Summary

{narrative}

---

"""
    
    def _build_regime_section(self, regime_score: Dict) -> str:
        """Format regime score section."""
        
        # Create visual score bar
        score = regime_score['score']
        score_bar = self._create_score_bar(score)
        
        components_text = '\n'.join([
            f"  {icon} **{component}**: {weight:+.1f}"
            for component, weight, icon in regime_score['components']
        ])
        
        return f"""## Regime Score: {score:.1f} / 10

{score_bar}

**Assessment:** {regime_score['assessment']}  
**Conviction:** {regime_score['conviction']}  
**Recommended Action:** {regime_score['action']}

### Score Components:

{components_text}

**Methodology:**
- Real yields: ±2 points (primary driver)
- USD strength: ±1.5 points  
- Central bank buying: ±2 points
- Valuation: -1 point if overextended (z-score > 1.5)

*Score interpretation: >+3 = high conviction bullish | -1 to +1 = neutral | <-3 = bearish*

---

"""
    
    def _create_score_bar(self, score: float) -> str:
        """Create visual ASCII score bar."""
        # Map score (-5 to +5) to bar position
        normalized = (score + 5) / 10  # 0 to 1
        bar_position = int(normalized * 20)  # 0 to 20
        
        bar = ['─'] * 21
        bar[10] = '┼'  # Center mark
        bar[bar_position] = '█'
        
        bar_str = ''.join(bar)
        
        return f"""
```
Bearish                Neutral                Bullish
   -5         -3         0         +3         +5
    {bar_str}
```
"""
    
    def _build_metrics_section(self, metrics: Dict) -> str:
        """Format key metrics section."""
        
        def fmt_pct(key, label="N/A"):
            val = metrics.get(key)
            if val is None or pd.isna(val):
                return label
            sign = '+' if val >= 0 else ''
            return f"{sign}{val*100:.2f}%"
        
        def fmt_num(key, decimals=2):
            val = metrics.get(key)
            if val is None or pd.isna(val):
                return "N/A"
            return f"{val:.{decimals}f}"
        
        # Real yields interpretation
        ry_interp = "Falling real yields = bullish for gold" \
            if metrics.get('real_yield_momentum_30d', 0) < 0 \
            else "Rising real yields = bearish for gold"
        
        # USD interpretation
        dxy_interp = "Weakening USD = bullish for gold" \
            if metrics.get('dxy_momentum_30d', 0) < 0 \
            else "Strengthening USD = bearish for gold"
        
        # Z-score interpretation
        zscore = metrics.get('real_gold_zscore')
        if zscore is not None and not pd.isna(zscore):
            if zscore > 1.5:
                zscore_interp = "⚠️ Significantly overvalued vs 5Y average"
            elif zscore > 1.0:
                zscore_interp = "⚠️ Moderately overvalued vs 5Y average"
            elif zscore < -1.0:
                zscore_interp = "💡 Undervalued vs 5Y average"
            else:
                zscore_interp = "Fair value range"
        else:
            zscore_interp = "Insufficient history for z-score"
        
        return f"""## Key Metrics

### Real Interest Rates (Primary Gold Driver)
- **10Y TIPS Yield:** {fmt_num('real_yield_current')}%
- **30-Day Change:** {fmt_pct('real_yield_momentum_30d')}
- **90-Day Change:** {fmt_pct('real_yield_momentum_90d')}
- **Interpretation:** {ry_interp}

### US Dollar Strength
- **DXY Index:** {fmt_num('dxy_current')}
- **30-Day Change:** {fmt_pct('dxy_momentum_30d')}
- **90-Day Change:** {fmt_pct('dxy_momentum_90d')}
- **Interpretation:** {dxy_interp}

### Market Sentiment
- **VIX Index:** {fmt_num('vix_current')}
- **Geopolitical Risk Index:** {fmt_num('gpr_current', 1)}
- **Environment:** {'Elevated risk (VIX >20)' if metrics.get('vix_current', 0) > 20 else 'Normal risk levels'}

### Gold Valuation
- **Gold Spot Price:** ${fmt_num('gold_spot_current')}
- **30-Day Return:** {fmt_pct('gold_spot_momentum_30d')}
- **Real Gold Price (CPI-Adjusted):** ${fmt_num('real_gold_price_current')}
- **Real Gold Z-Score (5Y):** {fmt_num('real_gold_zscore') if metrics.get('real_gold_zscore') else 'N/A'}
  - *{zscore_interp}*
- **Gold/S&P 500 Ratio:** {fmt_num('gold_sp_ratio', 4)}

### Investment Flows
- **GLD Shares Outstanding:** {self._format_large_number(metrics.get('gld_shares_current'))}
  - *Note: Changes in shares outstanding indicate net ETF inflows/outflows*
- **Breakeven Inflation:** {fmt_num('breakeven_inflation')}%

---

"""
    
    def _build_cb_section(self, cb_data: Dict) -> str:
        """Format central bank activity section."""
        
        status = cb_data.get('status')
        
        if status == 'missing':
            return f"""## Central Bank Activity (Official Sector)

⚠️ **No central bank data available**

{cb_data.get('message', 'Initialize data with: python scripts/manual_cb_update.py --init')}

---

"""
        
        if status == 'error':
            return f"""## Central Bank Activity (Official Sector)

⚠️ **Error loading central bank data**

{cb_data.get('error', 'Unknown error')}

---

"""
        
        # Data exists
        freshness_icon = "⚠️" if cb_data.get('is_stale') else "✅"
        freshness_note = f"\n\n⚠️ **Data is {cb_data['days_old']} days old - check for new WGC report**" \
            if cb_data.get('is_stale') else ""
        
        tonnes = cb_data.get('cb_net_tonnes', 0)
        cb_interp = "Strong structural buying" if tonnes > 250 \
            else "Moderate buying" if tonnes > 100 \
            else "Weak buying" if tonnes > 0 \
            else "Net selling"
        
        return f"""## Central Bank Activity (Official Sector)

- **Latest Quarter:** {cb_data.get('quarter', 'N/A')}
- **Net Purchases:** {tonnes:.1f} tonnes
- **Source:** {cb_data.get('source', 'N/A')}
- **Last Updated:** {cb_data.get('validated_date', 'N/A')} {freshness_icon}{freshness_note}
- **Interpretation:** {cb_interp}

**Context:** Central banks have been consistent net buyers since 2010, with accelerated purchases post-2022. This represents structural, long-term demand often tied to reserve diversification and de-dollarization efforts.

---

"""
    
    def _build_data_quality_section(self, metrics: Dict) -> str:
        """Format data quality and sources section."""
        
        return f"""## Data Sources & Quality

**Primary Sources:**
- Real yields, gold spot, DXY, S&P 500, CPI, GPR: [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/)
- VIX, ETF holdings: [Yahoo Finance](https://finance.yahoo.com/)
- Central bank purchases: [World Gold Council](https://www.gold.org/goldhub/research/gold-demand-trends)

**Data Window:**
- Start: {metrics.get('data_start_date', 'N/A')}
- End: {metrics.get('data_end_date', 'N/A')}
- Days: {metrics.get('data_days', 'N/A')}

**Calculation Date:** {metrics.get('calculation_date', 'N/A')}

---

"""
    
    def _build_footer(self) -> str:
        """Generate report footer."""
        return f"""## Notes

- This report is generated automatically for monthly position review
- Focus on sustained regime changes, not daily volatility
- Z-scores require 1+ years of history (5 years optimal)
- Central bank data updates quarterly with ~45-60 day lag
- For questions or issues, review logs or contact the maintainer

---

*Report generated by Gold Market Monitor v1.0*
*GitHub: [esseedoubleyou/goldmonitor](https://github.com/esseedoubleyou/goldmonitor)*
"""
    
    def _generate_charts(
        self, 
        df: pd.DataFrame, 
        metrics: Dict,
        report_date: datetime
    ) -> str:
        """
        Generate charts and return markdown references.
        
        Returns:
            Markdown string with chart references
        """
        month_str = report_date.strftime('%Y-%m')
        
        chart_files = []
        
        try:
            # Chart 1: Gold vs Real Yields
            fig1_path = self._chart_gold_vs_yields(df, month_str)
            if fig1_path:
                chart_files.append(f"![Gold vs Real Yields](charts/{fig1_path.name})")
            
            # Chart 2: DXY and Gold
            fig2_path = self._chart_dxy_gold(df, month_str)
            if fig2_path:
                chart_files.append(f"![USD and Gold](charts/{fig2_path.name})")
            
        except Exception as e:
            print(f"⚠️  Chart generation failed: {e}")
        
        if chart_files:
            charts_md = "\n\n## Charts\n\n" + "\n\n".join(chart_files) + "\n\n---\n\n"
            return charts_md
        else:
            return ""
    
    def _chart_gold_vs_yields(self, df: pd.DataFrame, month_str: str) -> Optional[Path]:
        """Generate gold price vs real yields chart."""
        
        if 'gold_spot' not in df.columns or 'real_yield' not in df.columns:
            return None
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Gold price (left axis)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Gold Spot Price ($)', color='gold')
        ax1.plot(df.index, df['gold_spot'], color='gold', linewidth=2, label='Gold Spot')
        ax1.tick_params(axis='y', labelcolor='gold')
        ax1.grid(True, alpha=0.3)
        
        # Real yields (right axis - inverted for inverse relationship)
        ax2 = ax1.twinx()
        ax2.set_ylabel('10Y TIPS Real Yield (%)', color='steelblue')
        ax2.plot(df.index, df['real_yield'], color='steelblue', linewidth=2, label='Real Yield')
        ax2.tick_params(axis='y', labelcolor='steelblue')
        ax2.invert_yaxis()  # Invert so rising yields show as falling line
        
        plt.title(f'Gold Price vs Real Yields - {month_str}', fontsize=14, fontweight='bold')
        fig.tight_layout()
        
        filepath = self.CHART_DIR / f'{month_str}-gold-yields.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _chart_dxy_gold(self, df: pd.DataFrame, month_str: str) -> Optional[Path]:
        """Generate DXY and gold chart."""
        
        if 'dxy' not in df.columns or 'gold_spot' not in df.columns:
            return None
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # DXY (left axis)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('DXY Index', color='darkblue')
        ax1.plot(df.index, df['dxy'], color='darkblue', linewidth=2, label='DXY')
        ax1.tick_params(axis='y', labelcolor='darkblue')
        ax1.grid(True, alpha=0.3)
        
        # Gold (right axis)
        ax2 = ax1.twinx()
        ax2.set_ylabel('Gold Spot Price ($)', color='gold')
        ax2.plot(df.index, df['gold_spot'], color='gold', linewidth=2, label='Gold')
        ax2.tick_params(axis='y', labelcolor='gold')
        
        plt.title(f'USD Strength vs Gold Price - {month_str}', fontsize=14, fontweight='bold')
        fig.tight_layout()
        
        filepath = self.CHART_DIR / f'{month_str}-dxy-gold.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _format_large_number(self, value) -> str:
        """Format large numbers with commas."""
        if value is None or pd.isna(value):
            return 'N/A'
        return f"{value:,.0f}"
    
    def save_report(self, content: str, report_date: Optional[datetime] = None) -> Path:
        """
        Save report to file with YYYY-MM naming.
        
        Args:
            content: Report markdown content
            report_date: Optional date (default: now)
            
        Returns:
            Path to saved report
        """
        if report_date is None:
            report_date = datetime.now()
        
        filename = f"{report_date.strftime('%Y-%m')}-gold.md"
        filepath = self.REPORT_DIR / filename
        
        filepath.write_text(content)
        
        print(f"\n{'='*60}")
        print(f"✅ Report saved!")
        print(f"   File: {filepath}")
        print(f"   Size: {len(content):,} characters")
        print(f"{'='*60}\n")
        
        return filepath


def test_generator():
    """Test report generation with sample data."""
    import numpy as np
    
    # Sample data
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    df = pd.DataFrame({
        'gold_spot': 2000 + np.random.randn(90) * 50,
        'sp500': 4500 + np.random.randn(90) * 100,
        'real_yield': 1.5 + np.random.randn(90) * 0.2,
        'dxy': 103 + np.random.randn(90) * 2,
        'cpi': 310 + np.arange(90) * 0.1,
        'vix': 15 + np.random.randn(90) * 3,
        'gpr': 120 + np.random.randn(90) * 10
    }, index=dates)
    
    metrics = {
        'real_yield_current': 1.75,
        'real_yield_momentum_30d': -0.05,
        'dxy_current': 102.5,
        'dxy_momentum_30d': -0.02,
        'gold_spot_current': 2650.0,
        'gold_spot_momentum_30d': 0.03,
        'real_gold_price_current': 2100.0,
        'real_gold_zscore': 0.8,
        'gold_sp_ratio': 0.47,
        'vix_current': 15.2,
        'gpr_current': 125.0,
        'gld_shares_current': 500000000,
        'breakeven_inflation': 2.3,
        'data_start_date': dates[0].date(),
        'data_end_date': dates[-1].date(),
        'data_days': 90,
        'calculation_date': datetime.now()
    }
    
    regime_score = {
        'score': 2.75,
        'assessment': 'MILDLY BULLISH',
        'conviction': 'Moderate conviction',
        'action': 'Maintain or slightly increase position',
        'components': [
            ('Real yields falling', +1, '✅'),
            ('USD weakening', +0.75, '✅'),
            ('Strong CB buying', +2, '✅'),
            ('Elevated valuation', 0, '⚠️')
        ]
    }
    
    cb_data = {
        'quarter': 'Q1_2025',
        'cb_net_tonnes': 290,
        'source': 'WGC',
        'validated_date': '2025-05-20',
        'days_old': 45,
        'is_stale': False,
        'status': 'current'
    }
    
    ai_narrative = """Gold's macro environment has turned moderately bullish over the past month, driven primarily by falling real yields and a weakening dollar. Real yields declined 5% while the DXY dropped 2%, creating favorable conditions for gold appreciation. These moves represent a shift from the previous quarter's tightening regime.

The correlation structure remains healthy - gold is responding as expected to its primary drivers. Central bank demand continues at elevated levels (290 tonnes in Q1), reinforcing the structural bid under prices. However, valuation metrics suggest caution, with real gold trading near the upper end of its 5-year range.

Position recommendation: Maintain current allocation with modest upside potential if the real yield decline proves durable. Key risk is a hawkish Fed surprise reversing rate expectations. Monitor 10Y TIPS closely - a move back above 2% would signal regime change."""
    
    generator = ReportGenerator(include_charts=True)
    report = generator.generate_report(metrics, regime_score, cb_data, ai_narrative, df)
    
    filepath = generator.save_report(report)
    print(f"Test report saved to: {filepath}")


if __name__ == "__main__":
    test_generator()

