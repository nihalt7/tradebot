# TradePulse AI - Advanced Indian Stock Market AI Trading Platform

An enterprise-grade, real-time AI quantitative trading chat application for the Indian Stock Market (NSE). Styled like **WhatsApp Web** with custom emerald financial styling, equipped with two independent monitoring engines, a 14-indicator multi-timeframe quantitative scoring model (0–100), automated position sizing, and strict capital protection.

---

## 1. Production Technology Stack (Updated)

| Component | Technology | Role |
|---|---|---|
| **Frontend Platform** | **Vercel** | React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend Platform** | **Render** | Python 3.12+, FastAPI, Uvicorn, WebSockets, APScheduler |
| **Database** | **MongoDB Atlas** | PyMongo, Cloud Document DB, Indexing |
| **Market Data Engine** | NSE Real-time & Simulator | High-liquidity F&O universe, realistic orderbook tick engine |
| **Quantitative Engine** | NumPy & Pandas | 14 Indicators, Multi-timeframe analysis (1m, 5m, 15m, 1h) |

---

## 2. Dual Monitoring Architecture

### Engine A: Personal Watchlist Monitoring
- Users add/remove stocks directly in chat (`ADD RELIANCE`, `REMOVE TCS`, `LIST`).
- Continuously scans user's selected stocks across multiple timeframes.
- Applies the **Golden Rule:** *No Quality Opportunity = No Message*. Confirmed opportunities (Score ≥ 75) trigger instant interactive trading alert cards in chat.

### Engine B: Automatic NSE Market Scanner
- Automatically monitors the liquid NSE equity universe.
- Identifies:
  - Top 5 BUY opportunities (ranked by Setup Score)
  - Top 5 SELL opportunities
  - Bullish breakouts above resistance with volume expansion
  - Bearish breakdowns below support
  - Unusual volume activity (≥ 1.5x 20-period volume MA)
  - Trend reversals (Hammer/Shooting Star, RSI momentum)

---

## 3. Local Development Quickstart

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm

### 1. Start Backend
```powershell
python run_backend.py
```
Backend will start on `http://127.0.0.1:8000`. Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Start Frontend
```powershell
cd frontend
npm run dev
```
Frontend will be available at `http://127.0.0.1:5173`.

---

## 4. Production Deployment

Follow the detailed instructions in [DEPLOYMENT.md](file:///c:/Users/HP/Desktop/tradebot/DEPLOYMENT.md):
- **MongoDB Atlas:** Create free cluster and copy `MONGODB_URI`.
- **Render:** Deploy backend using the included `render.yaml` or connect GitHub repo with start command `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
- **Vercel:** Import frontend and set `VITE_API_URL` and `VITE_WS_URL`.
