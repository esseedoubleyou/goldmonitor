#!/usr/bin/env python3
"""
Gold Monitor - Monthly Report Generator

Main orchestrator script that:
1. Fetches Tier 1 data (FRED + Yahoo Finance)
2. Checks for new WGC reports (Tier 2 detection)
3. Loads central bank data from CSV
4. Calculates derived metrics
5. Generates AI-synthesized narrative
6. Assembles and saves markdown report
7. Appends raw data to history

Usage:
    python scripts/run_monthly_report.py [options]

Options:
    --no-charts     Skip chart generation
    --no-ai         Skip AI synthesis (use fallback)
    --days N        Fetch N days of data (default: 90)
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import argparse
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

from data_fetcher import GoldDataFetcher
from cb_monitor import CentralBankMonitor
from metrics_calculator import MetricsCalculator
from ai_synthesizer import AISynthesizer
from report_generator import ReportGenerator


def load_historical_data() -> pd.DataFrame:
    """
    Load historical metrics data if it exists.
    
    Returns:
        DataFrame with historical data, or empty DataFrame
    """
    history_file = Path('data/gold_metrics_history.csv')
    
    if history_file.exists():
        try:
            df = pd.read_csv(history_file, index_col=0, parse_dates=True)
            print(f"✅ Loaded {len(df)} rows of historical data")
            return df
        except Exception as e:
            print(f"⚠️  Could not load historical data: {e}")
            return pd.DataFrame()
    else:
        print(f"ℹ️  No historical data file found (will be created)")
        return pd.DataFrame()


def save_historical_data(df: pd.DataFrame):
    """
    Append current data to historical CSV.
    
    Args:
        df: DataFrame with current data
    """
    history_file = Path('data/gold_metrics_history.csv')
    history_file.parent.mkdir(exist_ok=True)
    
    # Load existing
    if history_file.exists():
        existing = pd.read_csv(history_file, index_col=0, parse_dates=True)
        combined = pd.concat([existing, df]).drop_duplicates()
    else:
        combined = df
    
    # Sort by date and save
    combined = combined.sort_index()
    combined.to_csv(history_file)
    
    print(f"✅ Saved {len(combined)} rows to {history_file}")


def run_monthly_report(
    days: int = 90,
    include_charts: bool = True,
    use_ai: bool = True
):
    """
    Main execution function.
    
    Args:
        days: Number of days to fetch
        include_charts: Whether to generate charts
        use_ai: Whether to use AI synthesis
    """
    
    print("\n" + "="*70)
    print("🏆 GOLD MARKET MONITOR - Monthly Report Generator")
    print("="*70 + "\n")
    
    # Load environment variables
    load_dotenv()
    
    fred_key = os.getenv('FRED_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    # Validate API keys
    if not fred_key or fred_key == 'your_fred_api_key_here':
        print("❌ FRED_API_KEY not configured in .env file")
        print("   Get your key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return False
    
    if use_ai and (not openai_key or openai_key == 'your_openai_api_key_here'):
        print("⚠️  OpenAI API key not configured - will use fallback narrative")
        use_ai = False
    
    # Setup email config for CB monitor
    email_config = None
    if os.getenv('EMAIL_ENABLED', 'false').lower() == 'true':
        email_config = {
            'enabled': True,
            'from': os.getenv('EMAIL_FROM'),
            'to': os.getenv('EMAIL_TO'),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', 587)),
            'password': os.getenv('EMAIL_PASSWORD')
        }
    
    try:
        # ===== STEP 1: Fetch Tier 1 Data =====
        print("STEP 1: Fetching market data (FRED + Yahoo Finance)")
        print("-" * 70)
        
        fetcher = GoldDataFetcher(fred_key)
        df, yahoo_data = fetcher.fetch_all(days=days)
        
        if df.empty:
            print("❌ No data fetched - cannot generate report")
            return False
        
        # ===== STEP 2: Check for New WGC Reports =====
        print("\nSTEP 2: Checking for new central bank reports")
        print("-" * 70)
        
        monitor = CentralBankMonitor(email_config)
        new_report = monitor.check_for_new_report()
        
        if new_report:
            print(f"🚨 Action required: New WGC report for {new_report}")
            print(f"   Update data with: python scripts/manual_cb_update.py")
        
        # ===== STEP 3: Load Central Bank Data =====
        print("\nSTEP 3: Loading central bank data")
        print("-" * 70)
        
        cb_data = monitor.get_latest_data()
        
        if cb_data.get('status') == 'missing':
            print("⚠️  No central bank data found")
            print(f"   Initialize with: python scripts/manual_cb_update.py --init")
        elif cb_data.get('status') == 'current':
            print(f"✅ CB data: {cb_data['quarter']} - {cb_data['cb_net_tonnes']:.1f} tonnes")
        elif cb_data.get('status') == 'stale':
            print(f"⚠️  CB data is {cb_data['days_old']} days old")
        
        # ===== STEP 4: Calculate Metrics =====
        print("\nSTEP 4: Calculating derived metrics")
        print("-" * 70)
        
        history_df = load_historical_data()
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(df, yahoo_data, history_df)
        
        print(f"✅ Calculated {len(metrics)} metrics")
        print(f"   Real gold price: ${metrics.get('real_gold_price_current', 0):.2f}")
        print(f"   Gold spot: ${metrics.get('gold_spot_current', 0):.2f}")
        
        # ===== STEP 5: Calculate Regime Score =====
        print("\nSTEP 5: Calculating regime score")
        print("-" * 70)
        
        regime_score = calculator.calculate_regime_score(metrics, cb_data)
        
        print(f"✅ Regime Score: {regime_score['score']:.1f}")
        print(f"   Assessment: {regime_score['assessment']}")
        print(f"   Action: {regime_score['action']}")
        
        # ===== STEP 6: Generate AI Narrative =====
        print("\nSTEP 6: Generating narrative synthesis")
        print("-" * 70)
        
        if use_ai:
            try:
                synthesizer = AISynthesizer(openai_key)
                ai_narrative = synthesizer.synthesize_narrative(
                    metrics, regime_score, cb_data, df
                )
            except Exception as e:
                print(f"⚠️  AI synthesis failed: {e}")
                print("   Using fallback narrative")
                synthesizer = AISynthesizer("dummy")
                ai_narrative = synthesizer._fallback_narrative(metrics, regime_score)
        else:
            print("ℹ️  Using fallback narrative (AI disabled)")
            synthesizer = AISynthesizer("dummy")
            ai_narrative = synthesizer._fallback_narrative(metrics, regime_score)
        
        # ===== STEP 7: Generate Report =====
        print("\nSTEP 7: Generating markdown report")
        print("-" * 70)
        
        generator = ReportGenerator(include_charts=include_charts)
        report_content = generator.generate_report(
            metrics, regime_score, cb_data, ai_narrative, df
        )
        
        report_path = generator.save_report(report_content)
        
        # ===== STEP 8: Save Historical Data =====
        print("\nSTEP 8: Updating historical data")
        print("-" * 70)
        
        save_historical_data(df)
        
        # ===== SUCCESS =====
        print("\n" + "="*70)
        print("✅ REPORT GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📄 Report: {report_path}")
        print(f"📊 Charts: {generator.CHART_DIR if include_charts else 'Disabled'}")
        print(f"💾 History: data/gold_metrics_history.csv")
        print(f"\nNext steps:")
        print(f"  1. Review report: open {report_path}")
        print(f"  2. Check for WGC updates quarterly")
        print(f"  3. Next run: First of next month")
        print("")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Report generation cancelled by user")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Parse arguments and run report generation."""
    
    parser = argparse.ArgumentParser(
        description='Generate monthly gold market report',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=90,
        help='Number of days to fetch (default: 90)'
    )
    
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Skip chart generation'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI synthesis (use fallback narrative)'
    )
    
    args = parser.parse_args()
    
    success = run_monthly_report(
        days=args.days,
        include_charts=not args.no_charts,
        use_ai=not args.no_ai
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

