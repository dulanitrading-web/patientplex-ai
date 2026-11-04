"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  BarChart3,
  Calendar,
  MessageCircle,
  IndianRupee,
  MousePointerClick,
  Eye,
  Globe,
  LogOut,
  ArrowRight,
  Loader2,
  Zap,
  Activity,
  CheckCircle2,
  Clock,
  XCircle,
} from "lucide-react";
import Button from "@/components/ui/Button";
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

export default function DashboardPage() {
  const router = useRouter();
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [campaignOverview, setCampaignOverview] = useState<CampaignOverview | null>(null);
  const [appointmentStats, setAppointmentStats] = useState<AppointmentStats | null>(null);
  const [todayAppts, setTodayAppts] = useState<TodayAppointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
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

  function handleSignOut() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const hasCampaigns = (campaignOverview?.total_campaigns || 0) > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-[#0B2545]">PatientPlex AI</h1>
            <p className="text-sm text-gray-500">Welcome, {doctor?.full_name || "Doctor"}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500 hidden sm:block">
              {doctor?.clinic_name} · {doctor?.city}
            </span>
            <button onClick={handleSignOut} className="text-gray-400 hover:text-gray-600 p-2" title="Sign out">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Launch CTA */}
        {!hasCampaigns && (
          <div className="bg-gradient-to-r from-[#0B2545] to-[#13838C] rounded-2xl p-6 text-white">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Zap className="w-6 h-6" /> Ready to Get Patients?
                </h2>
                <p className="text-white/80 mt-1">
                  Launch AI-powered campaigns on Google &amp; Meta to start getting patient enquiries.
                </p>
              </div>
              <Button variant="primary" size="lg" onClick={handleLaunch} loading={launching}
                className="!bg-white !text-[#0B2545] hover:!bg-gray-100 whitespace-nowrap">
                Launch Campaigns <ArrowRight className="w-5 h-5" />
              </Button>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard icon={<Eye className="w-5 h-5" />} label="Impressions"
            value={fmt(campaignOverview?.total_impressions || 0)} color="blue" />
          <MetricCard icon={<MousePointerClick className="w-5 h-5" />} label="Clicks"
            value={fmt(campaignOverview?.total_clicks || 0)}
            sub={`₹${campaignOverview?.avg_cpc?.toFixed(1) || "0"} avg CPC`} color="green" />
          <MetricCard icon={<MessageCircle className="w-5 h-5" />} label="Enquiries"
            value={fmt(campaignOverview?.total_conversions || 0)} color="purple" />
          <MetricCard icon={<Calendar className="w-5 h-5" />} label="Appointments"
            value={fmt(appointmentStats?.total_booked || 0)}
            sub={`${appointmentStats?.attendance_rate || 0}% attended`} color="teal" />
        </div>

        {/* Spend + Funnel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-5 border border-gray-200">
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-4">
              <IndianRupee className="w-5 h-5" /> Ad Spend (30 days)
            </h3>
            <div className="text-3xl font-bold text-[#0B2545]">₹{fmt(campaignOverview?.total_spend || 0)}</div>
            <div className="mt-2 text-sm text-gray-500">
              Cost per patient: ₹{appointmentStats?.attended
                ? Math.round((campaignOverview?.total_spend || 0) / appointmentStats.attended) : "—"}
            </div>
            <div className="mt-4">
              <Link href="/dashboard/campaigns">
                <Button variant="secondary" size="sm">View Campaigns</Button>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-200">
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5" /> Patient Funnel (30 days)
            </h3>
            <div className="space-y-3">
              <FunnelRow label="Ad Clicks" value={campaignOverview?.total_clicks || 0}
                total={campaignOverview?.total_clicks || 1} color="bg-blue-500" />
              <FunnelRow label="Enquiries" value={campaignOverview?.total_conversions || 0}
                total={campaignOverview?.total_clicks || 1} color="bg-purple-500" />
              <FunnelRow label="Booked" value={appointmentStats?.total_booked || 0}
                total={campaignOverview?.total_clicks || 1} color="bg-teal-500" />
              <FunnelRow label="Attended" value={appointmentStats?.attended || 0}
                total={campaignOverview?.total_clicks || 1} color="bg-green-500" />
            </div>
          </div>
        </div>

        {/* Today + Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-gray-200">
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-4">
              <Calendar className="w-5 h-5" /> Today&apos;s Appointments
            </h3>
            {todayAppts.length === 0 ? (
              <p className="text-gray-400 text-sm py-4">No appointments today.</p>
            ) : (
              <div className="divide-y divide-gray-100">
                {todayAppts.map((a) => (
                  <div key={a.id} className="flex items-center justify-between py-3">
                    <div>
                      <div className="font-medium text-sm">{a.patient_name}</div>
                      <div className="text-xs text-gray-500">{a.treatment}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-600">{a.time}</span>
                      <StatusBadge status={a.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-3">
              <Link href="/dashboard/appointments">
                <Button variant="ghost" size="sm">View All <ArrowRight className="w-4 h-4" /></Button>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-200">
            <h3 className="font-semibold text-[#0B2545] mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Link href="/dashboard/campaigns" className="block"><QA icon={<BarChart3 className="w-4 h-4" />} label="Manage Campaigns" /></Link>
              <Link href="/dashboard/conversations" className="block"><QA icon={<MessageCircle className="w-4 h-4" />} label="WhatsApp Chats" /></Link>
              <Link href="/dashboard/appointments" className="block"><QA icon={<Calendar className="w-4 h-4" />} label="Appointments" /></Link>
              <Link href="/dashboard/landing-pages" className="block"><QA icon={<Globe className="w-4 h-4" />} label="Landing Pages" /></Link>
            </div>

            {appointmentStats && Object.keys(appointmentStats.by_treatment || {}).length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-100">
                <h4 className="text-sm font-medium text-gray-600 mb-3">By Treatment</h4>
                {Object.entries(appointmentStats.by_treatment).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([t, c]) => (
                  <div key={t} className="flex justify-between text-sm py-1">
                    <span className="text-gray-600">{t}</span>
                    <span className="font-medium">{c}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function MetricCard({ icon, label, value, sub, color }: {
  icon: React.ReactNode; label: string; value: string; sub?: string; color: string;
}) {
  const cm: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600", green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600", teal: "bg-teal-50 text-teal-600",
  };
  return (
    <div className="bg-white rounded-xl p-4 border border-gray-200">
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg ${cm[color]}`}>{icon}</div>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-[#0B2545]">{value}</div>
      {sub && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  );
}

function FunnelRow({ label, value, total, color }: {
  label: string; value: number; total: number; color: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{fmt(value)} ({pct}%)</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function QA({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
      <div className="text-gray-400">{icon}</div>
      <span className="text-sm text-gray-700">{label}</span>
      <ArrowRight className="w-3.5 h-3.5 text-gray-300 ml-auto" />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const c: Record<string, { icon: React.ReactNode; cls: string }> = {
    CONFIRMED: { icon: <Clock className="w-3 h-3" />, cls: "bg-blue-50 text-blue-600" },
    REMINDED: { icon: <Clock className="w-3 h-3" />, cls: "bg-yellow-50 text-yellow-600" },
    ATTENDED: { icon: <CheckCircle2 className="w-3 h-3" />, cls: "bg-green-50 text-green-600" },
    NO_SHOW: { icon: <XCircle className="w-3 h-3" />, cls: "bg-red-50 text-red-600" },
    CANCELLED: { icon: <XCircle className="w-3 h-3" />, cls: "bg-gray-100 text-gray-500" },
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
