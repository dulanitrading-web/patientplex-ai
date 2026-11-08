"use client";

import clsx from "clsx";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change?: number;
  color?: "emerald" | "cyan" | "violet" | "amber" | "red" | "rose";
  subtitle?: string;
}

const colorMap: Record<string, { bg: string; text: string }> = {
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400" },
  cyan: { bg: "bg-cyan-500/10", text: "text-cyan-400" },
  violet: { bg: "bg-violet-500/10", text: "text-violet-400" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400" },
  red: { bg: "bg-red-500/10", text: "text-red-400" },
  rose: { bg: "bg-rose-500/10", text: "text-rose-400" },
};

export default function StatCard({ icon, label, value, change, color = "emerald", subtitle }: StatCardProps) {
  const c = colorMap[color];
  return (
    <div className="bg-[#0F172A] border border-white/5 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className={clsx("p-1.5 rounded-lg", c.bg, c.text)}>{icon}</div>
        <span className="text-sm text-slate-500">{label}</span>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-white tabular-nums">{value}</span>
        {change !== undefined && (
          <span className={clsx(
            "flex items-center gap-0.5 text-xs font-medium pb-0.5",
            change >= 0 ? "text-emerald-400" : "text-red-400",
          )}>
            {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
    </div>
  );
}
