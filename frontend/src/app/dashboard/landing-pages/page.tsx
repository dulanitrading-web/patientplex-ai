"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Globe, ExternalLink, Copy, CheckCircle2,
  Loader2, Smartphone, FileText,
} from "lucide-react";
import { generateLandingPage, getLandingPages } from "@/lib/api";

interface LandingPage {
  url: string;
  type: string;
  title: string;
}

export default function LandingPagesPage() {
  const [pages, setPages] = useState<LandingPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  async function load() {
    try {
      const data = await getLandingPages();
      setPages(data.pages || []);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    try {
      const result = await generateLandingPage();
      setPreviewUrl(result.preview_url);
      await load();
    } finally {
      setGenerating(false);
    }
  }

  function copyUrl(url: string) {
    navigator.clipboard.writeText(url);
    setCopied(url);
    setTimeout(() => setCopied(null), 2000);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/dashboard" className="text-slate-600 hover:text-slate-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-slate-900">Landing Pages</h1>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium transition-colors disabled:opacity-50"
        >
          {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {pages.length > 0 ? "Regenerate" : "Generate Pages"}
        </button>
      </div>

      {/* Info Card */}
      <div className="rounded-xl p-5 border border-slate-300 bg-slate-900/[0.06]">
        <div className="flex items-start gap-3">
          <Globe className="w-6 h-6 shrink-0 mt-0.5 text-black" />
          <div>
            <h2 className="font-semibold text-slate-900">Your Doctor Landing Pages</h2>
            <p className="text-slate-500 text-sm mt-1">
              Each page is optimized for Google Ads quality score and mobile conversion.
              Patients land here from your ads and book via WhatsApp.
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-slate-900" />
        </div>
      ) : pages.length === 0 ? (
        <div className="bg-white rounded-xl p-8 border border-slate-200 text-center">
          <Globe className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-700 mb-1">No pages yet</h2>
          <p className="text-slate-600 text-sm mb-4">
            Generate your landing pages — one main page plus a page per treatment.
          </p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm transition-colors disabled:opacity-50"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            Generate Landing Pages
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {pages.map((page) => (
            <div key={page.url} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${page.type === "main" ? "bg-slate-50" : "bg-slate-50"}`}>
                    {page.type === "main" ? (
                      <Globe className="w-5 h-5 text-black" />
                    ) : (
                      <FileText className="w-5 h-5 text-slate-700" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-sm text-slate-900">{page.title}</div>
                    <div className="text-xs text-slate-600 mt-0.5 break-all">{page.url}</div>
                    <span className={`inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-medium ${
                      page.type === "main" ? "bg-slate-50 text-black" : "bg-slate-50 text-slate-700"
                    }`}>
                      {page.type === "main" ? "Main Page" : "Treatment Page"}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button onClick={() => copyUrl(page.url)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-500 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                    {copied === page.url ? (
                      <><CheckCircle2 className="w-3.5 h-3.5 text-black" /> Copied</>
                    ) : (
                      <><Copy className="w-3.5 h-3.5" /> Copy URL</>
                    )}
                  </button>
                  {previewUrl && page.type === "main" && (
                    <a href={`${process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || ''}${previewUrl}`} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-black bg-slate-50 rounded-lg hover:bg-black/10 transition-colors">
                      <ExternalLink className="w-3.5 h-3.5" /> Preview
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Mobile Preview Mockup */}
      {pages.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-3">
            <Smartphone className="w-5 h-5 text-slate-700" /> How Your Page Looks
          </h3>
          <p className="text-sm text-slate-600 mb-4">
            Your landing pages are mobile-first with WhatsApp booking, Google Maps,
            and treatment details. They load instantly for better ad quality scores.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="font-medium text-black">Mobile Optimized</div>
              <div className="text-black/60 text-xs mt-1">80% of patient traffic is mobile</div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="font-medium text-slate-700">Fast Loading</div>
              <div className="text-slate-700/60 text-xs mt-1">No frameworks — pure HTML/CSS</div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="font-medium text-slate-700">SEO Ready</div>
              <div className="text-slate-700/60 text-xs mt-1">Schema.org medical business markup</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
