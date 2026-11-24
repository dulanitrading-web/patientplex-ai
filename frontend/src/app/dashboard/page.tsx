"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
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
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  Zap,
  Activity,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  Circle,
  Users,
  TrendingUp,
  Phone,
  Star,
  RefreshCw,
  ChevronDown,
  Sparkles,
  Target,
  Megaphone,
  UserPlus,
  PhoneCall,
  Stethoscope,
  Bell,
} from "lucide-react";
import {
  getMe,
  getCampaignOverview,
  getTodayAppointments,
  getAppointmentStats,
  getIntegrationStatus,
  launchCampaigns,
  getAIIntelligence,
  getDashboardSummary,
  getLeadStats,
  getMetricTrend,
  getPatientStats,
  initializeClinicData,
  getSeedStatus,
} from "@/lib/api";

/* ================================================================
   Types
   ================================================================ */

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

interface LeadStatsData {
  total_leads: number;
  previous_period_leads: number;
  change_pct: number | null;
  by_source: Record<string, number>;
  daily_trend: { date: string; count: number }[];
}

type Period = "today" | "7d" | "14d" | "30d" | "90d";

const PERIOD_LABELS: Record<Period, string> = {
  today: "Today",
  "7d": "7 days",
  "14d": "14 days",
  "30d": "30 days",
  "90d": "90 days",
};

/* ================================================================
   Helpers
   ================================================================ */

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

function fmt(n: number): string {
  if (n >= 10000000) return (n / 10000000).toFixed(1) + "Cr";
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toLocaleString("en-IN");
}

function fmtCurrency(n: number): string {
  if (n >= 10000000) return "₹" + (n / 10000000).toFixed(1) + "Cr";
  if (n >= 100000) return "₹" + (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return "₹" + (n / 1000).toFixed(1) + "K";
  return "₹" + n.toLocaleString("en-IN");
}

/* ================================================================
   Main Component
   ================================================================ */

export default function DashboardPage() {
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [campaignOverview, setCampaignOverview] = useState<CampaignOverview | null>(null);
  const [appointmentStats, setAppointmentStats] = useState<AppointmentStats | null>(null);
  const [todayAppts, setTodayAppts] = useState<TodayAppointment[]>([]);
  const [integrations, setIntegrations] = useState<Record<string, { status: string }> | null>(null);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [leadStats, setLeadStats] = useState<LeadStatsData | null>(null);
  const [patientStats, setPatientStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [period, setPeriod] = useState<Period>("30d");
  const [showPeriodMenu, setShowPeriodMenu] = useState(false);

  const greeting = useMemo(() => getGreeting(), []);
  const dateStr = useMemo(() => getDateString(), []);

  const loadDashboard = useCallback(async (selectedPeriod?: Period) => {
    const p = selectedPeriod || period;
    try {
      const results = await Promise.allSettled([
        getMe(),
        getCampaignOverview(),
        getAppointmentStats(p === "today" ? 1 : p === "7d" ? 7 : p === "14d" ? 14 : p === "90d" ? 90 : 30),
        getTodayAppointments(),
        getIntegrationStatus(),
        getAIIntelligence(),
        getLeadStats(p).catch(() => null),
        getPatientStats().catch(() => null),
      ]);
      if (results[0].status === "fulfilled") setDoctor(results[0].value);
      if (results[1].status === "fulfilled") setCampaignOverview(results[1].value);
      if (results[2].status === "fulfilled") setAppointmentStats(results[2].value);
      if (results[3].status === "fulfilled") setTodayAppts(results[3].value.appointments || []);
      if (results[4].status === "fulfilled") setIntegrations(results[4].value);
      if (results[5].status === "fulfilled") setAiInsights(results[5].value);
      if (results[6].status === "fulfilled" && results[6].value) setLeadStats(results[6].value);
      if (results[7].status === "fulfilled" && results[7].value) setPatientStats(results[7].value);
      setLastUpdated(new Date());
    } catch {
      /* use defaults */
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [period]);

  // Auto-initialize clinic data if dashboard is empty
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    async function init() {
      // First load dashboard
      await loadDashboard();

      // Check if data exists, if not auto-seed
      if (!initialized) {
        try {
          const status = await getSeedStatus().catch(() => null);
          if (status && !status.initialized) {
            await initializeClinicData().catch(() => null);
            // Reload with fresh data
            await loadDashboard();
          }
          setInitialized(true);
        } catch {
          setInitialized(true);
        }
      }
    }
    init();
    // Auto-refresh every 5 minutes — data syncs automatically
    const interval = setInterval(() => loadDashboard(), 300000);
    return () => clearInterval(interval);
  }, [loadDashboard]);

  function handlePeriodChange(p: Period) {
    setPeriod(p);
    setShowPeriodMenu(false);
    setRefreshing(true);
    loadDashboard(p);
  }

  function handleRefresh() {
    setRefreshing(true);
    loadDashboard();
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

  /* ── Loading skeleton ── */
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="flex items-end justify-between">
          <div>
            <div className="h-8 w-64 bg-slate-200 rounded-lg" />
            <div className="h-4 w-44 bg-slate-100 rounded mt-2" />
          </div>
          <div className="h-9 w-28 bg-slate-100 rounded-lg" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-4 border border-slate-100 h-28" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-100 h-56" />
          <div className="bg-white rounded-2xl p-5 border border-slate-100 h-56" />
        </div>
      </div>
    );
  }

  const hasCampaigns = (campaignOverview?.total_campaigns || 0) > 0;
  const totalLeads = leadStats?.total_leads || campaignOverview?.total_conversions || 0;
  const totalSpend = campaignOverview?.total_spend || 0;
  const totalClicks = campaignOverview?.total_clicks || 0;
  const totalImpressions = campaignOverview?.total_impressions || 0;
  const totalBooked = appointmentStats?.total_booked || 0;
  const totalAttended = appointmentStats?.attended || 0;
  const totalRevenue = appointmentStats?.total_revenue || 0;

  return (
    <div className="space-y-5">
      {/* ── Header: Greeting + Period Selector + Refresh ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row sm:items-end justify-between gap-3"
      >
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            {greeting}, {doctor?.full_name?.split(" ")[0] || "Doctor"} 👋
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">{dateStr}</p>
          {doctor?.clinic_name && (
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
              <Stethoscope className="w-3 h-3" /> {doctor.clinic_name}
              {doctor.city ? ` · ${doctor.city}` : ""}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Period selector */}
          <div className="relative">
            <button
              onClick={() => setShowPeriodMenu(!showPeriodMenu)}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-sm font-medium text-slate-700 hover:border-slate-300 transition-colors shadow-sm"
            >
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {PERIOD_LABELS[period]}
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>
            {showPeriodMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowPeriodMenu(false)} />
                <div className="absolute right-0 top-full mt-1 z-20 bg-white rounded-xl border border-slate-200 shadow-lg py-1 min-w-[140px]">
                  {(Object.keys(PERIOD_LABELS) as Period[]).map((p) => (
                    <button
                      key={p}
                      onClick={() => handlePeriodChange(p)}
                      className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                        p === period
                          ? "bg-emerald-50 text-emerald-700 font-medium"
                          : "text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      {PERIOD_LABELS[p]}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-sm text-slate-600 hover:border-slate-300 transition-colors shadow-sm disabled:opacity-50"
            title="Data auto-syncs every 5 minutes"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
          </button>

          {/* Last updated */}
          <span className="text-[11px] text-slate-400 hidden sm:inline">
            Updated {lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>
      </motion.div>

      {/* ── Auto-sync indicator ── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50/60 border border-emerald-100 w-fit"
      >
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        <span className="text-xs text-emerald-700 font-medium">
          Data auto-syncs · Google Ads every 4hrs · Leads in real-time
        </span>
      </motion.div>

      {/* ── Welcome Checklist — shows until setup is complete ── */}
      <WelcomeChecklist
        hasCampaigns={hasCampaigns}
        integrations={integrations}
        onLaunch={handleLaunch}
        launching={launching}
      />

      {/* ── KPI Cards — 6 columns ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          {
            icon: <Eye className="w-4 h-4" />,
            label: "People Reached",
            value: totalImpressions > 0 ? fmt(totalImpressions) : "—",
            change: leadStats?.change_pct,
            color: "sky" as const,
            sub: totalImpressions > 0 ? `${((campaignOverview?.avg_ctr ?? 0) * 100).toFixed(1)}% CTR` : "Launch ads to start",
            sparkData: leadStats?.daily_trend?.map(d => d.count),
          },
          {
            icon: <MousePointerClick className="w-4 h-4" />,
            label: "Website Visitors",
            value: totalClicks > 0 ? fmt(totalClicks) : "—",
            color: "blue" as const,
            sub: totalClicks > 0 ? `${fmtCurrency(campaignOverview?.avg_cpc ?? 0)} per click` : "No clicks yet",
          },
          {
            icon: <UserPlus className="w-4 h-4" />,
            label: "New Leads",
            value: totalLeads > 0 ? fmt(totalLeads) : "—",
            change: leadStats?.change_pct,
            color: "violet" as const,
            sub: totalLeads > 0
              ? `${Math.round((totalLeads / Math.max(totalClicks, 1)) * 100)}% conversion`
              : "Leads auto-tracked",
            sparkData: leadStats?.daily_trend?.map(d => d.count),
          },
          {
            icon: <Calendar className="w-4 h-4" />,
            label: "Appointments",
            value: totalBooked > 0 ? fmt(totalBooked) : "—",
            color: "amber" as const,
            sub: totalBooked > 0
              ? `${appointmentStats?.attendance_rate || 0}% attended`
              : "No bookings yet",
          },
          {
            icon: <IndianRupee className="w-4 h-4" />,
            label: "Revenue",
            value: totalRevenue > 0 ? fmtCurrency(totalRevenue) : "—",
            color: "emerald" as const,
            sub: totalRevenue > 0 && totalSpend > 0
              ? `${((totalRevenue / totalSpend) * 100).toFixed(0)}% ROI`
              : totalSpend > 0
                ? `${fmtCurrency(totalSpend)} spent`
                : "Track revenue",
          },
          {
            icon: <Target className="w-4 h-4" />,
            label: "Cost per Patient",
            value: totalAttended > 0
              ? fmtCurrency(Math.round(totalSpend / totalAttended))
              : totalLeads > 0
                ? fmtCurrency(Math.round(totalSpend / totalLeads))
                : "—",
            color: "rose" as const,
            sub: totalAttended > 0
              ? `${totalAttended} patients acquired`
              : totalLeads > 0
                ? `per lead · ${totalLeads} leads`
                : "Needs data",
          },
        ].map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.1 + i * 0.05 }}
          >
            <KPICard {...m} />
          </motion.div>
        ))}
      </div>

      {/* ── Row 2: Funnel + Recent Leads ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Patient Funnel — wider */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          className="lg:col-span-3 bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"
        >
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600" /> Patient Funnel
            </h3>
            <span className="text-xs text-slate-400 font-medium">{PERIOD_LABELS[period]}</span>
          </div>

          <div className="space-y-3">
            <FunnelRow label="Impressions" value={totalImpressions} total={totalImpressions || 1} color="bg-sky-500" icon={<Eye className="w-3.5 h-3.5" />} />
            <FunnelRow label="Clicks" value={totalClicks} total={totalImpressions || 1} color="bg-blue-500" icon={<MousePointerClick className="w-3.5 h-3.5" />} />
            <FunnelRow label="Leads / Enquiries" value={totalLeads} total={totalImpressions || 1} color="bg-violet-500" icon={<UserPlus className="w-3.5 h-3.5" />} />
            <FunnelRow label="Booked" value={totalBooked} total={totalImpressions || 1} color="bg-amber-500" icon={<Calendar className="w-3.5 h-3.5" />} />
            <FunnelRow label="Attended" value={totalAttended} total={totalImpressions || 1} color="bg-emerald-500" icon={<CheckCircle2 className="w-3.5 h-3.5" />} />
          </div>

          {/* Funnel drop-off indicators */}
          {totalClicks > 0 && totalLeads > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-3">
              <span className="text-xs text-slate-500">
                Click→Lead: <strong className="text-slate-700">{((totalLeads / totalClicks) * 100).toFixed(1)}%</strong>
              </span>
              {totalBooked > 0 && (
                <span className="text-xs text-slate-500">
                  Lead→Book: <strong className="text-slate-700">{((totalBooked / totalLeads) * 100).toFixed(1)}%</strong>
                </span>
              )}
              {totalAttended > 0 && totalBooked > 0 && (
                <span className="text-xs text-slate-500">
                  Book→Attend: <strong className="text-slate-700">{((totalAttended / totalBooked) * 100).toFixed(1)}%</strong>
                </span>
              )}
            </div>
          )}

          {/* Empty state */}
          {totalImpressions === 0 && totalLeads === 0 && (
            <div className="mt-4 text-center py-4">
              <Megaphone className="w-8 h-8 text-slate-200 mx-auto mb-2" />
              <p className="text-sm text-slate-400">Launch your first campaign to see the funnel</p>
            </div>
          )}
        </motion.div>

        {/* Spend & ROI Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.45 }}
          className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"
        >
          <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
            <IndianRupee className="w-4 h-4 text-emerald-600" /> Ad Spend & ROI
          </h3>

          {totalSpend > 0 ? (
            <div>
              <div className="text-3xl font-bold text-slate-900 tabular-nums">{fmtCurrency(totalSpend)}</div>
              <p className="text-sm text-slate-500 mt-1">spent in {PERIOD_LABELS[period].toLowerCase()}</p>

              <div className="mt-5 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Revenue earned</span>
                  <span className="font-semibold text-emerald-600 tabular-nums">{fmtCurrency(totalRevenue)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">ROI</span>
                  <span className={`font-semibold tabular-nums ${totalRevenue > totalSpend ? "text-emerald-600" : "text-amber-600"}`}>
                    {totalSpend > 0 ? `${(((totalRevenue - totalSpend) / totalSpend) * 100).toFixed(0)}%` : "—"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Cost per click</span>
                  <span className="font-medium text-slate-700 tabular-nums">{fmtCurrency(campaignOverview?.avg_cpc ?? 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Cost per lead</span>
                  <span className="font-medium text-slate-700 tabular-nums">
                    {totalLeads > 0 ? fmtCurrency(Math.round(totalSpend / totalLeads)) : "—"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Cost per patient</span>
                  <span className="font-medium text-slate-700 tabular-nums">
                    {totalAttended > 0 ? fmtCurrency(Math.round(totalSpend / totalAttended)) : "—"}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <Link href="/dashboard/campaigns"
                  className="group/link inline-flex items-center gap-1.5 text-sm text-emerald-600 hover:text-emerald-700 font-medium transition-colors">
                  View campaigns <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="w-10 h-10 text-slate-200 mx-auto mb-3" />
              <p className="text-sm text-slate-400 mb-1">No ad spend yet</p>
              <p className="text-xs text-slate-400">Launch campaigns to track ROI automatically</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* ── Integration Status ── */}
      {integrations && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.5 }}
          className="flex flex-wrap gap-2"
        >
          {[
            { key: "google_ads", label: "Google Ads", icon: <Megaphone className="w-3 h-3" /> },
            { key: "google_calendar", label: "Calendar", icon: <Calendar className="w-3 h-3" /> },
            { key: "whatsapp", label: "WhatsApp", icon: <MessageCircle className="w-3 h-3" /> },
            { key: "exotel", label: "Calls", icon: <PhoneCall className="w-3 h-3" /> },
            { key: "meta_ads", label: "Meta Ads", icon: <Globe className="w-3 h-3" /> },
          ].map((item) => {
            const status = integrations?.[item.key]?.status;
            const isConnected = status === "connected";
            return (
              <Link key={item.key} href="/dashboard/settings"
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                  isConnected
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm shadow-emerald-100"
                    : "bg-slate-50 text-slate-500 border-slate-200 hover:border-slate-300"
                }`}
              >
                {item.icon}
                {item.label}
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-emerald-500" : "bg-slate-300"}`} />
              </Link>
            );
          })}
        </motion.div>
      )}

      {/* ── Row 3: Today's Appointments + AI Insights + Quick Actions ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Today's Appointments */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.55 }}
          className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-blue-600" /> Today
            </h3>
            {todayAppts.length > 0 && (
              <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                {todayAppts.length} appt{todayAppts.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>

          {todayAppts.length === 0 ? (
            <div className="text-center py-6">
              <Calendar className="w-8 h-8 text-slate-200 mx-auto mb-2" />
              <p className="text-sm text-slate-400 mb-3">No appointments today</p>
              <Link href="/dashboard/appointments" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition">
                <Calendar className="w-3.5 h-3.5" /> Book / Log walk-in
              </Link>
            </div>
          ) : (
            <div className="space-y-1">
              {todayAppts.slice(0, 5).map((a) => (
                <div key={a.id} className="flex items-center justify-between py-2 px-2 rounded-lg hover:bg-slate-50 transition-colors group/row">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className={`w-1 h-8 rounded-full flex-shrink-0 ${statusBarColor(a.status)}`} />
                    <div className="min-w-0">
                      <div className="font-medium text-sm text-slate-800 truncate">{a.patient_name}</div>
                      <div className="text-xs text-slate-500">{a.treatment}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs text-slate-400 tabular-nums">{a.time}</span>
                    <StatusBadge status={a.status} />
                  </div>
                </div>
              ))}
              {todayAppts.length > 5 && (
                <p className="text-xs text-slate-400 text-center pt-1">+{todayAppts.length - 5} more</p>
              )}
            </div>
          )}
          <div className="mt-3">
            <Link href="/dashboard/appointments"
              className="group/link inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors">
              All appointments <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        {/* AI Insights */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-500" /> AI Insights
            </h3>
            {aiInsights?.account_health && (
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${
                aiInsights.account_health.grade === "A" ? "bg-emerald-50 text-emerald-700" :
                aiInsights.account_health.grade === "B" ? "bg-blue-50 text-blue-700" :
                aiInsights.account_health.grade === "C" ? "bg-amber-50 text-amber-700" :
                "bg-red-50 text-red-700"
              }`}>
                {aiInsights.account_health.grade} · {aiInsights.account_health.score}/100
              </span>
            )}
          </div>

          {aiInsights?.next_actions?.length > 0 ? (
            <div className="space-y-2">
              {aiInsights.next_actions.slice(0, 3).map((action: any, i: number) => (
                <div key={i} className="flex items-start gap-2 p-2.5 rounded-xl bg-slate-50/80">
                  <span className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    action.severity === "CRITICAL" ? "bg-red-100 text-red-700" :
                    action.severity === "HIGH" ? "bg-amber-100 text-amber-700" :
                    "bg-blue-100 text-blue-600"
                  }`}>{i + 1}</span>
                  <p className="text-sm text-slate-600 leading-snug">{action.action}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6">
              <Sparkles className="w-8 h-8 text-slate-200 mx-auto mb-2" />
              <p className="text-sm text-slate-400">AI insights will appear once campaigns run</p>
            </div>
          )}

          {aiInsights?.account_health?.wins?.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {aiInsights.account_health.wins.slice(0, 3).map((win: string, i: number) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] bg-emerald-50 text-emerald-700">
                  <CheckCircle2 className="w-2.5 h-2.5" /> {win}
                </span>
              ))}
            </div>
          )}

          <div className="mt-4">
            <Link href="/dashboard/campaigns"
              className="group/link inline-flex items-center gap-1.5 text-sm text-violet-600 hover:text-violet-700 font-medium transition-colors">
              Full analysis <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        {/* Quick Actions + Treatment Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.65 }}
          className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"
        >
          <h3 className="font-semibold text-slate-900 mb-3">Quick actions</h3>
          <div className="space-y-0.5">
            <QA icon={<BarChart3 className="w-4 h-4" />} label="Manage campaigns" href="/dashboard/campaigns" />
            <QA icon={<MessageCircle className="w-4 h-4" />} label="WhatsApp chats" href="/dashboard/conversations" />
            <QA icon={<Calendar className="w-4 h-4" />} label="Appointments" href="/dashboard/appointments" />
            <QA icon={<Users className="w-4 h-4" />} label="Patient CRM" href="/dashboard/patients" />
            <QA icon={<Globe className="w-4 h-4" />} label="Landing pages" href="/dashboard/landing-pages" />
          </div>

          {/* Treatment breakdown */}
          {appointmentStats && Object.keys(appointmentStats.by_treatment || {}).length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h4 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">By Treatment</h4>
              {Object.entries(appointmentStats.by_treatment)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 4)
                .map(([t, c]) => (
                  <div key={t} className="flex justify-between text-sm py-1">
                    <span className="text-slate-500 truncate mr-2">{t}</span>
                    <span className="font-medium text-slate-700 tabular-nums">{c}</span>
                  </div>
                ))}
            </div>
          )}

          {/* Lead sources */}
          {leadStats && Object.keys(leadStats.by_source || {}).length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h4 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Lead Sources</h4>
              {Object.entries(leadStats.by_source)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 4)
                .map(([src, cnt]) => (
                  <div key={src} className="flex justify-between text-sm py-1">
                    <span className="text-slate-500 capitalize truncate mr-2">{src.replace(/_/g, " ")}</span>
                    <span className="font-medium text-slate-700 tabular-nums">{cnt}</span>
                  </div>
                ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* ── Conversion Tracking Warning ── */}
      {hasCampaigns && (campaignOverview?.total_conversions || 0) === 0 && totalSpend > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 rounded-xl border border-amber-200 bg-amber-50/80"
        >
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800">No conversions tracked yet</p>
            <p className="text-xs text-amber-600 mt-0.5">
              You{"'"}re spending on ads but no enquiries are tracked.{" "}
              <Link href="/dashboard/settings" className="underline font-medium">Set up conversion tracking</Link> to see your real ROI.
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}

/* ================================================================
   Sub-components
   ================================================================ */

const KPI_COLORS: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  sky: { bg: "bg-sky-50", text: "text-sky-600", border: "from-sky-500 to-sky-400", glow: "shadow-sky-200/50" },
  blue: { bg: "bg-blue-50", text: "text-blue-600", border: "from-blue-500 to-blue-400", glow: "shadow-blue-200/50" },
  violet: { bg: "bg-violet-50", text: "text-violet-600", border: "from-violet-500 to-violet-400", glow: "shadow-violet-200/50" },
  amber: { bg: "bg-amber-50", text: "text-amber-600", border: "from-amber-500 to-amber-400", glow: "shadow-amber-200/50" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", border: "from-emerald-500 to-emerald-400", glow: "shadow-emerald-200/50" },
  rose: { bg: "bg-rose-50", text: "text-rose-600", border: "from-rose-500 to-rose-400", glow: "shadow-rose-200/50" },
};

function KPICard({
  icon, label, value, sub, color, change, sparkData,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  color: string;
  change?: number | null;
  sparkData?: number[];
}) {
  const c = KPI_COLORS[color] || KPI_COLORS.blue;

  return (
    <div className={`relative bg-white rounded-2xl p-4 border border-slate-100 hover:shadow-md ${c.glow} transition-all duration-300 overflow-hidden group/card`}>
      {/* Gradient accent */}
      <div className={`absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b ${c.border} opacity-30 group-hover/card:opacity-100 transition-opacity duration-300`} />

      <div className="flex items-center gap-1.5 mb-2">
        <div className={`p-1 rounded-lg ${c.bg} ${c.text}`}>{icon}</div>
        <span className="text-[11px] font-medium text-slate-500 leading-tight">{label}</span>
      </div>

      <div className="flex items-baseline gap-2">
        <div className="text-xl font-bold text-slate-900 tabular-nums">{value}</div>
        {change !== null && change !== undefined && (
          <span className={`inline-flex items-center gap-0.5 text-[11px] font-semibold ${change >= 0 ? "text-emerald-600" : "text-red-500"}`}>
            {change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>

      {/* Mini sparkline */}
      {sparkData && sparkData.length > 2 && (
        <div className="mt-1.5 h-4">
          <MiniSparkline data={sparkData} color={c.text} />
        </div>
      )}

      {sub && (
        <div className="text-[11px] text-slate-400 mt-1 leading-tight">{sub}</div>
      )}
    </div>
  );
}

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min || 1;
  const w = 100;
  const h = 16;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={color}
      />
    </svg>
  );
}

function FunnelRow({ label, value, total, color, icon }: {
  label: string; value: number; total: number; color: string; icon?: React.ReactNode;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <div ref={ref}>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-500 flex items-center gap-1.5">
          {icon}
          {label}
        </span>
        <span className="font-medium text-slate-800 tabular-nums">
          {fmt(value)} <span className="text-slate-400 text-xs">({pct}%)</span>
        </span>
      </div>
      <div className="h-2 bg-slate-50 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${color} rounded-full`}
          initial={{ width: 0 }}
          animate={isInView ? { width: `${Math.max(pct, value > 0 ? 2 : 0)}%` } : { width: 0 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
        />
      </div>
    </div>
  );
}

function QA({ icon, label, href }: { icon: React.ReactNode; label: string; href: string }) {
  return (
    <Link href={href} className="group/qa flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-50 transition-colors">
      <div className="text-slate-400 group-hover/qa:text-blue-600 transition-colors">{icon}</div>
      <span className="text-sm text-slate-600 group-hover/qa:text-slate-800 transition-colors">{label}</span>
      <ArrowRight className="w-3 h-3 text-slate-300 ml-auto group-hover/qa:text-slate-400 group-hover/qa:translate-x-0.5 transition-all" />
    </Link>
  );
}

function statusBarColor(status: string): string {
  const m: Record<string, string> = {
    CONFIRMED: "bg-blue-400",
    REMINDED: "bg-amber-400",
    ATTENDED: "bg-emerald-400",
    NO_SHOW: "bg-red-400",
    CANCELLED: "bg-slate-400",
  };
  return m[status] || "bg-blue-400";
}

function StatusBadge({ status }: { status: string }) {
  const c: Record<string, { icon: React.ReactNode; cls: string }> = {
    CONFIRMED: { icon: <Clock className="w-2.5 h-2.5" />, cls: "bg-blue-50 text-blue-600" },
    REMINDED: { icon: <Bell className="w-2.5 h-2.5" />, cls: "bg-amber-50 text-amber-600" },
    ATTENDED: { icon: <CheckCircle2 className="w-2.5 h-2.5" />, cls: "bg-emerald-50 text-emerald-600" },
    NO_SHOW: { icon: <XCircle className="w-2.5 h-2.5" />, cls: "bg-red-50 text-red-600" },
    CANCELLED: { icon: <XCircle className="w-2.5 h-2.5" />, cls: "bg-slate-100 text-slate-500" },
  };
  const cfg = c[status] || c.CONFIRMED;
  return (
    <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-medium ${cfg.cls}`}>
      {cfg.icon}
    </span>
  );
}

/* ── Welcome Checklist ── */

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

  if (allDone) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="relative rounded-2xl border border-blue-200/60 bg-gradient-to-r from-blue-50/80 via-white to-violet-50/40 p-6 overflow-hidden shadow-sm"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(59,130,246,0.06),transparent_60%)]" />
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-600" /> Get started with PatientPlex
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              {completed} of {steps.length} steps completed
            </p>
          </div>
          <div className="relative w-12 h-12">
            <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="#e2e8f0" strokeWidth="3" />
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="#3b82f6" strokeWidth="3"
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
                <CheckCircle2 className="w-5 h-5 text-blue-500 flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-slate-300 flex-shrink-0" />
              )}
              {step.href && !step.done ? (
                <Link href={step.href} className="text-sm text-blue-600 hover:text-blue-700 font-medium">
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
          <div className="mt-4 pt-4 border-t border-blue-200/50">
            <button
              onClick={onLaunch}
              disabled={launching}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all whitespace-nowrap disabled:opacity-50 shadow-sm shadow-blue-200"
            >
              {launching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              Launch Campaigns
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
