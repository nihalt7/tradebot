"use client";

import React, { useState, useEffect } from "react";
import { 
  Star, Plus, Trash2, TrendingUp, TrendingDown, 
  BarChart2, Zap, Search, RefreshCw 
} from "lucide-react";

interface WatchlistViewProps {
  onAnalyzeStock?: (symbol: string) => void;
  onViewChart?: (symbol: string) => void;
}

export default function WatchlistView({
  onAnalyzeStock,
  onViewChart
}: WatchlistViewProps) {
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [newSymbol, setNewSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [filterQuery, setFilterQuery] = useState("");

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/watchlist");
      if (res.ok) {
        const data = await res.json();
        setWatchlist(data.watchlist || []);
      }
    } catch (e) {
      console.error("Failed to load watchlist:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim()) return;

    try {
      const res = await fetch("/api/watchlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: newSymbol.trim().toUpperCase() })
      });
      if (res.ok) {
        setNewSymbol("");
        fetchWatchlist();
      }
    } catch (e) {
      console.error("Failed to add symbol:", e);
    }
  };

  const handleRemove = async (symbol: string) => {
    try {
      const res = await fetch(`/api/watchlist/${symbol}`, {
        method: "DELETE"
      });
      if (res.ok) {
        fetchWatchlist();
      }
    } catch (e) {
      console.error("Failed to delete symbol:", e);
    }
  };

  const filtered = watchlist.filter((item) =>
    item.symbol.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header & Add form */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Star className="w-5 h-5 text-amber-400 fill-amber-400" />
            <span>Personal Stock Watchlist</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monitors real-time technical conditions and multi-timeframe confirmed alerts for your assets.
          </p>
        </div>

        {/* Add symbol form */}
        <div className="flex items-center space-x-2">
          <form onSubmit={handleAdd} className="flex items-center space-x-1.5">
            <input
              type="text"
              placeholder="Add symbol (e.g. SBIN)..."
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              className="px-3 py-1.5 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 uppercase font-mono w-48"
            />
            <button
              type="submit"
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </form>

          <button
            onClick={fetchWatchlist}
            className="p-1.5 rounded-lg bg-[#141A28] hover:bg-[#1C2438] text-slate-300 border border-[#1E2638] transition-colors"
            title="Refresh Quotes"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex items-center justify-between">
        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Filter watchlist..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="text-xs text-slate-400">
          Showing <span className="text-white font-bold">{filtered.length}</span> stocks
        </div>
      </div>

      {/* Watchlist Table */}
      <div className="rounded-xl border border-[#1E2638] bg-[#0E121B] overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#121722] text-slate-400 uppercase font-medium border-b border-[#1E2638]">
              <tr>
                <th className="py-3 px-4">Stock</th>
                <th className="py-3 px-4">Exchange</th>
                <th className="py-3 px-4">LTP (₹)</th>
                <th className="py-3 px-4">Change %</th>
                <th className="py-3 px-4">RSI (14)</th>
                <th className="py-3 px-4">VWAP (₹)</th>
                <th className="py-3 px-4">Trend</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1A2234]">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 text-xs">
                    {loading ? "Fetching live market quotes..." : "Your watchlist is empty. Add a symbol above."}
                  </td>
                </tr>
              ) : (
                filtered.map((stock) => {
                  const isUp = stock.change >= 0;
                  return (
                    <tr key={stock.symbol} className="hover:bg-[#141A28] transition-colors">
                      <td className="py-3 px-4 font-bold text-white font-mono flex items-center space-x-2">
                        <span>{stock.symbol}</span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {stock.exchange}
                      </td>
                      <td className="py-3 px-4 font-bold font-mono text-white">
                        ₹{stock.price?.toLocaleString("en-IN")}
                      </td>
                      <td className="py-3 px-4 font-mono font-semibold">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] ${
                            isUp ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                          }`}
                        >
                          {stock.percent_change > 0 ? `+${stock.percent_change}` : stock.percent_change}%
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {stock.rsi}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {stock.vwap !== "N/A" ? `₹${stock.vwap}` : "N/A"}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            stock.trend === "BULLISH"
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : stock.trend === "BEARISH"
                              ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                              : "bg-slate-700/30 text-slate-400"
                          }`}
                        >
                          {stock.trend}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          {onAnalyzeStock && (
                            <button
                              onClick={() => onAnalyzeStock(stock.symbol)}
                              className="px-2 py-1 rounded bg-[#182030] hover:bg-blue-600/30 text-blue-400 font-medium text-[11px] border border-[#1E2638] transition-colors"
                            >
                              Analyze
                            </button>
                          )}
                          {onViewChart && (
                            <button
                              onClick={() => onViewChart(stock.symbol)}
                              className="px-2 py-1 rounded bg-[#182030] hover:bg-slate-700 text-slate-300 font-medium text-[11px] border border-[#1E2638] transition-colors"
                            >
                              Chart
                            </button>
                          )}
                          <button
                            onClick={() => handleRemove(stock.symbol)}
                            className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                            title="Remove"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
