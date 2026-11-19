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
  AlertTriangle,
  Circle,
} from "lucide-react";
import {
  getMe,
  getCampaignOverview,
  getTodayAppointments,
  getAppointmentStats,
  getIntegrationStatus,
  launchCampaigns,
  getAIIntelligence,
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
  total_revenue: number;
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
  const [integrations, setIntegrations] = useState<Record<string, { status: string }> | null>(null);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const greeting = useMemo(() => getGreeting(), []);
  const dateStr = useMemo(() => getDateString(), []);

  useEffect(() => {
    loadDashboard();
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => loadDashboard(), 300000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboard() {
    try {
      const [profile, campaigns, stats, today, intRes, aiRes] = await Promise.allSettled([
        getMe(),
        getCampaignOverview(),
        getAppointmentStats(30),
        getTodayAppointments(),
        getIntegrationStatus(),
        getAIIntelligence(),
      ]);
      if (profile.status === "fulfilled") setDoctor(profile.value);
      if (campaigns.status === "fulfilled") setCampaignOverview(campaigns.value);
      if (stats.status === "fulfilled") setAppointmentStats(stats.value);
      if (today.status === "fulfilled") setTodayAppts(today.value.appointments || []);
      if (intRes.status === "fulfilled") setIntegrations(intRes.value);
      if (aiRes.status === "fulfilled") setAiInsights(aiRes.value);
      setLastUpdated(new Date());
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
      <div className="space-y-6 animate-pulse">
        {/* Greeting skeleton */}
        <div className="flex items-end justify-between">
          <div>
            <div className="h-7 w-56 bg-slate-200 rounded" />
            <div className="h-4 w-40 bg-slate-100 rounded mt-2" />
          </div>
          <div className="h-3 w-24 bg-slate-100 rounded" />
        </div>
        {/* KPI skeletons */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-4 border border-slate-200">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-slate-100 rounded-lg" />
                <div className="h-3 w-20 bg-slate-100 rounded" />
              </div>
              <div className="h-7 w-16 bg-slate-200 rounded" />
              <div className="h-3 w-28 bg-slate-100 rounded mt-2" />
            </div>
          ))}
        </div>
        {/* Chart skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-5 border border-slate-200 h-48" />
          <div className="bg-white rounded-xl p-5 border border-slate-200 h-48" />
        </div>
        {/* Table skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200 h-56" />
          <div className="bg-white rounded-xl p-5 border border-slate-200 h-56" />
        </div>
      </div>
    );
  }

  const hasCampaigns = (campaignOverview?.total_campaigns || 0) > 0;

  return (
    <div className="space-y-6">
      {/* Greeting + Last Updated */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-end justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {greeting}, {doctor?.full_name?.split(" ")[0] || "Doctor"}
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">{dateStr}</p>
        </div>
        <p className="text-xs text-slate-400">
          Updated {lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
        </p>
      </motion.div>

      {/* Welcome Checklist — shows until setup is complete */}
      <WelcomeChecklist
        hasCampaigns={hasCampaigns}
        integrations={integrations}
        onLaunch={handleLaunch}
        launching={launching}
      />

      {/* Conversion Tracking Warning */}
      {hasCampaigns && (campaignOverview?.total_conversions || 0) === 0 && (campaignOverview?.total_spend || 0) > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 rounded-xl border border-amber-200 bg-amber-50"
        >
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800">No conversions tracked yet</p>
            <p className="text-xs text-amber-600 mt-0.5">
              You{"'"}re spending on ads but no patient enquiries are being tracked.{" "}
              <Link href="/dashboard/settings" className="underline font-medium">Set up conversion tracking in Settings</Link> to see your real ROI.
            </p>
          </div>
        </motion.div>
      )}

      {/* KPI Cards — Doctor-friendly labels */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
        {[
          { icon: <Eye className="w-5 h-5" />, label: "People Reached", value: fmt(campaignOverview?.total_impressions || 0), color: "cyan" as const, sub: `${(campaignOverview?.avg_ctr ?? 0).toFixed(1)}% clicked`, trend: undefined },
          { icon: <MousePointerClick className="w-5 h-5" />, label: "Website Visitors", value: fmt(campaignOverview?.total_clicks || 0), color: "emerald" as const, sub: `₹${(campaignOverview?.avg_cpc ?? 0).toFixed(1)} per visitor`, trend: undefined },
          { icon: <MessageCircle className="w-5 h-5" />, label: "Enquiries", value: fmt(campaignOverview?.total_conversions || 0), color: "violet" as const, sub: (campaignOverview?.total_conversions || 0) > 0 ? `${Math.round(((campaignOverview?.total_conversions || 0) / Math.max(campaignOverview?.total_clicks || 1, 1)) * 100)}% of visitors` : undefined, trend: undefined },
          { icon: <Calendar className="w-5 h-5" />, label: "Appointments", value: fmt(appointmentStats?.total_booked || 0), color: "amber" as const, sub: (appointmentStats?.total_booked || 0) > 0 ? `${appointmentStats?.attendance_rate || 0}% attended` : "Set up booking tracking", trend: undefined },
          (() => {
            const spend = campaignOverview?.total_spend || 0;
            const enquiries = campaignOverview?.total_conversions || 0;
            const booked = appointmentStats?.total_booked || 0;
            if (booked > 0) {
              return {
                icon: <IndianRupee className="w-5 h-5" />,
                label: "Cost per Patient",
                value: `₹${fmt(Math.round(spend / booked))}`,
                color: "emerald" as const,
                sub: `${booked} patients from ₹${fmt(spend)} spend`,
                trend: undefined,
              };
            }
            if (enquiries > 0) {
              return {
                icon: <IndianRupee className="w-5 h-5" />,
                label: "Cost per Enquiry",
                value: `₹${fmt(Math.round(spend / enquiries))}`,
                color: "emerald" as const,
                sub: "Track bookings for cost per patient",
                trend: undefined,
              };
            }
            return {
              icon: <IndianRupee className="w-5 h-5" />,
              label: "Cost per Enquiry",
              value: "—",
              color: "emerald" as const,
              sub: spend > 0 ? `₹${fmt(spend)} spent` : undefined,
              trend: undefined,
            };
          })(),
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
          className="bg-white rounded-xl p-5 border border-slate-200 hover:border-slate-200 transition-colors duration-300"
        >
          <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
            <IndianRupee className="w-5 h-5 text-emerald-600" /> Ad spend (30 days)
          </h3>
          <div className="flex items-baseline gap-3">
            <div className="text-3xl font-bold text-slate-900 tabular-nums">₹{fmt(campaignOverview?.total_spend || 0)}</div>
            {(appointmentStats?.total_revenue || 0) > 0 && (
              <div className="text-sm font-medium text-emerald-600">
                Revenue: ₹{fmt(appointmentStats?.total_revenue || 0)}
              </div>
            )}
          </div>
          <div className="mt-2 text-sm text-slate-600">
            {(appointmentStats?.total_revenue || 0) > 0 && (campaignOverview?.total_spend || 0) > 0
              ? `${((appointmentStats!.total_revenue / (campaignOverview?.total_spend || 1)) * 100).toFixed(0)}% ROI · ₹${fmt(Math.round((campaignOverview?.total_spend || 0) / Math.max(appointmentStats?.attended || 1, 1)))} per patient`
              : appointmentStats?.attended
                ? `Cost per patient: ₹${fmt(Math.round((campaignOverview?.total_spend || 0) / appointmentStats.attended))}`
                : (campaignOverview?.total_conversions || 0) > 0
                  ? `Cost per enquiry: ₹${fmt(Math.round((campaignOverview?.total_spend || 0) / (campaignOverview?.total_conversions || 1)))}`
                  : "No conversion data yet"}
          </div>
          <div className="mt-4">
            <Link href="/dashboard/campaigns"
              className="group/link inline-flex items-center gap-1.5 text-sm text-emerald-600 hover:text-emerald-700 transition-colors">
              View campaigns <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.55 }}
          className="bg-white rounded-xl p-5 border border-slate-200 hover:border-slate-200 transition-colors duration-300"
        >
          <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-cyan-600" /> Patient funnel (30 days)
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
            {(appointmentStats?.total_revenue || 0) > 0 && (
              <div className="flex justify-between text-sm mt-2 pt-2 border-t border-slate-100">
                <span className="text-slate-500 font-medium">Revenue earned</span>
                <span className="font-bold text-emerald-600 tabular-nums">₹{fmt(appointmentStats?.total_revenue || 0)}</span>
              </div>
            )}
          </div>
          {/* Booking tracking warning */}
          {(campaignOverview?.total_conversions || 0) > 0 && (appointmentStats?.total_booked || 0) === 0 && (
            <div className="mt-3 flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
              <p className="text-xs text-amber-700">
                Booking tracking not connected yet.{" "}
                <Link href="/dashboard/settings" className="underline font-medium">Connect</Link> to see the full patient funnel.
              </p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Integration Status Bar */}
      {integrations && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.48 }}
          className="flex flex-wrap gap-2"
        >
          {[
            { key: "google_ads", label: "Google Ads", icon: "📊" },
            { key: "google_calendar", label: "Calendar", icon: "📅" },
            { key: "whatsapp", label: "WhatsApp", icon: "💬" },
            { key: "twilio", label: "Calls", icon: "📞" },
            { key: "meta_ads", label: "Meta Ads", icon: "📱" },
          ].map((item) => {
            const status = integrations?.[item.key]?.status;
            const isConnected = status === "connected";
            return (
              <Link key={item.key} href="/dashboard/settings"
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  isConnected
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                    : "bg-slate-50 text-slate-500 border-slate-200 hover:border-slate-300"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-emerald-500" : "bg-slate-300"}`} />
              </Link>
            );
          })}
        </motion.div>
      )}

      {/* AI Insights */}
      {aiInsights && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.58 }}
          className="bg-white rounded-xl p-5 border border-slate-200"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-violet-500" /> AI Insights
            </h3>
            {aiInsights.account_health && (
              <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${
                aiInsights.account_health.grade === "A" ? "bg-emerald-50 text-emerald-700" :
                aiInsights.account_health.grade === "B" ? "bg-cyan-50 text-cyan-700" :
                aiInsights.account_health.grade === "C" ? "bg-amber-50 text-amber-700" :
                aiInsights.account_health.grade === "D" ? "bg-orange-50 text-orange-700" :
                "bg-red-50 text-red-700"
              }`}>
                Health: {aiInsights.account_health.grade} ({aiInsights.account_health.score}/100)
              </span>
            )}
          </div>

          {/* Top actions */}
          {aiInsights.next_actions && aiInsights.next_actions.length > 0 && (
            <div className="space-y-2">
              {aiInsights.next_actions.slice(0, 3).map((action: any, i: number) => (
                <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-50">
                  <span className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    action.severity === "CRITICAL" ? "bg-red-100 text-red-700" :
                    action.severity === "HIGH" ? "bg-amber-100 text-amber-700" :
                    "bg-slate-200 text-slate-600"
                  }`}>{i + 1}</span>
                  <p className="text-sm text-slate-700">{action.action}</p>
                </div>
              ))}
            </div>
          )}

          {/* Wins */}
          {aiInsights.account_health?.wins?.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {aiInsights.account_health.wins.map((win: string, i: number) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-emerald-50 text-emerald-700">
                  <CheckCircle2 className="w-3 h-3" /> {win}
                </span>
              ))}
            </div>
          )}

          <div className="mt-4">
            <Link href="/dashboard/campaigns"
              className="group/link inline-flex items-center gap-1.5 text-sm text-violet-600 hover:text-violet-700 transition-colors">
              View full analysis <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>
      )}

      {/* Today + Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200 hover:border-slate-200 transition-colors duration-300"
        >
          <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-cyan-600" /> Today{"'"}s appointments
          </h3>
          {todayAppts.length === 0 ? (
            <div className="text-center py-6">
              <Calendar className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-slate-500 text-sm mb-3">No appointments today</p>
              <Link href="/dashboard/appointments" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 rounded-lg hover:bg-emerald-100 transition">
                <Calendar className="w-3.5 h-3.5" /> Log a walk-in or book an appointment
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {todayAppts.map((a) => (
                <div key={a.id} className="flex items-center justify-between py-3 group/row">
                  <div className="flex items-center gap-3">
                    <div className={`w-0.5 h-8 rounded-full ${statusBarColor(a.status)}`} />
                    <div>
                      <div className="font-medium text-sm text-slate-800">{a.patient_name}</div>
                      <div className="text-xs text-slate-600">{a.treatment}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-500 tabular-nums">{a.time}</span>
                    <StatusBadge status={a.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="mt-3">
            <Link href="/dashboard/appointments"
              className="group/link inline-flex items-center gap-1.5 text-sm text-emerald-600 hover:text-emerald-700 transition-colors">
              View all <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.65 }}
          className="bg-white rounded-xl p-5 border border-slate-200 hover:border-slate-200 transition-colors duration-300"
        >
          <h3 className="font-semibold text-slate-900 mb-4">Quick actions</h3>
          <div className="space-y-1">
            <Link href="/dashboard/campaigns" className="block"><QA icon={<BarChart3 className="w-4 h-4" />} label="Manage campaigns" /></Link>
            <Link href="/dashboard/conversations" className="block"><QA icon={<MessageCircle className="w-4 h-4" />} label="WhatsApp chats" /></Link>
            <Link href="/dashboard/appointments" className="block"><QA icon={<Calendar className="w-4 h-4" />} label="Appointments" /></Link>
            <Link href="/dashboard/landing-pages" className="block"><QA icon={<Globe className="w-4 h-4" />} label="Landing pages" /></Link>
          </div>

          {appointmentStats && Object.keys(appointmentStats.by_treatment || {}).length > 0 && (
            <div className="mt-6 pt-4 border-t border-slate-200">
              <h4 className="text-sm font-medium text-slate-500 mb-3">By treatment</h4>
              {Object.entries(appointmentStats.by_treatment).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([t, c]) => (
                <div key={t} className="flex justify-between text-sm py-1">
                  <span className="text-slate-500">{t}</span>
                  <span className="font-medium text-slate-900 tabular-nums">{c}</span>
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
    cyan: "bg-cyan-50 text-cyan-600",
    emerald: "bg-emerald-50 text-emerald-600",
    violet: "bg-violet-50 text-violet-600",
    amber: "bg-amber-50 text-amber-600",
  };
  return (
    <div className="relative bg-white rounded-xl p-4 border border-slate-200 hover:border-slate-200 hover:bg-slate-50 transition-all duration-300 overflow-hidden group/card">
      {/* Gradient left border */}
      <div className={`absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b ${borderColors[color]} opacity-40 group-hover/card:opacity-100 transition-opacity duration-300`} />
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg ${cm[color]} shadow-sm ${glowShadows[color]}`}>{icon}</div>
        <span className="text-sm text-slate-600">{label}</span>
      </div>
      <div className="text-2xl font-bold text-slate-900 tabular-nums">{value}</div>
      {sub && (
        <div className="text-xs text-slate-600 mt-1 flex items-center gap-1">
          {trend === "up" && <span className="text-emerald-600">↑</span>}
          {trend === "down" && <span className="text-emerald-600">↓</span>}
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
        <span className="text-slate-500">{label}</span>
        <span className="font-medium text-slate-900 tabular-nums">{fmt(value)} ({pct}%)</span>
      </div>
      <div className="h-1.5 bg-slate-50 rounded-full overflow-hidden">
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
    <div className="group/qa flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-100 cursor-pointer transition-colors">
      <div className="text-slate-600 group-hover/qa:text-emerald-600 transition-colors">{icon}</div>
      <span className="text-sm text-slate-700">{label}</span>
      <ArrowRight className="w-3.5 h-3.5 text-slate-600 ml-auto group-hover/qa:text-slate-500 group-hover/qa:translate-x-1 transition-all" />
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
    CONFIRMED: { icon: <Clock className="w-3 h-3" />, cls: "bg-cyan-50 text-cyan-600" },
    REMINDED: { icon: <Clock className="w-3 h-3" />, cls: "bg-amber-50 text-amber-600" },
    ATTENDED: { icon: <CheckCircle2 className="w-3 h-3" />, cls: "bg-emerald-50 text-emerald-600" },
    NO_SHOW: { icon: <XCircle className="w-3 h-3" />, cls: "bg-red-50 text-red-600" },
    CANCELLED: { icon: <XCircle className="w-3 h-3" />, cls: "bg-slate-500/10 text-slate-500" },
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

/* ---------- Welcome Checklist ---------- */

function WelcomeChecklist({
  hasCampaigns,
  integrations,
  onLaunch,
  launching,
}: {
  hasCampaigns: boolean;
  integrations: Record<string, { status: string }> | null;
  onLaunch: () => void;
  launching: boolean;
}) {
  const googleAdsOk = integrations?.google_ads?.status === "connected";
  const calendarOk = integrations?.google_calendar?.status === "connected";
  const whatsappOk = integrations?.whatsapp?.status === "connected";

  const steps = [
    { label: "Create your account", done: true, href: undefined as string | undefined },
    { label: "Connect Google Ads", done: googleAdsOk, href: "/dashboard/settings" },
    { label: "Connect Google Calendar", done: calendarOk, href: "/dashboard/settings" },
    { label: "Set up WhatsApp", done: whatsappOk, href: "/dashboard/settings" },
    { label: "Launch your first campaign", done: hasCampaigns, href: "/dashboard/campaigns" },
  ];

  const completed = steps.filter((s) => s.done).length;
  const allDone = completed === steps.length;

  // Hide checklist once everything is set up
  if (allDone) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="relative rounded-xl border border-emerald-200 bg-gradient-to-r from-emerald-500/[0.08] to-cyan-500/[0.04] p-6 overflow-hidden"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(16,185,129,0.08),transparent_60%)]" />
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-600" /> Get started with PatientPlex
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              {completed} of {steps.length} steps completed
            </p>
          </div>
          {/* Progress circle */}
          <div className="relative w-12 h-12">
            <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="#e2e8f0" strokeWidth="3" />
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="#10b981" strokeWidth="3"
                strokeDasharray={`${(completed / steps.length) * 100}, 100`} strokeLinecap="round" />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-slate-700">
              {Math.round((completed / steps.length) * 100)}%
            </span>
          </div>
        </div>

        <div className="space-y-2">
          {steps.map((step) => (
            <div key={step.label} className="flex items-center gap-3">
              {step.done ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-slate-300 flex-shrink-0" />
              )}
              {step.href && !step.done ? (
                <Link href={step.href} className="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
                  {step.label} <ArrowRight className="w-3 h-3 inline ml-0.5" />
                </Link>
              ) : (
                <span className={`text-sm ${step.done ? "text-slate-400 line-through" : "text-slate-700"}`}>
                  {step.label}
                </span>
              )}
            </div>
          ))}
        </div>

        {!hasCampaigns && googleAdsOk && (
          <div className="mt-4 pt-4 border-t border-emerald-200/50">
            <button
              onClick={onLaunch}
              disabled={launching}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-all whitespace-nowrap disabled:opacity-50"
            >
              {launching ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Launch Campaigns <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
