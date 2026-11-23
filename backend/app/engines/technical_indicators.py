import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional

class TechnicalIndicatorsEngine:
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI 14) using Wilder's smoothing."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.fillna(50.0)

    @staticmethod
    def calculate_ema(series: pd.Series, span: int) -> pd.Series:
        """Calculate Exponential Moving Average (EMA)."""
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def calculate_sma(series: pd.Series, window: int) -> pd.Series:
        """Calculate Simple Moving Average (SMA)."""
        return series.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price (VWAP)."""
        typical_price = (df['high'] + df['low'] + df['close']) / 3.0
        pv = typical_price * df['volume']
        vwap = pv.cumsum() / (df['volume'].cumsum() + 1e-10)
        return vwap

    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (12, 26, 9): Line, Signal, Histogram."""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR 14)."""
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        return atr.fillna(tr.mean())

    @staticmethod
    def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Supertrend (10, 3).
        Returns (supertrend_value_series, direction_series where 1=Bullish, -1=Bearish).
        """
        atr = TechnicalIndicatorsEngine.calculate_atr(df, period)
        hl2 = (df['high'] + df['low']) / 2.0
        
        upper_basic = hl2 + (multiplier * atr)
        lower_basic = hl2 - (multiplier * atr)
        
        upper_band = upper_basic.copy()
        lower_band = lower_basic.copy()
        direction = pd.Series(1, index=df.index)
        supertrend = pd.Series(0.0, index=df.index)
        
        for i in range(1, len(df)):
            close_prev = df['close'].iloc[i - 1]
            close_curr = df['close'].iloc[i]
            
            # Lower band
            if lower_basic.iloc[i] > lower_band.iloc[i - 1] or close_prev < lower_band.iloc[i - 1]:
                lower_band.iloc[i] = lower_basic.iloc[i]
            else:
                lower_band.iloc[i] = lower_band.iloc[i - 1]
                
            # Upper band
            if upper_basic.iloc[i] < upper_band.iloc[i - 1] or close_prev > upper_band.iloc[i - 1]:
                upper_band.iloc[i] = upper_basic.iloc[i]
            else:
                upper_band.iloc[i] = upper_band.iloc[i - 1]
                
            # Direction
            if direction.iloc[i - 1] == 1:
                if close_curr < lower_band.iloc[i]:
                    direction.iloc[i] = -1
                    supertrend.iloc[i] = upper_band.iloc[i]
                else:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = lower_band.iloc[i]
            else:
                if close_curr > upper_band.iloc[i]:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = lower_band.iloc[i]
                else:
                    direction.iloc[i] = -1
                    supertrend.iloc[i] = upper_band.iloc[i]
                    
        return supertrend, direction

    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands (20, 2): Upper, Middle, Lower."""
        middle = series.rolling(window=window, min_periods=1).mean()
        std = series.rolling(window=window, min_periods=1).std(ddof=0).fillna(0.0)
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        return upper, middle, lower

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (ADX 14)."""
        high = df['high']
        low = df['low']
        
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        atr = TechnicalIndicatorsEngine.calculate_atr(df, period)
        plus_dm_series = pd.Series(plus_dm, index=df.index).ewm(alpha=1/period, min_periods=period).mean()
        minus_dm_series = pd.Series(minus_dm, index=df.index).ewm(alpha=1/period, min_periods=period).mean()
        
        plus_di = 100.0 * (plus_dm_series / (atr + 1e-10))
        minus_di = 100.0 * (minus_dm_series / (atr + 1e-10))
        
        dx = 100.0 * ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10))
        adx = dx.ewm(alpha=1/period, min_periods=period).mean().fillna(20.0)
        return adx

    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict[str, float]:
        """Calculate Support & Resistance levels using Pivot Points & Swing Highs/Lows."""
        recent = df.tail(lookback)
        high = float(recent['high'].max())
        low = float(recent['low'].min())
        close = float(df['close'].iloc[-1])
        
        # Standard Pivot Points
        pivot = (high + low + close) / 3.0
        r1 = (2.0 * pivot) - low
        s1 = (2.0 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            "pivot": round(pivot, 2),
            "resistance_1": round(r1, 2),
            "resistance_2": round(r2, 2),
            "support_1": round(s1, 2),
            "support_2": round(s2, 2),
            "swing_high": round(high, 2),
            "swing_low": round(low, 2)
        }

    @staticmethod
    def detect_breakout_breakdown(df: pd.DataFrame, lookback: int = 20) -> Dict[str, Any]:
        """Detect Bullish Breakout above resistance or Bearish Breakdown below support."""
        if len(df) < lookback + 1:
            return {"breakout": False, "breakdown": False, "level": None}
            
        prior_high = df['high'].iloc[-(lookback + 1):-1].max()
        prior_low = df['low'].iloc[-(lookback + 1):-1].min()
        current_close = df['close'].iloc[-1]
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:].mean()
        
        vol_surge = current_volume >= (1.5 * avg_volume)
        
        is_breakout = (current_close > prior_high) and vol_surge
        is_breakdown = (current_close < prior_low) and vol_surge
        
        return {
            "breakout": bool(is_breakout),
            "breakdown": bool(is_breakdown),
            "breakout_level": round(prior_high, 2),
            "breakdown_level": round(prior_low, 2),
            "volume_surge": bool(vol_surge)
        }

    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """Identify key intraday candlestick patterns."""
        if len(df) < 3:
            return {"pattern": None, "sentiment": "Neutral"}
            
        c = df['close'].iloc[-1]
        o = df['open'].iloc[-1]
        h = df['high'].iloc[-1]
        l = df['low'].iloc[-1]
        
        prev_c = df['close'].iloc[-2]
        prev_o = df['open'].iloc[-2]
        
        body = abs(c - o)
        range_bar = h - l + 1e-6
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        
        # Hammer (Bullish reversal)
        if lower_wick >= 2 * body and upper_wick <= 0.2 * body and c > o:
            return {"pattern": "Hammer", "sentiment": "Bullish"}
            
        # Shooting Star (Bearish reversal)
        if upper_wick >= 2 * body and lower_wick <= 0.2 * body and c < o:
            return {"pattern": "Shooting Star", "sentiment": "Bearish"}
            
        # Bullish Engulfing
        if prev_c < prev_o and c > o and c > prev_o and o < prev_c:
            return {"pattern": "Bullish Engulfing", "sentiment": "Bullish"}
            
        # Bearish Engulfing
        if prev_c > prev_o and c < o and c < prev_o and o > prev_c:
            return {"pattern": "Bearish Engulfing", "sentiment": "Bearish"}
            
        # Doji (Indecision)
        if body <= 0.1 * range_bar:
            return {"pattern": "Doji", "sentiment": "Indecision"}
            
        return {"pattern": "Standard Candle", "sentiment": "Bullish" if c >= o else "Bearish"}

    @classmethod
    def compute_all_indicators(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Run all 14 indicators on the dataframe and return the latest metrics."""
        if len(df) < 20:
            return {}

        df = df.copy()
        df['rsi_14'] = cls.calculate_rsi(df['close'], period=14)
        df['ema_9'] = cls.calculate_ema(df['close'], span=9)
        df['ema_20'] = cls.calculate_ema(df['close'], span=20)
        df['ema_50'] = cls.calculate_ema(df['close'], span=50)
        df['sma_200'] = cls.calculate_sma(df['close'], window=200)
        df['vwap'] = cls.calculate_vwap(df)
        
        macd_line, macd_sig, macd_hist = cls.calculate_macd(df['close'])
        df['macd'] = macd_line
        df['macd_signal'] = macd_sig
        df['macd_hist'] = macd_hist
        
        df['atr_14'] = cls.calculate_atr(df, period=14)
        supertrend, st_dir = cls.calculate_supertrend(df, period=10, multiplier=3.0)
        df['supertrend'] = supertrend
        df['supertrend_dir'] = st_dir
        
        df['vol_ma_20'] = df['volume'].rolling(window=20, min_periods=1).mean()
        bb_u, bb_m, bb_l = cls.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_u
        df['bb_middle'] = bb_m
        df['bb_lower'] = bb_l
        
        df['adx_14'] = cls.calculate_adx(df, period=14)
        
        sr_levels = cls.calculate_support_resistance(df)
        breakout_info = cls.detect_breakout_breakdown(df)
        candlestick_info = cls.detect_candlestick_patterns(df)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        curr_price = float(last['close'])
        curr_vol = float(last['volume'])
        vol_avg = float(last['vol_ma_20'])
        vol_ratio = round(curr_vol / (vol_avg + 1e-6), 2)
        
        # Trend and Momentum states
        ema_bullish = curr_price > last['ema_9'] > last['ema_20'] > last['ema_50']
        ema_bearish = curr_price < last['ema_9'] < last['ema_20'] < last['ema_50']
        vwap_status = "Bullish (Above VWAP)" if curr_price > last['vwap'] else "Bearish (Below VWAP)"
        macd_bias = "Bullish" if last['macd_hist'] > 0 and last['macd'] > last['macd_signal'] else "Bearish"
        supertrend_bias = "Bullish" if last['supertrend_dir'] == 1 else "Bearish"
        
        return {
            "current_price": round(curr_price, 2),
            "rsi_14": round(float(last['rsi_14']), 2),
            "ema_9": round(float(last['ema_9']), 2),
            "ema_20": round(float(last['ema_20']), 2),
            "ema_50": round(float(last['ema_50']), 2),
            "sma_200": round(float(last['sma_200']), 2),
            "vwap": round(float(last['vwap']), 2),
            "macd": round(float(last['macd']), 2),
            "macd_signal": round(float(last['macd_signal']), 2),
            "macd_hist": round(float(last['macd_hist']), 2),
            "atr_14": round(float(last['atr_14']), 2),
            "supertrend": round(float(last['supertrend']), 2),
            "supertrend_direction": supertrend_bias,
            "vol_ma_20": round(vol_avg, 0),
            "volume_ratio": vol_ratio,
            "bb_upper": round(float(last['bb_upper']), 2),
            "bb_middle": round(float(last['bb_middle']), 2),
            "bb_lower": round(float(last['bb_lower']), 2),
            "adx_14": round(float(last['adx_14']), 2),
            "ema_bullish": ema_bullish,
            "ema_bearish": ema_bearish,
            "vwap_status": vwap_status,
            "macd_bias": macd_bias,
            "support_resistance": sr_levels,
            "breakout": breakout_info,
            "candlestick": candlestick_info
        }
