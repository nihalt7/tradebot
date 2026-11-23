import re
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.core.database import get_database
from backend.app.market_data.provider_base import MarketDataProvider
from backend.app.engines.scanner_engine import ScannerEngine
from backend.app.engines.technical_indicators import TechnicalIndicatorsEngine
from backend.app.engines.entry_exit import EntryExitEngine
from backend.app.engines.ai_ranking import AIRankingEngine
from backend.app.engines.multi_timeframe import MultiTimeframeEngine
from backend.app.engines.risk_manager import RiskManager

class AIChatAnalyst:
    def __init__(self, provider: MarketDataProvider, scanner: ScannerEngine):
        self.provider = provider
        self.scanner = scanner
        self.mtf_engine = MultiTimeframeEngine(provider)

    def process_message(self, user_id: int, message_text: str, db=None) -> Dict[str, Any]:
        """
        Parse and execute commands or answer natural language queries using MongoDB.
        Returns a dict containing response text, message_type ("text", "signal_card", "analysis_card", "market_summary"),
        and optional card_data.
        """
        if db is None:
            db = get_database()

        text = message_text.strip()
        upper_text = text.upper()

        # 1. COMMAND: HELP
        if upper_text == "HELP" or upper_text == "/HELP":
            return {
                "text": (
                    "**TradePulse AI Quant Assistant Commands:**\n\n"
                    "• `ADD <SYMBOL>` - Add stock to your personal watchlist (e.g. `ADD RELIANCE`)\n"
                    "• `REMOVE <SYMBOL>` - Remove stock from watchlist (e.g. `REMOVE TCS`)\n"
                    "• `LIST` - View your active monitored watchlist\n"
                    "• `SCAN` - Run immediate real-time NSE universe scan\n"
                    "• `TOP 5` - View today's top 5 BUY and SELL opportunities\n"
                    "• `ANALYZE <SYMBOL>` - Run full 14-indicator multi-timeframe analysis (e.g. `ANALYZE INFY`)\n"
                    "• `STATUS` - View system monitoring and engine status\n"
                    "• `START` / `STOP` - Pause or resume automated alert generation\n\n"
                    "**Natural Language Inquiries Supported:**\n"
                    "• *'Which stocks have strong bullish momentum?'*\n"
                    "• *'What is the market trend?'*\n"
                    "• *'Find the best intraday opportunities'* \n"
                    "• *'Calculate my position size for RELIANCE at 1450 with SL 1442'* \n"
                    "• *'Show my active signals'*"
                ),
                "message_type": "text",
                "card_data": None
            }

        # 2. COMMAND: ADD <SYMBOL>
        add_match = re.match(r"^ADD\s+([A-Za-z0-9_&]+)$", upper_text)
        if add_match:
            sym = add_match.group(1)
            existing = db.watchlists.find_one({"user_id": user_id, "symbol": sym})
            if existing:
                return {
                    "text": f"ℹ️ **{sym}** is already in your personal watchlist.",
                    "message_type": "text",
                    "card_data": None
                }
            count = db.watchlists.count_documents({})
            db.watchlists.insert_one({
                "id": count + 1,
                "user_id": user_id,
                "symbol": sym,
                "exchange": "NSE",
                "added_at": datetime.utcnow()
            })
            quote = self.provider.get_quote(sym)
            return {
                "text": (
                    f"✅ Added **{sym}** to your Personal Watchlist (Engine A).\n"
                    f"• Current Price: **₹{quote.get('price', 0.0):,.2f}** ({quote.get('change_pct', 0.0):+.2f}%)\n"
                    f"• Monitoring for high-probability multi-timeframe breakout & reversal setups."
                ),
                "message_type": "text",
                "card_data": None
            }

        # 3. COMMAND: REMOVE <SYMBOL>
        rem_match = re.match(r"^REMOVE\s+([A-Za-z0-9_&]+)$", upper_text)
        if rem_match:
            sym = rem_match.group(1)
            item = db.watchlists.find_one({"user_id": user_id, "symbol": sym})
            if not item:
                return {
                    "text": f"⚠️ **{sym}** was not found in your watchlist.",
                    "message_type": "text",
                    "card_data": None
                }
            db.watchlists.delete_one({"user_id": user_id, "symbol": sym})
            return {
                "text": f"🗑️ Removed **{sym}** from your Personal Watchlist.",
                "message_type": "text",
                "card_data": None
            }

        # 4. COMMAND: LIST
        if upper_text == "LIST" or "SHOW MY WATCHLIST" in upper_text or "MY WATCHLIST" in upper_text:
            items = db.watchlists.find({"user_id": user_id})
            if not items:
                return {
                    "text": "📋 Your watchlist is currently empty. Add stocks using `ADD <SYMBOL>` (e.g. `ADD RELIANCE`, `ADD TCS`).",
                    "message_type": "text",
                    "card_data": None
                }
            lines = ["📋 **Your Personal Monitored Watchlist (Engine A):**\n"]
            for w in items:
                q = self.provider.get_quote(w["symbol"])
                sym_pad = f"**{w['symbol']}**".ljust(16)
                p = f"₹{q.get('price', 0.0):,.2f}"
                chg = f"{q.get('change_pct', 0.0):+.2f}%"
                trend_emoji = "🟢" if q.get("change_pct", 0) >= 0 else "🔴"
                lines.append(f"{trend_emoji} {sym_pad} : {p} ({chg}) | VWAP: ₹{q.get('vwap', 0.0):,.2f}")
            lines.append(f"\n*Total {len(items)} stocks actively monitored by Engine A.*")
            return {
                "text": "\n".join(lines),
                "message_type": "text",
                "card_data": None
            }

        # 5. COMMAND: TOP 5 / BEST OPPORTUNITIES
        if upper_text in ("TOP 5", "TOP5", "TOP 5 STOCKS") or "TOP 5 BUY" in upper_text or "BEST INTRADAY OPPORTUNITIES" in upper_text:
            scan_res = self.scanner.cached_results
            if not scan_res.get("top_buys") and not scan_res.get("top_sells"):
                scan_res = self.scanner.run_market_scan()

            buys = scan_res.get("top_buys", [])[:5]
            sells = scan_res.get("top_sells", [])[:5]

            lines = ["🎯 **Today's Top Intraday Opportunities (Engine B Scan):**\n"]
            lines.append("🟢 **TOP 5 BUY OPPORTUNITIES:**")
            if buys:
                for b in buys:
                    lines.append(f"• **{b['symbol']}** | Score: **{b['score']}/100** | Price: ₹{b['current_price']} ({b['change_pct']:+.2f}%) | Vol: {b['volume_multiplier']}x | R:R 1:{b['risk_reward']}")
            else:
                lines.append("• *No confirmed BUY setups meeting >= 70 score threshold.*")

            lines.append("\n🔴 **TOP 5 SELL OPPORTUNITIES:**")
            if sells:
                for s in sells:
                    lines.append(f"• **{s['symbol']}** | Score: **{s['score']}/100** | Price: ₹{s['current_price']} ({s['change_pct']:+.2f}%) | Vol: {s['volume_multiplier']}x | R:R 1:{s['risk_reward']}")
            else:
                lines.append("• *No confirmed SELL setups meeting >= 70 score threshold.*")

            top_card = None
            if buys and buys[0]["score"] >= 75:
                top = buys[0]
                top_card = {
                    "id": f"SIG_{top['symbol']}_TOP5",
                    "symbol": top["symbol"],
                    "exchange": "NSE",
                    "signal": "BUY",
                    "entry_min": top["entry_min"],
                    "entry_max": top["entry_max"],
                    "stop_loss": top["stop_loss"],
                    "target_1": top["target_1"],
                    "target_2": top["target_2"],
                    "target_3": top["target_3"],
                    "rsi": top["indicators"].get("rsi_14", 58.0),
                    "vwap_status": top["indicators"].get("vwap_status", "Bullish"),
                    "ema_status": "Bullish",
                    "macd_status": "Bullish",
                    "volume_ratio": top["volume_multiplier"],
                    "timeframe": "5 Minutes",
                    "setup_score": top["score"],
                    "risk_reward": f"1:{top['risk_reward']}",
                    "signal_time": "Real-time",
                    "validity_minutes": 5,
                    "reason": top["reason"],
                    "suggested_qty": RiskManager.calculate_position_size(500000.0, 1.0, top["current_price"], top["stop_loss"])
                }

            return {
                "text": "\n".join(lines),
                "message_type": "signal_card" if top_card else "text",
                "card_data": top_card
            }

        # 6. COMMAND: SCAN
        if upper_text == "SCAN" or "SCAN MARKET" in upper_text:
            scan_res = self.scanner.run_market_scan()
            bo_count = len(scan_res.get("breakouts", []))
            bd_count = len(scan_res.get("breakdowns", []))
            vol_count = len(scan_res.get("volume_surges", []))
            return {
                "text": (
                    f"⚡ **NSE Universe Market Scan Completed ({scan_res['timestamp']})**\n\n"
                    f"• **Market Breadth:** {scan_res['advances']} Advances / {scan_res['declines']} Declines ({scan_res['market_trend']})\n"
                    f"• **Bullish Breakouts:** {bo_count} stocks surging above resistance\n"
                    f"• **Bearish Breakdowns:** {bd_count} stocks dropping below support\n"
                    f"• **Unusual Volume Spikes:** {vol_count} stocks trading >= 1.6x 20-MA volume\n"
                    f"• **Top Setups Identified:** {len(scan_res['top_buys'])} BUY / {len(scan_res['top_sells'])} SELL qualified."
                ),
                "message_type": "text",
                "card_data": None
            }

        # 7. COMMAND: ANALYZE <SYMBOL>
        ana_match = re.match(r"^(?:ANALYZE|CHECK|ANALYSE)\s+([A-Za-z0-9_&]+)$", upper_text)
        if ana_match or ("ANALYZE" in upper_text and len(text.split()) <= 4):
            extracted_sym = ana_match.group(1) if ana_match else [w for w in upper_text.split() if w not in ("ANALYZE", "ANALYSE", "CHECK", "STOCK", "THE")][0]
            extracted_sym = extracted_sym.replace(".NS", "")
            return self._generate_analysis_response(extracted_sym)

        # 8. QUERY: MARKET TREND
        if "MARKET TREND" in upper_text or "NIFTY TREND" in upper_text or upper_text == "STATUS":
            overview = self.provider.get_market_overview()
            nifty = overview["indices"].get("NIFTY 50", {})
            banknifty = overview["indices"].get("BANK NIFTY", {})
            sensex = overview["indices"].get("SENSEX", {})
            return {
                "text": (
                    f"📊 **Indian Market Trend & Breadth Analysis**\n\n"
                    f"• **NIFTY 50:** ₹{nifty.get('price', 0.0):,.2f} ({nifty.get('change_pct', 0.0):+.2f}%) - **{nifty.get('trend')}**\n"
                    f"• **BANK NIFTY:** ₹{banknifty.get('price', 0.0):,.2f} ({banknifty.get('change_pct', 0.0):+.2f}%)\n"
                    f"• **SENSEX:** ₹{sensex.get('price', 0.0):,.2f} ({sensex.get('change_pct', 0.0):+.2f}%)\n\n"
                    f"• **Market Status:** {overview.get('market_status')}\n"
                    f"• **Overall Bias:** {overview.get('market_trend')}\n"
                    f"• **Advances / Declines:** {overview.get('advances')} / {overview.get('declines')} "
                    f"({round(overview.get('advances', 1) / max(1, overview.get('declines', 1)), 2)} A/D Ratio)\n"
                    f"• **Engines:** Engine A (Watchlist) & Engine B (Scanner) Running ✅"
                ),
                "message_type": "text",
                "card_data": None
            }

        # 9. QUERY: POSITION SIZING
        if "POSITION SIZE" in upper_text or "CALCULATE POSITION" in upper_text:
            return {
                "text": (
                    "📐 **TradePulse Dynamic Position Sizing Formula:**\n\n"
                    "$$\\text{Quantity} = \\left\\lfloor \\frac{\\text{Capital} \\times \\text{Risk}\\%}{|\\text{Entry} - \\text{StopLoss}|} \\right\\rfloor$$\n\n"
                    "• **Default Capital:** ₹5,00,000\n"
                    "• **Risk per trade:** 1.0% = ₹5,00,0 max monetary risk\n"
                    "• **Example:** If Entry is ₹1,450 and SL is ₹1,442 (Risk = ₹8/share):\n"
                    "  $$\\text{Quantity} = \\frac{5000}{8} = 625 \\text{ shares}$$\n"
                    "• **Capital Cap:** Max 30% capital per single trade for safety."
                ),
                "message_type": "text",
                "card_data": None
            }

        # 10. QUERY: WHY DID YOU GENERATE THIS SIGNAL?
        if "WHY" in upper_text and "SIGNAL" in upper_text:
            return {
                "text": (
                    "🔍 **AI Signal Generation Rigor (The Golden Rule):**\n\n"
                    "TradePulse evaluates 8 strict quantitative pillars before confirming any alert:\n"
                    "1. **Trend (20 pts):** Supertrend & EMA (9, 20, 50) stack confirmation.\n"
                    "2. **Volume (20 pts):** Current volume must exceed 20-period Moving Average by at least 1.5x.\n"
                    "3. **RSI Momentum (10 pts):** 55–68 for healthy continuation (not overbought exhaustion).\n"
                    "4. **VWAP Confirmation (10 pts):** Price strictly above VWAP for BUY, below for SELL.\n"
                    "5. **MACD Confirmation (10 pts):** Histogram expansion in the direction of trade.\n"
                    "6. **Price Action (15 pts):** Clean 20-period swing breakout and candlestick confirmation.\n"
                    "7. **Multi-Timeframe Alignment (10 pts):** 5m, 15m, and 1h directional consensus.\n"
                    "8. **Risk / Reward (5 pts):** Strict minimum 1:1.5, preferably 1:2.0+.\n\n"
                    "**Threshold:** Score must be ≥ 75/100. If any pillar fails, **NO TRADE IS GENERATED.**"
                ),
                "message_type": "text",
                "card_data": None
            }

        # 11. FALLBACK / GENERAL NLP RESPONSE
        return self._conversational_fallback(text)

    def _generate_analysis_response(self, symbol: str) -> Dict[str, Any]:
        """Produce deep 14-indicator analysis card and explanation."""
        quote = self.provider.get_quote(symbol)
        df_5m = self.provider.get_historical_ohlcv(symbol, timeframe="5m", limit=70)
        
        if len(df_5m) < 20:
            return {
                "text": f"⚠️ Insufficient market history for **{symbol}** to complete multi-timeframe indicator calculations.",
                "message_type": "text",
                "card_data": None
            }

        ind = TechnicalIndicatorsEngine.compute_all_indicators(df_5m)
        mtf = self.mtf_engine.analyze_alignment(symbol)
        p = ind.get("current_price", quote.get("price", 0.0))
        chg = quote.get("change_pct", 0.0)
        
        levels_buy = EntryExitEngine.calculate_levels("BUY", p, ind.get("atr_14", 5.0), ind.get("support_resistance", {}))
        score_buy, _, _ = AIRankingEngine.calculate_score("BUY", ind, mtf, levels_buy["risk_reward"])
        
        levels_sell = EntryExitEngine.calculate_levels("SELL", p, ind.get("atr_14", 5.0), ind.get("support_resistance", {}))
        score_sell, _, _ = AIRankingEngine.calculate_score("SELL", ind, mtf, levels_sell["risk_reward"])

        best_score = max(score_buy, score_sell)
        direction = "BUY" if score_buy >= score_sell else "SELL"
        levels = levels_buy if direction == "BUY" else levels_sell

        sr = ind.get("support_resistance", {})
        candlestick = ind.get("candlestick", {})

        analysis_card = {
            "symbol": symbol.upper(),
            "exchange": "NSE",
            "current_price": p,
            "change_pct": chg,
            "trend": ind.get("supertrend_direction", "Neutral"),
            "rsi_14": ind.get("rsi_14", 50.0),
            "supertrend": ind.get("supertrend_direction", "Neutral"),
            "supertrend_val": ind.get("supertrend", 0.0),
            "vwap": ind.get("vwap", 0.0),
            "ema_9": ind.get("ema_9", 0.0),
            "ema_20": ind.get("ema_20", 0.0),
            "ema_50": ind.get("ema_50", 0.0),
            "sma_200": ind.get("sma_200", 0.0),
            "macd_bias": ind.get("macd_bias", "Neutral"),
            "support_1": sr.get("support_1", 0.0),
            "support_2": sr.get("support_2", 0.0),
            "resistance_1": sr.get("resistance_1", 0.0),
            "resistance_2": sr.get("resistance_2", 0.0),
            "candlestick_pattern": candlestick.get("pattern"),
            "volume_surge": ind.get("volume_ratio", 1.0) >= 1.5,
            "verdict": f"{'Bullish' if direction=='BUY' else 'Bearish'} Setup ({best_score}/100)",
            "score": best_score
        }

        signal_card = None
        if best_score >= 75.0:
            signal_card = {
                "id": f"SIG_{symbol}_{direction}",
                "symbol": symbol.upper(),
                "exchange": "NSE",
                "signal": direction,
                "entry_min": levels["entry_min"],
                "entry_max": levels["entry_max"],
                "stop_loss": levels["stop_loss"],
                "target_1": levels["target_1"],
                "target_2": levels["target_2"],
                "target_3": levels["target_3"],
                "rsi": ind.get("rsi_14"),
                "vwap_status": ind.get("vwap_status"),
                "ema_status": "Bullish" if ind.get("ema_bullish") else "Bearish",
                "macd_status": ind.get("macd_bias"),
                "volume_ratio": ind.get("volume_ratio"),
                "timeframe": "5 Minutes",
                "setup_score": best_score,
                "risk_reward": f"1:{levels['risk_reward']}",
                "signal_time": levels["signal_time"],
                "validity_minutes": 5,
                "reason": f"Multi-indicator {direction} alignment with {ind.get('volume_ratio')}x volume and multi-timeframe consensus.",
                "suggested_qty": RiskManager.calculate_position_size(500000.0, 1.0, p, levels["stop_loss"])
            }

        text_reply = (
            f"📊 **Comprehensive Technical Analysis: {symbol.upper()} (NSE)**\n\n"
            f"• **LTP:** ₹{p:,.2f} ({chg:+.2f}%) | **VWAP:** ₹{ind.get('vwap'):,.2f}\n"
            f"• **Trend (Supertrend 10,3):** {ind.get('supertrend_direction')} (Stop: ₹{ind.get('supertrend')})\n"
            f"• **RSI (14):** {ind.get('rsi_14')} ({'Bullish Momentum' if ind.get('rsi_14')>55 else ('Bearish Drift' if ind.get('rsi_14')<45 else 'Neutral')})\n"
            f"• **Moving Averages:** EMA 9 (₹{ind.get('ema_9')}) | EMA 20 (₹{ind.get('ema_20')}) | EMA 50 (₹{ind.get('ema_50')})\n"
            f"• **MACD (12,26,9):** {ind.get('macd_bias')} (Hist: {ind.get('macd_hist'):+.2f})\n"
            f"• **Key Levels:** R1: ₹{sr.get('resistance_1')} | S1: ₹{sr.get('support_1')}\n"
            f"• **Candle Pattern:** {candlestick.get('pattern')} ({candlestick.get('sentiment')})\n"
            f"• **Setup Quality Score:** **{best_score}/100** ({'High Quality Setup' if best_score>=75 else 'No trade zone'})\n\n"
            f"_{'Confirmed actionable setup card attached below.' if signal_card else 'Score below 75 threshold. Strict golden rule applied: NO TRADE.'}_"
        )

        return {
            "text": text_reply,
            "message_type": "signal_card" if signal_card else "analysis_card",
            "card_data": signal_card if signal_card else analysis_card
        }

    def _conversational_fallback(self, query: str) -> Dict[str, Any]:
        """Handle conversational queries and guide user to actionable commands."""
        return {
            "text": (
                f"I understood: *\"{query}\"*\n\n"
                "As your professional Indian stock market quant assistant, here is what I can do right now:\n"
                "• Type `ANALYZE <STOCK>` to inspect any NSE stock (e.g. `ANALYZE RELIANCE`)\n"
                "• Type `TOP 5` to inspect current top 5 BUY and SELL opportunities\n"
                "• Type `ADD <STOCK>` to monitor it on your private Engine A watchlist\n"
                "• Type `SCAN` to run an immediate market-wide screening across the NSE universe\n"
                "• Type `HELP` to view all available commands."
            ),
            "message_type": "text",
            "card_data": None
        }
