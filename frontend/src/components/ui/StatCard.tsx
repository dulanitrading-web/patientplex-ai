"use client";

import clsx from "clsx";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change?: number; // Percentage change, e.g. 12.5 or -3.2
  color?: "blue" | "green" | "purple" | "teal" | "red" | "yellow";
  subtitle?: string;
}

const colorMap: Record<string, { bg: string; text: string }> = {
  blue: { bg: "bg-blue-50 dark:bg-blue-950", text: "text-blue-600 dark:text-blue-400" },
  green: { bg: "bg-green-50 dark:bg-green-950", text: "text-green-600 dark:text-green-400" },
  purple: { bg: "bg-purple-50 dark:bg-purple-950", text: "text-purple-600 dark:text-purple-400" },
  teal: { bg: "bg-teal-50 dark:bg-teal-950", text: "text-teal-600 dark:text-teal-400" },
  red: { bg: "bg-red-50 dark:bg-red-950", text: "text-red-600 dark:text-red-400" },
  yellow: { bg: "bg-yellow-50 dark:bg-yellow-950", text: "text-yellow-600 dark:text-yellow-400" },
};

export default function StatCard({ icon, label, value, change, color = "blue", subtitle }: StatCardProps) {
  const c = colorMap[color];
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className={clsx("p-1.5 rounded-lg", c.bg, c.text)}>{icon}</div>
        <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-gray-900 dark:text-gray-100 tabular-nums">{value}</span>
        {change !== undefined && (
          <span className={clsx(
            "flex items-center gap-0.5 text-xs font-medium pb-0.5",
            change >= 0 ? "text-green-600 dark:text-green-400" : "text-red-500 dark:text-red-400",
          )}>
            {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      {subtitle && <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">{subtitle}</div>}
    </div>
  );
}
