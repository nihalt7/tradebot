import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, CheckCheck, Trash2, Sparkles, HelpCircle, ArrowRight } from 'lucide-react';
import { ChatMessage } from '../types';
import { SignalCardComponent } from './SignalCardComponent';
import { AnalysisCardComponent } from './AnalysisCardComponent';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => Promise<void>;
  onClearChat: () => Promise<void>;
  isTyping: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  onClearChat,
  isTyping
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isTyping) return;
    const text = inputText;
    setInputText('');
    await onSendMessage(text);
  };

  const handleQuickCommand = async (cmd: string) => {
    if (isTyping) return;
    await onSendMessage(cmd);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0c1317] relative overflow-hidden select-text">
      {/* WhatsApp Web Style Chat Header */}
      <div className="h-16 bg-[#202c33] border-b border-gray-700/50 px-4 flex items-center justify-between z-10 shadow-sm flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-emerald-700/60 border border-emerald-500/40 flex items-center justify-center text-white shadow-md">
              <Bot className="w-6 h-6 text-emerald-400" />
            </div>
            <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#202c33]"></span>
          </div>

          <div>
            <div className="font-bold text-white text-sm flex items-center space-x-2">
              <span>Chanakya AI Quant Analyst</span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.2 rounded border border-emerald-500/30">
                PRO QUANT
              </span>
            </div>
            <div className="text-xs text-emerald-400 flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[11px] text-gray-300">Online | Real-time NSE Dual Monitoring Active</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleQuickCommand('HELP')}
            className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-700/50 transition-colors"
            title="Help & Commands"
          >
            <HelpCircle className="w-5 h-5" />
          </button>
          <button
            onClick={onClearChat}
            className="p-2 rounded-full text-gray-400 hover:text-rose-400 hover:bg-gray-700/50 transition-colors"
            title="Clear Chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Quick Action Suggestion Chips Bar */}
      <div className="bg-[#111b21] border-b border-gray-800/80 px-4 py-2 flex items-center space-x-2 overflow-x-auto text-xs no-scrollbar flex-shrink-0">
        <span className="text-gray-400 text-[11px] flex items-center whitespace-nowrap">
          <Sparkles className="w-3.5 h-3.5 text-amber-400 mr-1" /> Quick Commands:
        </span>
        <button
          onClick={() => handleQuickCommand('TOP 5')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          🎯 Top 5 Opportunities
        </button>
        <button
          onClick={() => handleQuickCommand('SCAN')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          ⚡ Scan NSE Universe
        </button>
        <button
          onClick={() => handleQuickCommand('ANALYZE RELIANCE')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          📊 Analyze RELIANCE
        </button>
        <button
          onClick={() => handleQuickCommand('ANALYZE TCS')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          📊 Analyze TCS
        </button>
        <button
          onClick={() => handleQuickCommand('MARKET TREND')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          📈 Market Trend & Breadth
        </button>
        <button
          onClick={() => handleQuickCommand('LIST')}
          className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#202c33] text-gray-200 hover:bg-emerald-700 hover:text-white transition-colors border border-gray-700/50 text-[11px] font-medium"
        >
          📋 My Watchlist
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 chat-wallpaper-dark">
        {/* Security / Golden Rule Watermark Notice */}
        <div className="flex justify-center my-2">
          <div className="bg-[#182229]/90 border border-gray-700/60 rounded-lg px-3 py-1.5 text-center text-[11px] text-gray-400 max-w-md shadow-sm">
            🔒 <strong className="text-gray-300">The Golden Rule Active:</strong> High-Quality Confirmed Setups (Score ≥ 75) trigger instant alert cards. If conditions are unsuitable: <em>NO TRADE</em>.
          </div>
        </div>

        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now';

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} my-1`}
            >
              <div
                className={`rounded-2xl px-4 py-2.5 max-w-[85%] md:max-w-[70%] text-sm shadow-md ${
                  isUser
                    ? 'bg-[#005c4b] text-white rounded-tr-none'
                    : 'bg-[#202c33] text-gray-100 rounded-tl-none border border-gray-700/30'
                }`}
              >
                {/* Text Content */}
                <div className="whitespace-pre-line leading-relaxed select-text">
                  {msg.text}
                </div>

                {/* Optional Signal Card */}
                {msg.message_type === 'signal_card' && msg.card_data && (
                  <div className="mt-2">
                    <SignalCardComponent data={msg.card_data} />
                  </div>
                )}

                {/* Optional Analysis Card */}
                {msg.message_type === 'analysis_card' && msg.card_data && (
                  <div className="mt-2">
                    <AnalysisCardComponent data={msg.card_data} />
                  </div>
                )}

                {/* Timestamp & Read Receipt */}
                <div className="flex items-center justify-end space-x-1 mt-1 text-[10px] text-gray-300/80">
                  <span>{time}</span>
                  {isUser && <CheckCheck className="w-3.5 h-3.5 text-cyan-400 inline" />}
                </div>
              </div>
            </div>
          );
        })}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-center space-x-2 text-xs text-gray-400 bg-[#202c33] px-3.5 py-2 rounded-xl w-fit border border-gray-700/40 animate-pulse">
            <Bot className="w-4 h-4 text-emerald-400 animate-spin" />
            <span>Chanakya Quant is computing multi-timeframe indicators...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input Bar (WhatsApp Web Style) */}
      <form
        onSubmit={handleSubmit}
        className="h-16 bg-[#202c33] border-t border-gray-700/50 px-4 flex items-center space-x-3 flex-shrink-0 z-10"
      >
        <div className="flex-1 bg-[#2a3942] rounded-xl px-4 py-2 flex items-center border border-transparent focus-within:border-emerald-500/50">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type command (e.g. ADD RELIANCE, TOP 5, ANALYZE TCS) or ask a market question..."
            className="w-full bg-transparent text-white placeholder-gray-400 text-sm focus:outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={!inputText.trim() || isTyping}
          className={`p-2.5 rounded-full transition-all duration-150 flex items-center justify-center ${
            inputText.trim() && !isTyping
              ? 'bg-emerald-500 hover:bg-emerald-400 text-white shadow-lg shadow-emerald-900/50'
              : 'bg-gray-700/40 text-gray-500 cursor-not-allowed'
          }`}
          title="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
