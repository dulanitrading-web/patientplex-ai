"use client";

import clsx from "clsx";
import { ChevronDown } from "lucide-react";

interface Option { value: string; label: string; }

interface SelectProps {
  label?: string;
  options: Option[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  className?: string;
}

export default function Select({ label, options, value, onChange, placeholder, error, className }: SelectProps) {
  return (
    <div className={clsx("w-full", className)}>
      {label && <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">{label}</label>}
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={clsx(
            "w-full appearance-none rounded-lg border px-3 py-2.5 pr-9 text-sm bg-white dark:bg-gray-900 transition-colors",
            error
              ? "border-red-400 focus:ring-red-500"
              : "border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500",
            "focus:outline-none focus:ring-2 focus:ring-offset-0",
            "text-gray-900 dark:text-gray-100"
          )}
        >
          {placeholder && <option value="" disabled>{placeholder}</option>}
          {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}
