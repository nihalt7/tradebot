"use client";

import React, { useState } from "react";
import { 
  History, Play, CheckCircle2, TrendingUp, TrendingDown, 
  BarChart, AlertTriangle, Layers, ShieldCheck 
} from "lucide-react";

export default function BacktestingView() {
  const [symbol, setSymbol] = useState("RELIANCE");
  const [strategy, setStrategy] = useState("EMA_CROSSOVER_RSI");
  const [timeframe, setTimeframe] = useState("15m");
  const [period, setPeriod] = useState("1mo");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("/api/backtesting/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: symbol.trim().toUpperCase(),
          strategy,
          timeframe,
          period
        })
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("Backtest failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <History className="w-5 h-5 text-blue-400" />
            <span>Quantitative Strategy Backtesting Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Tests algorithmic setups on genuine historical NSE candles. Strict prevention of lookahead and survivorship bias.
          </p>
        </div>
      </div>

      {/* Strategy Configuration Form */}
      <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638]">
        <form onSubmit={handleRunBacktest} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 items-end">
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase">NSE Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs font-mono text-white focus:outline-none focus:border-blue-500 uppercase"
              required
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Strategy Model</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="EMA_CROSSOVER_RSI">EMA Crossover (9/20) + RSI</option>
              <option value="SUPERTREND_BREAKOUT">Supertrend (10,3) + Volume Surge</option>
              <option value="VWAP_PULLBACK">VWAP Pullback Rebound</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Timeframe</label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="5m">5 Minutes (Intraday)</option>
              <option value="15m">15 Minutes (Swing)</option>
              <option value="1h">1 Hour</option>
              <option value="1d">1 Day</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Historical Period</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="5d">Last 5 Days</option>
              <option value="1mo">Last 1 Month</option>
              <option value="3mo">Last 3 Months</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold transition-colors shadow-lg shadow-blue-600/20 flex items-center justify-center space-x-1.5"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{loading ? "Simulating..." : "Run Backtest"}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Results Display */}
      {result && result.success && (
        <div className="space-y-6">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Win Rate</span>
              <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
                {result.win_rate}%
              </div>
              <div className="text-[10px] text-slate-500 mt-1">
                In-Sample: {result.in_sample_win_rate}% | Out-Sample: {result.out_of_sample_win_rate}%
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Profit Factor</span>
              <div className="text-2xl font-black text-blue-400 font-mono mt-1">
                {result.profit_factor}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Gross Profit / Gross Loss</div>
            </div>

            <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Drawdown</span>
              <div className="text-2xl font-black text-rose-400 font-mono mt-1">
                {result.max_drawdown_percent}%
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Peak-to-trough decline</div>
            </div>

            <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Net Return</span>
              <div className={`text-2xl font-black font-mono mt-1 ${result.total_net_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {result.total_net_pnl >= 0 ? `+₹${result.total_net_pnl}` : `₹${result.total_net_pnl}`} ({result.total_return_percent}%)
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Net after Indian taxes &amp; brokerage</div>
            </div>
          </div>

          {/* Out of sample notice */}
          <div className="p-3 rounded-lg bg-[#121826] border border-blue-500/20 text-xs text-slate-300 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong>Out-of-Sample Verification:</strong> 70% of historical bars were used for calibration and 30% held out for blind verification to prevent curve fitting.
            </span>
          </div>

          {/* Trade Execution Log Table */}
          <div className="rounded-xl border border-[#1E2638] bg-[#0E121B] overflow-hidden">
            <div className="px-4 py-3 bg-[#121722] border-b border-[#1E2638] font-bold text-xs text-white">
              Backtested Trades Sample Log ({result.total_trades} trades executed)
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#121722] text-slate-400 uppercase font-medium border-b border-[#1E2638]">
                  <tr>
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Side</th>
                    <th className="py-2.5 px-3">Entry (₹)</th>
                    <th className="py-2.5 px-3">Exit (₹)</th>
                    <th className="py-2.5 px-3">Qty</th>
                    <th className="py-2.5 px-3">Net P&amp;L (₹)</th>
                    <th className="py-2.5 px-3">Charges (₹)</th>
                    <th className="py-2.5 px-3">Exit Reason</th>
                    <th className="py-2.5 px-3">Sample</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1A2234]">
                  {result.recent_trades?.map((t: any) => {
                    const isProfit = t.net_pnl >= 0;
                    return (
                      <tr key={t.trade_num} className="hover:bg-[#141A28]">
                        <td className="py-2 px-3 font-mono text-slate-400">{t.trade_num}</td>
                        <td className="py-2 px-3">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${t.side === 'BUY' ? 'text-emerald-400 bg-emerald-500/15' : 'text-rose-400 bg-rose-500/15'}`}>
                            {t.side}
                          </span>
                        </td>
                        <td className="py-2 px-3 font-mono text-white">₹{t.entry_price}</td>
                        <td className="py-2 px-3 font-mono text-white">₹{t.exit_price}</td>
                        <td className="py-2 px-3 font-mono text-slate-300">{t.quantity}</td>
                        <td className={`py-2 px-3 font-mono font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isProfit ? `+₹${t.net_pnl}` : `₹${t.net_pnl}`}
                        </td>
                        <td className="py-2 px-3 font-mono text-slate-400">₹{t.charges}</td>
                        <td className="py-2 px-3 text-slate-300">{t.exit_reason}</td>
                        <td className="py-2 px-3 text-[10px] font-mono text-slate-400">{t.sample_type}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
