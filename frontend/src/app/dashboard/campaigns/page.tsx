"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, Play, Pause, TrendingUp, IndianRupee, MousePointerClick,
  Eye, Loader2, AlertCircle, CheckCircle2, Clock, XCircle,
} from "lucide-react";
import { getCampaigns, pauseCampaign, resumeCampaign, launchCampaigns } from "@/lib/api";

interface Campaign {
  id: string;
  platform: string;
  name: string;
  status: string;
  campaign_type: string;
  daily_budget: number;
  total_budget: number;
  currency: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  cpc: number;
  ctr: number;
  created_at: string;
}

export default function CampaignsPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadCampaigns();
  }, []);

  async function loadCampaigns() {
    try {
      const data = await getCampaigns();
      setCampaigns(data.campaigns || []);
    } catch {
      setCampaigns([]);
    } finally {
      setLoading(false);
    }
  }

  async function handlePause(id: string) {
    setActionLoading(id);
    try {
      await pauseCampaign(id);
      await loadCampaigns();
    } finally {
      setActionLoading(null);
    }
  }

  async function handleResume(id: string) {
    setActionLoading(id);
    try {
      await resumeCampaign(id);
      await loadCampaigns();
    } finally {
      setActionLoading(null);
    }
  }

  async function handleLaunch() {
    setLoading(true);
    try {
      await launchCampaigns(["GOOGLE", "META"]);
      await loadCampaigns();
    } finally {
      setLoading(false);
    }
  }

  const platformIcon = (p: string) => {
    if (p === "GOOGLE") return "🔍";
    if (p === "META") return "📘";
    if (p === "LINKEDIN") return "💼";
    return "📢";
  };

  const statusConfig: Record<string, { cls: string; icon: React.ReactNode }> = {
    ACTIVE: { cls: "bg-emerald-500/10 text-emerald-400", icon: <CheckCircle2 className="w-3 h-3" /> },
    PAUSED: { cls: "bg-amber-500/10 text-amber-400", icon: <Pause className="w-3 h-3" /> },
    DRAFT: { cls: "bg-white/5 text-slate-400", icon: <Clock className="w-3 h-3" /> },
    PENDING_REVIEW: { cls: "bg-cyan-500/10 text-cyan-400", icon: <Clock className="w-3 h-3" /> },
    ERROR: { cls: "bg-red-500/10 text-red-400", icon: <XCircle className="w-3 h-3" /> },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Campaigns</h1>
        <button
          onClick={handleLaunch}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] text-sm font-medium transition-colors"
        >
          + Launch New
        </button>
      </div>

      {campaigns.length === 0 ? (
        <div className="bg-[#0F172A] rounded-xl p-8 border border-white/5 text-center">
          <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-white mb-1">No campaigns yet</h2>
          <p className="text-slate-400 text-sm mb-4">Launch your first AI-powered campaigns on Google and Meta.</p>
          <button
            onClick={handleLaunch}
            className="px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] text-sm font-medium transition-colors"
          >
            Launch Campaigns
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {campaigns.map((c) => {
            const sc = statusConfig[c.status] || statusConfig.DRAFT;
            return (
              <div key={c.id} className="bg-[#0F172A] rounded-xl border border-white/5 p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{platformIcon(c.platform)}</span>
                      <h3 className="font-semibold text-white">{c.name}</h3>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${sc.cls}`}>
                        {sc.icon} {c.status}
                      </span>
                      <span className="text-xs text-slate-500">{c.platform} · {c.campaign_type}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {c.status === "ACTIVE" && (
                      <button
                        onClick={() => handlePause(c.id)}
                        disabled={actionLoading === c.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                      >
                        {actionLoading === c.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />} Pause
                      </button>
                    )}
                    {c.status === "PAUSED" && (
                      <button
                        onClick={() => handleResume(c.id)}
                        disabled={actionLoading === c.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm border border-white/10 hover:border-white/20 text-slate-300 hover:text-white transition-colors disabled:opacity-50"
                      >
                        {actionLoading === c.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />} Resume
                      </button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  <Stat icon={<IndianRupee className="w-3.5 h-3.5" />} label="Budget" value={`₹${c.daily_budget}/day`} />
                  <Stat icon={<Eye className="w-3.5 h-3.5" />} label="Impressions" value={fmt(c.impressions)} />
                  <Stat icon={<MousePointerClick className="w-3.5 h-3.5" />} label="Clicks" value={fmt(c.clicks)} />
                  <Stat icon={<TrendingUp className="w-3.5 h-3.5" />} label="CTR" value={`${c.ctr.toFixed(1)}%`} />
                  <Stat icon={<IndianRupee className="w-3.5 h-3.5" />} label="Spend" value={`₹${fmt(c.spend)}`} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-white/[0.03] rounded-lg p-2.5 border border-white/5">
      <div className="flex items-center gap-1 text-slate-500 text-xs mb-0.5">{icon} {label}</div>
      <div className="font-semibold text-sm text-white tabular-nums">{value}</div>
    </div>
  );
}

function fmt(n: number): string {
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}
