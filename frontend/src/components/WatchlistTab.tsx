import React, { useState } from 'react';
import { Plus, Trash2, TrendingUp, TrendingDown, Eye, Activity } from 'lucide-react';
import { WatchlistItem } from '../types';

interface WatchlistTabProps {
  watchlist: WatchlistItem[];
  onAddStock: (symbol: string) => Promise<void>;
  onRemoveStock: (symbol: string) => Promise<void>;
  onAnalyzeStock: (symbol: string) => void;
}

export const WatchlistTab: React.FC<WatchlistTabProps> = ({
  watchlist,
  onAddStock,
  onRemoveStock,
  onAnalyzeStock
}) => {
  const [newSymbol, setNewSymbol] = useState('');
  const [adding, setAdding] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim() || adding) return;
    setAdding(true);
    await onAddStock(newSymbol.trim().toUpperCase());
    setNewSymbol('');
    setAdding(false);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-700/50 gap-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
            Engine A: Personal Watchlist Monitoring
          </h2>
          <p className="text-xs text-gray-400">
            Continuously monitors chosen NSE stocks. When score ≥ 75, instant alert card appears in chat.
          </p>
        </div>

        {/* Add Stock Form */}
        <form onSubmit={handleAdd} className="flex items-center space-x-2">
          <input
            type="text"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            placeholder="Symbol (e.g. RELIANCE, TCS)"
            className="px-3 py-1.5 rounded-lg bg-[#202c33] border border-gray-700 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
          />
          <button
            type="submit"
            disabled={adding}
            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center space-x-1 shadow"
          >
            <Plus className="w-4 h-4" />
            <span>{adding ? 'Adding...' : 'Add'}</span>
          </button>
        </form>
      </div>

      {/* Stock Cards / Table */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {watchlist.map((item) => {
          const isUp = item.change_pct >= 0;
          return (
            <div
              key={item.symbol}
              className="bg-[#202c33] rounded-xl p-3.5 border border-gray-700/50 hover:border-emerald-500/40 transition-all shadow-md flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-base font-bold text-white tracking-tight">{item.symbol}</span>
                    <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                      {item.exchange}
                    </span>
                    <p className="text-[11px] text-gray-400 truncate max-w-[160px]">{item.company_name}</p>
                  </div>

                  <div className="text-right">
                    <div className="text-sm font-extrabold text-white">₹{item.current_price?.toFixed(2)}</div>
                    <div className={`text-xs font-bold flex items-center justify-end ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isUp ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
                      {isUp ? '+' : ''}{item.change_pct?.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="mt-3 grid grid-cols-3 gap-1.5 text-[10px] bg-[#111b21] p-2 rounded-lg">
                  <div>
                    <span className="text-gray-500 block">VWAP</span>
                    <span className="text-gray-200 font-semibold">₹{item.vwap?.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Day High</span>
                    <span className="text-emerald-400 font-semibold">₹{item.high?.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Day Low</span>
                    <span className="text-rose-400 font-semibold">₹{item.low?.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-3.5 pt-2.5 border-t border-gray-700/40 flex items-center justify-between">
                <button
                  onClick={() => onAnalyzeStock(item.symbol)}
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center space-x-1"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Analyze in Chat</span>
                </button>

                <button
                  onClick={() => onRemoveStock(item.symbol)}
                  className="p-1 rounded text-gray-400 hover:text-rose-400 transition-colors"
                  title="Remove from Watchlist"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
