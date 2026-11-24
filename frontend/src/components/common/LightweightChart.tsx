"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi } from "lightweight-charts";

interface CandleData {
  time: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface LightweightChartProps {
  candles: CandleData[];
  symbol?: string;
  height?: number;
}

export default function LightweightChart({
  candles,
  symbol = "NSE STOCK",
  height = 420
}: LightweightChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    chartContainerRef.current.innerHTML = "";

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: "#0B0E14" },
        textColor: "#94A3B8",
      },
      grid: {
        vertLines: { color: "#161D2B" },
        horzLines: { color: "#161D2B" },
      },
      timeScale: {
        borderColor: "#1E2638",
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: "#1E2638",
      },
    });

    chartRef.current = chart;

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#00C076",
      downColor: "#FF3B30",
      borderVisible: false,
      wickUpColor: "#00C076",
      wickDownColor: "#FF3B30",
    });

    // Format candle timestamps cleanly for lightweight-charts
    const formattedData = candles.map((c) => {
      let t: any = c.time;
      if (typeof t === "string") {
        // Parse date string to unix timestamp (seconds)
        const parsed = new Date(t).getTime();
        if (!isNaN(parsed)) {
          t = Math.floor(parsed / 1000);
        }
      }
      return {
        time: t,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      };
    });

    candlestickSeries.setData(formattedData);

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [candles, height]);

  return (
    <div className="w-full relative bg-[#0B0E14] rounded-xl overflow-hidden border border-[#1E2638]">
      <div className="px-4 py-2 bg-[#0E121B] border-b border-[#1E2638] flex items-center justify-between text-xs">
        <span className="font-semibold text-white tracking-wide">{symbol} — Lightweight Candlestick Feed</span>
        <span className="text-[10px] text-slate-400 font-mono">NSE OHLCV</span>
      </div>
      <div ref={chartContainerRef} className="w-full" style={{ height }} />
    </div>
  );
}
