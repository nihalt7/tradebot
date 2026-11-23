import React from 'react';
import { Briefcase, XCircle, TrendingUp, TrendingDown, Shield } from 'lucide-react';
import { ActivePosition } from '../types';

interface PortfolioTabProps {
  positions: ActivePosition[];
  onClosePosition: (id: number) => Promise<void>;
}

export const PortfolioTab: React.FC<PortfolioTabProps> = ({ positions, onClosePosition }) => {
  const totalUnrealizedPnl = positions.reduce((acc, p) => acc + (p.pnl || 0), 0);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-700/50">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Briefcase className="w-5 h-5 text-emerald-400" />
            <span>Active Portfolio & Paper Trading</span>
          </h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Default Mode: Paper Trading (Real capital protected. No real orders sent without broker authorization.)
          </p>
        </div>

        {/* Unrealized PnL summary */}
        <div className="bg-[#202c33] px-4 py-2 rounded-xl border border-gray-700/50 text-right">
          <span className="text-[10px] text-gray-400 uppercase font-semibold block">Total Unrealized P&L</span>
          <span className={`text-base font-extrabold flex items-center justify-end ${totalUnrealizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {totalUnrealizedPnl >= 0 ? '+' : ''}₹{totalUnrealizedPnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {positions.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-gray-500">
          <Shield className="w-12 h-12 text-gray-600 mb-3" />
          <h4 className="text-sm font-semibold text-gray-300">No Open Paper Positions</h4>
          <p className="text-xs max-w-sm mt-1 text-gray-500">
            Execute a trade from an AI Trading Alert Card or from the Live Market Scanner to track real-time intraday P&L and target progression.
          </p>
        </div>
      ) : (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {positions.map((pos) => {
            const isProfit = (pos.pnl || 0) >= 0;
            const isBuy = pos.direction === 'BUY';

            return (
              <div
                key={pos.id}
                className="bg-[#202c33] rounded-xl p-4 border border-gray-700/50 shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-extrabold text-white">{pos.symbol}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                          isBuy ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                        }`}>
                          {pos.direction} • {pos.quantity} QTY
                        </span>
                      </div>
                      <span className="text-[11px] text-gray-400 mt-0.5 block">
                        Mode: <span className="text-amber-400 font-semibold">{pos.mode}</span>
                      </span>
                    </div>

                    <div className="text-right">
                      <div className={`text-base font-extrabold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isProfit ? '+' : ''}₹{pos.pnl?.toFixed(2)}
                      </div>
                      <div className={`text-xs font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isProfit ? '+' : ''}{pos.pnl_percentage?.toFixed(2)}%
                      </div>
                    </div>
                  </div>

                  {/* Price Tracker */}
                  <div className="mt-3 grid grid-cols-2 gap-2 bg-[#111b21] p-2.5 rounded-lg text-xs">
                    <div>
                      <span className="text-gray-500 text-[10px] block uppercase">Entry Price</span>
                      <span className="text-white font-bold">₹{pos.entry_price?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] block uppercase">Current LTP</span>
                      <span className="text-white font-bold">₹{pos.current_price?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] block uppercase">Stop Loss</span>
                      <span className="text-rose-400 font-bold">₹{pos.stop_loss?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] block uppercase">Target 1</span>
                      <span className="text-emerald-400 font-bold">₹{pos.target_1?.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Close Button */}
                <div className="mt-4 pt-3 border-t border-gray-700/50">
                  <button
                    onClick={() => onClosePosition(pos.id)}
                    className="w-full py-2 rounded-lg bg-rose-600/20 hover:bg-rose-600 hover:text-white text-rose-400 border border-rose-500/40 text-xs font-bold transition-all flex items-center justify-center space-x-1.5"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Square Off Position (Market)</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
