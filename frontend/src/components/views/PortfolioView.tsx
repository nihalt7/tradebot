"use client";

import React from "react";
import { Briefcase, Wallet, TrendingUp, PieChart, ShieldCheck, CheckCircle2 } from "lucide-react";

interface PortfolioViewProps {
  portfolio: any;
  onNavigateToPaperTrading?: () => void;
}

export default function PortfolioView({
  portfolio,
  onNavigateToPaperTrading
}: PortfolioViewProps) {
  const initialCap = portfolio?.virtual_initial_capital || 1000000;
  const netWorth = portfolio?.net_worth || 1000000;
  const availableBal = portfolio?.available_balance || 1000000;
  const invested = portfolio?.invested_margin || 0;
  const unrealized = portfolio?.unrealized_pnl || 0;
  const realized = portfolio?.realized_pnl || 0;
  const totalPnl = portfolio?.total_pnl || 0;
  const winRate = portfolio?.win_rate || 0;
  const positions = portfolio?.open_positions || [];

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Briefcase className="w-5 h-5 text-blue-400" />
            <span>Virtual Portfolio &amp; Capital Allocation</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time equity curve, margin deployment, and mark-to-market performance.
          </p>
        </div>

        <div className="px-3 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
          MODE: PAPER TRADING
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Net Worth</span>
          <div className="mt-2 text-xl md:text-2xl font-black text-white font-mono">
            ₹{netWorth.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Base Capital: ₹{initialCap.toLocaleString("en-IN")}</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Available Cash</span>
          <div className="mt-2 text-xl md:text-2xl font-black text-emerald-400 font-mono">
            ₹{availableBal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Free Trading Margin</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Deployed Margin</span>
          <div className="mt-2 text-xl md:text-2xl font-black text-blue-400 font-mono">
            ₹{invested.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">In {positions.length} Active Positions</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Net P&amp;L</span>
          <div className={`mt-2 text-xl md:text-2xl font-black font-mono ${totalPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {totalPnl >= 0 ? `+₹${totalPnl.toLocaleString("en-IN")}` : `-₹${Math.abs(totalPnl).toLocaleString("en-IN")}`}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Win Rate: {winRate}%</div>
        </div>
      </div>

      {/* Asset Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <PieChart className="w-4 h-4 text-blue-400" />
            <span>Capital Deployment Ratio</span>
          </h3>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Cash Margin</span>
                <span className="font-mono text-emerald-400 font-semibold">
                  {Math.round((availableBal / netWorth) * 100)}%
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#182030] overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${Math.min(100, Math.round((availableBal / netWorth) * 100))}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Deployed Equity Exposure</span>
                <span className="font-mono text-blue-400 font-semibold">
                  {Math.round((invested / netWorth) * 100)}%
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#182030] overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${Math.min(100, Math.round((invested / netWorth) * 100))}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638] text-xs text-slate-300 leading-relaxed">
            <ShieldCheck className="w-4 h-4 text-emerald-400 inline mr-1.5" />
            Risk rule active: No single position may exceed 25% of total capital.
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>P&amp;L Performance Breakdown</span>
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase">Unrealized MTM P&amp;L</span>
              <div className={`text-base font-bold font-mono mt-1 ${unrealized >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {unrealized >= 0 ? `+₹${unrealized}` : `₹${unrealized}`}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#141A28] border border-[#1E2638]">
              <span className="text-[10px] text-slate-400 uppercase">Realized Closed P&amp;L</span>
              <div className={`text-base font-bold font-mono mt-1 ${realized >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {realized >= 0 ? `+₹${realized}` : `₹${realized}`}
              </div>
            </div>
          </div>

          {onNavigateToPaperTrading && (
            <button
              onClick={onNavigateToPaperTrading}
              className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors"
            >
              Open Paper Trading Terminal
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
