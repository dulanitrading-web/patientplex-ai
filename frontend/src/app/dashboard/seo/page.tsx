"use client";

import { useState, useEffect } from "react";
import { Search, FileText, Code, TrendingUp, BarChart3, RefreshCw, CheckCircle2, AlertTriangle, XCircle, ExternalLink } from "lucide-react";
import { useAuth } from "@/context/auth";

interface AuditCheck {
  name: string;
  status: "pass" | "warning" | "fail";
  detail: string;
  priority: string;
}

interface AuditResult {
  score: number;
  max_score: number;
  checks: AuditCheck[];
  recommendations: string[];
  demo_mode?: boolean;
}

interface Keyword {
  keyword: string;
  volume: number;
  competition: string;
  cpc: number;
}

export default function SEOPage() {
  const { token } = useAuth();
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"audit" | "keywords" | "schema" | "blog" | "report">("audit");
  const [schemaMarkup, setSchemaMarkup] = useState<string>("");
  const [auditUrl, setAuditUrl] = useState("");

  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (!token) return;
    fetchData();
  }, [token]);

  async function fetchData() {
    setLoading(true);
    const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
    try {
      const [auditRes, keywordRes, schemaRes] = await Promise.all([
        fetch(`${API}/api/v1/seo/audit`, { method: "POST", headers, body: JSON.stringify({ url: "" }) }),
        fetch(`${API}/api/v1/seo/keywords`, { headers }),
        fetch(`${API}/api/v1/seo/schema`, { headers }),
      ]);
      if (auditRes.ok) setAudit(await auditRes.json());
      if (keywordRes.ok) {
        const data = await keywordRes.json();
        setKeywords(data.keywords || []);
      }
      if (schemaRes.ok) {
        const data = await schemaRes.json();
        setSchemaMarkup(data.html_snippet || "");
      }
    } catch (err) {
      console.error("SEO fetch error:", err);
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

  const statusIcon = (s: string) => {
    if (s === "pass") return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
    if (s === "warning") return <AlertTriangle className="w-4 h-4 text-amber-500" />;
    return <XCircle className="w-4 h-4 text-red-500" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Website SEO</h1>
          <p className="text-sm text-slate-500 mt-1">Optimize your clinic&apos;s website for organic search traffic</p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" /> Run Audit
        </button>
      </div>

      {audit?.demo_mode && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
          <strong>Demo Mode:</strong> Enter your website URL to get a live SEO audit. Connect Google Search Console for keyword tracking.
        </div>
      )}

      {/* SEO Score */}
      {audit && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 flex items-center gap-6">
          <div className="w-20 h-20 rounded-full border-4 border-emerald-500 flex items-center justify-center shrink-0">
            <span className="text-2xl font-black text-slate-900">{audit.score}</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">SEO Health Score</h3>
            <p className="text-sm text-slate-500 mt-1">
              {audit.checks.filter(c => c.status === "pass").length} passed,{" "}
              {audit.checks.filter(c => c.status === "warning").length} warnings,{" "}
              {audit.checks.filter(c => c.status === "fail").length} failures
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 w-fit">
        {([
          { key: "audit", label: "Audit", icon: Search },
          { key: "keywords", label: "Keywords", icon: TrendingUp },
          { key: "schema", label: "Schema", icon: Code },
          { key: "blog", label: "Blog Ideas", icon: FileText },
          { key: "report", label: "Report", icon: BarChart3 },
        ] as const).map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition ${
              activeTab === tab.key ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <tab.icon className="w-3.5 h-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Audit Tab */}
      {activeTab === "audit" && audit && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {audit.checks.map((check) => (
              <div key={check.name} className="px-5 py-3.5 flex items-start gap-3">
                {statusIcon(check.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-slate-900">{check.name}</span>
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                      check.priority === "high" ? "bg-red-50 text-red-600" :
                      check.priority === "medium" ? "bg-amber-50 text-amber-600" : "bg-slate-100 text-slate-500"
                    }`}>{check.priority}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{check.detail}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-900 mb-3">Recommendations</h3>
            <ul className="space-y-2">
              {audit.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-emerald-500 font-bold mt-0.5">{i + 1}.</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Keywords Tab */}
      {activeTab === "keywords" && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left py-3 px-4 font-semibold text-slate-700">Keyword</th>
                <th className="text-right py-3 px-4 font-semibold text-slate-700">Volume/mo</th>
                <th className="text-center py-3 px-4 font-semibold text-slate-700">Competition</th>
                <th className="text-right py-3 px-4 font-semibold text-slate-700">CPC (₹)</th>
              </tr>
            </thead>
            <tbody>
              {keywords.map((kw) => (
                <tr key={kw.keyword} className="border-b border-slate-50 last:border-0">
                  <td className="py-3 px-4 font-medium text-slate-900">{kw.keyword}</td>
                  <td className="py-3 px-4 text-right tabular-nums">{kw.volume.toLocaleString()}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      kw.competition === "high" ? "bg-red-50 text-red-600" :
                      kw.competition === "medium" ? "bg-amber-50 text-amber-600" : "bg-green-50 text-green-600"
                    }`}>{kw.competition}</span>
                  </td>
                  <td className="py-3 px-4 text-right tabular-nums">₹{kw.cpc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Schema Tab */}
      {activeTab === "schema" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-2">JSON-LD Schema Markup</h3>
          <p className="text-sm text-slate-500 mb-4">Add this to your website&apos;s &lt;head&gt; for Google rich snippets</p>
          <pre className="bg-slate-900 text-emerald-400 rounded-lg p-4 text-xs overflow-x-auto">
            {schemaMarkup || "Loading..."}
          </pre>
          <button
            onClick={() => navigator.clipboard.writeText(schemaMarkup)}
            className="mt-3 text-sm text-emerald-600 hover:text-emerald-700 font-medium"
          >
            Copy to clipboard
          </button>
        </div>
      )}

      {/* Blog Ideas Tab */}
      {activeTab === "blog" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">AI Blog Content Ideas</h3>
          <p className="text-sm text-slate-500 mb-4">NMC-compliant blog topics that drive organic traffic to your clinic</p>
          <div className="space-y-3">
            {[
              "Cost of Dental Implants — Complete Guide",
              "Teeth Whitening: Professional vs At-Home — What Works",
              "When Should You See a Dentist? 7 Warning Signs",
              "Root Canal vs Extraction — How to Decide",
              "Braces vs Clear Aligners — Cost, Time, Results Compared",
            ].map((topic, i) => (
              <div key={i} className="flex items-center justify-between px-4 py-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span className="text-sm font-medium text-slate-900">{topic}</span>
                </div>
                <button className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">Generate Outline</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Tab */}
      {activeTab === "report" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 text-center">
          <BarChart3 className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-slate-900 mb-1">Monthly SEO Report</h3>
          <p className="text-sm text-slate-500 mb-4">Connect Google Search Console to generate your first SEO report with live keyword rankings and organic traffic data.</p>
          <button className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition text-sm font-medium">
            Connect Search Console
          </button>
        </div>
      )}
    </div>
  );
}
