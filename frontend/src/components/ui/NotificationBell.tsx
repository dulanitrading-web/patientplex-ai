"use client";

import { useState, useRef, useEffect } from "react";
import { Bell, Calendar, PhoneMissed, Megaphone, Info, X } from "lucide-react";
import clsx from "clsx";

interface Notification {
  id: string;
  type: "new_booking" | "missed_call" | "campaign_update" | "system";
  message: string;
  timestamp: string;
  read: boolean;
}

const DEMO_NOTIFICATIONS: Notification[] = [
  { id: "1", type: "new_booking", message: "New appointment booked: Priya Sharma at 3:00 PM today", timestamp: "10 min ago", read: false },
  { id: "2", type: "missed_call", message: "Missed call from +91 98765 43210", timestamp: "25 min ago", read: false },
  { id: "3", type: "campaign_update", message: "Google Ads campaign 'Dental Implants' reached 1,000 impressions", timestamp: "1 hour ago", read: false },
  { id: "4", type: "system", message: "Your monthly report is ready to view", timestamp: "3 hours ago", read: true },
  { id: "5", type: "new_booking", message: "New appointment booked: Rahul Verma tomorrow at 11:00 AM", timestamp: "5 hours ago", read: true },
];

const ICON_MAP = {
  new_booking: Calendar,
  missed_call: PhoneMissed,
  campaign_update: Megaphone,
  system: Info,
};

const ICON_COLOR_MAP = {
  new_booking: "text-cyan-400 bg-cyan-500/10",
  missed_call: "text-red-600 bg-red-500/10",
  campaign_update: "text-violet-400 bg-violet-500/10",
  system: "text-slate-400 bg-white/5",
};

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(DEMO_NOTIFICATIONS);
  const ref = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  function markAllRead() {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-100 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-emerald-500 text-[#0A0E1A] text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white border border-slate-200 rounded-xl shadow-2xl shadow-lg z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-white">Notifications</h3>
              <span className="text-[10px] font-medium text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">Demo</span>
            </div>
            <div className="flex items-center gap-1">
              {unreadCount > 0 && (
                <button onClick={markAllRead} className="text-xs text-emerald-400 hover:text-emerald-300 font-medium">Mark all read</button>
              )}
              <button onClick={() => setOpen(false)} className="p-1 rounded text-slate-500 hover:text-slate-700">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-white/[0.03]">
            {notifications.map((n) => {
              const Icon = ICON_MAP[n.type];
              return (
                <div key={n.id} className={clsx("flex gap-3 px-4 py-3 transition-colors", !n.read && "bg-emerald-500/[0.03]")}>
                  <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center shrink-0", ICON_COLOR_MAP[n.type])}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className={clsx("text-sm leading-snug", !n.read ? "text-white" : "text-slate-400")}>{n.message}</p>
                    <p className="text-xs text-slate-600 mt-0.5">{n.timestamp}</p>
                  </div>
                  {!n.read && <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 shrink-0" />}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
