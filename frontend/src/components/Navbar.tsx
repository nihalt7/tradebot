import React from 'react';
import { TrendingUp, TrendingDown, Sun, Moon, ShieldAlert, Cpu, Activity } from 'lucide-react';
import { DashboardOverview } from '../types';

interface NavbarProps {
  overview: DashboardOverview | null;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  onOpenRisk: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ overview, darkMode, setDarkMode, onOpenRisk }) => {
  const nifty = overview?.indices?.['NIFTY 50'];
  const bankNifty = overview?.indices?.['BANK NIFTY'];
  const sensex = overview?.indices?.['SENSEX'];

  const isBullish = overview?.market_trend === 'Bullish';

  return (
    <header className="h-14 border-b border-gray-700/50 bg-[#111b21] dark:bg-[#111b21] text-gray-200 px-4 flex items-center justify-between z-30 select-none shadow-sm">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-900/30">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold tracking-tight text-white text-base">TradePulse <span className="text-emerald-400">AI</span></span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold uppercase tracking-wider border border-emerald-500/30">
              NSE Intraday
            </span>
          </div>
          <div className="text-[11px] text-gray-400 flex items-center space-x-2">
            <span className="flex items-center text-emerald-400"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span> Engine A: Watchlist</span>
            <span>•</span>
            <span className="flex items-center text-cyan-400"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-1 animate-pulse"></span> Engine B: Scanner</span>
          </div>
        </div>
      </div>

      {/* Indices Ticker Bar */}
      <div className="hidden lg:flex items-center space-x-6 text-xs">
        {/* NIFTY 50 */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#202c33] border border-gray-700/50">
          <span className="text-gray-400 font-medium">NIFTY 50</span>
          <span className="font-bold text-white">₹{nifty ? nifty.price.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '23,850.50'}</span>
          <span className={`flex items-center font-semibold ${(nifty?.change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {(nifty?.change_pct || 0) >= 0 ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
            {(nifty?.change_pct || 0) >= 0 ? '+' : ''}{nifty ? nifty.change_pct.toFixed(2) : '+0.32'}%
          </span>
        </div>

        {/* BANK NIFTY */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#202c33] border border-gray-700/50">
          <span className="text-gray-400 font-medium">BANK NIFTY</span>
          <span className="font-bold text-white">₹{bankNifty ? bankNifty.price.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '51,240.80'}</span>
          <span className={`flex items-center font-semibold ${(bankNifty?.change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {(bankNifty?.change_pct || 0) >= 0 ? '+' : ''}{bankNifty ? bankNifty.change_pct.toFixed(2) : '+0.45'}%
          </span>
        </div>

        {/* SENSEX */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#202c33] border border-gray-700/50">
          <span className="text-gray-400 font-medium">SENSEX</span>
          <span className="font-bold text-white">₹{sensex ? sensex.price.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '78,620.40'}</span>
          <span className={`flex items-center font-semibold ${(sensex?.change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {(sensex?.change_pct || 0) >= 0 ? '+' : ''}{sensex ? sensex.change_pct.toFixed(2) : '+0.28'}%
          </span>
        </div>

        {/* Market Breadth */}
        <div className="flex items-center space-x-2 bg-[#202c33]/70 px-2.5 py-1 rounded text-[11px] text-gray-300 border border-gray-700/40">
          <Activity className="w-3.5 h-3.5 text-amber-400" />
          <span>A/D:</span>
          <span className="text-emerald-400 font-bold">{overview?.advances ?? 32} Adv</span>
          <span>/</span>
          <span className="text-rose-400 font-bold">{overview?.declines ?? 18} Dec</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3 text-xs">
        {/* Market Trend Badge */}
        <div className={`px-2.5 py-1 rounded font-semibold text-[11px] flex items-center space-x-1.5 ${
          isBullish 
            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
            : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
        }`}>
          <span className={`w-2 h-2 rounded-full ${isBullish ? 'bg-emerald-400' : 'bg-rose-400'} animate-ping`}></span>
          <span>Trend: {overview?.market_trend || 'Bullish'}</span>
        </div>

        {/* Risk Manager Shortcut */}
        <button 
          onClick={onOpenRisk}
          className="flex items-center space-x-1 px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-colors"
          title="Risk Controls & Circuit Breaker"
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span className="hidden sm:inline font-medium">Risk: Paper Mode</span>
        </button>

        {/* Dark/Light mode toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-1.5 rounded bg-[#202c33] text-gray-300 hover:text-white hover:bg-gray-700/50 transition-colors"
          title="Toggle Dark/Light Mode"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-gray-400" />}
        </button>
      </div>
    </header>
  );
};
