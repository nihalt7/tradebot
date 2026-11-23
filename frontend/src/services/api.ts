import { 
  ChatMessage, 
  WatchlistItem, 
  ScannerResults, 
  ActivePosition, 
  RiskSettings, 
  DashboardOverview, 
  BacktestResult 
} from '../types';

// Environment-aware API & WebSocket endpoints for Vercel + Render
const getApiBase = (): string => {
  const envUrl = (import.meta as any).env?.VITE_API_URL;
  if (envUrl) {
    const cleanUrl = envUrl.replace(/\/+$/, '');
    return cleanUrl.endsWith('/api/v1') ? cleanUrl : `${cleanUrl}/api/v1`;
  }
  return 'http://127.0.0.1:8000/api/v1';
};

const getWsUrl = (): string => {
  const envWs = (import.meta as any).env?.VITE_WS_URL;
  if (envWs) {
    return envWs;
  }
  const envApi = (import.meta as any).env?.VITE_API_URL;
  if (envApi) {
    const wsProto = envApi.startsWith('https') ? 'wss' : 'ws';
    const cleanHost = envApi.replace(/^https?:\/\//, '').replace(/\/+$/, '').replace(/\/api\/v1$/, '');
    return `${wsProto}://${cleanHost}/ws/market`;
  }
  return 'ws://127.0.0.1:8000/ws/market';
};

const API_BASE = getApiBase();
const WS_URL = getWsUrl();

export const api = {
  // Dashboard & Indices
  async getDashboardOverview(): Promise<DashboardOverview> {
    const res = await fetch(`${API_BASE}/dashboard/overview`);
    return res.json();
  },

  // Watchlist (Engine A)
  async getWatchlist(): Promise<WatchlistItem[]> {
    const res = await fetch(`${API_BASE}/watchlist/`);
    return res.json();
  },

  async addToWatchlist(symbol: string): Promise<any> {
    const res = await fetch(`${API_BASE}/watchlist/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol })
    });
    return res.json();
  },

  async removeFromWatchlist(symbol: string): Promise<any> {
    const res = await fetch(`${API_BASE}/watchlist/remove/${symbol}`, {
      method: 'DELETE'
    });
    return res.json();
  },

  // Scanner (Engine B)
  async getScannerLatest(): Promise<ScannerResults> {
    const res = await fetch(`${API_BASE}/scanner/latest`);
    return res.json();
  },

  async scanNow(): Promise<ScannerResults> {
    const res = await fetch(`${API_BASE}/scanner/scan-now`, {
      method: 'POST'
    });
    return res.json();
  },

  // AI Chat
  async getMessages(conversationId: string = 'main_chat'): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/chat/messages/${conversationId}`);
    return res.json();
  },

  async sendMessage(conversationId: string = 'main_chat', text: string): Promise<ChatMessage> {
    const res = await fetch(`${API_BASE}/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId, text })
    });
    return res.json();
  },

  async clearChat(conversationId: string = 'main_chat'): Promise<any> {
    const res = await fetch(`${API_BASE}/chat/messages/${conversationId}/clear`, {
      method: 'DELETE'
    });
    return res.json();
  },

  // Signals & Positions
  async getActiveSignals(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/signals/active`);
    return res.json();
  },

  async getActivePositions(): Promise<ActivePosition[]> {
    const res = await fetch(`${API_BASE}/signals/positions`);
    return res.json();
  },

  async placePaperOrder(order: any): Promise<any> {
    const res = await fetch(`${API_BASE}/signals/paper-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(order)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Order execution failed');
    }
    return res.json();
  },

  async closePosition(positionId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/signals/positions/${positionId}/close`, {
      method: 'POST'
    });
    return res.json();
  },

  // Risk Management
  async getRiskSettings(): Promise<RiskSettings> {
    const res = await fetch(`${API_BASE}/risk/`);
    return res.json();
  },

  async updateRiskSettings(settings: Partial<RiskSettings>): Promise<RiskSettings> {
    const res = await fetch(`${API_BASE}/risk/update`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    return res.json();
  },

  async resetDailyLoss(): Promise<any> {
    const res = await fetch(`${API_BASE}/risk/reset-daily-loss`, {
      method: 'POST'
    });
    return res.json();
  },

  // Backtest
  async runBacktest(symbol: string, timeframe: string = '5m', capital: number = 500000, riskPct: number = 1.0): Promise<BacktestResult> {
    const res = await fetch(`${API_BASE}/backtest/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, timeframe, capital, risk_pct: riskPct })
    });
    return res.json();
  }
};

// WebSocket Service with Auto-Reconnect
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectInterval = 3000;
  private onMarketTickCallback?: (data: any) => void;
  private onSignalAlertCallback?: (data: any) => void;
  private onChatMessageCallback?: (data: any) => void;

  constructor(
    onMarketTick?: (data: any) => void,
    onSignalAlert?: (data: any) => void,
    onChatMessage?: (data: any) => void
  ) {
    this.onMarketTickCallback = onMarketTick;
    this.onSignalAlertCallback = onSignalAlert;
    this.onChatMessageCallback = onChatMessage;
    this.connect();
  }

  private connect() {
    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log(`Connected to TradePulse WebSocket server at ${WS_URL}`);
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'MARKET_TICK' && this.onMarketTickCallback) {
            this.onMarketTickCallback(msg.data);
          } else if (msg.type === 'SIGNAL_ALERT' && this.onSignalAlertCallback) {
            this.onSignalAlertCallback(msg.data);
          } else if (msg.type === 'CHAT_MESSAGE' && this.onChatMessageCallback) {
            this.onChatMessageCallback(msg.data);
          }
        } catch (e) {
          // non-json or ping
        }
      };

      this.ws.onclose = () => {
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket error, attempting reconnect:', err);
        this.ws?.close();
      };
    } catch (e) {
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public send(msg: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(msg);
    }
  }
}
