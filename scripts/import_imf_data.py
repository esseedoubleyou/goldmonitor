#!/usr/bin/env python3
"""
IMF Data Import Helper

Converts IMF central bank gold data into the format needed for Gold Monitor.

Usage:
    python scripts/import_imf_data.py <path_to_imf_csv>
"""

import sys
import pandas as pd
from pathlib import Path

def preview_csv(filepath):
    """Preview the CSV structure."""
    print(f"\n📊 Previewing: {filepath}\n")
    
    try:
        # Read first few rows
        df = pd.read_csv(filepath, nrows=5)
        
        print("Columns found:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        print(f"\nTotal rows in file: {len(pd.read_csv(filepath))}")
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_imf_data.py <path_to_csv>")
        print("\nThis will preview your IMF data and help convert it.")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    preview_csv(csv_path)
    
    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("1. Share the column names and date format with me")
    print("2. I'll customize this script to import your data")
    print("3. Run: python scripts/import_imf_data.py <your_csv>")
    print("")

if __name__ == "__main__":
    main()
