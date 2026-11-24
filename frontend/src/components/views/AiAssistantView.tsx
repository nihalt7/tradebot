"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Bot, User, Search, Zap, TrendingUp, Sparkles, 
  MessageSquare, HelpCircle, Check, CheckCheck, RefreshCw 
} from "lucide-react";
import TradingSignalCard from "../cards/TradingSignalCard";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  cards?: any[];
}

interface AiAssistantViewProps {
  onExecutePaperTrade?: (signal: any) => void;
  onViewChart?: (symbol: string) => void;
  activeOpportunities?: any[];
}

export default function AiAssistantView({
  onExecutePaperTrade,
  onViewChart,
  activeOpportunities = []
}: AiAssistantViewProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSession, setActiveSession] = useState("default");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickCommands = [
    { label: "TOP 5", cmd: "TOP 5" },
    { label: "ANALYZE RELIANCE", cmd: "ANALYZE RELIANCE" },
    { label: "ANALYZE TCS", cmd: "ANALYZE TCS" },
    { label: "SCAN NSE", cmd: "SCAN" },
    { label: "MARKET STATUS", cmd: "STATUS" },
    { label: "POSITION SIZE", cmd: "CALCULATE POSITION SIZE" },
    { label: "BULLISH STOCKS", cmd: "Show the strongest bullish stocks" },
    { label: "BEARISH STOCKS", cmd: "Which stocks have bearish momentum?" },
  ];

  // Fetch initial history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("/api/chat/history");
        if (res.ok) {
          const data = await res.json();
          setMessages(data.history || []);
        }
      } catch (e) {
        console.error("Failed to load chat history:", e);
      }
    };
    fetchHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query) return;

    setInputText("");
    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await fetch("/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, session_id: activeSession })
      });

      if (res.ok) {
        const botReply = await res.json();
        setMessages((prev) => [...prev, botReply]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `bot_err_${Date.now()}`,
            sender: "bot",
            text: "Sorry, I encountered an error communicating with the analysis engine. Please retry.",
            timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false })
          }
        ]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot_err_${Date.now()}`,
          sender: "bot",
          text: "Connection to the backend API failed. Ensure the server is online.",
          timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false })
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const filteredMessages = searchQuery
    ? messages.filter((m) => m.text.toLowerCase().includes(searchQuery.toLowerCase()))
    : messages;

  return (
    <div className="flex h-full w-full bg-[#0B0E14] overflow-hidden">
      {/* WhatsApp-style Sidebar for conversations */}
      <div className="w-72 bg-[#0E121B] border-r border-[#1E2638] flex flex-col shrink-0 hidden md:flex">
        {/* Search header */}
        <div className="p-3 border-b border-[#1E2638]">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search chat or commands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-[#141A28] border border-[#1E2638] rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <div
            onClick={() => setActiveSession("default")}
            className="p-3 rounded-lg bg-[#151D2D] border border-blue-500/30 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Bot className="w-3.5 h-3.5 text-blue-400" />
                <span>Trade Bot AI Assistant</span>
              </span>
              <span className="text-[10px] text-emerald-400 font-medium">Online</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1 truncate">
              {messages.length > 0 ? messages[messages.length - 1].text.slice(0, 45) + "..." : "Quantitative trading support..."}
            </p>
          </div>

          <div className="pt-3 px-2">
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
              Quick Suggestions
            </span>
            <div className="mt-2 space-y-1.5">
              {quickCommands.slice(0, 5).map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(q.cmd)}
                  className="w-full text-left p-2 rounded-md bg-[#121722] hover:bg-[#1A2234] border border-[#1E2638] text-[11px] text-slate-300 transition-colors flex items-center justify-between group"
                >
                  <span className="font-mono text-slate-300">{q.label}</span>
                  <Send className="w-3 h-3 text-slate-500 group-hover:text-blue-400 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main WhatsApp-style Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#0B0E14]">
        {/* Chat top info header */}
        <div className="h-12 border-b border-[#1E2638] bg-[#0E121B] px-4 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                <span>Trade Bot AI Intelligence</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              </div>
              <div className="text-[10px] text-slate-400">
                Multi-Timeframe Models • VWAP • Supertrend • ATR Targets
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleSendMessage("SCAN")}
              className="px-2.5 py-1 rounded-md bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 text-xs font-semibold border border-blue-500/30 flex items-center space-x-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span className="hidden sm:inline">Trigger NSE Scan</span>
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {filteredMessages.map((msg) => {
            const isUser = msg.sender === "user";

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-3.5 shadow-md ${
                    isUser
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-[#141A28] border border-[#1E2638] text-slate-200 rounded-bl-none"
                  }`}
                >
                  {/* Sender title if bot */}
                  {!isUser && (
                    <div className="flex items-center space-x-1.5 mb-1.5 text-blue-400 font-semibold text-xs">
                      <Bot className="w-3.5 h-3.5" />
                      <span>Trade Bot AI</span>
                    </div>
                  )}

                  {/* Message body */}
                  <div className="text-xs md:text-sm leading-relaxed whitespace-pre-wrap font-sans">
                    {msg.text}
                  </div>

                  {/* Render Signal Cards if attached */}
                  {msg.cards && msg.cards.length > 0 && (
                    <div className="mt-3 space-y-3">
                      {msg.cards.map((card: any, idx: number) => (
                        <TradingSignalCard
                          key={idx}
                          signal={card}
                          onExecutePaperTrade={onExecutePaperTrade}
                          onViewChart={onViewChart}
                        />
                      ))}
                    </div>
                  )}

                  {/* Timestamp & read ticks */}
                  <div className="flex items-center justify-end space-x-1 mt-1.5 text-[10px] text-slate-400">
                    <span>{msg.timestamp}</span>
                    {isUser && <CheckCheck className="w-3 h-3 text-blue-200" />}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex items-center space-x-2 text-slate-400 text-xs p-2">
              <Bot className="w-4 h-4 text-blue-400 animate-bounce" />
              <span>Analyzing live market data &amp; calculating setup scores...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Command Pills Carousel */}
        <div className="px-4 py-2 border-t border-[#1E2638] bg-[#0E121B] flex items-center space-x-2 overflow-x-auto no-scrollbar">
          {quickCommands.map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(item.cmd)}
              className="px-2.5 py-1 rounded-full bg-[#151D2D] hover:bg-blue-600/20 hover:border-blue-500/40 text-slate-300 hover:text-blue-400 text-[11px] font-mono border border-[#1E2638] shrink-0 transition-colors"
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-[#1E2638] bg-[#0E121B] shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask anything or enter command (e.g., TOP 5, ANALYZE RELIANCE, SCAN)..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-[#141A28] border border-[#1E2638] rounded-xl px-4 py-2.5 text-xs md:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white font-semibold text-xs flex items-center space-x-1.5 transition-colors shadow-lg shadow-blue-600/20"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
