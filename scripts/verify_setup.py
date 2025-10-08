#!/usr/bin/env python3
"""
Setup Verification Script

Checks that all components are properly configured and working.

Usage:
    python scripts/verify_setup.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro}")
        print(f"   Required: Python 3.10+")
        return False


def check_dependencies():
    """Check required packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required = [
        'fredapi',
        'yfinance',
        'pandas',
        'numpy',
        'openai',
        'requests',
        'bs4',
        'matplotlib',
        'dotenv'
    ]
    
    missing = []
    
    for package in required:
        try:
            if package == 'bs4':
                __import__('bs4')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_env_file():
    """Check .env file exists and has keys."""
    print("\n🔒 Checking environment configuration...")
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print(f"   ❌ .env file not found")
        print(f"   Create it: cp .env.example .env")
        return False
    
    print(f"   ✅ .env file exists")
    
    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    fred_key = os.getenv('FRED_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    issues = []
    
    if not fred_key or fred_key == 'your_fred_api_key_here':
        print(f"   ⚠️  FRED_API_KEY not configured")
        issues.append('FRED_API_KEY')
    else:
        print(f"   ✅ FRED_API_KEY configured")
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print(f"   ⚠️  OPENAI_API_KEY not configured")
        issues.append('OPENAI_API_KEY')
    else:
        print(f"   ✅ OPENAI_API_KEY configured")
    
    if issues:
        print(f"\n   Edit .env and add your actual API keys:")
        for key in issues:
            print(f"   - {key}")
        return False
    
    return True


def check_data_files():
    """Check data directory structure."""
    print("\n📁 Checking data files...")
    
    data_dir = Path('data')
    
    if not data_dir.exists():
        print(f"   ⚠️  data/ directory not found - will be created")
        data_dir.mkdir()
    
    cb_file = data_dir / 'cb_reserves.csv'
    
    if cb_file.exists():
        print(f"   ✅ Central bank data file exists")
        
        # Check it's readable
        try:
            import pandas as pd
            df = pd.read_csv(cb_file)
            print(f"      {len(df)} quarters of data")
        except Exception as e:
            print(f"   ⚠️  Error reading CB data: {e}")
    else:
        print(f"   ⚠️  Central bank data file not found")
        print(f"   Initialize it: python scripts/manual_cb_update.py --init")
    
    return True


def check_reports_dir():
    """Check reports directory."""
    print("\n📄 Checking reports directory...")
    
    reports_dir = Path('reports')
    
    if not reports_dir.exists():
        print(f"   ⚠️  reports/ directory not found - will be created")
        reports_dir.mkdir()
    else:
        print(f"   ✅ reports/ directory exists")
        
        # Check for existing reports
        reports = list(reports_dir.glob('*.md'))
        if reports:
            print(f"      Found {len(reports)} existing report(s)")
    
    return True


def test_fred_connection():
    """Test FRED API connection."""
    print("\n🌐 Testing FRED API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from fredapi import Fred
        
        fred_key = os.getenv('FRED_API_KEY')
        if not fred_key or fred_key == 'your_fred_api_key_here':
            print(f"   ⚠️  Skipping (API key not configured)")
            return False
        
        fred = Fred(api_key=fred_key)
        
        # Test with a simple series
        data = fred.get_series('DFII10', observation_start='2025-01-01', observation_end='2025-01-31')
        
        if not data.empty:
            print(f"   ✅ FRED API connected successfully")
            print(f"      Retrieved {len(data)} data points")
            return True
        else:
            print(f"   ⚠️  FRED API returned no data")
            return False
            
    except Exception as e:
        print(f"   ❌ FRED API error: {e}")
        print(f"   Check your API key at: https://fred.stlouisfed.org/")
        return False


def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from openai import OpenAI
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or openai_key == 'your_openai_api_key_here':
            print(f"   ⚠️  Skipping (API key not configured)")
            return False
        
        client = OpenAI(api_key=openai_key)
        
        # Test with a minimal request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10
        )
        
        if response.choices:
            print(f"   ✅ OpenAI API connected successfully")
            print(f"      Model: {response.model}")
            return True
        else:
            print(f"   ⚠️  OpenAI API returned no response")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        print(f"   Check your API key and billing at: https://platform.openai.com/")
        return False


def main():
    """Run all verification checks."""
    print("="*70)
    print("🔍 GOLD MONITOR - Setup Verification")
    print("="*70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
        ("Data Files", check_data_files),
        ("Reports Directory", check_reports_dir),
    ]
    
    results = []
    
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    # Optional API tests
    print("\n" + "="*70)
    print("🔌 Testing API Connections (Optional)")
    print("="*70)
    
    fred_ok = test_fred_connection()
    openai_ok = test_openai_connection()
    
    # Summary
    print("\n" + "="*70)
    print("📋 VERIFICATION SUMMARY")
    print("="*70)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n🔌 API Connections:")
    print(f"{'✅' if fred_ok else '⚠️ '} FRED API")
    print(f"{'✅' if openai_ok else '⚠️ '} OpenAI API")
    
    print("\n" + "="*70)
    
    if all_passed and fred_ok and openai_ok:
        print("🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to generate reports:")
        print("   python scripts/run_monthly_report.py")
    elif all_passed:
        print("⚠️  SETUP INCOMPLETE")
        print("\nConfigure your API keys in .env and try again:")
        print("   nano .env")
    else:
        print("❌ SETUP ISSUES DETECTED")
        print("\nFix the issues above and run this script again:")
        print("   python scripts/verify_setup.py")
    
    print("="*70 + "\n")
    
    return all_passed and fred_ok and openai_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

