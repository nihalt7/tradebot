"use client";

import React, { useState } from "react";
import { 
  Radar, RefreshCw, Zap, TrendingUp, TrendingDown, 
  Flame, Compass, ArrowUpRight, ArrowDownRight, ShieldCheck 
} from "lucide-react";
import TradingSignalCard from "../cards/TradingSignalCard";

interface ScannerViewProps {
  scannerData: any;
  onTriggerScan: () => void;
  isScanning: boolean;
  onExecutePaperTrade?: (signal: any) => void;
  onViewChart?: (symbol: string) => void;
}

export default function ScannerView({
  scannerData,
  onTriggerScan,
  isScanning,
  onExecutePaperTrade,
  onViewChart
}: ScannerViewProps) {
  const [activeTab, setActiveTab] = useState<"opportunities" | "breakouts" | "volume" | "momentum" | "reversals">("opportunities");

  const topBuy = scannerData?.top_buy || [];
  const topSell = scannerData?.top_sell || [];
  const breakouts = scannerData?.breakouts || [];
  const breakdowns = scannerData?.breakdowns || [];
  const unusualVolume = scannerData?.unusual_volume || [];
  const momentum = scannerData?.momentum || [];
  const reversals = scannerData?.reversals || [];

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Radar className="w-5 h-5 text-blue-400" />
            <span>Automatic NSE Market Scanner</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Continuous background quantitative scan across the eligible NSE equity universe.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
            Last scan: {scannerData?.last_scan_time || "Pending..."}
          </span>
          <button
            onClick={onTriggerScan}
            disabled={isScanning}
            className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-lg shadow-blue-600/20"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? "animate-spin" : ""}`} />
            <span>{isScanning ? "Scanning NSE Universe..." : "Trigger Live Scan"}</span>
          </button>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="flex items-center space-x-1 border-b border-[#1E2638] pb-2 overflow-x-auto no-scrollbar">
        <button
          onClick={() => setActiveTab("opportunities")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
            activeTab === "opportunities"
              ? "bg-blue-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-[#141A28]"
          }`}
        >
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>Top Opportunities ({topBuy.length + topSell.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("breakouts")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
            activeTab === "breakouts"
              ? "bg-blue-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-[#141A28]"
          }`}
        >
          <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
          <span>Breakouts &amp; Breakdowns ({breakouts.length + breakdowns.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("volume")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
            activeTab === "volume"
              ? "bg-blue-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-[#141A28]"
          }`}
        >
          <Flame className="w-3.5 h-3.5 text-amber-400" />
          <span>Unusual Volume ({unusualVolume.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("momentum")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
            activeTab === "momentum"
              ? "bg-blue-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-[#141A28]"
          }`}
        >
          <Compass className="w-3.5 h-3.5 text-cyan-400" />
          <span>Strong Momentum ({momentum.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === "opportunities" && (
        <div className="space-y-6">
          {topBuy.length === 0 && topSell.length === 0 ? (
            <div className="p-12 text-center bg-[#0E121B] rounded-xl border border-[#1E2638]">
              <ShieldCheck className="w-10 h-10 text-emerald-400 mx-auto mb-2 opacity-80" />
              <div className="text-sm font-bold text-white">No 70+ Setup Score Opportunities Triggered</div>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Trade Bot enforces strict accuracy over quantity. No alerts are generated unless technical alignment across 15 indicators and multi-timeframes meets the threshold.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {topBuy.map((sig: any, idx: number) => (
                <TradingSignalCard
                  key={`buy_${idx}`}
                  signal={sig}
                  onExecutePaperTrade={onExecutePaperTrade}
                  onViewChart={onViewChart}
                />
              ))}
              {topSell.map((sig: any, idx: number) => (
                <TradingSignalCard
                  key={`sell_${idx}`}
                  signal={sig}
                  onExecutePaperTrade={onExecutePaperTrade}
                  onViewChart={onViewChart}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "breakouts" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-1.5">
              <TrendingUp className="w-4 h-4" />
              <span>Bullish Breakouts (20-Period Highs)</span>
            </h3>
            <div className="divide-y divide-[#182030]">
              {breakouts.length === 0 ? (
                <div className="py-4 text-xs text-slate-500 text-center">No breakouts in latest scan</div>
              ) : (
                breakouts.map((b: any, i: number) => (
                  <div key={i} className="py-2.5 flex items-center justify-between text-xs">
                    <span className="font-bold text-white font-mono">{b.symbol}</span>
                    <span className="text-slate-300 font-mono">₹{b.price}</span>
                    <span className="text-emerald-400 font-mono">{b.volume_ratio}x Vol</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center space-x-1.5">
              <TrendingDown className="w-4 h-4" />
              <span>Bearish Breakdowns (20-Period Lows)</span>
            </h3>
            <div className="divide-y divide-[#182030]">
              {breakdowns.length === 0 ? (
                <div className="py-4 text-xs text-slate-500 text-center">No breakdowns in latest scan</div>
              ) : (
                breakdowns.map((b: any, i: number) => (
                  <div key={i} className="py-2.5 flex items-center justify-between text-xs">
                    <span className="font-bold text-white font-mono">{b.symbol}</span>
                    <span className="text-slate-300 font-mono">₹{b.price}</span>
                    <span className="text-rose-400 font-mono">{b.volume_ratio}x Vol</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === "volume" && (
        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-1.5">
            <Flame className="w-4 h-4" />
            <span>Unusual Volume Surges (&ge; 1.8x 20-MA)</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {unusualVolume.map((v: any, i: number) => (
              <div key={i} className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white font-mono">{v.symbol}</div>
                  <div className="text-[10px] text-slate-400">₹{v.price}</div>
                </div>
                <div className="text-xs font-bold font-mono text-amber-400">
                  {v.volume_ratio}x
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "momentum" && (
        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center space-x-1.5">
            <Compass className="w-4 h-4" />
            <span>Strong ADX Trend Momentum (ADX &gt; 25)</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {momentum.map((m: any, i: number) => (
              <div key={i} className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white font-mono">{m.symbol}</div>
                  <div className={`text-[10px] font-semibold ${m.trend === 'Bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {m.trend}
                  </div>
                </div>
                <div className="text-right text-xs font-mono">
                  <div className="text-white">RSI: {m.rsi}</div>
                  <div className="text-cyan-400">ADX: {m.adx}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
