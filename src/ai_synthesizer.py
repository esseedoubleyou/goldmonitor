"""
AI Synthesizer: OpenAI-Powered Narrative Generation

Uses OpenAI's GPT-4 to synthesize monthly gold market data into actionable narratives.

Focus: Sustained regime changes (not daily noise) and position implications.
"""

from openai import OpenAI
import pandas as pd
from typing import Dict, Optional
import json


class AISynthesizer:
    """Uses OpenAI API to generate narrative synthesis."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize synthesizer.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o for best quality/price)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def synthesize_narrative(
        self, 
        metrics: Dict, 
        regime_score: Dict,
        cb_data: Dict,
        df: pd.DataFrame
    ) -> str:
        """
        Send metrics to OpenAI for narrative synthesis.
        
        Args:
            metrics: Calculated metrics dict
            regime_score: Regime scoring results
            cb_data: Central bank data
            df: Recent price data DataFrame
            
        Returns:
            3-5 paragraph executive summary
        """
        
        # Prepare data summary for AI
        data_summary = self._format_data_for_ai(metrics, regime_score, cb_data, df)
        
        prompt = self._build_prompt(data_summary, regime_score)
        
        try:
            print("\n🤖 Generating AI narrative synthesis...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a macro analyst specializing in gold markets. Provide concise, actionable analysis for position decisions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            narrative = response.choices[0].message.content
            
            print(f"✅ Narrative generated ({len(narrative)} characters)")
            print(f"   Model: {self.model}")
            print(f"   Tokens used: {response.usage.total_tokens}")
            
            return narrative
            
        except Exception as e:
            print(f"⚠️  OpenAI synthesis failed: {e}")
            return self._fallback_narrative(metrics, regime_score)
    
    def _format_data_for_ai(
        self, 
        metrics: Dict, 
        regime_score: Dict,
        cb_data: Dict,
        df: pd.DataFrame
    ) -> str:
        """
        Format data into structured summary for AI.
        
        Returns:
            Formatted string with key metrics and changes
        """
        
        # Helper function for formatting
        def fmt_pct(val):
            if val is None or pd.isna(val):
                return "N/A"
            return f"{val*100:+.2f}%"
        
        def fmt_num(val, decimals=2):
            if val is None or pd.isna(val):
                return "N/A"
            return f"{val:.{decimals}f}"
        
        summary = f"""
## Current Market State (as of {metrics.get('data_end_date', 'N/A')})

### Key Drivers

**Real Interest Rates (Primary Gold Driver)**
- Current 10Y TIPS Yield: {fmt_num(metrics.get('real_yield_current'))}%
- 30-day change: {fmt_pct(metrics.get('real_yield_momentum_30d'))}
- 90-day change: {fmt_pct(metrics.get('real_yield_momentum_90d'))}
- Direction: {'Falling (bullish for gold)' if metrics.get('real_yield_momentum_30d', 0) < 0 else 'Rising (bearish for gold)'}

**US Dollar Strength**
- Current DXY: {fmt_num(metrics.get('dxy_current'))}
- 30-day change: {fmt_pct(metrics.get('dxy_momentum_30d'))}
- 90-day change: {fmt_pct(metrics.get('dxy_momentum_90d'))}
- Direction: {'Weakening (bullish for gold)' if metrics.get('dxy_momentum_30d', 0) < 0 else 'Strengthening (bearish for gold)'}

**Market Sentiment**
- VIX: {fmt_num(metrics.get('vix_current'))}
- Geopolitical Risk Index: {fmt_num(metrics.get('gpr_current'), 1)}
- Risk environment: {'Elevated' if metrics.get('vix_current', 0) > 20 else 'Normal'}

**Central Bank Activity**
- Latest quarter: {cb_data.get('quarter', 'N/A')}
- Net purchases: {fmt_num(cb_data.get('cb_net_tonnes'), 1)} tonnes
- Data freshness: {cb_data.get('days_old', 'N/A')} days old {'⚠️ STALE' if cb_data.get('is_stale') else '✓'}
- Context: {'Strong buying (>250t)' if cb_data.get('cb_net_tonnes', 0) > 250 else 'Moderate buying'}

### Valuation Metrics

**Gold Price**
- Spot: ${fmt_num(metrics.get('gold_spot_current'))}
- Real (inflation-adjusted): ${fmt_num(metrics.get('real_gold_price_current'))}
- Real gold z-score (5Y): {fmt_num(metrics.get('real_gold_zscore'))}
  * Z-score interpretation: {'Overvalued' if metrics.get('real_gold_zscore', 0) > 1.0 else 'Undervalued' if metrics.get('real_gold_zscore', 0) < -1.0 else 'Fair value'}

**Relative Performance**
- Gold/S&P 500 ratio: {fmt_num(metrics.get('gold_sp_ratio'), 4)}
- 30-day gold return: {fmt_pct(metrics.get('gold_spot_momentum_30d'))}
- Trend: {'Gold outperforming stocks' if metrics.get('gold_spot_momentum_30d', 0) > 0 else 'Stocks outperforming gold'}

### Regime Score: {regime_score['score']} ({regime_score['assessment']})

**Components:**
"""
        
        # Add regime components
        for component, weight, icon in regime_score['components']:
            summary += f"\n{icon} {component}: {weight:+.1f}"
        
        summary += f"""

**Interpretation:** {regime_score['conviction']}
**Suggested action:** {regime_score['action']}

### Data Quality
- Data window: {metrics.get('data_days', 'N/A')} days
- Period: {metrics.get('data_start_date')} to {metrics.get('data_end_date')}
"""
        
        return summary
    
    def _build_prompt(self, data_summary: str, regime_score: Dict) -> str:
        """Build the prompt for OpenAI."""
        
        return f"""You are analyzing gold market data to inform a monthly position decision. Focus on SUSTAINED trend changes (not daily noise) and regime implications.

{data_summary}

## Your Task

Provide a concise, actionable analysis structured as:

**1. What Changed (2-3 sentences)**
- Identify the most significant trend shifts in the past 30 days
- Note any correlation anomalies (e.g., gold rallying despite rising yields)
- Focus on regime-level changes, not daily volatility

**2. Why It Matters (2-3 sentences)**
- Explain the macro regime implications
- Connect to gold's fundamental drivers (real yields, USD, risk sentiment, CB buying)
- Distinguish between cyclical noise and structural shifts

**3. Position Implications (2-3 sentences)**
- State conviction level based on the regime score ({regime_score['score']})
- Suggest position action: {regime_score['action']}
- Note any key risks or catalysts to monitor

## Style Guidelines
- Be direct and avoid hedging language
- Use specific numbers from the data
- Write for an experienced investor who understands gold fundamentals
- Focus on what's actionable for a monthly rebalancing decision
- If signals are mixed, explain the conflict clearly

Keep the entire response to 3-5 paragraphs (~300-400 words).
"""
    
    def _fallback_narrative(self, metrics: Dict, regime_score: Dict) -> str:
        """
        Generate a simple narrative if AI synthesis fails.
        
        This is a basic fallback - less insightful but functional.
        """
        
        ry_change = metrics.get('real_yield_momentum_30d', 0)
        dxy_change = metrics.get('dxy_momentum_30d', 0)
        gold_change = metrics.get('gold_spot_momentum_30d', 0)
        
        narrative = f"""## Executive Summary

**Market Regime:** {regime_score['assessment']} (Score: {regime_score['score']})

Over the past 30 days, real yields have {'fallen' if ry_change < 0 else 'risen'} by {abs(ry_change)*100:.1f}%, \
while the US dollar has {'weakened' if dxy_change < 0 else 'strengthened'} by {abs(dxy_change)*100:.1f}%. \
Gold spot prices {'increased' if gold_change > 0 else 'decreased'} by {abs(gold_change)*100:.1f}% during this period.

**Key Drivers:**
"""
        
        for component, weight, icon in regime_score['components']:
            narrative += f"\n{icon} {component} ({weight:+.1f})"
        
        narrative += f"""

**Position Recommendation:** {regime_score['action']}

**Conviction Level:** {regime_score['conviction']}

Note: This is a fallback analysis. For more detailed insights, check OpenAI API configuration.
"""
        
        return narrative


def test_synthesizer():
    """Test AI synthesis with sample data."""
    import os
    from dotenv import load_dotenv
    import numpy as np
    
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Sample data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=90, freq='D')
    df = pd.DataFrame({
        'gold_spot': 2000 + np.random.randn(90) * 50,
        'real_yield': 1.5 + np.random.randn(90) * 0.2,
        'dxy': 103 + np.random.randn(90) * 2,
    }, index=dates)
    
    metrics = {
        'real_yield_current': 1.75,
        'real_yield_momentum_30d': -0.05,
        'real_yield_momentum_90d': -0.08,
        'dxy_current': 102.5,
        'dxy_momentum_30d': -0.02,
        'dxy_momentum_90d': -0.03,
        'gold_spot_current': 2650.0,
        'gold_spot_momentum_30d': 0.03,
        'real_gold_price_current': 2100.0,
        'real_gold_zscore': 0.8,
        'gold_sp_ratio': 0.47,
        'vix_current': 15.2,
        'gpr_current': 125.0,
        'data_start_date': dates[0],
        'data_end_date': dates[-1],
        'data_days': 90
    }
    
    regime_score = {
        'score': 2.75,
        'assessment': 'MILDLY BULLISH',
        'conviction': 'Moderate conviction',
        'action': 'Maintain or slightly increase position',
        'components': [
            ('Real yields falling', +1, '✅'),
            ('USD weakening', +0.75, '✅'),
            ('Strong CB buying >250t', +2, '✅'),
            ('Elevated valuation', 0, '⚠️')
        ]
    }
    
    cb_data = {
        'quarter': 'Q1_2025',
        'cb_net_tonnes': 290,
        'days_old': 45,
        'is_stale': False
    }
    
    synthesizer = AISynthesizer(api_key)
    narrative = synthesizer.synthesize_narrative(metrics, regime_score, cb_data, df)
    
    print("\n" + "="*60)
    print("GENERATED NARRATIVE:")
    print("="*60)
    print(narrative)
    print("="*60)


if __name__ == "__main__":
    test_synthesizer()

