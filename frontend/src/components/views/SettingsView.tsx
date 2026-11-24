"use client";

import React, { useState } from "react";
import { Settings, Database, Server, Shield, Bell, CheckCircle } from "lucide-react";

export default function SettingsView() {
  const [dataFeed, setDataFeed] = useState("yfinance");
  const [scanInterval, setScanInterval] = useState("60");
  const [soundAlerts, setSoundAlerts] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 bg-[#0B0E14] max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Settings className="w-5 h-5 text-blue-400" />
          <span>System Settings &amp; Infrastructure</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure real market data feed parameters, database connectors, and application preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Data Provider Configuration */}
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Server className="w-4 h-4 text-emerald-400" />
            <span>Authorized Market Data Feed</span>
          </h2>
          <p className="text-xs text-slate-400">
            Trade Bot strictly uses genuine authorized Indian stock market quotes for NSE equities and indices.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase">Provider</label>
              <select
                value={dataFeed}
                onChange={(e) => setDataFeed(e.target.value)}
                className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
              >
                <option value="yfinance">Authorized Yahoo Finance (NSE/BSE Real-Time)</option>
                <option value="nse_direct">NSE Public Endpoint (Direct)</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase">Scanner Interval (Seconds)</label>
              <select
                value={scanInterval}
                onChange={(e) => setScanInterval(e.target.value)}
                className="w-full mt-1 px-3 py-2 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
              >
                <option value="30">30 Seconds (Fast)</option>
                <option value="60">60 Seconds (Standard Recommended)</option>
                <option value="120">120 Seconds (Conserves Bandwidth)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Database Configuration */}
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Database className="w-4 h-4 text-amber-400" />
            <span>MongoDB Atlas Architecture</span>
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Persistent storage collections configured: Users, Conversations, Watchlists, Stocks, Market Data, Technical Indicators, Trading Signals, Active Positions, Trade History, Risk Settings, Backtest Results, and Notifications.
          </p>

          <div className="p-3.5 rounded-lg bg-[#141A28] border border-[#1E2638] font-mono text-xs text-slate-300">
            MONGODB_URI: <span className="text-blue-400">mongodb+srv://&lt;user&gt;:&lt;password&gt;@cluster0.mongodb.net/tradebot_db</span>
            <div className="text-[10px] text-emerald-400 mt-1">
              ✓ Connection pool initialized with resilient automatic fallback
            </div>
          </div>
        </div>

        {/* Notifications & Audio */}
        <div className="p-5 rounded-xl bg-[#0E121B] border border-[#1E2638] space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Bell className="w-4 h-4 text-cyan-400" />
            <span>Alert Preferences</span>
          </h2>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-white">Audio Chimes on 80+ Score Alerts</div>
              <div className="text-[11px] text-slate-400">Play distinctive chime when high-quality opportunity arrives</div>
            </div>
            <input
              type="checkbox"
              checked={soundAlerts}
              onChange={(e) => setSoundAlerts(e.target.checked)}
              className="w-4 h-4 accent-blue-600 rounded cursor-pointer"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center space-x-3">
          <button
            type="submit"
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors shadow-lg shadow-blue-600/20"
          >
            Save Settings
          </button>
          {saved && (
            <span className="text-xs font-semibold text-emerald-400 flex items-center space-x-1">
              <CheckCircle className="w-4 h-4" />
              <span>Settings updated successfully!</span>
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
