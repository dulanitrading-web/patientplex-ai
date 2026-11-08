"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import {
  BarChart3,
  Calendar,
  MessageCircle,
  IndianRupee,
  MousePointerClick,
  Eye,
  Globe,
  ArrowRight,
  Loader2,
  Zap,
  Activity,
  CheckCircle2,
  Clock,
  XCircle,
} from "lucide-react";
import {
  getMe,
  getCampaignOverview,
  getTodayAppointments,
  getAppointmentStats,
  launchCampaigns,
} from "@/lib/api";

interface DoctorProfile {
  full_name: string;
  clinic_name: string;
  specialty: string;
  city: string;
  onboarding_completed: boolean;
}

interface CampaignOverview {
  total_campaigns: number;
  active_campaigns: number;
  total_spend: number;
  total_clicks: number;
  total_impressions: number;
  total_conversions: number;
  avg_cpc: number;
  avg_ctr: number;
  cost_per_conversion: number;
}

interface AppointmentStats {
  total_booked: number;
  attended: number;
  no_show: number;
  cancelled: number;
  upcoming: number;
  attendance_rate: number;
  by_treatment: Record<string, number>;
}

interface TodayAppointment {
  id: string;
  patient_name: string;
  treatment: string;
  time: string;
  status: string;
}

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function getDateString(): string {
  return new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export default function DashboardPage() {
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [campaignOverview, setCampaignOverview] = useState<CampaignOverview | null>(null);
  const [appointmentStats, setAppointmentStats] = useState<AppointmentStats | null>(null);
  const [todayAppts, setTodayAppts] = useState<TodayAppointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);

  const greeting = useMemo(() => getGreeting(), []);
  const dateStr = useMemo(() => getDateString(), []);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [profile, campaigns, stats, today] = await Promise.allSettled([
        getMe(),
        getCampaignOverview(),
        getAppointmentStats(30),
        getTodayAppointments(),
      ]);
      if (profile.status === "fulfilled") setDoctor(profile.value);
      if (campaigns.status === "fulfilled") setCampaignOverview(campaigns.value);
      if (stats.status === "fulfilled") setAppointmentStats(stats.value);
      if (today.status === "fulfilled") setTodayAppts(today.value.appointments || []);
    } catch {
      /* use defaults */
    } finally {
      setLoading(false);
    }
  }

  async function handleLaunch() {
    setLaunching(true);
    try {
      await launchCampaigns(["GOOGLE", "META"]);
      await loadDashboard();
    } finally {
      setLaunching(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  const hasCampaigns = (campaignOverview?.total_campaigns || 0) > 0;

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-2xl font-bold text-white">
          {greeting}, {doctor?.full_name?.split(" ")[0] || "Doctor"}
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">{dateStr}</p>
      </motion.div>

      {/* Launch CTA */}
      {!hasCampaigns && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="relative rounded-xl border border-emerald-500/20 bg-gradient-to-r from-emerald-500/[0.08] to-cyan-500/[0.04] p-6 overflow-hidden group"
          style={{ boxShadow: "0 0 40px rgba(16,185,129,0.06)" }}
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(16,185,129,0.08),transparent_60%)]" />
          <div className="absolute -top-20 -right-20 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/15 transition-colors duration-700" />
          <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Zap className="w-6 h-6 text-emerald-400" /> Ready to get patients?
              </h2>
              <p className="text-slate-400 mt-1">
                Launch AI-powered campaigns on Google & Meta to start getting patient enquiries.
              </p>
            </div>
            <button
              onClick={handleLaunch}
              disabled={launching}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] font-semibold text-sm transition-all whitespace-nowrap disabled:opacity-50 hover:shadow-lg hover:shadow-emerald-500/20"
            >
              {launching ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Launch Campaigns <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: <Eye className="w-5 h-5" />, label: "Impressions", value: fmt(campaignOverview?.total_impressions || 0), color: "cyan" as const, sub: undefined, trend: undefined },
          { icon: <MousePointerClick className="w-5 h-5" />, label: "Clicks", value: fmt(campaignOverview?.total_clicks || 0), color: "emerald" as const, sub: `₹${campaignOverview?.avg_cpc?.toFixed(1) || "0"} avg CPC`, trend: "down" as const },
          { icon: <MessageCircle className="w-5 h-5" />, label: "Enquiries", value: fmt(campaignOverview?.total_conversions || 0), color: "violet" as const, sub: undefined, trend: undefined },
          { icon: <Calendar className="w-5 h-5" />, label: "Appointments", value: fmt(appointmentStats?.total_booked || 0), color: "amber" as const, sub: `${appointmentStats?.attendance_rate || 0}% attended`, trend: "up" as const },
        ].map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 + i * 0.08 }}
          >
            <MetricCard {...m} />
          </motion.div>
        ))}
      </div>

      {/* Spend + Funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.5 }}
          className="bg-[#0F172A] rounded-xl p-5 border border-white/5 hover:border-white/10 transition-colors duration-300"
        >
          <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
            <IndianRupee className="w-5 h-5 text-emerald-400" /> Ad spend (30 days)
          </h3>
          <div className="text-3xl font-bold text-white tabular-nums">₹{fmt(campaignOverview?.total_spend || 0)}</div>
          <div className="mt-2 text-sm text-slate-500">
            Cost per patient: ₹{appointmentStats?.attended
              ? Math.round((campaignOverview?.total_spend || 0) / appointmentStats.attended) : "—"}
          </div>
          <div className="mt-4">
            <Link href="/dashboard/campaigns"
              className="group/link inline-flex items-center gap-1.5 text-sm text-emerald-400 hover:text-emerald-300 transition-colors">
              View campaigns <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.55 }}
          className="bg-[#0F172A] rounded-xl p-5 border border-white/5 hover:border-white/10 transition-colors duration-300"
        >
          <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-cyan-400" /> Patient funnel (30 days)
          </h3>
          <div className="space-y-3">
            <FunnelRow label="Ad clicks" value={campaignOverview?.total_clicks || 0}
              total={campaignOverview?.total_clicks || 1} color="bg-cyan-500" />
            <FunnelRow label="Enquiries" value={campaignOverview?.total_conversions || 0}
              total={campaignOverview?.total_clicks || 1} color="bg-violet-500" />
            <FunnelRow label="Booked" value={appointmentStats?.total_booked || 0}
              total={campaignOverview?.total_clicks || 1} color="bg-emerald-500" />
            <FunnelRow label="Attended" value={appointmentStats?.attended || 0}
              total={campaignOverview?.total_clicks || 1} color="bg-emerald-400" />
          </div>
        </motion.div>
      </div>

      {/* Today + Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          className="lg:col-span-2 bg-[#0F172A] rounded-xl p-5 border border-white/5 hover:border-white/10 transition-colors duration-300"
        >
          <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-cyan-400" /> Today{"'"}s appointments
          </h3>
          {todayAppts.length === 0 ? (
            <p className="text-slate-500 text-sm py-4">No appointments today.</p>
          ) : (
            <div className="divide-y divide-white/5">
              {todayAppts.map((a) => (
                <div key={a.id} className="flex items-center justify-between py-3 group/row">
                  <div className="flex items-center gap-3">
                    <div className={`w-0.5 h-8 rounded-full ${statusBarColor(a.status)}`} />
                    <div>
                      <div className="font-medium text-sm text-slate-200">{a.patient_name}</div>
                      <div className="text-xs text-slate-500">{a.treatment}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-400 tabular-nums">{a.time}</span>
                    <StatusBadge status={a.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="mt-3">
            <Link href="/dashboard/appointments"
              className="group/link inline-flex items-center gap-1.5 text-sm text-emerald-400 hover:text-emerald-300 transition-colors">
              View all <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.65 }}
          className="bg-[#0F172A] rounded-xl p-5 border border-white/5 hover:border-white/10 transition-colors duration-300"
        >
          <h3 className="font-semibold text-white mb-4">Quick actions</h3>
          <div className="space-y-1">
            <Link href="/dashboard/campaigns" className="block"><QA icon={<BarChart3 className="w-4 h-4" />} label="Manage campaigns" /></Link>
            <Link href="/dashboard/conversations" className="block"><QA icon={<MessageCircle className="w-4 h-4" />} label="WhatsApp chats" /></Link>
            <Link href="/dashboard/appointments" className="block"><QA icon={<Calendar className="w-4 h-4" />} label="Appointments" /></Link>
            <Link href="/dashboard/landing-pages" className="block"><QA icon={<Globe className="w-4 h-4" />} label="Landing pages" /></Link>
          </div>

          {appointmentStats && Object.keys(appointmentStats.by_treatment || {}).length > 0 && (
            <div className="mt-6 pt-4 border-t border-white/5">
              <h4 className="text-sm font-medium text-slate-400 mb-3">By treatment</h4>
              {Object.entries(appointmentStats.by_treatment).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([t, c]) => (
                <div key={t} className="flex justify-between text-sm py-1">
                  <span className="text-slate-400">{t}</span>
                  <span className="font-medium text-white tabular-nums">{c}</span>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

/* ---------- Sub-components ---------- */

const borderColors: Record<string, string> = {
  cyan: "from-cyan-500 to-cyan-400",
  emerald: "from-emerald-500 to-emerald-400",
  violet: "from-violet-500 to-violet-400",
  amber: "from-amber-500 to-amber-400",
};

const glowShadows: Record<string, string> = {
  cyan: "shadow-cyan-500/20",
  emerald: "shadow-emerald-500/20",
  violet: "shadow-violet-500/20",
  amber: "shadow-amber-500/20",
};

function MetricCard({ icon, label, value, sub, color, trend }: {
  icon: React.ReactNode; label: string; value: string; sub?: string; color: "cyan" | "emerald" | "violet" | "amber"; trend?: "up" | "down";
}) {
  const cm: Record<string, string> = {
    cyan: "bg-cyan-500/10 text-cyan-400",
    emerald: "bg-emerald-500/10 text-emerald-400",
    violet: "bg-violet-500/10 text-violet-400",
    amber: "bg-amber-500/10 text-amber-400",
  };
  return (
    <div className="relative bg-[#0F172A] rounded-xl p-4 border border-white/5 hover:border-white/10 hover:bg-white/[0.02] transition-all duration-300 overflow-hidden group/card">
      {/* Gradient left border */}
      <div className={`absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b ${borderColors[color]} opacity-40 group-hover/card:opacity-100 transition-opacity duration-300`} />
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg ${cm[color]} shadow-sm ${glowShadows[color]}`}>{icon}</div>
        <span className="text-sm text-slate-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white tabular-nums">{value}</div>
      {sub && (
        <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
          {trend === "up" && <span className="text-emerald-400">↑</span>}
          {trend === "down" && <span className="text-emerald-400">↓</span>}
          {sub}
        </div>
      )}
    </div>
  );
}

function FunnelRow({ label, value, total, color }: {
  label: string; value: number; total: number; color: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <div ref={ref}>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-400">{label}</span>
        <span className="font-medium text-white tabular-nums">{fmt(value)} ({pct}%)</span>
      </div>
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${color} rounded-full`}
          initial={{ width: 0 }}
          animate={isInView ? { width: `${pct}%` } : { width: 0 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
        />
      </div>
    </div>
  );
}

function QA({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="group/qa flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 cursor-pointer transition-colors">
      <div className="text-slate-500 group-hover/qa:text-emerald-400 transition-colors">{icon}</div>
      <span className="text-sm text-slate-300">{label}</span>
      <ArrowRight className="w-3.5 h-3.5 text-slate-600 ml-auto group-hover/qa:text-slate-400 group-hover/qa:translate-x-1 transition-all" />
    </div>
  );
}

function statusBarColor(status: string): string {
  const m: Record<string, string> = {
    CONFIRMED: "bg-cyan-400",
    REMINDED: "bg-amber-400",
    ATTENDED: "bg-emerald-400",
    NO_SHOW: "bg-red-400",
    CANCELLED: "bg-slate-500",
  };
  return m[status] || "bg-cyan-400";
}

function StatusBadge({ status }: { status: string }) {
  const c: Record<string, { icon: React.ReactNode; cls: string }> = {
    CONFIRMED: { icon: <Clock className="w-3 h-3" />, cls: "bg-cyan-500/10 text-cyan-400" },
    REMINDED: { icon: <Clock className="w-3 h-3" />, cls: "bg-amber-500/10 text-amber-400" },
    ATTENDED: { icon: <CheckCircle2 className="w-3 h-3" />, cls: "bg-emerald-500/10 text-emerald-400" },
    NO_SHOW: { icon: <XCircle className="w-3 h-3" />, cls: "bg-red-500/10 text-red-400" },
    CANCELLED: { icon: <XCircle className="w-3 h-3" />, cls: "bg-slate-500/10 text-slate-400" },
  };
  const cfg = c[status] || c.CONFIRMED;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
      {cfg.icon} {status}
    </span>
  );
}

function fmt(n: number): string {
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}
