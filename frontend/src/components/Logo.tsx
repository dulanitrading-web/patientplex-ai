"use client";

export default function Logo({ size = 36 }: { size?: number }) {
  const id = `lg_${size}`;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="PatientPlex logo"
    >
      <defs>
        <linearGradient id={`${id}_bg`} x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
          <stop stopColor="#1e293b" />
          <stop offset="0.5" stopColor="#334155" />
          <stop offset="1" stopColor="#475569" />
        </linearGradient>
        <linearGradient id={`${id}_pulse`} x1="4" y1="32" x2="44" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="white" stopOpacity="0.5" />
          <stop offset="0.5" stopColor="white" stopOpacity="1" />
          <stop offset="1" stopColor="white" stopOpacity="0.5" />
        </linearGradient>
      </defs>
      {/* Background rounded rectangle */}
      <rect width="48" height="48" rx="14" fill={`url(#${id}_bg)`} />
      {/* Stylised P letterform */}
      <path
        d="M15 11h8.5a8.5 8.5 0 0 1 8.5 8.5v0a8.5 8.5 0 0 1-8.5 8.5H20v9h-5V11z"
        fill="white"
        fillOpacity="0.95"
      />
      <path
        d="M20 15.5v8.5h3.5a4.25 4.25 0 0 0 0-8.5H20z"
        fill={`url(#${id}_bg)`}
      />
      {/* Heartbeat / pulse line */}
      <path
        d="M6 35h7l2.5-5 3 10 3.5-12 3 10 2.5-5H35l3.5-3 3.5 3h3"
        stroke={`url(#${id}_pulse)`}
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
