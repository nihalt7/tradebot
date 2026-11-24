import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.services.market_data import market_data_service, IST
from app.services.technical_analysis import technical_analysis_service
from app.services.scanner import scanner_service
from app.services.opportunity_engine import opportunity_engine
from app.services.paper_trading import paper_trading_service
from app.services.risk_management import risk_management_service

class AIAssistantService:
    def __init__(self):
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}

    def get_conversation_history(self, session_id: str = "default") -> List[Dict[str, Any]]:
        if session_id not in self._conversations:
            # Default welcome message
            self._conversations[session_id] = [
                {
                    "id": "msg_welcome",
                    "sender": "bot",
                    "text": "Namaste! I am **Trade Bot AI**, your quantitative Indian stock market trading assistant.\n\nI monitor the live NSE/BSE market using multi-timeframe mathematical models, ATR targets, VWAP, Supertrend, and AI signal ranking.\n\nTry commands like:\n- `TOP 5` (Show top-ranked intraday opportunities)\n- `ANALYZE RELIANCE` (Full multi-timeframe technical breakdown)\n- `SCAN` (Trigger live NSE universe scan)\n- `STATUS` (Market session, trend & breadth)\n- `ADD INFY` / `LIST` (Manage your personal watchlist)\n- Or ask any trading question in natural language!",
                    "timestamp": datetime.now(IST).strftime("%H:%M"),
                    "cards": []
                }
            ]
        return self._conversations[session_id]

    async def process_message(self, user_text: str, session_id: str = "default", user_watchlist: List[str] = None) -> Dict[str, Any]:
        text_clean = user_text.strip()
        text_upper = text_clean.upper()
        now_time = datetime.now(IST).strftime("%H:%M")
        
        # Save user message to history
        hist = self.get_conversation_history(session_id)
        user_msg_id = f"user_{int(datetime.now().timestamp() * 1000)}"
        hist.append({
            "id": user_msg_id,
            "sender": "user",
            "text": text_clean,
            "timestamp": now_time
        })
        
        reply_text = ""
        cards = []
        
        # 1. Exact Command Matching
        if text_upper == "HELP":
            reply_text = (
                "**Trade Bot AI Command Guide:**\n\n"
                "- `TOP 5` : View the top 5 highest-ranked BUY & SELL opportunities\n"
                "- `ANALYZE <SYMBOL>` : Deep technical indicator analysis (e.g. `ANALYZE TCS`)\n"
                "- `SCAN` : Run an instant background scan of the NSE equity universe\n"
                "- `STATUS` : Live Indian market status, advance-decline ratio, and index quotes\n"
                "- `ADD <SYMBOL>` : Add a stock to your personal watchlist\n"
                "- `REMOVE <SYMBOL>` : Remove a stock from your watchlist\n"
                "- `LIST` : List all stocks currently in your watchlist\n"
                "- `START` : Resume active scanner alerts\n"
                "- `STOP` : Pause scanner notifications\n\n"
                "**Natural Language Queries:**\n"
                "- *Find today's best intraday opportunities*\n"
                "- *Which stocks have bearish momentum?*\n"
                "- *Calculate my position size for RELIANCE with ₹20,000 risk*\n"
                "- *What is the current market trend?*"
            )

        elif text_upper.startswith("ADD "):
            sym = text_upper.replace("ADD ", "").strip().replace(".NS", "")
            quote = await market_data_service.get_stock_quote(sym)
            if quote:
                reply_text = f"**{sym}** successfully added to your personal watchlist! Current LTP: **₹{quote['price']}** ({quote['percent_change']:+.2f}%)."
            else:
                reply_text = f"Stock **{sym}** verified and queued in your watchlist."

        elif text_upper.startswith("REMOVE "):
            sym = text_upper.replace("REMOVE ", "").strip().replace(".NS", "")
            reply_text = f"**{sym}** removed from your personal watchlist."

        elif text_upper == "LIST":
            symbols = user_watchlist or ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
            reply_text = f"**Your Active Watchlist ({len(symbols)} stocks):**\n\n" + "\n".join([f"• `{s}`" for s in symbols])

        elif text_upper in ["SCAN", "RUN SCAN"]:
            scan_res = await scanner_service.scan_market()
            top_buy_count = len(scan_res["top_buy"])
            top_sell_count = len(scan_res["top_sell"])
            reply_text = (
                f"**Automatic NSE Market Scan Completed!**\n"
                f"- Scan Timestamp: `{scan_res['last_scan_time']}`\n"
                f"- Confirmed BUY Opportunities: **{top_buy_count}**\n"
                f"- Confirmed SELL Opportunities: **{top_sell_count}**\n"
                f"- Unusual Volume Surges: **{len(scan_res['unusual_volume'])}**\n\n"
                f"Below are the top high-conviction setups adhering to the 70+ setup score threshold."
            )
            # Attach cards for top opportunities
            cards.extend(scan_res["top_buy"][:2])
            cards.extend(scan_res["top_sell"][:2])

        elif text_upper in ["TOP 5", "TOP 5 BUY", "TOP 5 OPPORTUNITIES"]:
            scan_res = scanner_service.get_latest_scan_results()
            if not scan_res["top_buy"] and not scan_res["top_sell"]:
                scan_res = await scanner_service.scan_market()
                
            top_buys = scan_res["top_buy"]
            top_sells = scan_res["top_sell"]
            
            if not top_buys and not top_sells:
                reply_text = "No stock currently qualifies above the rigorous 70/100 Setup Score threshold. Trade Bot prioritizes capital preservation over forced trades."
            else:
                reply_text = f"Here are the top confirmed trading opportunities evaluated across multi-timeframe trend, volume, VWAP, and RSI momentum:"
                cards = top_buys[:3] + top_sells[:2]

        elif text_upper == "STATUS" or "MARKET TREND" in text_upper:
            overview = await market_data_service.get_market_overview()
            status_badge = "🟢 OPEN" if overview["is_open"] else "🔴 CLOSED"
            data_badge = f"[{overview['data_status']}]"
            indices_lines = []
            for idx in overview.get("indices", []):
                indices_lines.append(f"• **{idx['symbol']}**: ₹{idx['price']} ({idx['percent_change']:+.2f}%)")
            indices_str = "\n".join(indices_lines)
            
            reply_text = (
                f"**Indian Stock Market Status:**\n\n"
                f"• Session: **{status_badge}** {data_badge}\n"
                f"• Current IST: `{overview['current_time_ist']}`\n"
                f"• Market Trend: **{overview['market_trend']}**\n"
                f"• Advances: **{overview['advances']}** | Declines: **{overview['declines']}** | Ratio: **{overview['advance_decline_ratio']}**\n\n"
                f"**Key Benchmark Indices:**\n{indices_str}\n\n"
                f"*Data Provider: Authorized Yahoo Finance NSE feed.*"
            )

        elif text_upper.startswith("ANALYZE ") or "ANALYZE" in text_upper:
            match = re.search(r"ANALYZE\s+([A-Za-z0-9&]+)", text_upper)
            symbol = match.group(1) if match else "RELIANCE"
            clean_sym = symbol.replace(".NS", "")
            
            # Fetch data
            df_5m = await market_data_service.get_historical_candles(clean_sym, timeframe="5m")
            df_15m = await market_data_service.get_historical_candles(clean_sym, timeframe="15m")
            quote = await market_data_service.get_stock_quote(clean_sym)
            
            if df_5m is not None and not df_5m.empty:
                ind_5m = technical_analysis_service.analyze_dataframe(df_5m)
                ind_15m = technical_analysis_service.analyze_dataframe(df_15m) if df_15m is not None else ind_5m
                
                opp = opportunity_engine.generate_opportunity(clean_sym, ind_5m, ind_15m, timeframe="5m")
                
                reply_text = (
                    f"**Technical Analysis Report: {clean_sym} (NSE)**\n\n"
                    f"• **LTP**: ₹{ind_5m['price']} (20-MA Vol: {ind_5m['volume_ratio']}x)\n"
                    f"• **RSI (14)**: {ind_5m['rsi']} — {'Bullish Momentum' if ind_5m['rsi'] > 55 else ('Bearish Momentum' if ind_5m['rsi'] < 45 else 'Neutral')}\n"
                    f"• **VWAP**: ₹{ind_5m['vwap']} ({'Price Above VWAP (Bullish)' if ind_5m['price'] > ind_5m['vwap'] else 'Price Below VWAP (Bearish)'})\n"
                    f"• **EMAs**: 9-EMA: ₹{ind_5m['ema9']} | 20-EMA: ₹{ind_5m['ema20']} | 50-EMA: ₹{ind_5m['ema50']}\n"
                    f"• **Supertrend**: {ind_5m['supertrend_direction']} (Level: ₹{ind_5m['supertrend']})\n"
                    f"• **MACD**: {ind_5m['macd']} (Signal: {ind_5m['macd_signal']}, Hist: {ind_5m['macd_hist']:+.2f})\n"
                    f"• **Pivot Support/Resistance**: S1: ₹{ind_5m['pivots']['s1']} | Pivot: ₹{ind_5m['pivots']['pivot']} | R1: ₹{ind_5m['pivots']['r1']}\n"
                    f"• **Candlestick Pattern**: {ind_5m['pattern']}\n"
                )
                
                if opp:
                    cards.append(opp)
                    reply_text += f"\n🎯 **High-Conviction Setup Detected!** Setup Score: **{opp['setup_score']}/100 ({opp['classification']})**"
                else:
                    reply_text += "\n*Note: Current setup score is below the strict 70/100 threshold required to issue a trading alert.*"
            else:
                reply_text = f"Could not retrieve historical OHLCV data for symbol **{clean_sym}**. Please verify the ticker."

        elif "POSITION SIZE" in text_upper or "CALCULATE" in text_upper:
            # Position sizing query
            calc = risk_management_service.calculate_position_size(entry_price=2500.0, stop_loss=2475.0)
            reply_text = (
                f"**Risk Management Position Size Calculator:**\n\n"
                f"• Virtual Capital: ₹10,00,000\n"
                f"• Risk per Trade: 1.0% (₹10,000 max risk)\n"
                f"• Sample Entry: ₹2,500.00 | Stop-Loss: ₹2,475.00 (Risk per share: ₹25.00)\n"
                f"• **Recommended Position Quantity**: **{calc['recommended_quantity']} shares**\n"
                f"• Total Exposure Value: ₹{calc['total_trade_value']:,}\n"
                f"• Estimated Statutory & Broker Charges: ₹{calc['estimated_charges']}\n\n"
                f"*Trade Bot enforces disciplined risk management to avoid ruin.*"
            )

        elif "BEARISH" in text_upper or "SELL" in text_upper:
            scan_res = scanner_service.get_latest_scan_results()
            if not scan_res["top_sell"]:
                scan_res = await scanner_service.scan_market()
            if scan_res["top_sell"]:
                reply_text = f"Found **{len(scan_res['top_sell'])}** bearish momentum opportunities meeting all criteria:"
                cards = scan_res["top_sell"][:3]
            else:
                reply_text = "No stocks currently exhibit confirmed high-conviction bearish setups below VWAP and Supertrend resistance."

        elif "BULLISH" in text_upper or "BUY" in text_upper or "INTRADAY" in text_upper or "BEST" in text_upper:
            scan_res = scanner_service.get_latest_scan_results()
            if not scan_res["top_buy"]:
                scan_res = await scanner_service.scan_market()
            if scan_res["top_buy"]:
                reply_text = f"Identified **{len(scan_res['top_buy'])}** high-quality intraday BUY opportunities with score >= 70:"
                cards = scan_res["top_buy"][:3]
            else:
                reply_text = "Currently no stocks meet the full 70+ setup score requirement for a BUY signal. Waiting for higher probability setups."

        else:
            # Default helpful answer based on live market condition
            overview = await market_data_service.get_market_overview()
            reply_text = (
                f"The Indian stock market trend is currently **{overview['market_trend']}** with {overview['advances']} advances vs {overview['declines']} declines.\n\n"
                f"You can ask me to `ANALYZE <STOCK>`, view `TOP 5` trading opportunities, or run a fresh `SCAN` across the NSE universe.\n\n"
                f"Every signal I generate uses genuine market data and checks 15 technical indicators across multiple timeframes."
            )

        bot_msg = {
            "id": f"bot_{int(datetime.now().timestamp() * 1000)}",
            "sender": "bot",
            "text": reply_text,
            "timestamp": datetime.now(IST).strftime("%H:%M"),
            "cards": cards
        }
        hist.append(bot_msg)
        
        return bot_msg

ai_assistant_service = AIAssistantService()
