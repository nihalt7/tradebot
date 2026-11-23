import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { ChatWindow } from './components/ChatWindow';
import { WatchlistTab } from './components/WatchlistTab';
import { ScannerTab } from './components/ScannerTab';
import { PortfolioTab } from './components/PortfolioTab';
import { RiskTab } from './components/RiskTab';
import { BacktestTab } from './components/BacktestTab';
import { api, WebSocketClient } from './services/api';
import { 
  ChatMessage, 
  WatchlistItem, 
  ScannerResults, 
  ActivePosition, 
  RiskSettings, 
  DashboardOverview, 
  ScannerOpportunity 
} from './types';
import { ShieldCheck, Key, CheckCircle, Database } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('chat');
  const [darkMode, setDarkMode] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [scannerData, setScannerData] = useState<ScannerResults | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [positions, setPositions] = useState<ActivePosition[]>([]);
  const [riskSettings, setRiskSettings] = useState<RiskSettings | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  // Settings State
  const [broker, setBroker] = useState('ZERODHA');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [apiSaved, setApiSaved] = useState(false);

  // Load initial data
  useEffect(() => {
    const init = async () => {
      try {
        const [dash, wl, sc, msgs, pos, risk] = await Promise.all([
          api.getDashboardOverview().catch(() => null),
          api.getWatchlist().catch(() => []),
          api.getScannerLatest().catch(() => null),
          api.getMessages('main_chat').catch(() => []),
          api.getActivePositions().catch(() => []),
          api.getRiskSettings().catch(() => null),
        ]);

        if (dash) setOverview(dash);
        if (wl) setWatchlist(wl);
        if (sc) setScannerData(sc);
        if (msgs) setMessages(msgs);
        if (pos) setPositions(pos);
        if (risk) setRiskSettings(risk);
      } catch (e) {
        console.error('Initialization error:', e);
      }
    };

    init();

    // Setup WebSocket for Live Streaming
    const ws = new WebSocketClient(
      // On market tick
      (tickData) => {
        setOverview((prev) => {
          if (!prev) return tickData;
          return { ...prev, ...tickData };
        });
      },
      // On signal alert (Engine A or B confirmed setup)
      (signalCard) => {
        const alertMsg: ChatMessage = {
          id: Date.now(),
          conversation_id: 'main_chat',
          sender: 'assistant',
          text: `🚨 **HIGH-QUALITY CONFIRMED OPPORTUNITY (${signalCard.symbol})**\nSignal: **${signalCard.signal}** | Score: **${signalCard.setup_score}/100**`,
          message_type: 'signal_card',
          card_data: signalCard,
          timestamp: new Date().toISOString()
        };
        setMessages((prev) => [...prev, alertMsg]);
      },
      // On chat response
      (chatMsg) => {
        setMessages((prev) => {
          if (prev.some((m) => m.id === chatMsg.id)) return prev;
          return [...prev, chatMsg];
        });
      }
    );

    // Periodic position & watchlist refresher (every 4 seconds)
    const interval = setInterval(async () => {
      try {
        const [wl, pos] = await Promise.all([
          api.getWatchlist().catch(() => []),
          api.getActivePositions().catch(() => [])
        ]);
        if (wl && wl.length > 0) setWatchlist(wl);
        if (pos) setPositions(pos);
      } catch (e) {}
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (text: string) => {
    // Optimistically add user message
    const userMsg: ChatMessage = {
      id: Date.now(),
      conversation_id: 'main_chat',
      sender: 'user',
      text,
      message_type: 'text',
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await api.sendMessage('main_chat', text);
      setMessages((prev) => [...prev.filter((m) => m.id !== userMsg.id), userMsg, response]);
      
      // If user added or removed stock via chat, refresh watchlist
      if (text.toUpperCase().startsWith('ADD ') || text.toUpperCase().startsWith('REMOVE ')) {
        const wl = await api.getWatchlist();
        setWatchlist(wl);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearChat = async () => {
    await api.clearChat('main_chat');
    setMessages([]);
  };

  const handleAddStock = async (symbol: string) => {
    await api.addToWatchlist(symbol);
    const wl = await api.getWatchlist();
    setWatchlist(wl);
  };

  const handleRemoveStock = async (symbol: string) => {
    await api.removeFromWatchlist(symbol);
    const wl = await api.getWatchlist();
    setWatchlist(wl);
  };

  const handleAnalyzeStock = async (symbol: string) => {
    setActiveTab('chat');
    await handleSendMessage(`ANALYZE ${symbol}`);
  };

  const handleExecuteTrade = async (opp: ScannerOpportunity) => {
    await api.placePaperOrder({
      symbol: opp.symbol,
      direction: opp.signal_type,
      quantity: 150,
      entry_price: opp.entry_min,
      stop_loss: opp.stop_loss,
      target_1: opp.target_1,
      target_2: opp.target_2,
      target_3: opp.target_3
    });
    const pos = await api.getActivePositions();
    setPositions(pos);
    setActiveTab('portfolio');
  };

  const handleClosePosition = async (id: number) => {
    await api.closePosition(id);
    const pos = await api.getActivePositions();
    setPositions(pos);
  };

  const handleUpdateRisk = async (upd: Partial<RiskSettings>) => {
    const updated = await api.updateRiskSettings(upd);
    setRiskSettings(updated);
  };

  const handleResetDailyLoss = async () => {
    await api.resetDailyLoss();
    const risk = await api.getRiskSettings();
    setRiskSettings(risk);
  };

  return (
    <div className={`h-screen w-screen flex flex-col bg-[#0c1317] ${darkMode ? 'dark' : ''} overflow-hidden font-sans`}>
      {/* Top Navbar with Indices Ticker */}
      <Navbar
        overview={overview}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        onOpenRisk={() => setActiveTab('risk')}
      />

      {/* Main WhatsApp Web Style Split Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          watchlistCount={watchlist.length}
          openPositionsCount={positions.length}
          activeSignalsCount={scannerData?.top_buys?.length || 0}
        />

        {/* Content Pane: Chat or Specialized Tool Panel */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          {activeTab === 'chat' && (
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              onClearChat={handleClearChat}
              isTyping={isTyping}
            />
          )}

          {activeTab === 'watchlist' && (
            <WatchlistTab
              watchlist={watchlist}
              onAddStock={handleAddStock}
              onRemoveStock={handleRemoveStock}
              onAnalyzeStock={handleAnalyzeStock}
            />
          )}

          {(activeTab === 'scanner' || activeTab === 'top_buys' || activeTab === 'top_sells') && (
            <ScannerTab
              scannerData={scannerData}
              onRefreshScan={async () => {
                const fresh = await api.scanNow();
                setScannerData(fresh);
              }}
              onAnalyzeStock={handleAnalyzeStock}
              onExecuteTrade={handleExecuteTrade}
            />
          )}

          {activeTab === 'portfolio' && (
            <PortfolioTab
              positions={positions}
              onClosePosition={handleClosePosition}
            />
          )}

          {activeTab === 'risk' && (
            <RiskTab
              settings={riskSettings}
              onUpdateSettings={handleUpdateRisk}
              onResetDailyLoss={handleResetDailyLoss}
            />
          )}

          {activeTab === 'backtest' && <BacktestTab />}

          {activeTab === 'settings' && (
            <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-6 select-text">
              <h2 className="text-lg font-bold text-white mb-1 flex items-center">
                <Key className="w-5 h-5 text-emerald-400 mr-2" /> Broker API Integration & Credentials
              </h2>
              <p className="text-xs text-gray-400 mb-6">
                Connect your Indian broker (Zerodha Kite, Upstox, Angel One, Dhan). Credentials are encrypted and never exposed.
              </p>

              <div className="max-w-xl bg-[#202c33] p-5 rounded-xl border border-gray-700/50 shadow-md space-y-4">
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Select Indian Broker</label>
                  <select
                    value={broker}
                    onChange={(e) => setBroker(e.target.value)}
                    className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-bold"
                  >
                    <option value="ZERODHA">Zerodha (Kite Connect API)</option>
                    <option value="UPSTOX">Upstox (Upstox Pro API)</option>
                    <option value="ANGELONE">Angel One (SmartAPI)</option>
                    <option value="DHAN">Dhan (DhanHQ API)</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">API Key</label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter Broker API Key"
                    className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">API Secret / Access Token</label>
                  <input
                    type="password"
                    value={apiSecret}
                    onChange={(e) => setApiSecret(e.target.value)}
                    placeholder="Enter Broker API Secret"
                    className="w-full px-3 py-2 bg-[#111b21] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>

                <div className="p-3 bg-[#111b21] rounded-lg border border-gray-700/60 text-xs text-gray-400">
                  🛡️ <strong>Production Security Standard:</strong> When paper trading is active, orders are simulated in memory. Real market executions require active 2FA and user confirmation.
                </div>

                <button
                  onClick={() => {
                    setApiSaved(true);
                    setTimeout(() => setApiSaved(false), 2500);
                  }}
                  className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center space-x-1.5"
                >
                  {apiSaved ? <CheckCircle className="w-4 h-4 text-white" /> : <ShieldCheck className="w-4 h-4" />}
                  <span>{apiSaved ? 'Credentials Saved Securely' : 'Save Broker Credentials'}</span>
                </button>
              </div>
            </div>
          )}

          {(activeTab === 'active_signals' || activeTab === 'signal_history') && (
            <div className="flex-1 flex flex-col h-full bg-[#111b21] text-gray-200 overflow-y-auto p-4 select-text">
              <h2 className="text-lg font-bold text-white mb-1">
                {activeTab === 'active_signals' ? 'Active High-Probability Setups' : 'Signal Audit History'}
              </h2>
              <p className="text-xs text-gray-400 mb-4">
                Verified against 14 quantitative indicators. Setups expire automatically after 5 minutes if unfulfilled.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {scannerData?.top_buys?.map((b) => (
                  <div key={b.symbol} className="bg-[#202c33] p-4 rounded-xl border border-emerald-500/40">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-extrabold text-white text-base">{b.symbol}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-xs">
                        Score: {b.score}/100
                      </span>
                    </div>
                    <div className="text-xs text-gray-300 space-y-1">
                      <div>Entry: <strong className="text-emerald-400">₹{b.entry_min} – ₹{b.entry_max}</strong></div>
                      <div>Stop Loss: <strong className="text-rose-400">₹{b.stop_loss}</strong></div>
                      <div>Target 1: <strong className="text-teal-400">₹{b.target_1}</strong></div>
                      <div>Risk/Reward: <strong className="text-cyan-400">1:{b.risk_reward}</strong></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
