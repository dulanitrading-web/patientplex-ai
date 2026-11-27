"use client";

import { useState, useEffect } from "react";
import { LineChart, BarChart3, Users, ArrowUpRight, Globe, RefreshCw, TrendingUp, MousePointerClick, AlertTriangle } from "lucide-react";
import { fetchWithAuth } from "@/lib/api";

interface GA4Report {
  demo_mode?: boolean;
  status?: "not_configured" | "unavailable";
  period: string;
  metrics: {
    active_users: number;
    sessions: number;
    conversions: number;
    total_revenue: number;
    avg_session_duration: string;
    bounce_rate: string;
  };
  top_sources: Array<{ source: string; users: number; conversions: number }>;
  top_pages: Array<{ page: string; views: number }>;
  conversion_funnel: {
    ad_clicks: number;
    whatsapp_starts: number;
    bookings: number;
    attended: number;
    conversion_rate: string;
  };
}

interface RealtimeData {
  demo_mode?: boolean;
  status?: "not_configured" | "unavailable";
  active_users: number;
  top_pages?: string[];
  top_sources?: string[];
}

export default function GA4AnalyticsPage() {
  const [report, setReport] = useState<GA4Report | null>(null);
  const [realtime, setRealtime] = useState<RealtimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState("30daysAgo");

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  async function fetchData() {
    setLoading(true);
    try {
      const [reportRes, realtimeRes] = await Promise.allSettled([
        fetchWithAuth(`/ga4/report?date_range=${dateRange}`),
        fetchWithAuth("/ga4/realtime"),
      ]);
      setReport(reportRes.status === "fulfilled" && reportRes.value.ok
        ? await reportRes.value.json()
        : null);
      setRealtime(realtimeRes.status === "fulfilled" && realtimeRes.value.ok
        ? await realtimeRes.value.json()
        : null);
    } catch (err) {
      console.error("GA4 fetch error:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">GA4 Analytics</h1>
          <p className="text-sm text-slate-500 mt-1">Google Analytics 4 — track your full patient acquisition funnel</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm"
            aria-label="Date range"
          >
            <option value="7daysAgo">Last 7 days</option>
            <option value="30daysAgo">Last 30 days</option>
            <option value="90daysAgo">Last 90 days</option>
          </select>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition text-sm font-medium"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>
      </div>

      {(!report || report.demo_mode || !report.metrics) && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-900">{report?.status === "not_configured" ? "GA4 reporting is not configured" : "GA4 reporting data is unavailable"}</p>
            <p className="text-sm text-amber-700 mt-1">
              Connect Google Analytics 4 to see real website traffic, conversions, and patient funnel data.
              Go to <a href="/dashboard/settings" className="underline font-medium">Settings → Integrations</a> to set up GA4.
            </p>
          </div>
        </div>
      )}

      {/* Realtime Badge */}
      {realtime && !realtime.demo_mode && typeof realtime.active_users === "number" && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-slate-600">
            <strong className="text-slate-900">{realtime.active_users}</strong> active users right now
          </span>
        </div>
      )}

      {/* Key Metrics */}
      {!report?.demo_mode && report?.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: "Active Users", value: report.metrics.active_users.toLocaleString(), icon: Users, color: "blue" },
            { label: "Sessions", value: report.metrics.sessions.toLocaleString(), icon: Globe, color: "emerald" },
            { label: "Conversions", value: report.metrics.conversions.toLocaleString(), icon: TrendingUp, color: "purple" },
            { label: "Revenue", value: `₹${(report.metrics.total_revenue / 1000).toFixed(0)}K`, icon: ArrowUpRight, color: "green" },
            { label: "Avg Duration", value: report.metrics.avg_session_duration, icon: LineChart, color: "sky" },
            { label: "Bounce Rate", value: report.metrics.bounce_rate, icon: MousePointerClick, color: "orange" },
          ].map((stat) => (
            <div key={stat.label} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500 mb-1">{stat.label}</div>
              <div className="text-xl font-bold text-slate-900">{stat.value}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {/* Conversion Funnel */}
        {!report?.demo_mode && report?.conversion_funnel && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              Patient Conversion Funnel
            </h3>
            <div className="space-y-3">
              {[
                { stage: "Ad Clicks", value: report.conversion_funnel.ad_clicks, color: "bg-blue-500" },
                { stage: "WhatsApp Starts", value: report.conversion_funnel.whatsapp_starts, color: "bg-emerald-500" },
                { stage: "Bookings", value: report.conversion_funnel.bookings, color: "bg-purple-500" },
                { stage: "Attended", value: report.conversion_funnel.attended, color: "bg-green-500" },
              ].map((step, i) => {
                const maxVal = report.conversion_funnel.ad_clicks || 1;
                const pct = ((step.value / maxVal) * 100).toFixed(0);
                return (
                  <div key={step.stage}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-slate-600">{step.stage}</span>
                      <span className="font-medium">{step.value.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full ${step.color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-sm">
                <span className="text-slate-600 font-medium">Overall Conversion Rate</span>
                <span className="font-bold text-emerald-600 text-lg">{report.conversion_funnel.conversion_rate}</span>
              </div>
            </div>
          </div>
        )}

        {/* Top Sources */}
        {!report?.demo_mode && report?.top_sources && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              Top Traffic Sources
            </h3>
            <div className="space-y-2">
              {report.top_sources.map((src) => (
                <div key={src.source} className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
                  <div>
                    <div className="text-sm font-medium text-slate-900 capitalize">{src.source.replace(/_/g, " ")}</div>
                    <div className="text-xs text-slate-500">{src.users} users</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-emerald-600">{src.conversions} conversions</div>
                    <div className="text-xs text-slate-500">
                      {((src.conversions / (src.users || 1)) * 100).toFixed(1)}% rate
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Top Pages */}
      {!report?.demo_mode && report?.top_pages && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">Top Pages</h3>
          <div className="space-y-2">
            {report.top_pages.map((page) => (
              <div key={page.page} className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
                <span className="text-sm text-slate-700 font-mono">{page.page}</span>
                <span className="text-sm font-medium text-slate-900">{page.views.toLocaleString()} views</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
