"use client";

import clsx from "clsx";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circle" | "rect";
  width?: string;
  height?: string;
}

export default function Skeleton({ className, variant = "text", width, height }: SkeletonProps) {
  const base = "animate-pulse bg-white/5";
  const variants = {
    text: "h-4 rounded",
    circle: "rounded-full",
    rect: "rounded-lg",
  };

  return (
    <div
      className={clsx(base, variants[variant], className)}
      style={{ width: width || "100%", height: height || (variant === "circle" ? width : undefined) }}
    />
  );
}

export function StatSkeleton() {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <Skeleton width="60%" className="mb-2" />
      <Skeleton width="40%" height="28px" className="rounded-md" />
    </div>
  );
}

export function ListSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
          <Skeleton variant="circle" width="40px" />
          <div className="flex-1 space-y-2">
            <Skeleton width="50%" />
            <Skeleton width="30%" />
          </div>
        </div>
      ))}
    </div>
  );
}
