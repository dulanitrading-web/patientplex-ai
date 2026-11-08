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

// Demo data — replace with real API integration
const DEMO_NOTIFICATIONS: Notification[] = [
  {
    id: "1",
    type: "new_booking",
    message: "New appointment booked: Priya Sharma at 3:00 PM today",
    timestamp: "10 min ago",
    read: false,
  },
  {
    id: "2",
    type: "missed_call",
    message: "Missed call from +91 98765 43210",
    timestamp: "25 min ago",
    read: false,
  },
  {
    id: "3",
    type: "campaign_update",
    message: "Google Ads campaign 'Dental Implants' reached 1,000 impressions",
    timestamp: "1 hour ago",
    read: false,
  },
  {
    id: "4",
    type: "system",
    message: "Your monthly report is ready to view",
    timestamp: "3 hours ago",
    read: true,
  },
  {
    id: "5",
    type: "new_booking",
    message: "New appointment booked: Rahul Verma tomorrow at 11:00 AM",
    timestamp: "5 hours ago",
    read: true,
  },
];

const ICON_MAP = {
  new_booking: Calendar,
  missed_call: PhoneMissed,
  campaign_update: Megaphone,
  system: Info,
};

const ICON_COLOR_MAP = {
  new_booking: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40",
  missed_call: "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/40",
  campaign_update: "text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/40",
  system: "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800",
};

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(DEMO_NOTIFICATIONS);
  const ref = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  function markAllRead() {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  return (
    <div className="relative" ref={ref}>
      {/* Bell button */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Notifications</h3>
              <span className="text-[10px] font-medium text-amber-700 bg-amber-100 dark:text-amber-300 dark:bg-amber-900/40 px-1.5 py-0.5 rounded">
                Demo data
              </span>
            </div>
            <div className="flex items-center gap-1">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setOpen(false)}
                className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Notification list */}
          <div className="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
            {notifications.map((n) => {
              const Icon = ICON_MAP[n.type];
              return (
                <div
                  key={n.id}
                  className={clsx(
                    "flex gap-3 px-4 py-3 transition-colors",
                    !n.read && "bg-blue-50/50 dark:bg-blue-950/20",
                  )}
                >
                  <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center shrink-0", ICON_COLOR_MAP[n.type])}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className={clsx("text-sm leading-snug", !n.read ? "text-gray-900 dark:text-gray-100" : "text-gray-600 dark:text-gray-400")}>
                      {n.message}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">{n.timestamp}</p>
                  </div>
                  {!n.read && (
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
