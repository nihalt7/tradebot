"use client";

import React, { useState } from "react";
import { 
  TrendingUp, TrendingDown, Shield, Target, Clock, 
  CheckCircle2, ArrowRight, Zap, PlaySquare
} from "lucide-react";

interface TradingSignalCardProps {
  signal: {
    id: string;
    symbol: string;
    full_symbol: string;
    exchange: string;
    signal: "BUY" | "SELL";
    setup_score: number;
    classification: string;
    entry_price: number;
    stop_loss: number;
    target1: number;
    target2: number;
    target3: number;
    risk_reward: number;
    recommended_quantity: number;
    allocated_capital: number;
    timeframe: string;
    max_holding_period: string;
    signal_time: string;
    indicators: {
      rsi: number;
      vwap_status: string;
      ema_status: string;
      macd_status: string;
      volume_comparison: string;
      supertrend: string;
    };
    explanation: string;
  };
  onExecutePaperTrade?: (signal: any) => void;
  onViewChart?: (symbol: string) => void;
}

export default function TradingSignalCard({
  signal,
  onExecutePaperTrade,
  onViewChart
}: TradingSignalCardProps) {
  const [executed, setExecuted] = useState(false);
  const isBuy = signal.signal === "BUY";

  const handleTrade = () => {
    if (onExecutePaperTrade) {
      onExecutePaperTrade(signal);
      setExecuted(true);
    }
  };

  return (
    <div className={`rounded-xl border ${isBuy ? 'border-emerald-500/30 bg-gradient-to-b from-[#101F18] to-[#0D1418]' : 'border-rose-500/30 bg-gradient-to-b from-[#201215] to-[#120D12]'} p-4 shadow-xl transition-all hover:border-blue-500/40 relative overflow-hidden`}>
      {/* Top Banner */}
      <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]/60">
        <div className="flex items-center space-x-2.5">
          <div className={`px-2 py-0.5 rounded text-xs font-black uppercase tracking-wider flex items-center space-x-1 ${
            isBuy ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
          }`}>
            {isBuy ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            <span>{signal.signal} OPPORTUNITY</span>
          </div>
          <span className="text-base font-bold text-white tracking-tight">{signal.symbol}</span>
          <span className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded bg-[#182030] font-mono">{signal.exchange}</span>
        </div>

        {/* Setup Score Badge */}
        <div className="flex items-center space-x-1.5 bg-[#141C2E] px-2.5 py-1 rounded-lg border border-blue-500/30">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs font-bold text-white font-mono">
            {signal.setup_score}<span className="text-[10px] text-slate-400">/100</span>
          </span>
          <span className="text-[10px] text-blue-400 font-semibold uppercase">
            ({signal.classification})
          </span>
        </div>
      </div>

      {/* Main Prices Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 my-3">
        <div className="p-2.5 rounded-lg bg-[#0C101A]/80 border border-[#1A2234]">
          <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Entry Price</div>
          <div className="text-sm font-bold text-white font-mono mt-0.5">₹{signal.entry_price?.toLocaleString("en-IN")}</div>
        </div>

        <div className="p-2.5 rounded-lg bg-[#0C101A]/80 border border-rose-500/20">
          <div className="text-[10px] font-medium text-rose-400 uppercase tracking-wider flex items-center space-x-1">
            <Shield className="w-3 h-3" />
            <span>Stop Loss</span>
          </div>
          <div className="text-sm font-bold text-rose-400 font-mono mt-0.5">₹{signal.stop_loss?.toLocaleString("en-IN")}</div>
        </div>

        <div className="p-2.5 rounded-lg bg-[#0C101A]/80 border border-emerald-500/20">
          <div className="text-[10px] font-medium text-emerald-400 uppercase tracking-wider flex items-center space-x-1">
            <Target className="w-3 h-3" />
            <span>Target 1 (1:1.5)</span>
          </div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">₹{signal.target1?.toLocaleString("en-IN")}</div>
        </div>

        <div className="p-2.5 rounded-lg bg-[#0C101A]/80 border border-[#1A2234]">
          <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Target 2 & 3</div>
          <div className="text-xs font-semibold text-emerald-300 font-mono mt-0.5">
            T2: ₹{signal.target2} | T3: ₹{signal.target3}
          </div>
        </div>
      </div>

      {/* Indicators Matrix */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 py-2 px-3 rounded-lg bg-[#090D15] border border-[#182030] text-[11px]">
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">RSI (14)</span>
          <span className={`font-mono font-semibold ${signal.indicators.rsi > 55 ? 'text-emerald-400' : 'text-slate-200'}`}>
            {signal.indicators.rsi}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">VWAP</span>
          <span className="font-semibold text-blue-400 truncate block">
            {signal.indicators.vwap_status}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">EMA Align</span>
          <span className="font-semibold text-slate-200">
            {signal.indicators.ema_status}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">MACD</span>
          <span className="font-semibold text-emerald-400">
            {signal.indicators.macd_status}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">Volume</span>
          <span className="font-mono font-semibold text-amber-400">
            {signal.indicators.volume_comparison}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[9px] uppercase">Risk / Reward</span>
          <span className="font-mono font-bold text-white">
            1:{signal.risk_reward}
          </span>
        </div>
      </div>

      {/* Rationale explanation */}
      <div className="mt-2.5 text-xs text-slate-300 leading-relaxed bg-[#101624]/60 p-2 rounded-lg border border-[#182030]">
        <span className="text-blue-400 font-semibold">Quantitative Rationale: </span>
        {signal.explanation}
      </div>

      {/* Footer Info & Actions */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#1E2638]/60 text-[11px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1 font-mono">
            <Clock className="w-3 h-3 text-slate-400" />
            <span>Timeframe: {signal.timeframe}</span>
          </span>
          <span className="hidden sm:inline text-slate-400">|</span>
          <span className="hidden sm:inline text-slate-400 font-mono">Pos Qty: {signal.recommended_quantity} qty</span>
        </div>

        <div className="flex items-center space-x-2">
          {onViewChart && (
            <button
              onClick={() => onViewChart(signal.symbol)}
              className="px-2.5 py-1 rounded-md bg-[#161E30] hover:bg-[#202B44] text-slate-200 text-xs font-medium border border-[#1E2638] transition-colors"
            >
              View Chart
            </button>
          )}

          <button
            onClick={handleTrade}
            disabled={executed}
            className={`px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-sm ${
              executed
                ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 cursor-default'
                : isBuy
                ? 'bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold'
                : 'bg-rose-500 hover:bg-rose-600 text-white font-bold'
            }`}
          >
            {executed ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Paper Order Placed</span>
              </>
            ) : (
              <>
                <PlaySquare className="w-3.5 h-3.5" />
                <span>Execute Paper Trade</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
