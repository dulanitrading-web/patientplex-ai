"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, Play, Pause, TrendingUp, IndianRupee, MousePointerClick,
  Eye, Loader2, AlertCircle, CheckCircle2, Clock, XCircle,
} from "lucide-react";
import Button from "@/components/ui/Button";
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
    ACTIVE: { cls: "bg-green-50 text-green-700", icon: <CheckCircle2 className="w-3 h-3" /> },
    PAUSED: { cls: "bg-yellow-50 text-yellow-700", icon: <Pause className="w-3 h-3" /> },
    DRAFT: { cls: "bg-gray-100 text-gray-600", icon: <Clock className="w-3 h-3" /> },
    PENDING_REVIEW: { cls: "bg-blue-50 text-blue-700", icon: <Clock className="w-3 h-3" /> },
    ERROR: { cls: "bg-red-50 text-red-700", icon: <XCircle className="w-3 h-3" /> },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-gray-400 hover:text-gray-600">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-lg font-bold text-[#0B2545]">Campaigns</h1>
          </div>
          <Button variant="primary" size="sm" onClick={handleLaunch}>
            + Launch New
          </Button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6">
        {campaigns.length === 0 ? (
          <div className="bg-white rounded-xl p-8 border border-gray-200 text-center">
            <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-gray-700 mb-1">No campaigns yet</h2>
            <p className="text-gray-500 text-sm mb-4">Launch your first AI-powered campaigns on Google and Meta.</p>
            <Button onClick={handleLaunch}>Launch Campaigns</Button>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map((c) => {
              const sc = statusConfig[c.status] || statusConfig.DRAFT;
              return (
                <div key={c.id} className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{platformIcon(c.platform)}</span>
                        <h3 className="font-semibold text-[#0B2545]">{c.name}</h3>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${sc.cls}`}>
                          {sc.icon} {c.status}
                        </span>
                        <span className="text-xs text-gray-400">{c.platform} · {c.campaign_type}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {c.status === "ACTIVE" && (
                        <Button variant="ghost" size="sm" onClick={() => handlePause(c.id)}
                          loading={actionLoading === c.id}>
                          <Pause className="w-4 h-4 mr-1" /> Pause
                        </Button>
                      )}
                      {c.status === "PAUSED" && (
                        <Button variant="secondary" size="sm" onClick={() => handleResume(c.id)}
                          loading={actionLoading === c.id}>
                          <Play className="w-4 h-4 mr-1" /> Resume
                        </Button>
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
      </main>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-2.5">
      <div className="flex items-center gap-1 text-gray-400 text-xs mb-0.5">{icon} {label}</div>
      <div className="font-semibold text-sm text-[#0B2545]">{value}</div>
    </div>
  );
}

function fmt(n: number): string {
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}
