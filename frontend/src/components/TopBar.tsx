"use client";

import React, { useState, useEffect } from "react";
import { 
  Activity, Bell, Moon, Sun, ShieldCheck, Clock, 
  Wifi, CheckCircle2, AlertTriangle, X, TrendingUp
} from "lucide-react";

interface TopBarProps {
  marketStatus: {
    is_open: boolean;
    status: string;
    ist_time: string;
  };
  dataStatus: string; // LIVE, DELAYED, OFFLINE
  lastUpdated: string;
  notifications: any[];
  onOpenNotifications: () => void;
  activeNotificationsCount: number;
}

export default function TopBar({
  marketStatus,
  dataStatus,
  lastUpdated,
  notifications,
  onOpenNotifications,
  activeNotificationsCount
}: TopBarProps) {
  const [istTime, setIstTime] = useState<string>("");
  const [showNotifications, setShowNotifications] = useState(false);

  // Live IST Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // IST is UTC + 5:30
      const istString = now.toLocaleTimeString("en-IN", {
        timeZone: "Asia/Kolkata",
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
      setIstTime(istString);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-14 border-b border-[#1E2638] bg-[#0E121B] px-4 flex items-center justify-between z-30 select-none">
      {/* Left: Brand & Logo */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-bold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Trade Bot AI
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                PRO NSE
              </span>
            </div>
          </div>
        </div>

        {/* Vertical divider */}
        <div className="h-5 w-[1px] bg-[#1E2638] hidden sm:block"></div>

        {/* Market Status Badge */}
        <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-md bg-[#141A28] border border-[#1E2638]">
          <span className={`w-2 h-2 rounded-full ${marketStatus?.is_open ? 'bg-emerald-400 pulse-live' : 'bg-rose-500'}`}></span>
          <span className="text-xs font-medium text-slate-300">
            NSE/BSE: <span className={marketStatus?.is_open ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>{marketStatus?.status || "CLOSED"}</span>
          </span>
        </div>

        {/* Data Feed Mode Badge */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-[#141A28] border border-[#1E2638]">
          <Wifi className={`w-3.5 h-3.5 ${dataStatus === 'LIVE' ? 'text-emerald-400' : (dataStatus === 'DELAYED' ? 'text-amber-400' : 'text-rose-400')}`} />
          <span className="text-xs font-medium text-slate-300">
            Feed: <span className={`font-semibold ${dataStatus === 'LIVE' ? 'text-emerald-400' : (dataStatus === 'DELAYED' ? 'text-amber-400' : 'text-rose-400')}`}>{dataStatus || "DELAYED"}</span>
          </span>
          {lastUpdated && (
            <span className="text-[10px] text-slate-500 hidden lg:inline">
              ({lastUpdated.split(' ')[1] || 'Sync'})
            </span>
          )}
        </div>
      </div>

      {/* Right: Clock, Alerts, Profile */}
      <div className="flex items-center space-x-3">
        {/* Live IST Market Clock */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-[#141A28] border border-[#1E2638] font-mono text-xs text-slate-200">
          <Clock className="w-3.5 h-3.5 text-blue-400" />
          <span>{istTime || "09:15:00"} <span className="text-[10px] text-slate-500">IST</span></span>
        </div>

        {/* Notifications Popover Toggle */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg bg-[#141A28] hover:bg-[#1C2438] border border-[#1E2638] text-slate-300 transition-colors"
            title="Notification Center"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center">
                {Math.min(notifications.length, 9)}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 md:w-96 bg-[#121722] border border-[#1E2638] rounded-xl shadow-2xl z-50 overflow-hidden">
              <div className="px-4 py-3 border-b border-[#1E2638] flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Bell className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold text-slate-100">Live Trade Alerts</span>
                </div>
                <button 
                  onClick={() => setShowNotifications(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-[#1A2234]">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400">
                    No active trading alerts. Trade Bot only notifies on confirmed 70+ setups.
                  </div>
                ) : (
                  notifications.map((n, i) => (
                    <div key={i} className="p-3 hover:bg-[#182030] transition-colors">
                      <div className="flex items-start justify-between">
                        <span className={`text-xs font-semibold ${n.type === 'BUY_ALERT' ? 'text-emerald-400' : (n.type === 'SELL_ALERT' ? 'text-rose-400' : 'text-blue-400')}`}>
                          {n.title}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {n.timestamp?.split(' ')[1] || 'Just now'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                        {n.message}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill */}
        <div className="flex items-center space-x-2 pl-2">
          <div className="w-7 h-7 rounded-full bg-blue-600/30 border border-blue-500/40 text-blue-400 text-xs font-bold flex items-center justify-center">
            P
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-medium text-slate-200">Pro Trader</div>
            <div className="text-[10px] text-emerald-400 font-mono">₹10,00,000 (Paper)</div>
          </div>
        </div>
      </div>
    </header>
  );
}
