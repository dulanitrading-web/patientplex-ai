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
  default: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  success: "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400",
  warning: "bg-yellow-50 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400",
  danger: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-400",
  info: "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
  outline: "bg-transparent border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400",
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
