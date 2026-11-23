export interface SignalCardData {
  id: string;
  symbol: string;
  exchange: string;
  signal: 'BUY' | 'SELL';
  entry_min: number;
  entry_max: number;
  stop_loss: number;
  target_1: number;
  target_2: number;
  target_3: number;
  rsi: number;
  vwap_status: string;
  ema_status: string;
  macd_status: string;
  volume_ratio: number;
  timeframe: string;
  setup_score: number;
  risk_reward: string;
  signal_time: string;
  validity_minutes: number;
  reason: string;
  suggested_qty?: number;
}

export interface AnalysisCardData {
  symbol: string;
  exchange: string;
  current_price: number;
  change_pct: number;
  trend: string;
  rsi_14: number;
  supertrend: string;
  supertrend_val: number;
  vwap: number;
  ema_9: number;
  ema_20: number;
  ema_50: number;
  sma_200: number;
  macd_bias: string;
  support_1: number;
  support_2: number;
  resistance_1: number;
  resistance_2: number;
  candlestick_pattern?: string;
  volume_surge: boolean;
  verdict: string;
  score: number;
}

export interface ChatMessage {
  id: number;
  conversation_id: string;
  sender: 'user' | 'assistant' | 'system';
  text: string;
  message_type: 'text' | 'signal_card' | 'analysis_card' | 'market_summary';
  card_data?: SignalCardData | AnalysisCardData | any;
  timestamp: string;
}

export interface WatchlistItem {
  id: number;
  symbol: string;
  exchange: string;
  company_name: string;
  sector?: string;
  current_price: number;
  change_pct: number;
  high: number;
  low: number;
  volume: number;
  vwap: number;
  trend: string;
  added_at: string;
}

export interface ScannerOpportunity {
  symbol: string;
  name?: string;
  sector?: string;
  signal_type: 'BUY' | 'SELL';
  current_price: number;
  change_pct: number;
  score: number;
  tier?: string;
  volume_multiplier: number;
  category: string;
  entry_min: number;
  entry_max: number;
  stop_loss: number;
  target_1: number;
  target_2: number;
  target_3: number;
  risk_reward: number;
  reason: string;
  indicators: any;
}

export interface ScannerResults {
  timestamp: string;
  market_trend: string;
  advances: number;
  declines: number;
  top_buys: ScannerOpportunity[];
  top_sells: ScannerOpportunity[];
  breakouts: any[];
  breakdowns: any[];
  volume_surges: any[];
}

export interface ActivePosition {
  id: number;
  signal_id?: string;
  symbol: string;
  direction: 'BUY' | 'SELL';
  quantity: number;
  entry_price: number;
  current_price: number;
  stop_loss: number;
  target_1: number;
  target_2: number;
  target_3: number;
  pnl: number;
  pnl_percentage: number;
  mode: string;
  status: string;
  opened_at: string;
}

export interface RiskSettings {
  capital: number;
  risk_per_trade_pct: number;
  max_daily_loss: number;
  current_daily_loss: number;
  max_open_trades: number;
  paper_trading_enabled: boolean;
  trading_halted: boolean;
}

export interface MarketIndex {
  name: string;
  symbol: string;
  price: number;
  change: number;
  change_pct: number;
  trend: string;
}

export interface DashboardOverview {
  indices: Record<string, MarketIndex>;
  market_status: string;
  market_trend: string;
  advances: number;
  declines: number;
  unchanged: number;
  timestamp: string;
  top_gainers: any[];
  top_losers: any[];
  highest_volume: any[];
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  max_drawdown: number;
  total_return_pct: number;
  net_profit: number;
  total_charges: number;
  trades: any[];
  equity_curve: { time: string; equity: number }[];
}
