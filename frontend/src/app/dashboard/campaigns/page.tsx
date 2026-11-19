"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Play, Pause, TrendingUp, IndianRupee, MousePointerClick,
  Eye, Loader2, AlertCircle, CheckCircle2, Clock, XCircle,
  ChevronDown, ChevronUp, Pencil, Check, X, Plus, Trash2,
  Brain, ArrowUpRight, ArrowDownRight, Minus,
  Wifi, WifiOff, Search,
} from "lucide-react";
import {
  getCampaigns, pauseCampaign, resumeCampaign, launchCampaigns,
  getAIIntelligence, updateCampaignBudget, updateCampaignKeywords,
  getCampaignDetail,
} from "@/lib/api";

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
  keywords?: string[];
  negative_keywords?: string[];
}

interface HealthIssue { severity: string; issue: string; action: string }
interface ActionItem { priority: number; action: string; category: string; severity: string }
interface NetworkDecision { enabled: boolean; budget_share: number; reason: string }
interface BudgetRealloc { campaign_name: string; performance_score: number; current_daily_inr: number; recommended_daily_inr: number; action: string; reason: string }

interface AIIntelligence {
  account_health: { score: number; grade: string; issues: HealthIssue[]; wins: string[] };
  network_decisions: Record<string, NetworkDecision>;
  bidding_decisions: { campaigns: Record<string, string | number | boolean>[] };
  budget_reallocation: { reallocation: BudgetRealloc[]; daily_budget_total: number };
  campaign_actions: Record<string, string>[];
  meta_decisions: Record<string, unknown>;
  next_actions: ActionItem[];
  summary_metrics: Record<string, number>;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [intelligence, setIntelligence] = useState<AIIntelligence | null>(null);
  const [intelLoading, setIntelLoading] = useState(false);
  const [intelOpen, setIntelOpen] = useState(true);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [editingBudget, setEditingBudget] = useState<string | null>(null);
  const [budgetValue, setBudgetValue] = useState("");
  const [newKeyword, setNewKeyword] = useState("");
  const [campaignDetails, setCampaignDetails] = useState<Record<string, Campaign>>({});
  const [platformFilter, setPlatformFilter] = useState<string>("ALL");

  const loadCampaigns = useCallback(async () => {
    try {
      const data = await getCampaigns();
      setCampaigns(data.campaigns || []);
    } catch {
      setCampaigns([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCampaigns();
    loadIntelligence();
  }, [loadCampaigns]);

  async function loadIntelligence() {
    setIntelLoading(true);
    try {
      const data = await getAIIntelligence();
      setIntelligence(data);
    } catch {
      // Intelligence is optional — page works without it
    } finally {
      setIntelLoading(false);
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
      await launchCampaigns(["GOOGLE", "META", "CHATGPT", "LINKEDIN", "WHATSAPP"]);
      await loadCampaigns();
    } finally {
      setLoading(false);
    }
  }

  async function handleBudgetSave(id: string) {
    const val = parseInt(budgetValue, 10);
    if (!val || val < 0) return;
    setActionLoading(id);
    try {
      await updateCampaignBudget(id, val);
      await loadCampaigns();
      setEditingBudget(null);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleExpandCard(id: string) {
    if (expandedCard === id) {
      setExpandedCard(null);
      return;
    }
    setExpandedCard(id);
    if (!campaignDetails[id]) {
      try {
        const detail = await getCampaignDetail(id);
        setCampaignDetails((prev) => ({ ...prev, [id]: detail }));
      } catch { /* ignore */ }
    }
  }

  async function handleAddKeyword(campaignId: string) {
    if (!newKeyword.trim()) return;
    setActionLoading(campaignId);
    try {
      const result = await updateCampaignKeywords(campaignId, [newKeyword.trim()], []);
      setCampaignDetails((prev) => ({
        ...prev,
        [campaignId]: { ...prev[campaignId], keywords: result.keywords },
      }));
      setNewKeyword("");
      await loadCampaigns();
    } finally {
      setActionLoading(null);
    }
  }

  async function handleRemoveKeyword(campaignId: string, keyword: string) {
    setActionLoading(campaignId);
    try {
      const result = await updateCampaignKeywords(campaignId, [], [keyword]);
      setCampaignDetails((prev) => ({
        ...prev,
        [campaignId]: { ...prev[campaignId], keywords: result.keywords },
      }));
      await loadCampaigns();
    } finally {
      setActionLoading(null);
    }
  }

  const platformIcon = (p: string) => {
    if (p === "GOOGLE") return "🔍";
    if (p === "META") return "📘";
    if (p === "LINKEDIN") return "💼";
    if (p === "CHATGPT") return "🤖";
    if (p === "WHATSAPP") return "💬";
    return "📢";
  };

  const statusConfig: Record<string, { cls: string; icon: React.ReactNode }> = {
    ACTIVE: { cls: "bg-emerald-50 text-emerald-600", icon: <CheckCircle2 className="w-3 h-3" /> },
    PAUSED: { cls: "bg-amber-50 text-amber-600", icon: <Pause className="w-3 h-3" /> },
    DRAFT: { cls: "bg-slate-50 text-slate-500", icon: <Clock className="w-3 h-3" /> },
    PENDING_REVIEW: { cls: "bg-cyan-50 text-cyan-600", icon: <Clock className="w-3 h-3" /> },
    ERROR: { cls: "bg-red-50 text-red-600", icon: <XCircle className="w-3 h-3" /> },
    COMPLETED: { cls: "bg-slate-50 text-slate-400", icon: <CheckCircle2 className="w-3 h-3" /> },
  };

  const gradeColor = (g: string) => {
    if (g === "A") return "text-emerald-600 bg-emerald-50";
    if (g === "B") return "text-cyan-600 bg-cyan-50";
    if (g === "C") return "text-amber-600 bg-amber-50";
    return "text-red-600 bg-red-50";
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
        <h1 className="text-xl font-bold text-slate-900">Campaigns</h1>
        <a
          href="/dashboard/campaigns/new"
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors inline-block"
        >
          + Launch New
        </a>
      </div>

      {/* ── AI Intelligence Panel ── */}
      {intelligence && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <button
            onClick={() => setIntelOpen(!intelOpen)}
            className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-violet-600" />
              <span className="font-semibold text-slate-900">AI Recommendations</span>
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${gradeColor(intelligence.account_health.grade)}`}>
                {intelligence.account_health.grade} — {intelligence.account_health.score}/100
              </span>
            </div>
            {intelOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </button>

          {intelOpen && (
            <div className="px-4 pb-4 space-y-4">
              {/* Wins */}
              {intelligence.account_health.wins.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {intelligence.account_health.wins.map((w, i) => (
                    <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs">
                      <CheckCircle2 className="w-3 h-3" /> {w}
                    </span>
                  ))}
                </div>
              )}

              {/* Top Actions */}
              {intelligence.next_actions.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Priority Actions</h4>
                  <div className="space-y-2">
                    {intelligence.next_actions.slice(0, 5).map((a, i) => (
                      <div key={i} className="flex items-start gap-2 p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                        <span className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                          a.severity === "CRITICAL" ? "bg-red-100 text-red-700" :
                          a.severity === "HIGH" ? "bg-amber-100 text-amber-700" :
                          "bg-slate-100 text-slate-600"
                        }`}>
                          {i + 1}
                        </span>
                        <p className="text-sm text-slate-700">{a.action}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Network Decisions */}
              <div>
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Network Status</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                  {Object.entries(intelligence.network_decisions).map(([key, val]) => (
                    <div key={key} className={`p-2.5 rounded-lg border text-xs ${
                      val.enabled ? "bg-emerald-50 border-emerald-200" : "bg-slate-50 border-slate-200"
                    }`}>
                      <div className="flex items-center gap-1 font-semibold mb-1">
                        {val.enabled ? <Wifi className="w-3 h-3 text-emerald-600" /> : <WifiOff className="w-3 h-3 text-slate-400" />}
                        <span className={val.enabled ? "text-emerald-700" : "text-slate-500"}>
                          {key.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}
                        </span>
                      </div>
                      <p className="text-slate-500 leading-tight">{val.enabled ? "Active" : "Off"} — {Math.round((val.budget_share || 0) * 100)}% budget</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Budget Reallocation */}
              {intelligence.budget_reallocation.reallocation.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Budget Reallocation</h4>
                  <div className="space-y-1.5">
                    {intelligence.budget_reallocation.reallocation
                      .filter((r) => r.action !== "keep")
                      .slice(0, 5)
                      .map((r, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg text-sm">
                        <span className="text-slate-700 truncate max-w-[50%]">{r.campaign_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">₹{r.current_daily_inr}/d</span>
                          {r.action === "increase" ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-600" />
                          ) : (
                            <ArrowDownRight className="w-4 h-4 text-red-500" />
                          )}
                          <span className={`font-semibold ${r.action === "increase" ? "text-emerald-700" : "text-red-600"}`}>
                            ₹{r.recommended_daily_inr}/d
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {intelLoading && !intelligence && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-2 text-sm text-slate-500">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading AI recommendations...
        </div>
      )}

      {/* ── Platform Filter ── */}
      {campaigns.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          {["ALL", ...Array.from(new Set(campaigns.map(c => c.platform)))].map((p) => (
            <button
              key={p}
              onClick={() => setPlatformFilter(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                platformFilter === p
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {p === "ALL" ? `All Platforms (${campaigns.length})` : `${p} (${campaigns.filter(c => c.platform === p).length})`}
            </button>
          ))}
        </div>
      )}

      {/* ── Campaign Cards ── */}
      {campaigns.length === 0 ? (
        <div className="bg-white rounded-xl p-8 border border-slate-200 text-center">
          <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-1">No campaigns yet</h2>
          <p className="text-slate-500 text-sm mb-4">Launch your first AI-powered campaigns across Google, Meta, and more.</p>
          <a
            href="/dashboard/campaigns/new"
            className="inline-block px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors"
          >
            Create Your First Campaign
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {campaigns.filter(c => platformFilter === "ALL" || c.platform === platformFilter).map((c) => {
            const sc = statusConfig[c.status] || statusConfig.DRAFT;
            const isExpanded = expandedCard === c.id;
            const detail = campaignDetails[c.id];
            const keywords = detail?.keywords || c.keywords || [];
            const negativeKeywords = detail?.negative_keywords || [];

            return (
              <div key={c.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                {/* Header */}
                <div className="p-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{platformIcon(c.platform)}</span>
                        <h3 className="font-semibold text-slate-900">{c.name}</h3>
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
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors disabled:opacity-50"
                        >
                          {actionLoading === c.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />} Pause
                        </button>
                      )}
                      {c.status === "PAUSED" && (
                        <button
                          onClick={() => handleResume(c.id)}
                          disabled={actionLoading === c.id}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm border border-slate-200 hover:border-slate-300 text-slate-700 transition-colors disabled:opacity-50"
                        >
                          {actionLoading === c.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />} Resume
                        </button>
                      )}
                      <button
                        onClick={() => handleExpandCard(c.id)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-50 transition-colors"
                      >
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        {isExpanded ? "Less" : "Edit"}
                      </button>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                    {/* Budget — editable */}
                    <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-slate-500 text-xs mb-0.5">
                          <IndianRupee className="w-3.5 h-3.5" /> Budget
                        </div>
                        {editingBudget !== c.id && (
                          <button onClick={() => { setEditingBudget(c.id); setBudgetValue(String(c.daily_budget || "")); }}
                            className="text-slate-400 hover:text-slate-600">
                            <Pencil className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                      {editingBudget === c.id ? (
                        <div className="flex items-center gap-1 mt-1">
                          <span className="text-xs text-slate-500">₹</span>
                          <input
                            type="number"
                            value={budgetValue}
                            onChange={(e) => setBudgetValue(e.target.value)}
                            className="w-16 text-sm font-semibold border border-slate-300 rounded px-1.5 py-0.5 focus:outline-none focus:border-emerald-500"
                            placeholder="500"
                            autoFocus
                            onKeyDown={(e) => { if (e.key === "Enter") handleBudgetSave(c.id); if (e.key === "Escape") setEditingBudget(null); }}
                          />
                          <button onClick={() => handleBudgetSave(c.id)} className="text-emerald-600 hover:text-emerald-700">
                            <Check className="w-4 h-4" />
                          </button>
                          <button onClick={() => setEditingBudget(null)} className="text-slate-400 hover:text-slate-600">
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="font-semibold text-sm text-slate-900 tabular-nums">
                          {c.daily_budget > 0 ? `₹${fmt(c.daily_budget)}/day` : <span className="text-slate-400">Not set</span>}
                        </div>
                      )}
                    </div>
                    <StatCell icon={<Eye className="w-3.5 h-3.5" />} label="Impressions" value={fmt(c.impressions)} />
                    <StatCell icon={<MousePointerClick className="w-3.5 h-3.5" />} label="Clicks" value={fmt(c.clicks)} />
                    <StatCell icon={<TrendingUp className="w-3.5 h-3.5" />} label="CTR" value={`${c.ctr > 0 ? c.ctr.toFixed(1) : "0.0"}%`} />
                    <StatCell icon={<IndianRupee className="w-3.5 h-3.5" />} label="Spend" value={c.spend > 0 ? `₹${fmt(c.spend)}` : "₹0"} />
                  </div>
                </div>

                {/* Expanded: Keywords + Details */}
                {isExpanded && (
                  <div className="border-t border-slate-100 px-5 py-4 bg-slate-50/50 space-y-4">
                    {/* Keywords */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Search className="w-3 h-3" /> Keywords ({keywords.length})
                      </h4>
                      {keywords.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5 mb-2">
                          {keywords.map((kw: string, i: number) => (
                            <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-slate-200 rounded-md text-xs text-slate-700">
                              {kw}
                              <button
                                onClick={() => handleRemoveKeyword(c.id, kw)}
                                className="text-slate-400 hover:text-red-500 ml-0.5"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-400 mb-2">No keywords set — add some to improve targeting</p>
                      )}
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={newKeyword}
                          onChange={(e) => setNewKeyword(e.target.value)}
                          placeholder="Add keyword..."
                          className="flex-1 max-w-xs text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-emerald-500"
                          onKeyDown={(e) => { if (e.key === "Enter") handleAddKeyword(c.id); }}
                        />
                        <button
                          onClick={() => handleAddKeyword(c.id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-medium rounded-lg transition-colors"
                        >
                          <Plus className="w-3 h-3" /> Add
                        </button>
                      </div>
                    </div>

                    {/* Negative Keywords */}
                    {negativeKeywords.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                          Negative Keywords ({negativeKeywords.length})
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {negativeKeywords.map((kw: string, i: number) => (
                            <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-red-50 border border-red-100 rounded-md text-xs text-red-600">
                              <Minus className="w-3 h-3" /> {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Quick Metrics */}
                    {c.conversions > 0 && c.spend > 0 && (
                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-white rounded-lg p-2.5 border border-slate-200 text-center">
                          <div className="text-xs text-slate-500">Cost/Lead</div>
                          <div className="font-bold text-sm text-slate-900">₹{fmt(Math.round(c.spend / c.conversions))}</div>
                        </div>
                        <div className="bg-white rounded-lg p-2.5 border border-slate-200 text-center">
                          <div className="text-xs text-slate-500">Conversions</div>
                          <div className="font-bold text-sm text-emerald-600">{c.conversions}</div>
                        </div>
                        <div className="bg-white rounded-lg p-2.5 border border-slate-200 text-center">
                          <div className="text-xs text-slate-500">Avg CPC</div>
                          <div className="font-bold text-sm text-slate-900">₹{c.cpc > 0 ? c.cpc.toFixed(0) : "—"}</div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function StatCell({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-200">
      <div className="flex items-center gap-1 text-slate-500 text-xs mb-0.5">{icon} {label}</div>
      <div className="font-semibold text-sm text-slate-900 tabular-nums">{value}</div>
    </div>
  );
}

function fmt(n: number): string {
  if (n >= 10000000) return (n / 10000000).toFixed(1) + "Cr";
  if (n >= 100000) return (n / 100000).toFixed(1) + "L";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toLocaleString("en-IN");
}
