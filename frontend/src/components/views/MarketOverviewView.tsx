"use client";

import React from "react";
import { 
  TrendingUp, TrendingDown, Activity, BarChart3, 
  Flame, Clock, ArrowUpRight, ArrowDownRight, RefreshCw 
} from "lucide-react";

interface MarketOverviewViewProps {
  overview: any;
  onRefresh?: () => void;
  onSelectStock?: (symbol: string) => void;
}

export default function MarketOverviewView({
  overview,
  onRefresh,
  onSelectStock
}: MarketOverviewViewProps) {
  const indices = overview?.indices || [];
  const topGainers = overview?.top_gainers || [];
  const topLosers = overview?.top_losers || [];
  const volumeShockers = overview?.volume_shockers || [];

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Indian Stock Market Overview</span>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
              NSE / BSE
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time index quotes, market breadth advances/declines, and momentum movers.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-3 py-1.5 rounded-lg bg-[#141A28] hover:bg-[#1C2438] text-slate-300 text-xs font-medium border border-[#1E2638] flex items-center space-x-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Feed</span>
            </button>
          )}
        </div>
      </div>

      {/* Indices Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {indices.map((idx: any, i: number) => {
          const isUp = idx.change >= 0;
          return (
            <div
              key={i}
              className="p-4 rounded-xl bg-[#101522] border border-[#1E2638] shadow-lg relative overflow-hidden"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  {idx.symbol}
                </span>
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded flex items-center space-x-0.5 ${
                    isUp
                      ? "bg-emerald-500/15 text-emerald-400"
                      : "bg-rose-500/15 text-rose-400"
                  }`}
                >
                  {isUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  <span>{idx.percent_change > 0 ? `+${idx.percent_change}` : idx.percent_change}%</span>
                </span>
              </div>

              <div className="mt-3 flex items-baseline space-x-2">
                <span className="text-2xl font-black text-white font-mono">
                  ₹{idx.price?.toLocaleString("en-IN")}
                </span>
                <span
                  className={`text-xs font-semibold font-mono ${
                    isUp ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {idx.change > 0 ? `+${idx.change}` : idx.change}
                </span>
              </div>

              <div className="mt-3 pt-3 border-t border-[#1A2234] flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>H: ₹{idx.high}</span>
                <span>L: ₹{idx.low}</span>
                <span>Prev: ₹{idx.prev_close}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Market Breadth & Sentiment */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Market Sentiment</span>
          <div className="mt-2 text-lg font-bold text-blue-400">
            {overview?.market_trend || "SIDEWAYS"}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Based on multi-factor breadth analysis</div>
        </div>

        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638]">
          <span className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Advances</span>
          <div className="mt-2 text-2xl font-bold text-emerald-400 font-mono">
            {overview?.advances ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Stocks trading in green</div>
        </div>

        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638]">
          <span className="text-xs font-medium text-rose-400 uppercase tracking-wider">Declines</span>
          <div className="mt-2 text-2xl font-bold text-rose-400 font-mono">
            {overview?.declines ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Stocks trading in red</div>
        </div>

        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">A/D Ratio</span>
          <div className="mt-2 text-2xl font-bold text-white font-mono">
            {overview?.advance_decline_ratio ?? "1.0"}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Advance-to-decline velocity</div>
        </div>
      </div>

      {/* Three Columns: Top Gainers, Top Losers, Volume Shockers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Gainers */}
        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638] space-y-3">
          <div className="flex items-center space-x-2 text-emerald-400 pb-2 border-b border-[#1E2638]">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-bold text-white">Top Gainers (NSE)</span>
          </div>

          <div className="divide-y divide-[#182030]">
            {topGainers.map((stock: any, i: number) => (
              <div
                key={i}
                onClick={() => onSelectStock && onSelectStock(stock.symbol)}
                className="py-2.5 flex items-center justify-between hover:bg-[#161D2C] px-2 rounded-lg cursor-pointer transition-colors"
              >
                <div>
                  <div className="text-xs font-bold text-white">{stock.symbol}</div>
                  <div className="text-[10px] text-slate-500 font-mono">Vol: {stock.volume?.toLocaleString("en-IN")}</div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-semibold text-white">₹{stock.price}</div>
                  <div className="text-xs font-bold text-emerald-400">+{stock.percent_change}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Losers */}
        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638] space-y-3">
          <div className="flex items-center space-x-2 text-rose-400 pb-2 border-b border-[#1E2638]">
            <TrendingDown className="w-4 h-4" />
            <span className="text-sm font-bold text-white">Top Losers (NSE)</span>
          </div>

          <div className="divide-y divide-[#182030]">
            {topLosers.map((stock: any, i: number) => (
              <div
                key={i}
                onClick={() => onSelectStock && onSelectStock(stock.symbol)}
                className="py-2.5 flex items-center justify-between hover:bg-[#161D2C] px-2 rounded-lg cursor-pointer transition-colors"
              >
                <div>
                  <div className="text-xs font-bold text-white">{stock.symbol}</div>
                  <div className="text-[10px] text-slate-500 font-mono">Vol: {stock.volume?.toLocaleString("en-IN")}</div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-semibold text-white">₹{stock.price}</div>
                  <div className="text-xs font-bold text-rose-400">{stock.percent_change}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Volume Shockers */}
        <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638] space-y-3">
          <div className="flex items-center space-x-2 text-amber-400 pb-2 border-b border-[#1E2638]">
            <Flame className="w-4 h-4" />
            <span className="text-sm font-bold text-white">Volume Shockers</span>
          </div>

          <div className="divide-y divide-[#182030]">
            {volumeShockers.map((stock: any, i: number) => (
              <div
                key={i}
                onClick={() => onSelectStock && onSelectStock(stock.symbol)}
                className="py-2.5 flex items-center justify-between hover:bg-[#161D2C] px-2 rounded-lg cursor-pointer transition-colors"
              >
                <div>
                  <div className="text-xs font-bold text-white">{stock.symbol}</div>
                  <div className="text-[10px] text-amber-400 font-mono font-medium">
                    {stock.volume_ratio}x 20-period avg
                  </div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-semibold text-white">₹{stock.price}</div>
                  <div className={`text-xs font-bold ${stock.percent_change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {stock.percent_change >= 0 ? `+${stock.percent_change}%` : `${stock.percent_change}%`}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
