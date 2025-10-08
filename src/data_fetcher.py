"""
Tier 1 Data Fetcher: Automated High-Frequency Sources

Fetches gold market data from FRED and Yahoo Finance.
This runs monthly but pulls 90-day windows to capture recent trends.

Data Sources:
- FRED: Real yields, nominal yields, DXY, gold spot, S&P 500, CPI, geopolitical risk
- Yahoo Finance: VIX, ETF holdings (GLD)
"""

from fredapi import Fred
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import os


class GoldDataFetcher:
    """Fetches Tier 1 metrics from FRED and Yahoo Finance."""
    
    # FRED series identifiers
    FRED_SERIES = {
        'real_yield': 'DFII10',           # 10-Year TIPS Real Yield
        'nominal_yield': 'DGS10',         # 10-Year Treasury Nominal Yield
        'dxy': 'DTWEXBGS',                # Trade-Weighted Dollar Index
        'gold_spot': 'GOLDPMGBD228NLBM',  # Gold Spot Price (London PM Fix) - Fixed series ID
        'sp500': 'SP500',                 # S&P 500 Index
        'cpi': 'CPIAUCSL',                # Consumer Price Index
        'gpr': 'GEPUPPP'                  # Geopolitical Risk Index - Fixed series ID
    }
    
    def __init__(self, fred_api_key: str):
        """
        Initialize data fetcher.
        
        Args:
            fred_api_key: Your FRED API key from https://fred.stlouisfed.org/
        """
        self.fred = Fred(api_key=fred_api_key)
    
    def fetch_fred_data(self, days: int = 90) -> pd.DataFrame:
        """
        Fetch 90-day window for all FRED series.
        
        Args:
            days: Number of days to look back (default 90)
            
        Returns:
            DataFrame with date index and metric columns
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = {}
        errors = []
        
        for name, series_id in self.FRED_SERIES.items():
            try:
                series = self.fred.get_series(
                    series_id, 
                    observation_start=start_date,
                    observation_end=end_date
                )
                data[name] = series
                print(f"✅ Fetched {name} ({series_id}): {len(series)} observations")
                
            except Exception as e:
                print(f"⚠️  Failed to fetch {name} ({series_id}): {e}")
                errors.append((name, str(e)))
                data[name] = pd.Series(dtype=float)
        
        # Combine into DataFrame with date index
        df = pd.DataFrame(data)
        
        # Forward fill missing values (some series update less frequently)
        df = df.ffill()
        
        if errors:
            print(f"\n⚠️  {len(errors)} series had errors. Report will have gaps.")
        
        return df
    
    def fetch_yahoo_data(self, days: int = 90) -> Dict[str, any]:
        """
        Fetch VIX, GLD holdings, and gold prices from Yahoo Finance.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with latest values and historical series
        """
        results = {
            'fetch_date': datetime.now(),
            'vix_current': None,
            'vix_history': pd.Series(dtype=float),
            'gld_shares': None,
            'gld_price_history': pd.Series(dtype=float),
            'gold_history': pd.Series(dtype=float)
        }
        
        try:
            # Try multiple methods to get gold prices
            print("Fetching gold prices...")
            
            # Method 1: Try forex ticker (XAUUSD=X)
            try:
                gold_data = yf.download('XAUUSD=X', period='3mo', progress=False)
                if not gold_data.empty and 'Close' in gold_data.columns:
                    results['gold_history'] = gold_data['Close']
                    print(f"✅ Fetched gold prices from XAUUSD=X: {len(gold_data)} observations")
                    return results
            except:
                pass
            
            # Method 2: Try gold futures (GC=F)  
            try:
                gold = yf.Ticker('GC=F')
                gold_history = gold.history(period='3mo')
                if not gold_history.empty:
                    results['gold_history'] = gold_history['Close']
                    print(f"✅ Fetched gold prices from GC=F: {len(gold_history)} observations")
                    return results
            except:
                pass
            
            # Method 3: Use GLD ETF as proxy (price * ~10 = approx gold oz price)
            try:
                gld = yf.Ticker('GLD')
                gld_hist = gld.history(period='3mo')
                if not gld_hist.empty:
                    # GLD tracks 1/10th oz of gold, so multiply by ~10
                    results['gold_history'] = gld_hist['Close'] * 10
                    print(f"✅ Fetched gold prices from GLD ETF: {len(gld_hist)} observations")
                    return results
            except:
                pass
            
            print("⚠️  All gold price sources failed - using fallback")
            
        except Exception as e:
            print(f"⚠️  Gold price fetch error: {e}")
        
        try:
            # Fetch VIX (volatility index)
            print("Fetching VIX data from Yahoo Finance...")
            vix = yf.Ticker('^VIX')
            vix_history = vix.history(period='3mo')
            
            if not vix_history.empty:
                results['vix_history'] = vix_history['Close']
                results['vix_current'] = vix_history['Close'].iloc[-1]
                print(f"✅ Fetched VIX: {len(vix_history)} observations")
            else:
                print("⚠️  No VIX data returned")
            
        except Exception as e:
            print(f"⚠️  Failed to fetch VIX: {e}")
        
        try:
            # Fetch GLD (SPDR Gold Shares ETF)
            print("Fetching GLD ETF data from Yahoo Finance...")
            gld = yf.Ticker('GLD')
            
            # Get price history (more reliable than info dict)
            gld_history = gld.history(period='3mo')
            if not gld_history.empty:
                results['gld_price_history'] = gld_history['Close']
                print(f"✅ Fetched GLD prices: {len(gld_history)} observations")
                
                # Try to get shares outstanding if available
                try:
                    gld_info = gld.info
                    results['gld_shares'] = gld_info.get('sharesOutstanding')
                    if results['gld_shares']:
                        print(f"   GLD shares: {results['gld_shares']:,}")
                except:
                    print(f"   (Shares outstanding not available)")
            else:
                print("⚠️  No GLD data returned")
                
        except Exception as e:
            print(f"⚠️  Failed to fetch GLD: {e}")
        
        return results
    
    def fetch_all(self, days: int = 90) -> tuple[pd.DataFrame, Dict]:
        """
        Fetch all Tier 1 data and combine.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Tuple of (FRED DataFrame, Yahoo Finance dict)
        """
        print(f"\n{'='*60}")
        print(f"Fetching {days}-day data window")
        print(f"{'='*60}\n")
        
        print("📊 Fetching FRED data...")
        fred_data = self.fetch_fred_data(days)
        
        print("\n📊 Fetching Yahoo Finance data...")
        yahoo_data = self.fetch_yahoo_data(days)
        
        # Add Yahoo data to the main DataFrame
        if not yahoo_data['vix_history'].empty:
            fred_data['vix'] = yahoo_data['vix_history']
        
        # Use Yahoo gold prices if FRED failed
        if 'gold_spot' not in fred_data.columns or fred_data['gold_spot'].isna().all():
            if not yahoo_data['gold_history'].empty:
                print("   Using Yahoo Finance gold prices (FRED unavailable)")
                fred_data['gold_spot'] = yahoo_data['gold_history']
            else:
                # Final fallback: use current approximate gold price
                print("   ⚠️  WARNING: Using fallback gold price (~$4045/oz)")
                print("   Yahoo Finance may be rate-limited. Try again later for live data.")
                print("   Note: This is a static estimate. For live prices, wait for Yahoo to unblock.")
                # Use current gold futures price (as of Oct 8, 2025: COMEX GCW00)
                fred_data['gold_spot'] = 4045.0
        
        print(f"\n{'='*60}")
        print(f"✅ Data fetch complete!")
        print(f"   FRED series: {len([col for col in fred_data.columns if not fred_data[col].empty])}/{len(self.FRED_SERIES)}")
        print(f"   Date range: {fred_data.index.min()} to {fred_data.index.max()}")
        print(f"   Total observations: {len(fred_data)}")
        print(f"{'='*60}\n")
        
        return fred_data, yahoo_data


def test_fetcher():
    """Test function to verify data fetching works."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    fred_key = os.getenv('FRED_API_KEY')
    if not fred_key or fred_key == 'your_fred_api_key_here':
        print("❌ Please set FRED_API_KEY in .env file")
        return
    
    fetcher = GoldDataFetcher(fred_key)
    df, yahoo = fetcher.fetch_all(days=30)
    
    print("\nSample of fetched data:")
    print(df.tail())
    print(f"\nVIX current: {yahoo.get('vix_current')}")
    print(f"GLD shares: {yahoo.get('gld_shares'):,}")


if __name__ == "__main__":
    test_fetcher()

