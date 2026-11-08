"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, TrendingUp, Loader2, BarChart3, MousePointerClick,
  Globe, Phone, MessageCircle, UserCheck, Calendar, CheckCircle2, Users,
} from "lucide-react";
import { getConversionFunnel, getConversionAttribution } from "@/lib/api";

interface FunnelStage {
  stage: string;
  count: number;
  conversion_rate: number | null;
}

interface AttributionChannel {
  channel: string;
  leads: number;
  appointments: number;
  conversion_rate: number;
  spend?: number;
  cost_per_lead?: number;
}

const STAGE_LABELS: Record<string, string> = {
  AD_CLICK: "Ad Click",
  LANDING_PAGE: "Landing Page",
  CALL_ATTEMPTED: "Call Attempted",
  WHATSAPP_STARTED: "WhatsApp Started",
  LEAD_QUALIFIED: "Lead Qualified",
  APPOINTMENT_BOOKED: "Appointment Booked",
  CONFIRMED: "Confirmed",
  ATTENDED: "Attended",
};

const STAGE_ICONS: Record<string, React.ReactNode> = {
  AD_CLICK: <MousePointerClick className="w-4 h-4" />,
  LANDING_PAGE: <Globe className="w-4 h-4" />,
  CALL_ATTEMPTED: <Phone className="w-4 h-4" />,
  WHATSAPP_STARTED: <MessageCircle className="w-4 h-4" />,
  LEAD_QUALIFIED: <UserCheck className="w-4 h-4" />,
  APPOINTMENT_BOOKED: <Calendar className="w-4 h-4" />,
  CONFIRMED: <CheckCircle2 className="w-4 h-4" />,
  ATTENDED: <Users className="w-4 h-4" />,
};

const STAGE_COLORS = [
  "bg-cyan-500",
  "bg-cyan-400",
  "bg-violet-500",
  "bg-violet-400",
  "bg-emerald-500",
  "bg-emerald-400",
  "bg-green-500",
  "bg-green-400",
];

const PERIOD_OPTIONS = [
  { label: "7 days", value: 7 },
  { label: "30 days", value: 30 },
  { label: "90 days", value: 90 },
];

function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function ConversionsPage() {
  const [funnel, setFunnel] = useState<FunnelStage[]>([]);
  const [attribution, setAttribution] = useState<AttributionChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => { load(); }, [days]);

  async function load() {
    setLoading(true);
    try {
      const [funnelData, attrData] = await Promise.allSettled([
        getConversionFunnel(days),
        getConversionAttribution(days),
      ]);
      if (funnelData.status === "fulfilled") {
        setFunnel(funnelData.value.stages || funnelData.value.funnel || []);
      }
      if (attrData.status === "fulfilled") {
        setAttribution(attrData.value.channels || attrData.value.attribution || []);
      }
    } finally {
      setLoading(false);
    }
  }

  const maxCount = funnel.length > 0 ? Math.max(...funnel.map((s) => s.count), 1) : 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="text-slate-500 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-xl font-bold text-white">Conversion Funnel</h1>
      </div>

      {/* Period Filter */}
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-slate-500" />
        {PERIOD_OPTIONS.map((p) => (
          <button key={p.value} onClick={() => setDays(p.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              days === p.value
                ? "bg-emerald-500 text-[#0A0E1A]"
                : "bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10 hover:text-white"
            }`}>
            {p.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
        </div>
      ) : funnel.length === 0 ? (
        <div className="bg-[#0F172A] rounded-xl p-8 text-center border border-white/5">
          <TrendingUp className="w-10 h-10 text-slate-700 mx-auto mb-2" />
          <p className="text-slate-400">No funnel data yet.</p>
          <p className="text-slate-600 text-xs mt-1">Data will appear once patients start interacting.</p>
        </div>
      ) : (
        <>
          {/* Funnel Visualization */}
          <div className="bg-[#0F172A] rounded-xl border border-white/5 p-6">
            <h2 className="text-sm font-semibold text-white mb-4">Patient Journey Funnel</h2>
            <div className="space-y-3">
              {funnel.map((stage, i) => {
                const widthPct = Math.max((stage.count / maxCount) * 100, 8);
                return (
                  <div key={stage.stage} className="flex items-center gap-3">
                    <div className="w-36 shrink-0 flex items-center gap-2 text-sm text-slate-400">
                      <span className="text-slate-500">{STAGE_ICONS[stage.stage]}</span>
                      <span className="truncate">{STAGE_LABELS[stage.stage] || stage.stage}</span>
                    </div>
                    <div className="flex-1 relative">
                      <div className="h-8 bg-white/5 rounded-lg w-full absolute" />
                      <div
                        className={`h-8 rounded-lg ${STAGE_COLORS[i % STAGE_COLORS.length]} flex items-center px-3 transition-all duration-500 relative`}
                        style={{ width: `${widthPct}%` }}
                      >
                        <span className="text-white text-sm font-semibold whitespace-nowrap">
                          {stage.count}
                        </span>
                      </div>
                    </div>
                    <div className="w-16 text-right shrink-0">
                      {stage.conversion_rate !== null && stage.conversion_rate !== undefined ? (
                        <span className="text-xs text-slate-500">{stage.conversion_rate}%</span>
                      ) : (
                        <span className="text-xs text-slate-700">-</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-3 text-xs text-slate-600 text-right">
              Conversion rate shown is from previous stage
            </div>
          </div>

          {/* Attribution Breakdown */}
          {attribution.length > 0 && (
            <div className="bg-[#0F172A] rounded-xl border border-white/5 p-6">
              <h2 className="text-sm font-semibold text-white mb-4">Source Attribution</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="text-left py-2 pr-4 text-slate-500 font-medium">Channel</th>
                      <th className="text-right py-2 px-3 text-slate-500 font-medium">Leads</th>
                      <th className="text-right py-2 px-3 text-slate-500 font-medium">Appointments</th>
                      <th className="text-right py-2 px-3 text-slate-500 font-medium">Conv. Rate</th>
                      {attribution.some((a) => a.spend != null) && (
                        <th className="text-right py-2 px-3 text-slate-500 font-medium">Spend</th>
                      )}
                      {attribution.some((a) => a.cost_per_lead != null) && (
                        <th className="text-right py-2 pl-3 text-slate-500 font-medium">CPL</th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {attribution.map((ch) => (
                      <tr key={ch.channel} className="border-b border-white/[0.03] hover:bg-white/5">
                        <td className="py-2.5 pr-4 font-medium text-white">{ch.channel}</td>
                        <td className="py-2.5 px-3 text-right text-slate-300">{ch.leads}</td>
                        <td className="py-2.5 px-3 text-right text-slate-300">{ch.appointments}</td>
                        <td className="py-2.5 px-3 text-right">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            ch.conversion_rate >= 20 ? "bg-emerald-500/10 text-emerald-400" :
                            ch.conversion_rate >= 10 ? "bg-amber-500/10 text-amber-400" :
                            "bg-red-500/10 text-red-400"
                          }`}>
                            {ch.conversion_rate}%
                          </span>
                        </td>
                        {attribution.some((a) => a.spend != null) && (
                          <td className="py-2.5 px-3 text-right text-slate-300">
                            {ch.spend != null ? formatINR(ch.spend) : "-"}
                          </td>
                        )}
                        {attribution.some((a) => a.cost_per_lead != null) && (
                          <td className="py-2.5 pl-3 text-right text-slate-300">
                            {ch.cost_per_lead != null ? formatINR(ch.cost_per_lead) : "-"}
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
