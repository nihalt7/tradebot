import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List

class TechnicalAnalysisService:
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0.0))
        loss = (-delta.where(delta < 0, 0.0))
        
        # Wilder's smoothing
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        return series.rolling(window=period, min_periods=1).mean()

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        # Typical price
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        tp_vol = typical_price * df['Volume']
        
        # Group by date if available, otherwise cumulative
        if 'Datetime' in df.columns:
            try:
                dates = pd.to_datetime(df['Datetime']).dt.date
                cum_tp_vol = tp_vol.groupby(dates).cumsum()
                cum_vol = df['Volume'].groupby(dates).cumsum()
                vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
                return vwap.fillna(df['Close'])
            except Exception:
                pass
                
        cum_tp_vol = tp_vol.cumsum()
        cum_vol = df['Volume'].cumsum()
        vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
        return vwap.fillna(df['Close'])

    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        hist = macd_line - signal_line
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": hist
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df['High']
        low = df['Low']
        close_prev = df['Close'].shift(1)
        
        tr1 = high - low
        tr2 = (high - close_prev).abs()
        tr3 = (low - close_prev).abs()
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        return atr.fillna(true_range.mean())

    @staticmethod
    def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Dict[str, Any]:
        hl2 = (df['High'] + df['Low']) / 2
        atr = TechnicalAnalysisService.calculate_atr(df, period)
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        n = len(df)
        in_uptrend = np.ones(n, dtype=bool)
        final_upper = upper_band.values.copy()
        final_lower = lower_band.values.copy()
        close = df['Close'].values
        
        for i in range(1, n):
            if close[i] > final_upper[i-1]:
                in_uptrend[i] = True
            elif close[i] < final_lower[i-1]:
                in_uptrend[i] = False
            else:
                in_uptrend[i] = in_uptrend[i-1]
                if in_uptrend[i] and final_lower[i] < final_lower[i-1]:
                    final_lower[i] = final_lower[i-1]
                if not in_uptrend[i] and final_upper[i] > final_upper[i-1]:
                    final_upper[i] = final_upper[i-1]
                    
        trend_series = pd.Series(np.where(in_uptrend, 1, -1), index=df.index)
        st_val = pd.Series(np.where(in_uptrend, final_lower, final_upper), index=df.index)
        
        return {
            "supertrend": st_val,
            "trend": trend_series, # 1 for bullish, -1 for bearish
            "upper": pd.Series(final_upper, index=df.index),
            "lower": pd.Series(final_lower, index=df.index)
        }

    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        middle = series.rolling(window=period, min_periods=1).mean()
        std = series.rolling(window=period, min_periods=1).std().fillna(0)
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        pct_b = (series - lower) / (upper - lower).replace(0, np.nan)
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "percent_b": pct_b.fillna(0.5)
        }

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        high = df['High']
        low = df['Low']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)
        
        atr = TechnicalAnalysisService.calculate_atr(df, period)
        plus_di = 100 * (plus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr.replace(0, np.nan))
        minus_di = 100 * (minus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr.replace(0, np.nan))
        
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
        adx = dx.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        
        return {
            "adx": adx.fillna(25.0),
            "plus_di": plus_di.fillna(25.0),
            "minus_di": minus_di.fillna(25.0)
        }

    @staticmethod
    def calculate_pivots(high: float, low: float, close: float) -> Dict[str, float]:
        p = (high + low + close) / 3
        r1 = (2 * p) - low
        s1 = (2 * p) - high
        r2 = p + (high - low)
        s2 = p - (high - low)
        r3 = high + 2 * (p - low)
        s3 = low - 2 * (high - p)
        return {
            "pivot": round(p, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(r3, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2)
        }

    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        if len(df) < 3:
            return {"pattern": "None", "bullish": False, "bearish": False}
            
        c0 = df['Close'].iloc[-1]
        o0 = df['Open'].iloc[-1]
        h0 = df['High'].iloc[-1]
        l0 = df['Low'].iloc[-1]
        
        c1 = df['Close'].iloc[-2]
        o1 = df['Open'].iloc[-2]
        
        body0 = abs(c0 - o0)
        range0 = h0 - l0 if (h0 - l0) > 0 else 0.001
        body_to_range = body0 / range0
        
        patterns = []
        is_bullish = False
        is_bearish = False
        
        # Hammer (Bullish Reversal): Long lower shadow, small body at top
        lower_shadow0 = min(c0, o0) - l0
        upper_shadow0 = h0 - max(c0, o0)
        if lower_shadow0 > 2 * body0 and upper_shadow0 < 0.2 * body0:
            patterns.append("Hammer")
            is_bullish = True
            
        # Shooting Star (Bearish Reversal): Long upper shadow, small body at bottom
        if upper_shadow0 > 2 * body0 and lower_shadow0 < 0.2 * body0:
            patterns.append("Shooting Star")
            is_bearish = True
            
        # Bullish Engulfing
        if c1 < o1 and c0 > o0 and c0 >= o1 and o0 <= c1:
            patterns.append("Bullish Engulfing")
            is_bullish = True
            
        # Bearish Engulfing
        if c1 > o1 and c0 < o0 and c0 <= o1 and o0 >= c1:
            patterns.append("Bearish Engulfing")
            is_bearish = True
            
        # Doji (Indecision)
        if body_to_range < 0.1:
            patterns.append("Doji")
            
        pattern_str = ", ".join(patterns) if patterns else "Standard Bar"
        return {
            "pattern": pattern_str,
            "bullish": is_bullish,
            "bearish": is_bearish
        }

    @classmethod
    def analyze_dataframe(cls, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or len(df) < 20:
            return {}
            
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # 1. RSI
        rsi = cls.calculate_rsi(close, 14)
        
        # 2. EMAs
        ema9 = cls.calculate_ema(close, 9)
        ema20 = cls.calculate_ema(close, 20)
        ema50 = cls.calculate_ema(close, 50)
        
        # 3. SMA 200 (or available window)
        sma_len = min(200, len(close))
        sma200 = cls.calculate_sma(close, sma_len)
        
        # 4. VWAP
        vwap = cls.calculate_vwap(df)
        
        # 5. MACD
        macd_dict = cls.calculate_macd(close)
        
        # 6. ATR
        atr = cls.calculate_atr(df, 14)
        
        # 7. Supertrend
        st_dict = cls.calculate_supertrend(df, 10, 3.0)
        
        # 8. Volume MA
        vol_ma = cls.calculate_sma(volume, 20)
        
        # 9. Bollinger Bands
        bb_dict = cls.calculate_bollinger_bands(close, 20, 2.0)
        
        # 10. ADX
        adx_dict = cls.calculate_adx(df, 14)
        
        # 11. Pivots (from previous day or recent 20 candles)
        recent_high = float(high.iloc[-20:].max())
        recent_low = float(low.iloc[-20:].min())
        pivots = cls.calculate_pivots(recent_high, recent_low, float(close.iloc[-1]))
        
        # 12. Candlestick pattern
        candle_pattern = cls.detect_candlestick_patterns(df)
        
        # 13. Breakout / Breakdown
        current_close = float(close.iloc[-1])
        prior_20_high = float(high.iloc[-21:-1].max()) if len(df) > 21 else float(high.iloc[:-1].max())
        prior_20_low = float(low.iloc[-21:-1].min()) if len(df) > 21 else float(low.iloc[:-1].min())
        
        curr_vol = float(volume.iloc[-1])
        avg_vol = float(vol_ma.iloc[-1]) if vol_ma.iloc[-1] > 0 else curr_vol
        vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0
        
        is_breakout = (current_close > prior_20_high) and (vol_ratio >= 1.3)
        is_breakdown = (current_close < prior_20_low) and (vol_ratio >= 1.3)
        
        return {
            "price": round(current_close, 2),
            "rsi": round(float(rsi.iloc[-1]), 2),
            "ema9": round(float(ema9.iloc[-1]), 2),
            "ema20": round(float(ema20.iloc[-1]), 2),
            "ema50": round(float(ema50.iloc[-1]), 2),
            "sma200": round(float(sma200.iloc[-1]), 2),
            "vwap": round(float(vwap.iloc[-1]), 2),
            "macd": round(float(macd_dict["macd"].iloc[-1]), 2),
            "macd_signal": round(float(macd_dict["signal"].iloc[-1]), 2),
            "macd_hist": round(float(macd_dict["histogram"].iloc[-1]), 2),
            "atr": round(float(atr.iloc[-1]), 2),
            "supertrend": round(float(st_dict["supertrend"].iloc[-1]), 2),
            "supertrend_direction": "BULLISH" if st_dict["trend"].iloc[-1] == 1 else "BEARISH",
            "volume_ma": round(float(avg_vol), 0),
            "current_volume": int(curr_vol),
            "volume_ratio": round(vol_ratio, 2),
            "bb_upper": round(float(bb_dict["upper"].iloc[-1]), 2),
            "bb_middle": round(float(bb_dict["middle"].iloc[-1]), 2),
            "bb_lower": round(float(bb_dict["lower"].iloc[-1]), 2),
            "adx": round(float(adx_dict["adx"].iloc[-1]), 2),
            "plus_di": round(float(adx_dict["plus_di"].iloc[-1]), 2),
            "minus_di": round(float(adx_dict["minus_di"].iloc[-1]), 2),
            "pivots": pivots,
            "breakout": is_breakout,
            "breakdown": is_breakdown,
            "pattern": candle_pattern["pattern"],
            "pattern_bullish": candle_pattern["bullish"],
            "pattern_bearish": candle_pattern["bearish"]
        }

technical_analysis_service = TechnicalAnalysisService()
