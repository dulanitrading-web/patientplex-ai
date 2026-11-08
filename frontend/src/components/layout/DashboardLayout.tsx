"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import clsx from "clsx";
import {
  LayoutDashboard, BarChart3, Calendar, MessageCircle, Globe,
  Phone, TrendingUp, Settings, CreditCard, LogOut, Menu, X, Users,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/auth";
import Avatar from "@/components/ui/Avatar";
import NotificationBell from "@/components/ui/NotificationBell";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/patients", label: "Patients", icon: Users },
  { href: "/dashboard/campaigns", label: "Campaigns", icon: TrendingUp },
  { href: "/dashboard/appointments", label: "Appointments", icon: Calendar },
  { href: "/dashboard/conversations", label: "WhatsApp", icon: MessageCircle },
  { href: "/dashboard/calls", label: "Calls", icon: Phone },
  { href: "/dashboard/conversions", label: "Funnel", icon: BarChart3 },
  { href: "/dashboard/landing-pages", label: "Landing Pages", icon: Globe },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { doctor, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#FAFAF8] flex">
      {/* Sidebar */}
      <aside className={clsx(
        "fixed inset-y-0 left-0 z-30 w-60 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200",
        "lg:translate-x-0 lg:static",
        sidebarOpen ? "translate-x-0" : "-translate-x-full",
      )}>
        {/* Logo */}
        <div className="h-16 flex items-center gap-2.5 px-4 border-b border-slate-200 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">P</span>
          </div>
          <span className="font-semibold text-slate-900 tracking-tight">PatientPlex</span>
          <button onClick={() => setSidebarOpen(false)} className="ml-auto lg:hidden text-slate-500 hover:text-slate-900">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link key={item.href} href={item.href} onClick={() => setSidebarOpen(false)}>
                <div className={clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150",
                  active
                    ? "bg-emerald-50 text-emerald-700 border-l-2 border-emerald-500"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100 border-l-2 border-transparent",
                )}>
                  <item.icon className="w-4 h-4 shrink-0" />
                  {item.label}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Doctor info + logout */}
        <div className="px-3 py-3 border-t border-slate-200 shrink-0">
          <div className="flex items-center gap-2.5 px-2 mb-2">
            <Avatar name={doctor?.full_name || "D"} size="sm" />
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-slate-900 truncate">{doctor?.full_name || "Doctor"}</div>
              <div className="text-xs text-slate-500 truncate">{doctor?.clinic_name || doctor?.email}</div>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-500 hover:text-red-500 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <LogOut className="w-4 h-4" /> Sign out
          </button>
        </div>
      </aside>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-20 bg-black/50 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 bg-white/90 backdrop-blur-xl border-b border-slate-200 flex items-center px-4 lg:px-6 shrink-0 sticky top-0 z-10">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden mr-3 text-slate-500 hover:text-slate-900">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <NotificationBell />
          <span className="text-sm text-slate-500 hidden sm:block ml-3">
            {doctor?.clinic_name} · {doctor?.city}
          </span>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
