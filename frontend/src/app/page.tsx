"use client";

import React, { useState, useEffect, useCallback } from "react";
import TopBar from "../components/TopBar";
import Sidebar, { ViewType } from "../components/Sidebar";

// Views
import AiAssistantView from "../components/views/AiAssistantView";
import MarketOverviewView from "../components/views/MarketOverviewView";
import TradingViewChartsView from "../components/views/TradingViewChartsView";
import WatchlistView from "../components/views/WatchlistView";
import ScannerView from "../components/views/ScannerView";
import TopBuySignalsView from "../components/views/TopBuySignalsView";
import TopSellSignalsView from "../components/views/TopSellSignalsView";
import ActiveOpportunitiesView from "../components/views/ActiveOpportunitiesView";
import PortfolioView from "../components/views/PortfolioView";
import PaperTradingView from "../components/views/PaperTradingView";
import RiskManagementView from "../components/views/RiskManagementView";
import BacktestingView from "../components/views/BacktestingView";
import SignalHistoryView from "../components/views/SignalHistoryView";
import SettingsView from "../components/views/SettingsView";

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>("ai_assistant");
  const [selectedStockForChart, setSelectedStockForChart] = useState("RELIANCE");
  
  // Platform State
  const [marketOverview, setMarketOverview] = useState<any>(null);
  const [scannerData, setScannerData] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [isScanning, setIsScanning] = useState(false);

  // Fetch initial market overview
  const fetchOverview = useCallback(async () => {
    try {
      const res = await fetch("/api/market/overview");
      if (res.ok) {
        const data = await res.json();
        setMarketOverview(data);
      }
    } catch (e) {
      console.error("Failed to load market overview:", e);
    }
  }, []);

  // Fetch scanner data
  const fetchScanner = useCallback(async () => {
    try {
      const res = await fetch("/api/scanner/latest");
      if (res.ok) {
        const data = await res.json();
        setScannerData(data);
      }
    } catch (e) {
      console.error("Failed to load scanner:", e);
    }
  }, []);

  // Fetch paper portfolio
  const fetchPortfolio = useCallback(async () => {
    try {
      const res = await fetch("/api/paper-trading/portfolio");
      if (res.ok) {
        const data = await res.json();
        setPortfolio(data);
      }
    } catch (e) {
      console.error("Failed to load portfolio:", e);
    }
  }, []);

  // Trigger manual scan
  const handleTriggerScan = async () => {
    setIsScanning(true);
    try {
      const res = await fetch("/api/scanner/scan", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setScannerData(data);
      }
    } catch (e) {
      console.error("Scan trigger error:", e);
    } finally {
      setIsScanning(false);
    }
  };

  // One-click Paper Trade from Signal Card
  const handleExecutePaperTrade = async (signal: any) => {
    try {
      const res = await fetch("/api/paper-trading/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: signal.symbol,
          side: signal.signal,
          quantity: signal.recommended_quantity || 10,
          price: signal.entry_price,
          stop_loss: signal.stop_loss,
          target: signal.target1,
          signal_id: signal.id
        })
      });
      if (res.ok) {
        fetchPortfolio();
      }
    } catch (e) {
      console.error("Error executing paper trade:", e);
    }
  };

  // View chart shortcut
  const handleViewChart = (symbol: string) => {
    setSelectedStockForChart(symbol);
    setCurrentView("tradingview_charts");
  };

  // Setup WebSockets & Initial polling
  useEffect(() => {
    fetchOverview();
    fetchScanner();
    fetchPortfolio();

    // WebSocket connection for real-time market updates
    let ws: WebSocket | null = null;
    try {
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = window.location.hostname === "localhost" ? "127.0.0.1:8000" : window.location.host;
      ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/market`);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "MARKET_TICK" || payload.type === "INITIAL_STATE") {
            if (payload.overview) setMarketOverview(payload.overview);
            if (payload.top_buy && payload.top_sell) {
              setScannerData((prev: any) => ({
                ...prev,
                top_buy: payload.top_buy,
                top_sell: payload.top_sell
              }));
            }
          }
        } catch (err) {
          console.error("WS parse error:", err);
        }
      };

      ws.onerror = (e) => {
        console.warn("Market WebSocket connecting in background...");
      };
    } catch (e) {
      console.warn("WebSocket init deferred:", e);
    }

    // Interval refresh fallback every 30s
    const timer = setInterval(() => {
      fetchOverview();
      fetchPortfolio();
    }, 30000);

    return () => {
      clearInterval(timer);
      if (ws) ws.close();
    };
  }, [fetchOverview, fetchScanner, fetchPortfolio]);

  const topBuyCount = scannerData?.top_buy?.length || 0;
  const topSellCount = scannerData?.top_sell?.length || 0;
  const activeOppsCount = (scannerData?.active_opportunities?.length) || (topBuyCount + topSellCount);
  const openPositionsCount = portfolio?.open_positions?.length || 0;

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0E14] text-slate-100 font-sans">
      {/* Top Bar */}
      <TopBar
        marketStatus={
          marketOverview
            ? {
                is_open: marketOverview.is_open,
                status: marketOverview.market_status,
                ist_time: marketOverview.current_time_ist,
              }
            : { is_open: false, status: "CLOSED", ist_time: "IST" }
        }
        dataStatus={marketOverview?.data_status || "LIVE"}
        lastUpdated={marketOverview?.last_updated || ""}
        notifications={notifications}
        onOpenNotifications={() => {}}
        activeNotificationsCount={notifications.length}
      />

      {/* Main App Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          currentView={currentView}
          onSelectView={setCurrentView}
          counts={{
            topBuy: topBuyCount,
            topSell: topSellCount,
            activeOpps: activeOppsCount,
            openPositions: openPositionsCount,
          }}
        />

        {/* Dynamic Center Stage */}
        <main className="flex-1 h-full overflow-hidden relative bg-[#0B0E14]">
          {currentView === "ai_assistant" && (
            <AiAssistantView
              onExecutePaperTrade={handleExecutePaperTrade}
              onViewChart={handleViewChart}
              activeOpportunities={scannerData?.active_opportunities || []}
            />
          )}

          {currentView === "market_overview" && (
            <MarketOverviewView
              overview={marketOverview}
              onRefresh={fetchOverview}
              onSelectStock={handleViewChart}
            />
          )}

          {currentView === "tradingview_charts" && (
            <TradingViewChartsView initialSymbol={selectedStockForChart} />
          )}

          {currentView === "watchlist" && (
            <WatchlistView
              onAnalyzeStock={(sym) => {
                setSelectedStockForChart(sym);
                setCurrentView("ai_assistant");
              }}
              onViewChart={handleViewChart}
            />
          )}

          {currentView === "scanner" && (
            <ScannerView
              scannerData={scannerData}
              onTriggerScan={handleTriggerScan}
              isScanning={isScanning}
              onExecutePaperTrade={handleExecutePaperTrade}
              onViewChart={handleViewChart}
            />
          )}

          {currentView === "top_buy" && (
            <TopBuySignalsView
              signals={scannerData?.top_buy || []}
              onTriggerScan={handleTriggerScan}
              onExecutePaperTrade={handleExecutePaperTrade}
              onViewChart={handleViewChart}
            />
          )}

          {currentView === "top_sell" && (
            <TopSellSignalsView
              signals={scannerData?.top_sell || []}
              onTriggerScan={handleTriggerScan}
              onExecutePaperTrade={handleExecutePaperTrade}
              onViewChart={handleViewChart}
            />
          )}

          {currentView === "active_opportunities" && (
            <ActiveOpportunitiesView
              opportunities={scannerData?.active_opportunities || []}
              onTriggerScan={handleTriggerScan}
              onExecutePaperTrade={handleExecutePaperTrade}
              onViewChart={handleViewChart}
            />
          )}

          {currentView === "portfolio" && (
            <PortfolioView
              portfolio={portfolio}
              onNavigateToPaperTrading={() => setCurrentView("paper_trading")}
            />
          )}

          {currentView === "paper_trading" && (
            <PaperTradingView
              portfolio={portfolio}
              onRefreshPortfolio={fetchPortfolio}
            />
          )}

          {currentView === "risk_management" && <RiskManagementView />}

          {currentView === "backtesting" && <BacktestingView />}

          {currentView === "signal_history" && <SignalHistoryView />}

          {currentView === "settings" && <SettingsView />}
        </main>
      </div>
    </div>
  );
}
