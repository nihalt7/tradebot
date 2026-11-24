"use client";

import React from "react";
import { Zap, RefreshCw, Filter } from "lucide-react";
import TradingSignalCard from "../cards/TradingSignalCard";

interface ActiveOpportunitiesViewProps {
  opportunities: any[];
  onTriggerScan?: () => void;
  onExecutePaperTrade?: (signal: any) => void;
  onViewChart?: (symbol: string) => void;
}

export default function ActiveOpportunitiesView({
  opportunities,
  onTriggerScan,
  onExecutePaperTrade,
  onViewChart
}: ActiveOpportunitiesViewProps) {
  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <span>Active Trading Opportunities ({opportunities.length})</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time ranked setups currently active in the market, ordered by Setup Score descending.
          </p>
        </div>

        {onTriggerScan && (
          <button
            onClick={onTriggerScan}
            className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-lg shadow-blue-600/20"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Scan Universe</span>
          </button>
        )}
      </div>

      {opportunities.length === 0 ? (
        <div className="p-12 text-center bg-[#0E121B] rounded-xl border border-[#1E2638] space-y-2">
          <div className="text-base font-bold text-white">No Active High-Conviction Opportunities</div>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Trade Bot generates signals only when the 0–100 scoring model hits 70+. Run a scan or watch the market scanner updates.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {opportunities.map((opp: any, idx: number) => (
            <TradingSignalCard
              key={opp.id || idx}
              signal={opp}
              onExecutePaperTrade={onExecutePaperTrade}
              onViewChart={onViewChart}
            />
          ))}
        </div>
      )}
    </div>
  );
}
