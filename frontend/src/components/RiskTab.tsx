import React, { useState } from 'react';
import { ShieldAlert, RefreshCw, CheckCircle2, AlertOctagon, Percent, Calculator } from 'lucide-react';
import { RiskSettings } from '../types';

interface RiskTabProps {
  settings: RiskSettings | null;
  onUpdateSettings: (settings: Partial<RiskSettings>) => Promise<void>;
  onResetDailyLoss: () => Promise<void>;
}

export const RiskTab: React.FC<RiskTabProps> = ({
  settings,
  onUpdateSettings,
  onResetDailyLoss
}) => {
  const [capital, setCapital] = useState(settings?.capital || 500000);
  const [riskPct, setRiskPct] = useState(settings?.risk_per_trade_pct || 1.0);
  const [maxDailyLoss, setMaxDailyLoss] = useState(settings?.max_daily_loss || 15000);
  const [maxOpenTrades, setMaxOpenTrades] = useState(settings?.max_open_trades || 5);
  const [paperMode, setPaperMode] = useState(settings?.paper_trading_enabled ?? true);
  const [saved, setSaved] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await onUpdateSettings({
      capital: Number(capital),
      risk_per_trade_pct: Number(riskPct),
      max_daily_loss: Number(maxDailyLoss),
      max_open_trades: Number(maxOpenTrades),
      paper_trading_enabled: paperMode
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const riskPerTradeMonetary = capital * (riskPct / 100);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
      {/* Header */}
      <div className="pb-4 border-b border-gray-700/50">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <span>Capital Protection & Risk Management Engine</span>
        </h2>
        <p className="text-xs text-gray-400 mt-0.5">
          Strict intraday capital allocation, automatic position sizing, and mandatory circuit breaker halt.
        </p>
      </div>

      <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Risk Configuration Form */}
        <div className="lg:col-span-2 bg-[#202c33] p-4 rounded-xl border border-gray-700/50 shadow-md">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center">
            <Calculator className="w-4 h-4 mr-1.5 text-emerald-400" />
            Trading Portfolio Constraints
          </h3>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Total Capital */}
              <div>
                <label className="text-xs text-gray-300 font-medium block mb-1">
                  Total Trading Capital (₹)
                </label>
                <input
                  type="number"
                  value={capital}
                  onChange={(e) => setCapital(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-bold"
                />
              </div>

              {/* Risk Per Trade % */}
              <div>
                <label className="text-xs text-gray-300 font-medium block mb-1">
                  Risk Per Trade (% of Capital)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="5.0"
                    value={riskPct}
                    onChange={(e) => setRiskPct(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-bold"
                  />
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    = ₹{riskPerTradeMonetary.toLocaleString('en-IN')} max risk
                  </span>
                </div>
              </div>

              {/* Max Daily Loss */}
              <div>
                <label className="text-xs text-gray-300 font-medium block mb-1">
                  Circuit Breaker Max Daily Loss (₹)
                </label>
                <input
                  type="number"
                  value={maxDailyLoss}
                  onChange={(e) => setMaxDailyLoss(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-rose-400 focus:outline-none focus:border-rose-500 font-bold"
                />
              </div>

              {/* Max Simultaneous Positions */}
              <div>
                <label className="text-xs text-gray-300 font-medium block mb-1">
                  Max Simultaneous Positions
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={maxOpenTrades}
                  onChange={(e) => setMaxOpenTrades(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-bold"
                />
              </div>
            </div>

            {/* Paper Trading Toggle */}
            <div className="p-3 bg-[#111b21] rounded-lg border border-gray-700/60 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-white">Paper Trading Mode</div>
                <div className="text-[11px] text-gray-400">
                  Simulate orders with zero real capital risk until verified.
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={paperMode}
                  onChange={(e) => setPaperMode(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
              </label>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center space-x-1.5"
            >
              {saved ? <CheckCircle2 className="w-4 h-4 text-white" /> : <ShieldAlert className="w-4 h-4" />}
              <span>{saved ? 'Risk Rules Saved & Active' : 'Save & Enforce Risk Parameters'}</span>
            </button>
          </form>
        </div>

        {/* Circuit Breaker Status & Indian Taxes */}
        <div className="space-y-4">
          {/* Circuit Breaker Status Card */}
          <div className="bg-[#202c33] p-4 rounded-xl border border-gray-700/50 shadow-md">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2 flex items-center">
              <AlertOctagon className="w-4 h-4 mr-1 text-rose-400" />
              Circuit Breaker Status
            </h4>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Trading Status:</span>
                <span className={`font-bold ${settings?.trading_halted ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {settings?.trading_halted ? 'HALTED (CIRCUIT BREAKER)' : 'ACTIVE (SAFE)'}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Current Daily Loss:</span>
                <span className="font-bold text-white">₹{settings?.current_daily_loss?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Daily Loss Limit:</span>
                <span className="font-bold text-rose-400">₹{settings?.max_daily_loss?.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <button
              onClick={onResetDailyLoss}
              className="mt-3.5 w-full py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-200 text-xs font-semibold flex items-center justify-center space-x-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset Daily Loss Counter</span>
            </button>
          </div>

          {/* Indian Statutory Charges Reference */}
          <div className="bg-[#202c33] p-4 rounded-xl border border-gray-700/50 text-xs text-gray-300">
            <h4 className="font-bold text-white mb-2 flex items-center">
              <Percent className="w-4 h-4 mr-1 text-cyan-400" /> Indian Equity Intraday Statutory Charges
            </h4>
            <ul className="space-y-1.5 text-[11px] text-gray-400">
              <li className="flex justify-between"><span>Brokerage:</span> <strong className="text-gray-200">₹20 / order max</strong></li>
              <li className="flex justify-between"><span>STT:</span> <strong className="text-gray-200">0.025% (Sell side only)</strong></li>
              <li className="flex justify-between"><span>Exchange Turnover:</span> <strong className="text-gray-200">0.00325%</strong></li>
              <li className="flex justify-between"><span>GST:</span> <strong className="text-gray-200">18% on (Brok + Exch)</strong></li>
              <li className="flex justify-between"><span>Stamp Duty:</span> <strong className="text-gray-200">0.003% (Buy side)</strong></li>
              <li className="flex justify-between"><span>SEBI Charges:</span> <strong className="text-gray-200">₹10 / crore</strong></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
