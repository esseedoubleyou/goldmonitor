"""
Metrics Calculator: Derived Indicators

Calculates derived metrics from raw data:
- Real gold price (CPI-adjusted)
- Z-scores (5-year rolling window)
- Momentum indicators (30/60/90-day)
- Gold/S&P ratio
- ETF flow momentum

These transform raw data into actionable signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime


class MetricsCalculator:
    """Calculates derived indicators from raw data."""
    
    @staticmethod
    def calculate_real_gold_price(df: pd.DataFrame) -> pd.Series:
        """
        Real gold price = Gold spot / CPI (normalized to 100).
        
        This removes inflation distortion to show gold's purchasing power.
        
        Args:
            df: DataFrame with 'gold_spot' and 'cpi' columns
            
        Returns:
            Series of inflation-adjusted gold prices
        """
        if 'gold_spot' not in df.columns or 'cpi' not in df.columns:
            return pd.Series(dtype=float, name='real_gold_price')
        
        # Normalize CPI to 100 at earliest date
        cpi_normalized = (df['cpi'] / df['cpi'].iloc[0]) * 100
        
        # Adjust gold price by inflation
        real_gold = df['gold_spot'] / (cpi_normalized / 100)
        
        return real_gold
    
    @staticmethod
    def calculate_zscore(series: pd.Series, window: int = 1260, min_periods: int = 252) -> pd.Series:
        """
        Calculate rolling z-score.
        
        Z-score = (value - rolling_mean) / rolling_std
        
        Default window = 1260 trading days ≈ 5 years
        Min periods = 252 trading days ≈ 1 year
        
        Args:
            series: Time series data
            window: Rolling window size (days)
            min_periods: Minimum observations required
            
        Returns:
            Series of z-scores
        """
        rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
        rolling_std = series.rolling(window=window, min_periods=min_periods).std()
        
        # Avoid division by zero
        rolling_std = rolling_std.replace(0, np.nan)
        
        zscore = (series - rolling_mean) / rolling_std
        
        return zscore
    
    @staticmethod
    def calculate_momentum(series: pd.Series, days: int = 30) -> Optional[float]:
        """
        Calculate momentum as % change over N days.
        
        Returns: (current / N_days_ago) - 1
        
        Args:
            series: Time series data
            days: Lookback period
            
        Returns:
            Percentage change (e.g., 0.05 = 5% increase), or None if insufficient data
        """
        if len(series) < days:
            return None
        
        # Get values
        current = series.iloc[-1]
        past = series.iloc[-days] if len(series) >= days else series.iloc[0]
        
        if pd.isna(current) or pd.isna(past) or past == 0:
            return None
        
        return (current / past) - 1
    
    @staticmethod
    def calculate_gold_sp_ratio(df: pd.DataFrame) -> pd.Series:
        """
        Gold/S&P 500 ratio - measures relative performance.
        
        Rising ratio = gold outperforming equities (risk-off)
        Falling ratio = equities outperforming (risk-on)
        
        Args:
            df: DataFrame with 'gold_spot' and 'sp500' columns
            
        Returns:
            Series of gold/stock ratio
        """
        if 'gold_spot' not in df.columns or 'sp500' not in df.columns:
            return pd.Series(dtype=float, name='gold_sp_ratio')
        
        return df['gold_spot'] / df['sp500']
    
    @staticmethod
    def calculate_breakeven_inflation(df: pd.DataFrame) -> pd.Series:
        """
        Breakeven inflation = Nominal yield - Real yield
        
        This is the market's inflation expectation.
        
        Args:
            df: DataFrame with 'nominal_yield' and 'real_yield' columns
            
        Returns:
            Series of breakeven inflation rates
        """
        if 'nominal_yield' not in df.columns or 'real_yield' not in df.columns:
            return pd.Series(dtype=float, name='breakeven_inflation')
        
        return df['nominal_yield'] - df['real_yield']
    
    def calculate_all_metrics(
        self, 
        df: pd.DataFrame, 
        yahoo_data: Dict,
        history_df: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Calculate all derived metrics.
        
        Args:
            df: Recent data DataFrame from FRED
            yahoo_data: Yahoo Finance data dict
            history_df: Optional historical data for better z-scores
            
        Returns:
            Dict of metric name -> value or series
        """
        metrics = {}
        
        # Use historical data if available for better z-scores
        full_df = df
        if history_df is not None and not history_df.empty:
            # Combine historical + recent
            full_df = pd.concat([history_df, df]).drop_duplicates()
            full_df = full_df.sort_index()
        
        # ===== Real Gold Price =====
        real_gold = self.calculate_real_gold_price(full_df)
        if not real_gold.empty:
            metrics['real_gold_price_current'] = real_gold.iloc[-1]
            metrics['real_gold_price_series'] = real_gold
            
            # Z-score (requires history)
            real_gold_zscore = self.calculate_zscore(real_gold, window=1260, min_periods=252)
            if not real_gold_zscore.empty and not pd.isna(real_gold_zscore.iloc[-1]):
                metrics['real_gold_zscore'] = real_gold_zscore.iloc[-1]
            else:
                metrics['real_gold_zscore'] = None
                metrics['real_gold_zscore_note'] = 'Insufficient history for 5Y z-score'
        
        # ===== Gold/S&P Ratio =====
        gold_sp = self.calculate_gold_sp_ratio(full_df)
        if not gold_sp.empty:
            metrics['gold_sp_ratio'] = gold_sp.iloc[-1]
            
            # Z-score of ratio
            gold_sp_zscore = self.calculate_zscore(gold_sp, window=1260, min_periods=252)
            if not gold_sp_zscore.empty and not pd.isna(gold_sp_zscore.iloc[-1]):
                metrics['gold_sp_zscore'] = gold_sp_zscore.iloc[-1]
        
        # ===== Breakeven Inflation =====
        breakeven = self.calculate_breakeven_inflation(full_df)
        if not breakeven.empty:
            metrics['breakeven_inflation'] = breakeven.iloc[-1]
        
        # ===== Momentum Calculations =====
        momentum_periods = {
            '30d': 30,
            '60d': 60,
            '90d': 90
        }
        
        momentum_metrics = [
            'real_yield', 
            'dxy', 
            'gold_spot',
            'vix',
            'gpr'
        ]
        
        for metric in momentum_metrics:
            if metric in full_df.columns:
                for period_name, days in momentum_periods.items():
                    momentum = self.calculate_momentum(full_df[metric], days=days)
                    if momentum is not None:
                        metrics[f'{metric}_momentum_{period_name}'] = momentum
        
        # ===== Current Values (Latest) =====
        latest_metrics = [
            'real_yield', 
            'nominal_yield', 
            'dxy', 
            'gold_spot', 
            'sp500',
            'cpi',
            'vix', 
            'gpr'
        ]
        
        for metric in latest_metrics:
            if metric in full_df.columns and not full_df[metric].empty:
                latest_value = full_df[metric].iloc[-1]
                if not pd.isna(latest_value):
                    metrics[f'{metric}_current'] = latest_value
        
        # ===== ETF Flow Proxy =====
        if 'gld_shares' in yahoo_data and yahoo_data['gld_shares']:
            metrics['gld_shares_current'] = yahoo_data['gld_shares']
            
            # Note: For true flow momentum, we'd need historical shares outstanding
            # This would require storing GLD shares over time
            # For now, just capture current value
        
        # ===== Summary Statistics =====
        metrics['data_start_date'] = full_df.index.min()
        metrics['data_end_date'] = full_df.index.max()
        metrics['data_days'] = (full_df.index.max() - full_df.index.min()).days
        metrics['calculation_date'] = datetime.now()
        
        return metrics
    
    def calculate_regime_score(self, metrics: Dict, cb_data: Dict) -> Dict:
        """
        Calculate regime score based on key drivers.
        
        Score = weighted sum of bullish/bearish signals
        
        Weights:
        - Real yields: 2x (primary driver)
        - USD strength: 1.5x
        - Central bank buying: 2x
        - Valuation: -1 if overextended (z-score > 1.0)
        
        Args:
            metrics: Calculated metrics dict
            cb_data: Central bank data dict
            
        Returns:
            Dict with score, components, and interpretation
        """
        score = 0
        components = []
        
        # ===== Real Yields (Weight: 2x) =====
        ry_momentum = metrics.get('real_yield_momentum_30d', 0)
        if ry_momentum is not None:
            if ry_momentum < -0.02:  # Falling >2%
                score += 2
                components.append(('Real yields falling sharply', +2, '✅'))
            elif ry_momentum < 0:
                score += 1
                components.append(('Real yields falling', +1, '✅'))
            elif ry_momentum > 0.02:
                score -= 2
                components.append(('Real yields rising sharply', -2, '❌'))
            elif ry_momentum > 0:
                score -= 1
                components.append(('Real yields rising', -1, '❌'))
            else:
                components.append(('Real yields stable', 0, '➖'))
        
        # ===== USD Strength (Weight: 1.5x) =====
        dxy_momentum = metrics.get('dxy_momentum_30d', 0)
        if dxy_momentum is not None:
            if dxy_momentum < -0.02:
                score += 1.5
                components.append(('USD weakening sharply', +1.5, '✅'))
            elif dxy_momentum < 0:
                score += 0.75
                components.append(('USD weakening', +0.75, '✅'))
            elif dxy_momentum > 0.02:
                score -= 1.5
                components.append(('USD strengthening sharply', -1.5, '❌'))
            elif dxy_momentum > 0:
                score -= 0.75
                components.append(('USD strengthening', -0.75, '❌'))
            else:
                components.append(('USD stable', 0, '➖'))
        
        # ===== Central Bank Buying (Weight: 2x) =====
        if cb_data.get('status') in ['current', 'stale']:
            cb_tonnes = cb_data.get('cb_net_tonnes', 0)
            
            if cb_data.get('is_stale'):
                components.append((f'CB data stale ({cb_data["days_old"]} days)', 0, '⚠️'))
            elif cb_tonnes > 250:
                score += 2
                components.append(('Strong CB buying >250t', +2, '✅'))
            elif cb_tonnes > 100:
                score += 1
                components.append(('Moderate CB buying', +1, '✅'))
            elif cb_tonnes < 0:
                score -= 1
                components.append(('CB selling', -1, '❌'))
            else:
                components.append(('Weak CB buying', 0, '➖'))
        else:
            components.append(('CB data missing', 0, '⚠️'))
        
        # ===== Valuation Risk =====
        zscore = metrics.get('real_gold_zscore')
        if zscore is not None and not pd.isna(zscore):
            if zscore > 1.5:
                score -= 1
                components.append(('Overvalued (z-score >1.5)', -1, '⚠️'))
            elif zscore > 1.0:
                components.append(('Elevated valuation (z-score >1.0)', 0, '⚠️'))
            elif zscore < -1.0:
                components.append(('Undervalued (z-score <-1.0)', 0, '💡'))
        
        # ===== Interpret Score =====
        if score >= 3:
            assessment = 'BULLISH'
            conviction = 'High conviction for long position'
            action = 'Consider increasing allocation'
        elif score >= 1:
            assessment = 'MILDLY BULLISH'
            conviction = 'Moderate conviction'
            action = 'Maintain or slightly increase position'
        elif score <= -3:
            assessment = 'BEARISH'
            conviction = 'High conviction bearish'
            action = 'Consider reducing position'
        elif score <= -1:
            assessment = 'MILDLY BEARISH'
            conviction = 'Caution warranted'
            action = 'Maintain or reduce exposure'
        else:
            assessment = 'NEUTRAL'
            conviction = 'Mixed signals'
            action = 'Hold current position'
        
        return {
            'score': round(score, 2),
            'assessment': assessment,
            'conviction': conviction,
            'action': action,
            'components': components
        }


def test_calculator():
    """Test metrics calculation with sample data."""
    import numpy as np
    
    # Create sample data
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    df = pd.DataFrame({
        'gold_spot': 2000 + np.random.randn(90) * 50,
        'sp500': 4500 + np.random.randn(90) * 100,
        'real_yield': 1.5 + np.random.randn(90) * 0.2,
        'nominal_yield': 4.0 + np.random.randn(90) * 0.2,
        'dxy': 103 + np.random.randn(90) * 2,
        'cpi': 310 + np.arange(90) * 0.1,
        'vix': 15 + np.random.randn(90) * 3,
        'gpr': 120 + np.random.randn(90) * 10
    }, index=dates)
    
    yahoo_data = {
        'gld_shares': 500000000,
        'vix_current': 15.5
    }
    
    cb_data = {
        'quarter': 'Q1_2025',
        'cb_net_tonnes': 290,
        'days_old': 45,
        'is_stale': False,
        'status': 'current'
    }
    
    calc = MetricsCalculator()
    
    print("Calculating metrics...")
    metrics = calc.calculate_all_metrics(df, yahoo_data)
    
    print(f"\nSample metrics:")
    print(f"  Real gold price: ${metrics.get('real_gold_price_current', 0):.2f}")
    print(f"  Gold/S&P ratio: {metrics.get('gold_sp_ratio', 0):.4f}")
    print(f"  Real yield 30d momentum: {metrics.get('real_yield_momentum_30d', 0):.2%}")
    
    print(f"\nRegime score:")
    regime = calc.calculate_regime_score(metrics, cb_data)
    print(f"  Score: {regime['score']}")
    print(f"  Assessment: {regime['assessment']}")
    print(f"  Action: {regime['action']}")


if __name__ == "__main__":
    test_calculator()

