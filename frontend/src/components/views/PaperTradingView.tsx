"use client";

import React, { useState } from "react";
import { 
  PlaySquare, ArrowUpRight, ArrowDownRight, XCircle, 
  ShieldCheck, AlertCircle, RefreshCw, CheckCircle2 
} from "lucide-react";

interface PaperTradingViewProps {
  portfolio: any;
  onRefreshPortfolio?: () => void;
  onClosePosition?: (posId: string) => void;
  onPlaceManualOrder?: (order: any) => void;
}

export default function PaperTradingView({
  portfolio,
  onRefreshPortfolio,
  onClosePosition,
  onPlaceManualOrder
}: PaperTradingViewProps) {
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [sym, setSym] = useState("RELIANCE");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [qty, setQty] = useState(20);
  const [price, setPrice] = useState(1377.5);
  const [sl, setSl] = useState(1355.0);
  const [target, setTarget] = useState(1415.0);
  const [submitting, setSubmitting] = useState(false);
  const [orderFeedback, setOrderFeedback] = useState<string | null>(null);

  const openPositions = portfolio?.open_positions || [];
  const closedTrades = portfolio?.closed_trades || [];

  const handleOrderSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setOrderFeedback(null);

    try {
      const res = await fetch("/api/paper-trading/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: sym.trim().toUpperCase(),
          side,
          quantity: Number(qty),
          price: Number(price),
          stop_loss: Number(sl),
          target: Number(target)
        })
      });

      const data = await res.json();
      if (res.ok) {
        setOrderFeedback(`Order Executed: ${side} ${qty} ${sym} @ ₹${price}`);
        if (onRefreshPortfolio) onRefreshPortfolio();
        setTimeout(() => {
          setShowOrderModal(false);
          setOrderFeedback(null);
        }, 1500);
      } else {
        setOrderFeedback(`Rejected: ${data.detail || "Risk check failed"}`);
      }
    } catch (e: any) {
      setOrderFeedback(`Failed to place paper order`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = async (posId: string) => {
    try {
      const res = await fetch(`/api/paper-trading/close/${posId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Manual UI Exit" })
      });
      if (res.ok && onRefreshPortfolio) {
        onRefreshPortfolio();
      }
    } catch (e) {
      console.error("Error closing position:", e);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <PlaySquare className="w-5 h-5 text-amber-400" />
            <span>Paper Trading Terminal</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Simulated virtual order execution with live NSE prices. Zero real capital risk.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowOrderModal(true)}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors shadow-lg shadow-blue-600/20"
          >
            + New Paper Order
          </button>
          {onRefreshPortfolio && (
            <button
              onClick={onRefreshPortfolio}
              className="p-2 rounded-lg bg-[#141A28] hover:bg-[#1C2438] text-slate-300 border border-[#1E2638] transition-colors"
              title="Refresh Portfolio"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Capital Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Virtual Balance</span>
          <div className="text-lg md:text-xl font-black text-emerald-400 font-mono mt-1">
            ₹{portfolio?.available_balance?.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Invested Margin</span>
          <div className="text-lg md:text-xl font-black text-blue-400 font-mono mt-1">
            ₹{portfolio?.invested_margin?.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Unrealized MTM</span>
          <div className={`text-lg md:text-xl font-black font-mono mt-1 ${portfolio?.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {portfolio?.unrealized_pnl >= 0 ? `+₹${portfolio?.unrealized_pnl}` : `₹${portfolio?.unrealized_pnl}`}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#0E121B] border border-[#1E2638]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Realized Net P&amp;L</span>
          <div className={`text-lg md:text-xl font-black font-mono mt-1 ${portfolio?.realized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {portfolio?.realized_pnl >= 0 ? `+₹${portfolio?.realized_pnl}` : `₹${portfolio?.realized_pnl}`}
          </div>
        </div>
      </div>

      {/* Open Positions Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span>Open Paper Positions</span>
            <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[10px] font-mono">
              {openPositions.length} active
            </span>
          </h2>
        </div>

        <div className="rounded-xl border border-[#1E2638] bg-[#0E121B] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#121722] text-slate-400 uppercase font-medium border-b border-[#1E2638]">
                <tr>
                  <th className="py-3 px-4">Symbol</th>
                  <th className="py-3 px-4">Side</th>
                  <th className="py-3 px-4">Qty</th>
                  <th className="py-3 px-4">Entry (₹)</th>
                  <th className="py-3 px-4">Current (₹)</th>
                  <th className="py-3 px-4">Stop Loss</th>
                  <th className="py-3 px-4">Target</th>
                  <th className="py-3 px-4">MTM P&amp;L</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1A2234]">
                {openPositions.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-8 text-center text-slate-500 text-xs">
                      No open positions. Use "+ New Paper Order" or execute directly from any Trading Signal card.
                    </td>
                  </tr>
                ) : (
                  openPositions.map((pos: any) => {
                    const isProfit = (pos.unrealized_pnl || 0) >= 0;
                    return (
                      <tr key={pos.id} className="hover:bg-[#141A28] transition-colors">
                        <td className="py-3 px-4 font-bold text-white font-mono">{pos.symbol}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              pos.side === "BUY"
                                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                                : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                            }`}
                          >
                            {pos.side}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-white">{pos.quantity}</td>
                        <td className="py-3 px-4 font-mono text-slate-300">₹{pos.entry_price}</td>
                        <td className="py-3 px-4 font-mono font-bold text-white">₹{pos.current_price || pos.entry_price}</td>
                        <td className="py-3 px-4 font-mono text-rose-400">{pos.stop_loss ? `₹${pos.stop_loss}` : "-"}</td>
                        <td className="py-3 px-4 font-mono text-emerald-400">{pos.target ? `₹${pos.target}` : "-"}</td>
                        <td className="py-3 px-4 font-mono font-bold">
                          <span className={isProfit ? "text-emerald-400" : "text-rose-400"}>
                            {isProfit ? `+₹${pos.unrealized_pnl}` : `₹${pos.unrealized_pnl}`} ({pos.unrealized_pnl_percent}%)
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => handleClose(pos.id)}
                            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white border border-rose-500/30 text-[11px] font-semibold transition-colors"
                          >
                            Close MTM
                          </button>
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

      {/* Order Placement Modal */}
      {showOrderModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#101522] border border-[#1E2638] rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-[#1E2638]">
              <div className="flex items-center space-x-2">
                <PlaySquare className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">Place Virtual Paper Order</h3>
              </div>
              <button
                onClick={() => setShowOrderModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleOrderSubmit} className="space-y-4 mt-4">
              <div>
                <label className="text-[11px] font-semibold text-slate-400 uppercase">NSE Symbol</label>
                <input
                  type="text"
                  value={sym}
                  onChange={(e) => setSym(e.target.value)}
                  className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-400 uppercase">Action</label>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <button
                      type="button"
                      onClick={() => setSide("BUY")}
                      className={`py-1.5 rounded-lg text-xs font-bold ${side === 'BUY' ? 'bg-emerald-500 text-black' : 'bg-[#182030] text-slate-400'}`}
                    >
                      BUY
                    </button>
                    <button
                      type="button"
                      onClick={() => setSide("SELL")}
                      className={`py-1.5 rounded-lg text-xs font-bold ${side === 'SELL' ? 'bg-rose-500 text-white' : 'bg-[#182030] text-slate-400'}`}
                    >
                      SELL
                    </button>
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-400 uppercase">Quantity</label>
                  <input
                    type="number"
                    value={qty}
                    onChange={(e) => setQty(Number(e.target.value))}
                    className="w-full mt-1 px-3 py-1.5 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    required
                    min={1}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] font-semibold text-slate-400 uppercase">Price (₹)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={price}
                    onChange={(e) => setPrice(Number(e.target.value))}
                    className="w-full mt-1 px-2.5 py-1.5 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs font-mono text-white focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-rose-400 uppercase">Stop Loss (₹)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={sl}
                    onChange={(e) => setSl(Number(e.target.value))}
                    className="w-full mt-1 px-2.5 py-1.5 bg-[#141A28] border border-rose-500/30 rounded-lg text-xs font-mono text-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-emerald-400 uppercase">Target (₹)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={target}
                    onChange={(e) => setTarget(Number(e.target.value))}
                    className="w-full mt-1 px-2.5 py-1.5 bg-[#141A28] border border-emerald-500/30 rounded-lg text-xs font-mono text-white focus:outline-none"
                  />
                </div>
              </div>

              {orderFeedback && (
                <div className="p-2.5 rounded-lg bg-[#182030] text-xs text-center font-medium text-blue-300 border border-[#1E2638]">
                  {orderFeedback}
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all shadow-lg ${
                  side === 'BUY'
                    ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-950'
                    : 'bg-rose-500 hover:bg-rose-400 text-white'
                }`}
              >
                {submitting ? "Executing..." : `Submit Paper ${side} Order`}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
