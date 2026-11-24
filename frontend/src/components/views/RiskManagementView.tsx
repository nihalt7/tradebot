"use client";

import React, { useState, useEffect } from "react";
import { 
  ShieldAlert, Calculator, DollarSign, Percent, 
  AlertTriangle, CheckCircle, Scale, ShieldCheck 
} from "lucide-react";

export default function RiskManagementView() {
  const [settings, setSettings] = useState<any>({
    initial_capital: 1000000.0,
    current_capital: 1000000.0,
    risk_per_trade_percent: 1.0,
    max_daily_loss: 20000.0,
    max_trades_per_day: 8,
    max_simultaneous_positions: 5,
    slippage_percent: 0.05,
    daily_loss_triggered: false,
    trades_today_count: 0,
    realized_daily_pnl: 0.0
  });

  // Position sizing calculator state
  const [calcEntry, setCalcEntry] = useState(2500.0);
  const [calcSl, setCalcSl] = useState(2475.0);
  const [calcResult, setCalcResult] = useState<any>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await fetch("/api/risk/settings");
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
      }
    } catch (e) {
      console.error("Failed to load risk settings:", e);
    }
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/risk/calculate-position", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entry_price: Number(calcEntry),
          stop_loss: Number(calcSl),
          capital: settings.current_capital,
          risk_percent: settings.risk_per_trade_percent
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
      }
    } catch (e) {
      console.error("Error calculating position:", e);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>Risk Management &amp; Capital Protection</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Enforces strict capital preservation rules, position sizing, daily loss circuit breakers, and statutory cost estimation.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <div className={`px-3 py-1 rounded-md text-xs font-bold border flex items-center space-x-1.5 ${
            settings.daily_loss_triggered
              ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
              : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
          }`}>
            <ShieldCheck className="w-4 h-4" />
            <span>Circuit Breaker: {settings.daily_loss_triggered ? "HALTED" : "ACTIVE & PROTECTED"}</span>
          </div>
        </div>
      </div>

      {/* Grid: Settings & Position Size Calculator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Risk Parameters */}
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Scale className="w-4 h-4 text-blue-400" />
            <span>Active Risk Limits &amp; Parameters</span>
          </h2>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Risk Per Trade</span>
              <div className="text-lg font-bold text-white font-mono mt-1">
                {settings.risk_per_trade_percent}% <span className="text-xs text-slate-400">(₹10,000)</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Daily Loss</span>
              <div className="text-lg font-bold text-rose-400 font-mono mt-1">
                ₹{settings.max_daily_loss?.toLocaleString("en-IN")}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Simultaneous Positions</span>
              <div className="text-lg font-bold text-blue-400 font-mono mt-1">
                {settings.max_simultaneous_positions} Stocks
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Daily Trades</span>
              <div className="text-lg font-bold text-white font-mono mt-1">
                {settings.trades_today_count} / {settings.max_trades_per_day} Trades
              </div>
            </div>
          </div>

          {/* Indian Statutory Charges & Taxes Breakdown Box */}
          <div className="p-4 rounded-xl bg-[#101522] border border-[#1E2638] space-y-2.5">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Indian Equity Intraday Statutory Breakdown
            </h3>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
              <div>• Brokerage: <span className="text-slate-200 font-mono">₹20 flat or 0.05%</span></div>
              <div>• STT: <span className="text-slate-200 font-mono">0.025% on sell</span></div>
              <div>• NSE Turnover: <span className="text-slate-200 font-mono">0.00325%</span></div>
              <div>• GST: <span className="text-slate-200 font-mono">18% on fees</span></div>
              <div>• SEBI Turnover: <span className="text-slate-200 font-mono">₹10 / crore</span></div>
              <div>• Stamp Duty: <span className="text-slate-200 font-mono">0.003% on buy</span></div>
            </div>
          </div>
        </div>

        {/* Right: Position Sizing Calculator */}
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Calculator className="w-4 h-4 text-emerald-400" />
            <span>Quantitative Position Size Calculator</span>
          </h2>
          <p className="text-xs text-slate-400">
            Calculates exact share count based on risk tolerance and stop loss distance.
          </p>

          <form onSubmit={handleCalculate} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-400 uppercase">Entry Price (₹)</label>
                <input
                  type="number"
                  step="0.05"
                  value={calcEntry}
                  onChange={(e) => setCalcEntry(Number(e.target.value))}
                  className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-rose-400 uppercase">Stop Loss Price (₹)</label>
                <input
                  type="number"
                  step="0.05"
                  value={calcSl}
                  onChange={(e) => setCalcSl(Number(e.target.value))}
                  className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-rose-500/30 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-rose-500"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors shadow-lg shadow-blue-600/20"
            >
              Calculate Recommended Position
            </button>
          </form>

          {/* Calculator Output Display */}
          {calcResult && (
            <div className="p-4 rounded-xl bg-[#121929] border border-blue-500/30 space-y-2 mt-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Recommended Quantity:</span>
                <span className="text-base font-black text-white font-mono">
                  {calcResult.recommended_quantity} shares
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Total Trade Value:</span>
                <span className="text-sm font-bold text-white font-mono">
                  ₹{calcResult.total_trade_value?.toLocaleString("en-IN")}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Risk per Share:</span>
                <span className="text-sm font-bold text-rose-400 font-mono">
                  ₹{calcResult.per_share_risk}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Est. Brokerage &amp; Taxes:</span>
                <span className="text-sm font-bold text-amber-400 font-mono">
                  ₹{calcResult.estimated_charges}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
