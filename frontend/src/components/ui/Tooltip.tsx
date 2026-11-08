"use client";

import { useState } from "react";
import clsx from "clsx";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom";
}

export default function Tooltip({ content, children, position = "top" }: TooltipProps) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative inline-flex" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className={clsx(
          "absolute z-30 px-2.5 py-1.5 text-xs font-medium text-white bg-[#1E293B] border border-white/10 rounded-lg shadow-xl whitespace-nowrap pointer-events-none",
          position === "top" ? "bottom-full mb-2 left-1/2 -translate-x-1/2" : "top-full mt-2 left-1/2 -translate-x-1/2",
        )}>
          {content}
        </div>
      )}
    </div>
  );
}
