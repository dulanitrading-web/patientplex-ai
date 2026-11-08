"use client";

import clsx from "clsx";

interface Tab { id: string; label: string; count?: number; }

interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
  className?: string;
}

export default function Tabs({ tabs, active, onChange, className }: TabsProps) {
  return (
    <div className={clsx("flex items-center gap-1 border-b border-white/5", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={clsx(
            "px-3 py-2 text-sm font-medium border-b-2 transition-colors -mb-px",
            active === tab.id
              ? "border-emerald-500 text-emerald-400"
              : "border-transparent text-slate-500 hover:text-slate-300 hover:border-white/10",
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={clsx(
              "ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-semibold",
              active === tab.id
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-white/5 text-slate-500",
            )}>{tab.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}
