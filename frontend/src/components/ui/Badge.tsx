"use client";

import clsx from "clsx";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info" | "outline";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  icon?: React.ReactNode;
  className?: string;
}

const styles: Record<BadgeVariant, string> = {
  default: "bg-white/10 text-slate-700",
  success: "bg-black/5 text-slate-700",
  warning: "bg-amber-500/10 text-amber-400",
  danger: "bg-red-500/10 text-red-600",
  info: "bg-slate-500/10 text-slate-600",
  outline: "bg-transparent border border-slate-200 text-slate-400",
};

export default function Badge({ children, variant = "default", icon, className }: BadgeProps) {
  return (
    <span className={clsx(
      "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
      styles[variant],
      className,
    )}>
      {icon}
      {children}
    </span>
  );
}
