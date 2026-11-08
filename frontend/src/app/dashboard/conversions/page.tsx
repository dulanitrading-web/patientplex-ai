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
  "bg-slate-700",
  "bg-slate-600",
  "bg-slate-700",
  "bg-slate-600",
  "bg-slate-900",
  "bg-slate-700",
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
        <Link href="/dashboard" className="text-slate-600 hover:text-slate-900 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-xl font-bold text-slate-900">Conversion Funnel</h1>
      </div>

      {/* Period Filter */}
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-slate-600" />
        {PERIOD_OPTIONS.map((p) => (
          <button key={p.value} onClick={() => setDays(p.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              days === p.value
                ? "bg-slate-900 text-white"
                : "bg-white/5 text-slate-500 border border-slate-200 hover:bg-white/10 hover:text-slate-900"
            }`}>
            {p.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-slate-900" />
        </div>
      ) : funnel.length === 0 ? (
        <div className="bg-white rounded-xl p-8 text-center border border-slate-200">
          <TrendingUp className="w-10 h-10 text-slate-700 mx-auto mb-2" />
          <p className="text-slate-500">No funnel data yet.</p>
          <p className="text-slate-600 text-xs mt-1">Data will appear once patients start interacting.</p>
        </div>
      ) : (
        <>
          {/* Funnel Visualization */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-sm font-semibold text-slate-900 mb-4">Patient Journey Funnel</h2>
            <div className="space-y-3">
              {funnel.map((stage, i) => {
                const widthPct = Math.max((stage.count / maxCount) * 100, 8);
                return (
                  <div key={stage.stage} className="flex items-center gap-3">
                    <div className="w-36 shrink-0 flex items-center gap-2 text-sm text-slate-500">
                      <span className="text-slate-600">{STAGE_ICONS[stage.stage]}</span>
                      <span className="truncate">{STAGE_LABELS[stage.stage] || stage.stage}</span>
                    </div>
                    <div className="flex-1 relative">
                      <div className="h-8 bg-white/5 rounded-lg w-full absolute" />
                      <div
                        className={`h-8 rounded-lg ${STAGE_COLORS[i % STAGE_COLORS.length]} flex items-center px-3 transition-all duration-500 relative`}
                        style={{ width: `${widthPct}%` }}
                      >
                        <span className="text-slate-900 text-sm font-semibold whitespace-nowrap">
                          {stage.count}
                        </span>
                      </div>
                    </div>
                    <div className="w-16 text-right shrink-0">
                      {stage.conversion_rate !== null && stage.conversion_rate !== undefined ? (
                        <span className="text-xs text-slate-600">{stage.conversion_rate}%</span>
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
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h2 className="text-sm font-semibold text-slate-900 mb-4">Source Attribution</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 pr-4 text-slate-600 font-medium">Channel</th>
                      <th className="text-right py-2 px-3 text-slate-600 font-medium">Leads</th>
                      <th className="text-right py-2 px-3 text-slate-600 font-medium">Appointments</th>
                      <th className="text-right py-2 px-3 text-slate-600 font-medium">Conv. Rate</th>
                      {attribution.some((a) => a.spend != null) && (
                        <th className="text-right py-2 px-3 text-slate-600 font-medium">Spend</th>
                      )}
                      {attribution.some((a) => a.cost_per_lead != null) && (
                        <th className="text-right py-2 pl-3 text-slate-600 font-medium">CPL</th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {attribution.map((ch) => (
                      <tr key={ch.channel} className="border-b border-slate-100 hover:bg-slate-100">
                        <td className="py-2.5 pr-4 font-medium text-slate-900">{ch.channel}</td>
                        <td className="py-2.5 px-3 text-right text-slate-700">{ch.leads}</td>
                        <td className="py-2.5 px-3 text-right text-slate-700">{ch.appointments}</td>
                        <td className="py-2.5 px-3 text-right">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            ch.conversion_rate >= 20 ? "bg-slate-50 text-black" :
                            ch.conversion_rate >= 10 ? "bg-amber-50 text-amber-600" :
                            "bg-red-50 text-red-600"
                          }`}>
                            {ch.conversion_rate}%
                          </span>
                        </td>
                        {attribution.some((a) => a.spend != null) && (
                          <td className="py-2.5 px-3 text-right text-slate-700">
                            {ch.spend != null ? formatINR(ch.spend) : "-"}
                          </td>
                        )}
                        {attribution.some((a) => a.cost_per_lead != null) && (
                          <td className="py-2.5 pl-3 text-right text-slate-700">
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
