import React, { useState } from 'react';
import { RefreshCw, ArrowUpRight, ArrowDownRight, Zap, Volume2, ShieldCheck, TrendingUp } from 'lucide-react';
import { ScannerResults, ScannerOpportunity } from '../types';

interface ScannerTabProps {
  scannerData: ScannerResults | null;
  onRefreshScan: () => Promise<void>;
  onAnalyzeStock: (symbol: string) => void;
  onExecuteTrade: (opp: ScannerOpportunity) => Promise<void>;
}

export const ScannerTab: React.FC<ScannerTabProps> = ({
  scannerData,
  onRefreshScan,
  onAnalyzeStock,
  onExecuteTrade
}) => {
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    setScanning(true);
    await onRefreshScan();
    setScanning(false);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-700/50 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <h2 className="text-lg font-bold text-white">Engine B: Automatic NSE Market Scanner</h2>
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            Real-time screening across eligible NSE equities. Multi-indicator confirmation with strict Golden Rule filtering.
          </p>
        </div>

        <button
          onClick={handleScan}
          disabled={scanning}
          className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-cyan-900/40 w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
          <span>{scanning ? 'Scanning NSE...' : 'Scan Now'}</span>
        </button>
      </div>

      <div className="mt-4 space-y-6">
        {/* TOP 5 BUY OPPORTUNITIES */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold text-emerald-400 flex items-center space-x-1.5 uppercase tracking-wide">
              <span>🟢 Top 5 BUY Opportunities</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 font-mono">Score ≥ 70</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {scannerData?.top_buys?.map((opp) => (
              <div
                key={opp.symbol}
                className="bg-[#202c33] rounded-xl p-3.5 border border-emerald-500/30 hover:border-emerald-500/60 shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-base font-extrabold text-white">{opp.symbol}</span>
                      <span className="text-xs text-gray-400 block">{opp.name || 'NSE Equity'}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-extrabold text-white">₹{opp.current_price?.toFixed(2)}</div>
                      <span className="text-emerald-400 text-xs font-bold">+{opp.change_pct?.toFixed(2)}%</span>
                    </div>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between bg-[#111b21] p-2 rounded-lg text-xs">
                    <span className="text-gray-400">Score: <strong className="text-emerald-400 font-extrabold">{opp.score}/100</strong></span>
                    <span className="text-gray-400">Volume: <strong className="text-amber-400">{opp.volume_multiplier}x Avg</strong></span>
                    <span className="text-gray-400">R:R: <strong className="text-cyan-400">1:{opp.risk_reward}</strong></span>
                  </div>

                  <div className="mt-2 grid grid-cols-3 gap-1 text-[10px] text-center">
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Entry Zone</span>
                      <span className="text-emerald-300 font-bold">₹{opp.entry_min?.toFixed(1)}</span>
                    </div>
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Stop Loss</span>
                      <span className="text-rose-400 font-bold">₹{opp.stop_loss?.toFixed(1)}</span>
                    </div>
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Target 2</span>
                      <span className="text-teal-300 font-bold">₹{opp.target_2?.toFixed(1)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-2.5 border-t border-gray-700/50 flex items-center space-x-2">
                  <button
                    onClick={() => onExecuteTrade(opp)}
                    className="flex-1 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center space-x-1"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Paper Buy</span>
                  </button>
                  <button
                    onClick={() => onAnalyzeStock(opp.symbol)}
                    className="px-2.5 py-1.5 rounded bg-[#111b21] hover:bg-gray-700 text-gray-300 text-xs font-semibold"
                  >
                    Inspect
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* TOP 5 SELL OPPORTUNITIES */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold text-rose-400 flex items-center space-x-1.5 uppercase tracking-wide">
              <span>🔴 Top 5 SELL Opportunities</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 font-mono">Score ≥ 70</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {scannerData?.top_sells?.map((opp) => (
              <div
                key={opp.symbol}
                className="bg-[#202c33] rounded-xl p-3.5 border border-rose-500/30 hover:border-rose-500/60 shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-base font-extrabold text-white">{opp.symbol}</span>
                      <span className="text-xs text-gray-400 block">{opp.name || 'NSE Equity'}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-extrabold text-white">₹{opp.current_price?.toFixed(2)}</div>
                      <span className="text-rose-400 text-xs font-bold">{opp.change_pct?.toFixed(2)}%</span>
                    </div>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between bg-[#111b21] p-2 rounded-lg text-xs">
                    <span className="text-gray-400">Score: <strong className="text-rose-400 font-extrabold">{opp.score}/100</strong></span>
                    <span className="text-gray-400">Volume: <strong className="text-amber-400">{opp.volume_multiplier}x Avg</strong></span>
                    <span className="text-gray-400">R:R: <strong className="text-cyan-400">1:{opp.risk_reward}</strong></span>
                  </div>

                  <div className="mt-2 grid grid-cols-3 gap-1 text-[10px] text-center">
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Entry Zone</span>
                      <span className="text-rose-300 font-bold">₹{opp.entry_max?.toFixed(1)}</span>
                    </div>
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Stop Loss</span>
                      <span className="text-rose-400 font-bold">₹{opp.stop_loss?.toFixed(1)}</span>
                    </div>
                    <div className="bg-[#182229] p-1.5 rounded">
                      <span className="text-gray-500 block">Target 2</span>
                      <span className="text-teal-300 font-bold">₹{opp.target_2?.toFixed(1)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-2.5 border-t border-gray-700/50 flex items-center space-x-2">
                  <button
                    onClick={() => onExecuteTrade(opp)}
                    className="flex-1 py-1.5 rounded bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex items-center justify-center space-x-1"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Paper Short</span>
                  </button>
                  <button
                    onClick={() => onAnalyzeStock(opp.symbol)}
                    className="px-2.5 py-1.5 rounded bg-[#111b21] hover:bg-gray-700 text-gray-300 text-xs font-semibold"
                  >
                    Inspect
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* UNUSUAL VOLUME SURGES */}
        <div>
          <h3 className="text-sm font-bold text-amber-400 flex items-center space-x-1.5 uppercase tracking-wide mb-2">
            <Volume2 className="w-4 h-4" />
            <span>Unusual Volume Activity (&gt; 1.5x 20-MA)</span>
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
            {scannerData?.volume_surges?.map((v) => (
              <div key={v.symbol} className="bg-[#202c33] p-2.5 rounded-lg border border-gray-700/50 text-center">
                <span className="font-bold text-white text-xs block">{v.symbol}</span>
                <span className="text-amber-400 font-extrabold text-sm block mt-0.5">{v.volume_multiplier}x</span>
                <span className={`text-[10px] font-semibold ${v.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {v.change_pct >= 0 ? '+' : ''}{v.change_pct?.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
