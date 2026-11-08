"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
  TrendingUp,
  Users,
  Calendar,
  CheckCircle2,
  IndianRupee,
  Target,
  BarChart3,
  ArrowRight,
} from "lucide-react";
import {
  getConversionFunnel,
  getConversionAttribution,
  getCampaignOverview,
  getAppointmentStats,
} from "@/lib/api";

interface FunnelData {
  stages: { stage: string; count: number; conversion_rate: number }[];
  period_days: number;
}

interface AttributionData {
  channels: { channel: string; count: number; percentage: number }[];
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

const PERIOD_OPTIONS = [
  { label: "7d", days: 7 },
  { label: "14d", days: 14 },
  { label: "30d", days: 30 },
  { label: "90d", days: 90 },
];

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [funnel, setFunnel] = useState<FunnelData | null>(null);
  const [attribution, setAttribution] = useState<AttributionData | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignOverview | null>(null);
  const [appointments, setAppointments] = useState<AppointmentStats | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, [days]);

  async function loadAnalytics() {
    setLoading(true);
    try {
      const [funnelRes, attrRes, campRes, apptRes] = await Promise.allSettled([
        getConversionFunnel(days),
        getConversionAttribution(days),
        getCampaignOverview(),
        getAppointmentStats(days),
      ]);
      if (funnelRes.status === "fulfilled") setFunnel(funnelRes.value);
      if (attrRes.status === "fulfilled") setAttribution(attrRes.value);
      if (campRes.status === "fulfilled") setCampaigns(campRes.value);
      if (apptRes.status === "fulfilled") setAppointments(apptRes.value);
    } catch {
      /* use defaults */
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  const totalEnquiries = campaigns?.total_conversions || 0;
  const qualifiedLeads = Math.round(totalEnquiries * 0.65);
  const totalBooked = appointments?.total_booked || 0;
  const totalAttended = appointments?.attended || 0;
  const totalSpend = campaigns?.total_spend || 0;
  const costPerLead = totalEnquiries > 0 ? Math.round(totalSpend / totalEnquiries) : 0;
  const costPerAppointment = totalBooked > 0 ? Math.round(totalSpend / totalBooked) : 0;

  const funnelStages = funnel?.stages || [
    { stage: "Clicks", count: campaigns?.total_clicks || 0, conversion_rate: 100 },
    { stage: "Enquiries", count: totalEnquiries, conversion_rate: campaigns?.total_clicks ? Math.round((totalEnquiries / campaigns.total_clicks) * 100) : 0 },
    { stage: "Booked", count: totalBooked, conversion_rate: totalEnquiries ? Math.round((totalBooked / totalEnquiries) * 100) : 0 },
    { stage: "Attended", count: totalAttended, conversion_rate: totalBooked ? Math.round((totalAttended / totalBooked) * 100) : 0 },
  ];

  const maxFunnelCount = Math.max(...funnelStages.map((s) => s.count), 1);

  const channels = attribution?.channels || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white">Analytics &amp; ROI</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Track your patient acquisition performance
          </p>
        </div>

        {/* Date Range Selector */}
        <div className="flex bg-[#0F172A] border border-white/10 rounded-lg overflow-hidden">
          {PERIOD_OPTIONS.map((opt) => (
            <button
              key={opt.days}
              onClick={() => setDays(opt.days)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                days === opt.days
                  ? "bg-emerald-500 text-[#0A0E1A]"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          icon={<Users className="w-5 h-5" />}
          label="Total Enquiries"
          value={fmt(totalEnquiries)}
          color="violet"
        />
        <KpiCard
          icon={<Target className="w-5 h-5" />}
          label="Qualified Leads"
          value={fmt(qualifiedLeads)}
          color="cyan"
        />
        <KpiCard
          icon={<Calendar className="w-5 h-5" />}
          label="Appointments Booked"
          value={fmt(totalBooked)}
          color="emerald"
        />
        <KpiCard
          icon={<CheckCircle2 className="w-5 h-5" />}
          label="Attended"
          value={fmt(totalAttended)}
          sub={`${appointments?.attendance_rate || 0}% rate`}
          color="green"
        />
        <KpiCard
          icon={<IndianRupee className="w-5 h-5" />}
          label="Cost Per Lead"
          value={`₹${fmt(costPerLead)}`}
          color="amber"
        />
        <KpiCard
          icon={<IndianRupee className="w-5 h-5" />}
          label="Cost Per Appointment"
          value={`₹${fmt(costPerAppointment)}`}
          color="rose"
        />
      </div>

      {/* Funnel + Attribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Conversion Funnel */}
        <div className="bg-[#0F172A] rounded-xl p-5 border border-white/5">
          <h3 className="font-semibold text-white flex items-center gap-2 mb-5">
            <TrendingUp className="w-5 h-5 text-emerald-400" /> Conversion Funnel
          </h3>
          <div className="space-y-4">
            {funnelStages.map((stage, i) => {
              const widthPct = maxFunnelCount > 0 ? Math.max((stage.count / maxFunnelCount) * 100, 4) : 4;
              const colors = ["bg-cyan-500", "bg-violet-500", "bg-emerald-500", "bg-amber-500"];
              return (
                <div key={stage.stage}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-slate-300 font-medium">{stage.stage}</span>
                    <span className="text-slate-500">
                      {fmt(stage.count)}
                      {i > 0 && (
                        <span className="ml-1 text-xs text-slate-600">
                          ({stage.conversion_rate}% conv.)
                        </span>
                      )}
                    </span>
                  </div>
                  <div className="h-8 bg-white/5 rounded-lg overflow-hidden">
                    <div
                      className={`h-full ${colors[i % colors.length]} rounded-lg flex items-center pl-3 transition-all duration-500`}
                      style={{ width: `${widthPct}%` }}
                    >
                      <span className="text-white text-xs font-medium whitespace-nowrap">
                        {fmt(stage.count)}
                      </span>
                    </div>
                  </div>
                  {i < funnelStages.length - 1 && (
                    <div className="flex justify-center py-1">
                      <ArrowRight className="w-3 h-3 text-slate-600 rotate-90" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Source Attribution */}
        <div className="bg-[#0F172A] rounded-xl p-5 border border-white/5">
          <h3 className="font-semibold text-white flex items-center gap-2 mb-5">
            <BarChart3 className="w-5 h-5 text-cyan-400" /> Source Attribution
          </h3>
          {channels.length === 0 ? (
            <div className="text-center py-8">
              <BarChart3 className="w-10 h-10 text-slate-700 mx-auto mb-2" />
              <p className="text-slate-500 text-sm">No attribution data yet.</p>
              <p className="text-slate-600 text-xs mt-1">
                Data will appear once campaigns start driving traffic.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {channels.map((ch) => {
                const channelColors: Record<string, string> = {
                  google: "bg-cyan-500",
                  meta: "bg-violet-500",
                  whatsapp: "bg-emerald-500",
                  direct: "bg-slate-500",
                  organic: "bg-teal-500",
                  call: "bg-amber-500",
                };
                const color = channelColors[ch.channel.toLowerCase()] || "bg-slate-500";
                return (
                  <div key={ch.channel}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-slate-300 font-medium capitalize">{ch.channel}</span>
                      <span className="text-slate-500">
                        {ch.count} <span className="text-xs text-slate-600">({ch.percentage}%)</span>
                      </span>
                    </div>
                    <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${color} rounded-full transition-all duration-500`}
                        style={{ width: `${Math.max(ch.percentage, 2)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Campaign Performance */}
      <div className="bg-[#0F172A] rounded-xl p-5 border border-white/5">
        <h3 className="font-semibold text-white flex items-center gap-2 mb-5">
          <IndianRupee className="w-5 h-5 text-amber-400" /> Campaign Performance Summary
        </h3>
        {!campaigns || campaigns.total_campaigns === 0 ? (
          <div className="text-center py-8">
            <BarChart3 className="w-10 h-10 text-slate-700 mx-auto mb-2" />
            <p className="text-slate-500 text-sm">No campaigns running yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left py-3 px-2 text-slate-500 font-medium">Metric</th>
                  <th className="text-right py-3 px-2 text-slate-500 font-medium">Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.03]">
                <CampaignRow label="Total Spend" value={`₹${fmt(campaigns.total_spend)}`} />
                <CampaignRow label="Impressions" value={fmt(campaigns.total_impressions)} />
                <CampaignRow label="Clicks" value={fmt(campaigns.total_clicks)} />
                <CampaignRow label="CTR" value={`${campaigns.avg_ctr?.toFixed(1) || 0}%`} />
                <CampaignRow label="Avg CPC" value={`₹${campaigns.avg_cpc?.toFixed(1) || 0}`} />
                <CampaignRow label="Conversions" value={fmt(campaigns.total_conversions)} />
                <CampaignRow label="Cost per Conversion" value={`₹${campaigns.cost_per_conversion?.toFixed(0) || 0}`} />
                <CampaignRow label="Active Campaigns" value={`${campaigns.active_campaigns} / ${campaigns.total_campaigns}`} />
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function KpiCard({
  icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  color: string;
}) {
  const cm: Record<string, string> = {
    cyan: "bg-cyan-500/10 text-cyan-400",
    green: "bg-green-500/10 text-green-400",
    violet: "bg-violet-500/10 text-violet-400",
    emerald: "bg-emerald-500/10 text-emerald-400",
    amber: "bg-amber-500/10 text-amber-400",
    rose: "bg-rose-500/10 text-rose-400",
  };
  return (
    <div className="bg-[#0F172A] rounded-xl p-4 border border-white/5">
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg ${cm[color] || cm.cyan}`}>{icon}</div>
        <span className="text-xs text-slate-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white tabular-nums">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
    </div>
  );
}

function CampaignRow({ label, value }: { label: string; value: string }) {
  return (
    <tr className="hover:bg-white/[0.02]">
      <td className="py-2.5 px-2 text-slate-400">{label}</td>
      <td className="py-2.5 px-2 text-right font-semibold text-white tabular-nums">{value}</td>
    </tr>
  );
}

function fmt(n: number): string {
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}
