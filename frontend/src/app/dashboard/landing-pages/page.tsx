"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Globe, ExternalLink, Copy, CheckCircle2,
  Loader2, Smartphone, FileText,
} from "lucide-react";
import Button from "@/components/ui/Button";
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-gray-400 hover:text-gray-600">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-lg font-bold text-[#0B2545]">Landing Pages</h1>
          </div>
          <Button variant="primary" size="sm" onClick={handleGenerate} loading={generating}>
            {pages.length > 0 ? "Regenerate" : "Generate Pages"}
          </Button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Info Card */}
        <div className="bg-gradient-to-r from-[#0B2545] to-[#13838C] rounded-xl p-5 text-white">
          <div className="flex items-start gap-3">
            <Globe className="w-6 h-6 shrink-0 mt-0.5" />
            <div>
              <h2 className="font-semibold">Your Doctor Landing Pages</h2>
              <p className="text-white/80 text-sm mt-1">
                Each page is optimized for Google Ads quality score and mobile conversion.
                Patients land here from your ads and book via WhatsApp.
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : pages.length === 0 ? (
          <div className="bg-white rounded-xl p-8 border border-gray-200 text-center">
            <Globe className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-gray-700 mb-1">No pages yet</h2>
            <p className="text-gray-500 text-sm mb-4">
              Generate your landing pages — one main page plus a page per treatment.
            </p>
            <Button onClick={handleGenerate} loading={generating}>Generate Landing Pages</Button>
          </div>
        ) : (
          <div className="space-y-3">
            {pages.map((page) => (
              <div key={page.url} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${page.type === "main" ? "bg-blue-50" : "bg-teal-50"}`}>
                      {page.type === "main" ? (
                        <Globe className="w-5 h-5 text-blue-600" />
                      ) : (
                        <FileText className="w-5 h-5 text-teal-600" />
                      )}
                    </div>
                    <div>
                      <div className="font-medium text-sm text-[#0B2545]">{page.title}</div>
                      <div className="text-xs text-gray-400 mt-0.5 break-all">{page.url}</div>
                      <span className={`inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-medium ${
                        page.type === "main" ? "bg-blue-50 text-blue-600" : "bg-teal-50 text-teal-600"
                      }`}>
                        {page.type === "main" ? "Main Page" : "Treatment Page"}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <button onClick={() => copyUrl(page.url)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      {copied === page.url ? (
                        <><CheckCircle2 className="w-3.5 h-3.5 text-green-500" /> Copied</>
                      ) : (
                        <><Copy className="w-3.5 h-3.5" /> Copy URL</>
                      )}
                    </button>
                    {previewUrl && page.type === "main" && (
                      <a href={`http://localhost:8000${previewUrl}`} target="_blank" rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
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
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-3">
              <Smartphone className="w-5 h-5" /> How Your Page Looks
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Your landing pages are mobile-first with WhatsApp booking, Google Maps,
              and treatment details. They load instantly for better ad quality scores.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="font-medium text-green-700">📱 Mobile Optimized</div>
                <div className="text-green-600 text-xs mt-1">80% of patient traffic is mobile</div>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-700">⚡ Fast Loading</div>
                <div className="text-blue-600 text-xs mt-1">No frameworks — pure HTML/CSS</div>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <div className="font-medium text-purple-700">🔍 SEO Ready</div>
                <div className="text-purple-600 text-xs mt-1">Schema.org medical business markup</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
