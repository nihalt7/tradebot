import React from 'react';
import { BarChart3, TrendingUp, TrendingDown, Layers, Activity } from 'lucide-react';
import { AnalysisCardData } from '../types';

interface AnalysisCardProps {
  data: AnalysisCardData;
}

export const AnalysisCardComponent: React.FC<AnalysisCardProps> = ({ data }) => {
  const isBull = data.trend === 'Bullish' || data.change_pct >= 0;

  return (
    <div className="w-full max-w-md rounded-xl overflow-hidden border border-gray-700/60 bg-[#182229] text-gray-200 shadow-xl my-2">
      {/* Header */}
      <div className="bg-[#202c33] px-4 py-2.5 flex items-center justify-between border-b border-gray-700/50">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white text-sm">{data.symbol} Quantitative Deep Dive</span>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
          Score: {data.score}/100
        </span>
      </div>

      <div className="p-3.5 space-y-3 text-xs">
        {/* Price & Primary Status */}
        <div className="flex items-center justify-between bg-[#111b21] p-2.5 rounded-lg border border-gray-800">
          <div>
            <div className="text-[10px] text-gray-400 uppercase">Current LTP</div>
            <div className="text-base font-extrabold text-white">₹{data.current_price?.toFixed(2)}</div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-gray-400 uppercase">Daily Change</div>
            <div className={`font-bold text-sm flex items-center justify-end ${data.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {data.change_pct >= 0 ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
              {data.change_pct >= 0 ? '+' : ''}{data.change_pct?.toFixed(2)}%
            </div>
          </div>
        </div>

        {/* 14 Indicators Grid */}
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="bg-[#202c33] p-2 rounded border border-gray-700/40">
            <span className="text-gray-400 block text-[9px] uppercase">Supertrend (10,3)</span>
            <span className={`font-semibold ${data.supertrend === 'Bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
              {data.supertrend} (₹{data.supertrend_val?.toFixed(2)})
            </span>
          </div>

          <div className="bg-[#202c33] p-2 rounded border border-gray-700/40">
            <span className="text-gray-400 block text-[9px] uppercase">VWAP</span>
            <span className="font-semibold text-white">₹{data.vwap?.toFixed(2)}</span>
          </div>

          <div className="bg-[#202c33] p-2 rounded border border-gray-700/40">
            <span className="text-gray-400 block text-[9px] uppercase">RSI (14)</span>
            <span className={`font-semibold ${data.rsi_14 > 55 ? 'text-emerald-400' : (data.rsi_14 < 45 ? 'text-rose-400' : 'text-amber-400')}`}>
              {data.rsi_14} ({data.rsi_14 > 55 ? 'Bullish' : (data.rsi_14 < 45 ? 'Bearish' : 'Neutral')})
            </span>
          </div>

          <div className="bg-[#202c33] p-2 rounded border border-gray-700/40">
            <span className="text-gray-400 block text-[9px] uppercase">MACD Bias</span>
            <span className={`font-semibold ${data.macd_bias === 'Bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
              {data.macd_bias}
            </span>
          </div>
        </div>

        {/* Moving Averages Stack */}
        <div className="bg-[#202c33] p-2.5 rounded-lg border border-gray-700/40 text-[11px]">
          <div className="text-gray-400 font-semibold mb-1 flex items-center text-[10px]">
            <Layers className="w-3 h-3 mr-1 text-cyan-400" /> Moving Average Alignment
          </div>
          <div className="flex justify-between items-center text-gray-300">
            <span>EMA 9: <strong className="text-white">₹{data.ema_9?.toFixed(1)}</strong></span>
            <span>EMA 20: <strong className="text-white">₹{data.ema_20?.toFixed(1)}</strong></span>
            <span>EMA 50: <strong className="text-white">₹{data.ema_50?.toFixed(1)}</strong></span>
          </div>
        </div>

        {/* Support & Resistance Levels */}
        <div className="bg-[#111b21] p-2 rounded-lg border border-gray-800 text-[11px] flex justify-between">
          <div>
            <span className="text-rose-400 font-semibold block text-[10px]">Resistance</span>
            <span className="text-gray-300">R1: ₹{data.resistance_1?.toFixed(1)}</span>
          </div>
          <div className="text-right">
            <span className="text-emerald-400 font-semibold block text-[10px]">Support</span>
            <span className="text-gray-300">S1: ₹{data.support_1?.toFixed(1)}</span>
          </div>
        </div>

        {/* Candlestick & Volume Pattern */}
        {data.candlestick_pattern && (
          <div className="bg-black/25 p-2 rounded border border-gray-800 flex items-center justify-between text-[11px]">
            <span className="text-gray-400">Pattern:</span>
            <span className="font-semibold text-emerald-300">{data.candlestick_pattern}</span>
          </div>
        )}

        <div className="text-[11px] text-gray-300 bg-[#202c33]/50 p-2 rounded border border-gray-700/30">
          <strong className="text-emerald-400">Quantitative Summary: </strong>
          {data.verdict}
        </div>
      </div>
    </div>
  );
};
