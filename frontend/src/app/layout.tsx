import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trade Bot AI — Advanced Indian Stock Market Engine",
  description: "Advanced AI-Powered Indian Stock Market Analysis & Quantitative Trading Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0B0E14] text-slate-100 min-h-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}
