"use client";

import React, { useState, useEffect } from "react";
import { CheckCircle, Clock, Zap, Target, Shield, Search } from "lucide-react";

export default function SignalHistoryView() {
  const [history, setHistory] = useState<any[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("/api/signals/history");
        if (res.ok) {
          const data = await res.json();
          setHistory(data.history || []);
        }
      } catch (e) {
        console.error("Failed to load signal history:", e);
      }
    };
    fetchHistory();
  }, []);

  const filtered = history.filter((s) => s.symbol.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14]">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <span>Historical Signal Log &amp; Performance Audit</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Complete audit trail of all generated trading signals with entry, target 1/2/3, and stop-loss levels.
        </p>
      </div>

      <div className="rounded-xl border border-[#1E2638] bg-[#0E121B] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#121722] text-slate-400 uppercase font-medium border-b border-[#1E2638]">
              <tr>
                <th className="py-3 px-4">Signal ID</th>
                <th className="py-3 px-4">Stock</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Setup Score</th>
                <th className="py-3 px-4">Entry (₹)</th>
                <th className="py-3 px-4">Stop Loss (₹)</th>
                <th className="py-3 px-4">Target 1 (₹)</th>
                <th className="py-3 px-4">R:R</th>
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1A2234]">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-500 text-xs">
                    No signals logged yet. Run an NSE market scan to populate signals.
                  </td>
                </tr>
              ) : (
                filtered.map((s, i) => (
                  <tr key={i} className="hover:bg-[#141A28]">
                    <td className="py-3 px-4 font-mono text-[10px] text-slate-500">{s.id?.slice(0, 15)}...</td>
                    <td className="py-3 px-4 font-bold text-white font-mono">{s.symbol}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.signal === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                        {s.signal}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-amber-400">{s.setup_score}/100</td>
                    <td className="py-3 px-4 font-mono text-white">₹{s.entry_price}</td>
                    <td className="py-3 px-4 font-mono text-rose-400">₹{s.stop_loss}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400">₹{s.target1}</td>
                    <td className="py-3 px-4 font-mono text-slate-300">1:{s.risk_reward}</td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{s.signal_time?.split(' ')[1] || s.signal_time}</td>
                    <td className="py-3 px-4">
                      <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        {s.status || "CONFIRMED"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
