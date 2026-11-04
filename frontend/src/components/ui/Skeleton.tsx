"use client";

import clsx from "clsx";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circle" | "rect";
  width?: string;
  height?: string;
}

export default function Skeleton({ className, variant = "text", width, height }: SkeletonProps) {
  const base = "animate-pulse bg-gray-200 dark:bg-gray-700";
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

/** Pre-built skeleton for a stat card */
export function StatSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
      <Skeleton width="60%" className="mb-2" />
      <Skeleton width="40%" height="28px" className="rounded-md" />
    </div>
  );
}

/** Pre-built skeleton for a list item */
export function ListSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 flex items-center gap-3">
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
