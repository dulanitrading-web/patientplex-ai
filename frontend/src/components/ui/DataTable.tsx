"use client";

import clsx from "clsx";
import { ChevronUp, ChevronDown } from "lucide-react";

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  sortKey?: string;
  sortDir?: "asc" | "desc";
  onSort?: (key: string) => void;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  loading?: boolean;
}

export default function DataTable<T extends Record<string, unknown>>({
  columns, data, sortKey, sortDir, onSort, onRowClick, emptyMessage, loading,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="bg-[#0F172A] border border-white/5 rounded-xl overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="px-4 py-3 border-b border-white/[0.03]">
            <div className="h-4 bg-white/5 rounded animate-pulse" style={{ width: `${60 + Math.random() * 30}%` }} />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-[#0F172A] border border-white/5 rounded-xl overflow-hidden overflow-x-auto">
      <table className="w-full text-sm min-w-[500px]">
        <thead>
          <tr className="border-b border-white/5 bg-white/[0.02]">
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => col.sortable && onSort?.(col.key)}
                className={clsx(
                  "px-4 py-2.5 text-left font-semibold text-slate-500 text-xs uppercase tracking-wider",
                  col.sortable && "cursor-pointer hover:text-slate-300 select-none",
                  col.className,
                )}
              >
                <span className="flex items-center gap-1">
                  {col.label}
                  {col.sortable && sortKey === col.key && (
                    sortDir === "asc" ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                {emptyMessage || "No data found"}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr
                key={i}
                onClick={() => onRowClick?.(row)}
                className={clsx(
                  "border-b border-white/[0.03] last:border-0",
                  onRowClick && "cursor-pointer hover:bg-white/[0.03]",
                  "transition-colors",
                )}
              >
                {columns.map((col) => (
                  <td key={col.key} className={clsx("px-4 py-3 text-slate-300", col.className)}>
                    {col.render ? col.render(row) : String(row[col.key] ?? "")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
