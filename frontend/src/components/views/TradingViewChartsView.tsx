"use client";

import React, { useState, useEffect } from "react";
import TradingViewWidget from "../common/TradingViewWidget";
import LightweightChart from "../common/LightweightChart";
import { CandlestickChart, Search, Maximize2, Layers } from "lucide-react";

interface TradingViewChartsViewProps {
  initialSymbol?: string;
}

export default function TradingViewChartsView({
  initialSymbol = "RELIANCE"
}: TradingViewChartsViewProps) {
  const [selectedSymbol, setSelectedSymbol] = useState(initialSymbol);
  const [searchVal, setSearchVal] = useState("");
  const [timeframe, setTimeframe] = useState("5");
  const [chartMode, setChartMode] = useState<"tradingview" | "lightweight">("tradingview");
  const [candles, setCandles] = useState<any[]>([]);

  const popularSymbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
    "SBIN", "BHARTIARTL", "TATAMOTORS", "NIFTY", "BANKNIFTY"
  ];

  // Fetch candles if lightweight chart is selected
  useEffect(() => {
    if (chartMode === "lightweight") {
      const fetchCandles = async () => {
        try {
          const res = await fetch(`/api/market/history/${selectedSymbol}?timeframe=5m`);
          if (res.ok) {
            const data = await res.json();
            setCandles(data.candles || []);
          }
        } catch (e) {
          console.error("Failed to load candles:", e);
        }
      };
      fetchCandles();
    }
  }, [selectedSymbol, chartMode]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchVal.trim()) {
      setSelectedSymbol(searchVal.trim().toUpperCase());
      setSearchVal("");
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0B0E14] overflow-hidden">
      {/* Chart Control Bar */}
      <div className="p-3 border-b border-[#1E2638] bg-[#0E121B] flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center space-x-2">
          {/* Symbol chips */}
          <div className="flex items-center space-x-1 overflow-x-auto no-scrollbar">
            {popularSymbols.map((sym) => (
              <button
                key={sym}
                onClick={() => setSelectedSymbol(sym)}
                className={`px-2.5 py-1 rounded-md text-xs font-mono font-medium transition-colors ${
                  selectedSymbol === sym
                    ? "bg-blue-600 text-white font-bold"
                    : "bg-[#141A28] text-slate-400 hover:text-white border border-[#1E2638]"
                }`}
              >
                {sym}
              </button>
            ))}
          </div>
        </div>

        {/* Right side: Search & Switcher */}
        <div className="flex items-center space-x-2">
          {/* Mode Switcher */}
          <div className="flex items-center bg-[#141A28] p-0.5 rounded-lg border border-[#1E2638]">
            <button
              onClick={() => setChartMode("tradingview")}
              className={`px-2 py-1 rounded text-xs font-medium ${
                chartMode === "tradingview" ? "bg-blue-600 text-white" : "text-slate-400"
              }`}
            >
              TradingView Advanced
            </button>
            <button
              onClick={() => setChartMode("lightweight")}
              className={`px-2 py-1 rounded text-xs font-medium ${
                chartMode === "lightweight" ? "bg-blue-600 text-white" : "text-slate-400"
              }`}
            >
              Lightweight OHLCV
            </button>
          </div>

          {/* Search symbol */}
          <form onSubmit={handleSearch} className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search NSE/BSE..."
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              className="pl-8 pr-3 py-1 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white placeholder-slate-500 w-36 focus:outline-none focus:border-blue-500 font-mono"
            />
          </form>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div className="flex-1 p-2 md:p-3 relative overflow-hidden">
        {chartMode === "tradingview" ? (
          <TradingViewWidget
            symbol={selectedSymbol}
            interval={timeframe}
            height="100%"
          />
        ) : (
          <div className="h-full flex flex-col justify-center">
            {candles.length > 0 ? (
              <LightweightChart candles={candles} symbol={selectedSymbol} height={600} />
            ) : (
              <div className="p-12 text-center text-slate-400 text-xs">
                Loading genuine intraday candles for {selectedSymbol}...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
