"use client";

import React, { useEffect, useRef, memo } from "react";

interface TradingViewWidgetProps {
  symbol?: string; // e.g. "RELIANCE", "TCS", "NIFTY"
  theme?: "dark" | "light";
  interval?: string;
  height?: string | number;
}

function TradingViewWidgetComponent({
  symbol = "RELIANCE",
  theme = "dark",
  interval = "5",
  height = "100%"
}: TradingViewWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";

    const cleanSym = symbol.replace(".NS", "").replace(".BO", "");
    const tvSymbol = cleanSym.includes(":") ? cleanSym : `NSE:${cleanSym}`;

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.type = "text/javascript";
    script.async = true;
    script.onload = () => {
      if (typeof (window as any).TradingView !== "undefined" && containerRef.current) {
        new (window as any).TradingView.widget({
          autosize: true,
          symbol: tvSymbol,
          interval: interval,
          timezone: "Asia/Kolkata",
          theme: theme,
          style: "1",
          locale: "in",
          toolbar_bg: "#0B0E14",
          enable_publishing: false,
          allow_symbol_change: true,
          container_id: containerRef.current.id,
          hide_side_toolbar: false,
          studies: [
            "MASimple@tv-basicstudies",
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
            "VWAP@tv-basicstudies"
          ],
        });
      }
    };

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [symbol, theme, interval]);

  const uniqueId = `tv_chart_container_${symbol.replace(/[^a-zA-Z0-9]/g, "_")}`;

  return (
    <div className="w-full h-full relative min-h-[500px] bg-[#0E121B] rounded-xl overflow-hidden border border-[#1E2638]">
      <div
        id={uniqueId}
        ref={containerRef}
        className="tradingview-widget-container w-full h-full"
        style={{ height }}
      />
    </div>
  );
}

export const TradingViewWidget = memo(TradingViewWidgetComponent);
export default TradingViewWidget;
