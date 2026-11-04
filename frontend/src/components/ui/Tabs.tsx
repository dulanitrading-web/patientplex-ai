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
    <div className={clsx("flex items-center gap-1 border-b border-gray-200 dark:border-gray-700", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={clsx(
            "px-3 py-2 text-sm font-medium border-b-2 transition-colors -mb-px",
            active === tab.id
              ? "border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400"
              : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300",
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={clsx(
              "ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-semibold",
              active === tab.id
                ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
            )}>{tab.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}
