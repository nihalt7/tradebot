import React, { useState } from 'react';
import { History, Play, Award, TrendingUp, DollarSign, Percent, ShieldCheck } from 'lucide-react';
import { BacktestResult } from '../types';
import { api } from '../services/api';

export const BacktestTab: React.FC = () => {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [timeframe, setTimeframe] = useState('5m');
  const [capital, setCapital] = useState(500000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.runBacktest(symbol, timeframe, capital, riskPct);
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
      {/* Header */}
      <div className="pb-4 border-b border-gray-700/50">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <History className="w-5 h-5 text-cyan-400" />
          <span>Strategy Backtesting & Quantitative Validation</span>
        </h2>
        <p className="text-xs text-gray-400 mt-0.5">
          Evaluate historical win rate, profit factor, slippage, and net returns after Indian statutory charges.
        </p>
      </div>

      {/* Control Panel */}
      <form onSubmit={handleRunBacktest} className="mt-4 bg-[#202c33] p-4 rounded-xl border border-gray-700/50 shadow-md">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="text-gray-300 font-medium block mb-1">Stock Symbol</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-white font-bold focus:outline-none focus:border-cyan-500"
            >
              <option value="RELIANCE">RELIANCE</option>
              <option value="TCS">TCS</option>
              <option value="HDFCBANK">HDFCBANK</option>
              <option value="INFY">INFY</option>
              <option value="ICICIBANK">ICICIBANK</option>
              <option value="BHARTIARTL">BHARTIARTL</option>
              <option value="SBIN">SBIN</option>
              <option value="LT">LT</option>
            </select>
          </div>

          <div>
            <label className="text-gray-300 font-medium block mb-1">Timeframe</label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-white font-bold focus:outline-none focus:border-cyan-500"
            >
              <option value="5m">5 Minutes (Intraday)</option>
              <option value="15m">15 Minutes (Swing)</option>
              <option value="1h">1 Hour (Macro)</option>
            </select>
          </div>

          <div>
            <label className="text-gray-300 font-medium block mb-1">Starting Capital (₹)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-white font-bold focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg shadow-md flex items-center justify-center space-x-1.5"
            >
              <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Simulating...' : 'Run Backtest'}</span>
            </button>
          </div>
        </div>
      </form>

      {/* Results View */}
      {result && (
        <div className="mt-4 space-y-4">
          {/* Metrics Scorecard */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Win Rate</span>
              <span className="text-emerald-400 text-lg font-extrabold mt-0.5 block">{result.win_rate}%</span>
              <span className="text-[10px] text-gray-500">{result.winning_trades}W / {result.losing_trades}L</span>
            </div>

            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Profit Factor</span>
              <span className="text-white text-lg font-extrabold mt-0.5 block">{result.profit_factor}</span>
              <span className="text-[10px] text-emerald-400 font-semibold">Net Positive</span>
            </div>

            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Net Profit</span>
              <span className={`text-lg font-extrabold mt-0.5 block ${result.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {result.net_profit >= 0 ? '+' : ''}₹{result.net_profit.toLocaleString('en-IN')}
              </span>
              <span className="text-[10px] text-gray-400">{result.total_return_pct}% ROI</span>
            </div>

            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Max Drawdown</span>
              <span className="text-rose-400 text-lg font-extrabold mt-0.5 block">-{result.max_drawdown}%</span>
              <span className="text-[10px] text-gray-500">Peak-to-Trough</span>
            </div>

            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Total Trades</span>
              <span className="text-white text-lg font-extrabold mt-0.5 block">{result.total_trades}</span>
              <span className="text-[10px] text-gray-500">Closed Intraday</span>
            </div>

            <div className="bg-[#202c33] p-3 rounded-xl border border-gray-700/50">
              <span className="text-gray-400 text-[10px] uppercase font-semibold block">Total Taxes & Brok</span>
              <span className="text-amber-400 text-lg font-extrabold mt-0.5 block">₹{result.total_charges}</span>
              <span className="text-[10px] text-gray-500">STT + GST + NSE</span>
            </div>
          </div>

          {/* Trade Log Table */}
          <div className="bg-[#202c33] p-4 rounded-xl border border-gray-700/50 overflow-x-auto">
            <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wide mb-3">
              Executed Trade Audit Log ({result.trades.length} Trades)
            </h3>
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-[#111b21] text-gray-400 uppercase text-[10px]">
                <tr>
                  <th className="p-2">#</th>
                  <th className="p-2">Side</th>
                  <th className="p-2">Qty</th>
                  <th className="p-2">Entry</th>
                  <th className="p-2">Exit</th>
                  <th className="p-2">Gross P&L</th>
                  <th className="p-2">Charges</th>
                  <th className="p-2">Net P&L</th>
                  <th className="p-2">Exit Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/40">
                {result.trades.map((t) => (
                  <tr key={t.trade_num} className="hover:bg-gray-800/40">
                    <td className="p-2 font-mono">{t.trade_num}</td>
                    <td className="p-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        t.direction === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                      }`}>
                        {t.direction}
                      </span>
                    </td>
                    <td className="p-2 font-mono">{t.quantity}</td>
                    <td className="p-2 font-mono">₹{t.entry_price}</td>
                    <td className="p-2 font-mono">₹{t.exit_price}</td>
                    <td className="p-2 font-mono">₹{t.gross_pnl}</td>
                    <td className="p-2 font-mono text-gray-400">₹{t.charges}</td>
                    <td className={`p-2 font-bold font-mono ${t.net_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {t.net_pnl >= 0 ? '+' : ''}₹{t.net_pnl}
                    </td>
                    <td className="p-2 text-[11px] text-gray-400">{t.exit_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
