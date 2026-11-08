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
      {label && <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>}
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={clsx(
            "w-full appearance-none rounded-lg border px-3 py-2.5 pr-9 text-sm bg-white/[0.05] transition-colors",
            error
              ? "border-red-500/50 focus:ring-red-500/30"
              : "border-white/10 focus:border-emerald-500/50 focus:ring-emerald-500/30",
            "focus:outline-none focus:ring-2 focus:ring-offset-0",
            "text-white"
          )}
        >
          {placeholder && <option value="" disabled className="bg-[#0F172A] text-slate-500">{placeholder}</option>}
          {options.map((o) => <option key={o.value} value={o.value} className="bg-[#0F172A] text-white">{o.label}</option>)}
        </select>
        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
      </div>
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  );
}
