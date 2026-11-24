"use client";

import React from "react";
import { TrendingUp, ShieldCheck, RefreshCw } from "lucide-react";
import TradingSignalCard from "../cards/TradingSignalCard";

interface TopBuySignalsViewProps {
  signals: any[];
  onTriggerScan?: () => void;
  onExecutePaperTrade?: (signal: any) => void;
  onViewChart?: (symbol: string) => void;
}

export default function TopBuySignalsView({
  signals,
  onTriggerScan,
  onExecutePaperTrade,
  onViewChart
}: TopBuySignalsViewProps) {
  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <span>Top 5 Confirmed BUY Opportunities (NSE)</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Stocks with Setup Score &ge; 70, trading above VWAP, positive MACD histogram, and bullish momentum.
          </p>
        </div>

        {onTriggerScan && (
          <button
            onClick={onTriggerScan}
            className="px-3.5 py-1.5 rounded-lg bg-[#141A28] hover:bg-[#1C2438] text-slate-200 text-xs font-semibold border border-[#1E2638] flex items-center space-x-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5 text-blue-400" />
            <span>Rescan Opportunities</span>
          </button>
        )}
      </div>

      {signals.length === 0 ? (
        <div className="p-12 text-center bg-[#0E121B] rounded-xl border border-[#1E2638] space-y-2">
          <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto opacity-70" />
          <div className="text-base font-bold text-white">No Confirmed BUY Signals Right Now</div>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            The quantitative engine requires multi-timeframe confirmation, volume surge, and RSI between 55–70. Rather than forcing low-conviction trades, Trade Bot waits for mathematical edge.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {signals.slice(0, 5).map((sig: any, idx: number) => (
            <TradingSignalCard
              key={idx}
              signal={sig}
              onExecutePaperTrade={onExecutePaperTrade}
              onViewChart={onViewChart}
            />
          ))}
        </div>
      )}
    </div>
  );
}
