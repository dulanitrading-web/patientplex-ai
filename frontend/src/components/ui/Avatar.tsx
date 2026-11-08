"use client";

import clsx from "clsx";

interface AvatarProps {
  name: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizes = { sm: "w-8 h-8 text-xs", md: "w-10 h-10 text-sm", lg: "w-12 h-12 text-base" };

const colors = [
  "bg-emerald-500/15 text-emerald-400",
  "bg-cyan-500/15 text-cyan-400",
  "bg-violet-500/15 text-violet-400",
  "bg-amber-500/15 text-amber-400",
  "bg-rose-500/15 text-rose-400",
];

function getInitials(name: string): string {
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

function hashColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}

export default function Avatar({ name, size = "md", className }: AvatarProps) {
  return (
    <div className={clsx(
      "rounded-full flex items-center justify-center font-semibold shrink-0",
      sizes[size], hashColor(name), className,
    )}>
      {getInitials(name)}
    </div>
  );
}
