"use client";

import { useState, useRef, useEffect } from "react";
import { Bell, Calendar, PhoneMissed, Megaphone, Info, X, Loader2 } from "lucide-react";
import clsx from "clsx";
import { fetchWithAuth } from "@/lib/api";

interface Notification {
  id: string;
  type: "new_booking" | "missed_call" | "campaign_update" | "system";
  message: string;
  timestamp: string;
  read: boolean;
}

const ICON_MAP = {
  new_booking: Calendar,
  missed_call: PhoneMissed,
  campaign_update: Megaphone,
  system: Info,
};

const ICON_COLOR_MAP = {
  new_booking: "text-cyan-600 bg-cyan-100",
  missed_call: "text-red-600 bg-red-100",
  campaign_update: "text-violet-600 bg-violet-100",
  system: "text-slate-400 bg-slate-100",
};

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // Fetch notifications when bell opens or on mount
  useEffect(() => {
    fetchNotifications();
    // Refresh every 2 minutes
    const interval = setInterval(fetchNotifications, 120000);
    return () => clearInterval(interval);
  }, []);

  async function fetchNotifications() {
    try {
      const res = await fetchWithAuth("/notifications/");
      const data = await res.json();
      if (data.notifications && data.notifications.length > 0) {
        setNotifications(data.notifications);
        setIsLive(true);
      }
    } catch {
      // Silently fail — don't show errors for notifications
    }
  }

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
        onClick={() => { setOpen((prev) => !prev); if (!open) fetchNotifications(); }}
        className="relative p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-emerald-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white border border-slate-200 rounded-xl shadow-2xl z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-900">Notifications</h3>
              {isLive && (
                <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                  Live
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              {unreadCount > 0 && (
                <button onClick={markAllRead} className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">Mark all read</button>
              )}
              <button onClick={() => setOpen(false)} className="p-1 rounded text-slate-500 hover:text-slate-700">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <Bell className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                <p className="text-sm text-slate-400">No notifications yet</p>
                <p className="text-xs text-slate-300 mt-1">You&apos;ll see alerts when appointments are booked, patients arrive, and campaigns hit milestones.</p>
              </div>
            ) : (
              notifications.map((n) => {
                const Icon = ICON_MAP[n.type] || Info;
                return (
                  <div key={n.id} className={clsx("flex gap-3 px-4 py-3 transition-colors", !n.read && "bg-emerald-50")}>
                    <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center shrink-0", ICON_COLOR_MAP[n.type] || ICON_COLOR_MAP.system)}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className={clsx("text-sm leading-snug", !n.read ? "text-slate-900" : "text-slate-500")}>{n.message}</p>
                      {n.timestamp && <p className="text-xs text-slate-400 mt-0.5">{n.timestamp}</p>}
                    </div>
                    {!n.read && <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 shrink-0" />}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
