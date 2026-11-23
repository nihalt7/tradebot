import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, CheckCircle2, Clock, ShieldCheck, Zap, AlertTriangle } from 'lucide-react';
import { SignalCardData } from '../types';
import { api } from '../services/api';

interface SignalCardProps {
  data: SignalCardData;
}

export const SignalCardComponent: React.FC<SignalCardProps> = ({ data }) => {
  const [executed, setExecuted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const isBuy = data.signal === 'BUY';

  const handleExecutePaperTrade = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await api.placePaperOrder({
        symbol: data.symbol,
        direction: data.signal,
        quantity: data.suggested_qty || 200,
        entry_price: data.entry_min,
        stop_loss: data.stop_loss,
        target_1: data.target_1,
        target_2: data.target_2,
        target_3: data.target_3,
        signal_id: data.id
      });
      setExecuted(true);
    } catch (e: any) {
      setErrorMsg(e.message || 'Trade execution blocked by risk limit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md rounded-xl overflow-hidden border border-emerald-500/30 bg-[#182229] text-gray-200 shadow-xl my-2">
      {/* Top Banner */}
      <div className={`px-4 py-2.5 flex items-center justify-between font-bold text-xs ${
        isBuy ? 'bg-gradient-to-r from-emerald-700 to-teal-700 text-white' : 'bg-gradient-to-r from-rose-700 to-red-800 text-white'
      }`}>
        <div className="flex items-center space-x-1.5">
          <span className="text-base">🚨</span>
          <span className="tracking-wide uppercase">High-Quality Trading Opportunity</span>
        </div>
        <div className="flex items-center space-x-1 bg-black/30 px-2 py-0.5 rounded text-[11px]">
          <Clock className="w-3 h-3" />
          <span>{data.signal_time || 'Just now'}</span>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {/* Symbol & Direction Header */}
        <div className="flex items-center justify-between border-b border-gray-700/60 pb-3">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-extrabold text-white tracking-tight">{data.symbol}</span>
              <span className="text-[11px] px-1.5 py-0.5 rounded bg-gray-700/50 text-gray-300 font-medium">
                {data.exchange || 'NSE'}
              </span>
            </div>
            <div className="text-[11px] text-gray-400 mt-0.5">
              Timeframe: <span className="text-gray-200 font-semibold">{data.timeframe || '5 Minutes'}</span>
            </div>
          </div>

          <div className="flex flex-col items-end">
            <div className={`px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 ${
              isBuy ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
            }`}>
              {isBuy ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span>{isBuy ? '🟢 BUY' : '🔴 SELL'}</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-1">
              R:R <span className="text-emerald-400 font-bold">{data.risk_reward}</span>
            </div>
          </div>
        </div>

        {/* Price & Target Levels Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          {/* Entry Range */}
          <div className="bg-[#202c33] p-2.5 rounded-lg border border-gray-700/50">
            <div className="text-gray-400 text-[10px] uppercase font-semibold">Entry Zone</div>
            <div className="text-emerald-400 font-bold text-sm mt-0.5">
              ₹{data.entry_min?.toFixed(2)} – ₹{data.entry_max?.toFixed(2)}
            </div>
          </div>

          {/* Stop Loss */}
          <div className="bg-[#202c33] p-2.5 rounded-lg border border-gray-700/50">
            <div className="text-gray-400 text-[10px] uppercase font-semibold">Stop Loss</div>
            <div className="text-rose-400 font-bold text-sm mt-0.5">
              ₹{data.stop_loss?.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Targets Hierarchy */}
        <div className="bg-[#111b21] p-2.5 rounded-lg border border-gray-700/40 space-y-1.5 text-xs">
          <div className="flex justify-between items-center text-gray-300">
            <span className="flex items-center text-[11px]"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5"></span> Target 1 (1:1.5)</span>
            <span className="font-bold text-white">₹{data.target_1?.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center text-gray-300">
            <span className="flex items-center text-[11px]"><span className="w-1.5 h-1.5 rounded-full bg-teal-400 mr-1.5"></span> Target 2 (1:2.0)</span>
            <span className="font-bold text-white">₹{data.target_2?.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center text-gray-300">
            <span className="flex items-center text-[11px]"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-1.5"></span> Target 3 (1:2.8)</span>
            <span className="font-bold text-white">₹{data.target_3?.toFixed(2)}</span>
          </div>
        </div>

        {/* Technical Indicators Snapshot Badges */}
        <div className="grid grid-cols-3 gap-1.5 text-[11px]">
          <div className="bg-[#202c33] px-2 py-1 rounded text-center">
            <span className="text-gray-400 block text-[9px]">RSI (14)</span>
            <span className="font-semibold text-emerald-300">{data.rsi ?? 58}</span>
          </div>
          <div className="bg-[#202c33] px-2 py-1 rounded text-center">
            <span className="text-gray-400 block text-[9px]">VWAP</span>
            <span className="font-semibold text-emerald-300">{data.vwap_status || 'Bullish'}</span>
          </div>
          <div className="bg-[#202c33] px-2 py-1 rounded text-center">
            <span className="text-gray-400 block text-[9px]">Volume</span>
            <span className="font-semibold text-amber-300">{data.volume_ratio}x Avg</span>
          </div>
        </div>

        {/* Setup Score Meter */}
        <div className="bg-[#202c33] p-2.5 rounded-lg border border-gray-700/50">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="text-gray-300 font-semibold flex items-center">
              <Zap className="w-3.5 h-3.5 text-amber-400 mr-1" /> Setup Score
            </span>
            <span className="font-extrabold text-emerald-400 text-sm">
              {data.setup_score}/100
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-emerald-500 to-teal-400 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(100, data.setup_score)}%` }}
            ></div>
          </div>
        </div>

        {/* Reason Box */}
        <div className="text-[11px] bg-black/20 p-2 rounded text-gray-300 border border-gray-800">
          <span className="font-bold text-emerald-400">Reason: </span>
          {data.reason}
        </div>

        <div className="text-[10px] text-gray-400 italic text-center">
          ⚡ Entry Validity: {data.validity_minutes || 5} mins, subject to live market orderbook.
        </div>

        {errorMsg && (
          <div className="p-2 bg-rose-900/40 border border-rose-500/50 rounded text-rose-300 text-xs flex items-center space-x-1.5">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Action Button */}
        <div>
          {executed ? (
            <div className="w-full py-2 bg-emerald-600/30 border border-emerald-500/50 rounded-lg text-emerald-300 font-semibold text-xs flex items-center justify-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Paper Trade Active in Portfolio</span>
            </div>
          ) : (
            <button
              onClick={handleExecutePaperTrade}
              disabled={loading}
              className={`w-full py-2.5 rounded-lg text-xs font-bold tracking-wide transition-all duration-150 flex items-center justify-center space-x-1.5 shadow-md ${
                isBuy 
                  ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/40' 
                  : 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/40'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{loading ? 'Executing...' : `Execute Paper Trade (${isBuy ? 'BUY' : 'SELL'})`}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
