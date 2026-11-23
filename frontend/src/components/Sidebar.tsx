import React from 'react';
import { 
  MessageSquare, 
  ListFilter, 
  Radar, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  History, 
  Briefcase, 
  ShieldAlert, 
  BarChart2, 
  Settings,
  Bot,
  Search
} from 'lucide-react';

export type NavTab = 
  | 'chat' 
  | 'watchlist' 
  | 'scanner' 
  | 'top_buys' 
  | 'top_sells' 
  | 'active_signals' 
  | 'signal_history' 
  | 'portfolio' 
  | 'risk' 
  | 'backtest' 
  | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  watchlistCount: number;
  openPositionsCount: number;
  activeSignalsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  watchlistCount,
  openPositionsCount,
  activeSignalsCount
}) => {
  const navItems = [
    { id: 'chat' as NavTab, label: 'AI Trading Assistant', icon: MessageSquare, badge: null, color: 'text-emerald-400' },
    { id: 'watchlist' as NavTab, label: 'My Watchlist (Engine A)', icon: ListFilter, badge: watchlistCount, color: 'text-emerald-400' },
    { id: 'scanner' as NavTab, label: 'Live Market Scanner (Engine B)', icon: Radar, badge: null, color: 'text-cyan-400' },
    { id: 'top_buys' as NavTab, label: 'Top 5 BUY Signals', icon: TrendingUp, badge: '5', color: 'text-emerald-400' },
    { id: 'top_sells' as NavTab, label: 'Top 5 SELL Signals', icon: TrendingDown, badge: '5', color: 'text-rose-400' },
    { id: 'active_signals' as NavTab, label: 'Active Opportunities', icon: Zap, badge: activeSignalsCount || null, color: 'text-amber-400' },
    { id: 'portfolio' as NavTab, label: 'Portfolio & Paper Trading', icon: Briefcase, badge: openPositionsCount || null, color: 'text-teal-400' },
    { id: 'risk' as NavTab, label: 'Risk Management', icon: ShieldAlert, badge: null, color: 'text-amber-400' },
    { id: 'backtest' as NavTab, label: 'Strategy Backtesting', icon: BarChart2, badge: null, color: 'text-cyan-400' },
    { id: 'signal_history' as NavTab, label: 'Signal Audit History', icon: History, badge: null, color: 'text-gray-400' },
    { id: 'settings' as NavTab, label: 'Broker APIs & Settings', icon: Settings, badge: null, color: 'text-gray-400' },
  ];

  return (
    <aside className="w-80 h-full bg-[#111b21] border-r border-gray-700/50 flex flex-col flex-shrink-0 select-none">
      {/* WhatsApp-like User Header */}
      <div className="h-16 bg-[#202c33] px-4 flex items-center justify-between border-b border-gray-700/50 flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center">
            <Bot className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">NSE Quant Studio</div>
            <div className="text-[11px] text-gray-400">WhatsApp Web UI</div>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider px-3 py-1">
          Trading & Monitoring Engines
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                isActive
                  ? 'bg-[#202c33] text-white border-l-4 border-emerald-400 shadow-sm'
                  : 'text-gray-300 hover:bg-[#202c33]/50 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3 truncate">
                <Icon className={`w-4 h-4 flex-shrink-0 ${item.color}`} />
                <span className="truncate">{item.label}</span>
              </div>

              {item.badge !== null && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  isActive ? 'bg-emerald-500 text-black' : 'bg-gray-700 text-gray-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer System Status */}
      <div className="p-3 bg-[#0c1317] border-t border-gray-800 text-[11px] text-gray-400 flex items-center justify-between flex-shrink-0">
        <span className="flex items-center">
          <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
          NSE WebSocket Live
        </span>
        <span className="text-gray-500 text-[10px]">v1.0.0 Pro</span>
      </div>
    </aside>
  );
};
