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
      "bg-white border border-slate-200 rounded-xl",
      pads[padding],
      hover && "hover:border-slate-300 hover:shadow-md transition-all cursor-pointer",
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
    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
      {icon && <span className="text-slate-500">{icon}</span>}
      {children}
    </h3>
  );
}
