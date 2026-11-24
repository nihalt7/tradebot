"use client";

import React from "react";
import {
  Bot,
  LayoutDashboard,
  CandlestickChart,
  Star,
  Radar,
  TrendingUp,
  TrendingDown,
  Zap,
  Briefcase,
  PlaySquare,
  ShieldAlert,
  History,
  CheckCircle,
  Settings
} from "lucide-react";

export type ViewType =
  | "ai_assistant"
  | "market_overview"
  | "tradingview_charts"
  | "watchlist"
  | "scanner"
  | "top_buy"
  | "top_sell"
  | "active_opportunities"
  | "portfolio"
  | "paper_trading"
  | "risk_management"
  | "backtesting"
  | "signal_history"
  | "settings";

interface SidebarProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  counts: {
    topBuy: number;
    topSell: number;
    activeOpps: number;
    openPositions: number;
  };
}

export default function Sidebar({ currentView, onSelectView, counts }: SidebarProps) {
  const menuItems = [
    {
      id: "ai_assistant" as ViewType,
      label: "AI Trading Assistant",
      icon: Bot,
      highlight: true
    },
    {
      id: "market_overview" as ViewType,
      label: "Market Overview",
      icon: LayoutDashboard
    },
    {
      id: "tradingview_charts" as ViewType,
      label: "TradingView Charts",
      icon: CandlestickChart
    },
    {
      id: "watchlist" as ViewType,
      label: "My Watchlist",
      icon: Star
    },
    {
      id: "scanner" as ViewType,
      label: "Live NSE Scanner",
      icon: Radar
    },
    {
      id: "top_buy" as ViewType,
      label: "Top BUY Signals",
      icon: TrendingUp,
      badge: counts.topBuy > 0 ? counts.topBuy : undefined,
      badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
    },
    {
      id: "top_sell" as ViewType,
      label: "Top SELL Signals",
      icon: TrendingDown,
      badge: counts.topSell > 0 ? counts.topSell : undefined,
      badgeColor: "bg-rose-500/20 text-rose-400 border-rose-500/30"
    },
    {
      id: "active_opportunities" as ViewType,
      label: "Active Opportunities",
      icon: Zap,
      badge: counts.activeOpps > 0 ? counts.activeOpps : undefined,
      badgeColor: "bg-blue-500/20 text-blue-400 border-blue-500/30"
    },
    {
      id: "portfolio" as ViewType,
      label: "Portfolio",
      icon: Briefcase
    },
    {
      id: "paper_trading" as ViewType,
      label: "Paper Trading",
      icon: PlaySquare,
      badge: counts.openPositions > 0 ? `${counts.openPositions} Open` : undefined,
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30"
    },
    {
      id: "risk_management" as ViewType,
      label: "Risk Management",
      icon: ShieldAlert
    },
    {
      id: "backtesting" as ViewType,
      label: "Backtesting",
      icon: History
    },
    {
      id: "signal_history" as ViewType,
      label: "Signal History",
      icon: CheckCircle
    },
    {
      id: "settings" as ViewType,
      label: "Settings",
      icon: Settings
    }
  ];

  return (
    <aside className="w-64 bg-[#0E121B] border-r border-[#1E2638] flex flex-col h-[calc(100vh-3.5rem)] select-none shrink-0 overflow-y-auto">
      <div className="p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? "bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm"
                  : item.highlight
                  ? "text-slate-100 hover:bg-[#141A28] border border-blue-500/20 bg-blue-950/20"
                  : "text-slate-300 hover:bg-[#141A28] hover:text-white"
              }`}
            >
              <div className="flex items-center space-x-2.5 truncate">
                <Icon
                  className={`w-4 h-4 shrink-0 ${
                    isActive
                      ? "text-blue-400"
                      : item.highlight
                      ? "text-blue-400"
                      : "text-slate-400"
                  }`}
                />
                <span className="truncate">{item.label}</span>
              </div>

              {item.badge !== undefined && (
                <span
                  className={`px-1.5 py-0.5 text-[10px] font-bold rounded border ${item.badgeColor}`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom disclaimer footer */}
      <div className="mt-auto p-3 border-t border-[#1E2638] bg-[#0A0D15]/80">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
          <span className="text-[11px] font-medium text-slate-300">Strict Quantitative Rules</span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1 leading-normal">
          Real NSE data only. Setup score &ge; 70 required. Capital protection first.
        </p>
      </div>
    </aside>
  );
}
