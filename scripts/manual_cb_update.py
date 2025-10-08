#!/usr/bin/env python3
"""
Manual Central Bank Data Update Helper

Interactive script to help you add central bank purchase data
from WGC quarterly reports.

Usage:
    python scripts/manual_cb_update.py           # Interactive mode
    python scripts/manual_cb_update.py --init    # Initialize CSV with sample data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import argparse
import pandas as pd
from datetime import datetime
from cb_monitor import CentralBankMonitor


def initialize_cb_data():
    """Initialize CB data file with sample data."""
    print("\n🔧 Initializing Central Bank Data File")
    print("="*60)
    
    monitor = CentralBankMonitor()
    monitor.initialize_csv(sample_data=True)
    
    print("\n✅ Initialization complete!")
    print(f"   File: {monitor.DATA_FILE}")
    print(f"\n⚠️  Sample data included - replace with actual WGC figures!")
    print(f"   Run: python scripts/manual_cb_update.py")
    print("")


def interactive_update():
    """Interactive prompts to add new CB data."""
    print("\n📝 Central Bank Data Update - Interactive Mode")
    print("="*60)
    
    monitor = CentralBankMonitor()
    
    # Check if file exists
    if not monitor.DATA_FILE.exists():
        print("❌ Data file not found!")
        print(f"   Initialize first with: python {sys.argv[0]} --init")
        return False
    
    # Show current data
    current = monitor.get_latest_data()
    
    if current.get('status') in ['current', 'stale']:
        print(f"\nCurrent data:")
        print(f"  Quarter: {current['quarter']}")
        print(f"  Net tonnes: {current['cb_net_tonnes']:.1f}")
        print(f"  Last updated: {current['validated_date']} ({current['days_old']} days ago)")
    
    print("\n" + "-"*60)
    print("Adding new quarterly data")
    print("-"*60)
    
    # Prompt for quarter
    print("\nEnter quarter in format: Q1_2025, Q2_2025, etc.")
    quarter = input("Quarter: ").strip()
    
    # Validate format
    import re
    if not re.match(r'Q[1-4]_\d{4}', quarter):
        print("❌ Invalid format. Use: Q1_2025")
        return False
    
    # Prompt for tonnes
    print("\nEnter net central bank purchases in tonnes")
    print("(Find this in WGC Gold Demand Trends report, 'Central Banks' row)")
    
    try:
        tonnes_str = input("Net tonnes: ").strip()
        tonnes = float(tonnes_str)
    except ValueError:
        print("❌ Invalid number")
        return False
    
    # Source
    source = input("Source (default: WGC): ").strip() or "WGC"
    
    # Date
    validated_date = datetime.now().date()
    
    # Confirm
    print("\n" + "="*60)
    print("Confirm new entry:")
    print(f"  Quarter: {quarter}")
    print(f"  Net tonnes: {tonnes:.1f}")
    print(f"  Source: {source}")
    print(f"  Date: {validated_date}")
    print("="*60)
    
    confirm = input("\nAdd this entry? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled")
        return False
    
    # Append to CSV
    try:
        df = pd.read_csv(monitor.DATA_FILE)
        
        # Check for duplicates
        if quarter in df['quarter'].values:
            print(f"\n⚠️  Quarter {quarter} already exists!")
            overwrite = input("Overwrite? (y/n): ").strip().lower()
            
            if overwrite == 'y':
                df = df[df['quarter'] != quarter]
            else:
                print("❌ Cancelled")
                return False
        
        # Add new row
        new_row = pd.DataFrame({
            'quarter': [quarter],
            'cb_net_tonnes': [tonnes],
            'source': [source],
            'validated_date': [validated_date]
        })
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(monitor.DATA_FILE, index=False)
        
        print("\n✅ Data updated successfully!")
        print(f"   File: {monitor.DATA_FILE}")
        print(f"\nYou can now generate your monthly report:")
        print(f"   python scripts/run_monthly_report.py")
        print("")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error updating file: {e}")
        return False


def show_current_data():
    """Display current CB data."""
    print("\n📊 Current Central Bank Data")
    print("="*60)
    
    monitor = CentralBankMonitor()
    
    if not monitor.DATA_FILE.exists():
        print("❌ Data file not found!")
        print(f"   Initialize first with: python {sys.argv[0]} --init")
        return
    
    try:
        df = pd.read_csv(monitor.DATA_FILE)
        
        print(f"\nData file: {monitor.DATA_FILE}")
        print(f"Total quarters: {len(df)}\n")
        print(df.to_string(index=False))
        
        # Show latest
        latest = monitor.get_latest_data()
        
        if latest.get('status') in ['current', 'stale']:
            print(f"\n{'='*60}")
            print(f"Latest entry:")
            print(f"  Quarter: {latest['quarter']}")
            print(f"  Net tonnes: {latest['cb_net_tonnes']:.1f}")
            print(f"  Days old: {latest['days_old']}")
            
            if latest.get('is_stale'):
                print(f"\n⚠️  Data is stale (>{90} days old)")
                print(f"   Check for new WGC report at:")
                print(f"   https://www.gold.org/goldhub/research/gold-demand-trends")
        
        print("")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")


def main():
    """Parse arguments and run appropriate function."""
    
    parser = argparse.ArgumentParser(
        description='Manual central bank data update helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize data file with samples
  python scripts/manual_cb_update.py --init
  
  # Add new quarterly data (interactive)
  python scripts/manual_cb_update.py
  
  # View current data
  python scripts/manual_cb_update.py --show
        """
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize CB data CSV with sample data'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current CB data'
    )
    
    args = parser.parse_args()
    
    if args.init:
        initialize_cb_data()
    elif args.show:
        show_current_data()
    else:
        # Interactive update
        success = interactive_update()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

