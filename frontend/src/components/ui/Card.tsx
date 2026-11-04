"use client";

import clsx from "clsx";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
  hover?: boolean;
}

export default function Card({ children, className, padding = "md", hover }: CardProps) {
  const pads = { none: "", sm: "p-3", md: "p-5", lg: "p-6" };
  return (
    <div className={clsx(
      "bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl",
      pads[padding],
      hover && "hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 transition-all cursor-pointer",
      className,
    )}>
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={clsx("flex items-center justify-between mb-4", className)}>{children}</div>;
}

export function CardTitle({ children, icon }: { children: React.ReactNode; icon?: React.ReactNode }) {
  return (
    <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
      {icon && <span className="text-gray-400">{icon}</span>}
      {children}
    </h3>
  );
}
