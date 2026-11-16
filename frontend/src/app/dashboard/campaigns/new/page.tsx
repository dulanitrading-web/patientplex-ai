"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft, ArrowRight, Search, MessageCircle, Target,
  IndianRupee, Loader2, CheckCircle2, Zap, Globe,
  MousePointerClick, Calendar, Sparkles, Rocket,
} from "lucide-react";
import { getMe, launchCampaigns } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DoctorProfile {
  full_name: string;
  clinic_name: string;
  specialty: string;
  city: string;
  state: string;
  services: string[];
  monthly_budget: number;
  geo_radius_km: number;
}

interface PlatformOption {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  badge?: string;
  best_for: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PLATFORMS: PlatformOption[] = [
  {
    id: "GOOGLE",
    name: "Google Ads",
    icon: <Search className="w-6 h-6" />,
    description: "Show your clinic when patients search for treatments on Google. Highest intent — they're already looking.",
    badge: "Recommended",
    best_for: "Patients actively searching for treatment",
  },
  {
    id: "META",
    name: "Meta Ads (Facebook + Instagram)",
    icon: <Globe className="w-6 h-6" />,
    description: "Reach potential patients on Facebook and Instagram. Great for awareness and before/after showcases.",
    best_for: "Building awareness, showcasing results",
  },
  {
    id: "WHATSAPP",
    name: "Click-to-WhatsApp",
    icon: <MessageCircle className="w-6 h-6" />,
    description: "Ads on Facebook/Instagram that open a WhatsApp chat with your clinic. Highest conversion in India.",
    badge: "Best for India",
    best_for: "Instant patient conversations",
  },
];

const SPECIALTY_CPC: Record<string, number> = {
  DENTIST: 35, DERMATOLOGIST: 40, ORTHOPEDIC: 45, OPHTHALMOLOGIST: 30,
  PEDIATRICIAN: 20, ENT: 25, SURGEON: 50, GENERAL_PHYSICIAN: 15,
  GYNECOLOGIST: 30, OTHER: 25,
};

const TREATMENT_SEARCH_VOLUME: Record<string, number> = {
  "Dental Implants": 8100, "Root Canal": 6600, "Braces": 5400,
  "Teeth Whitening": 4400, "Teeth Cleaning": 3600, "Aligners": 2900,
  "Smile Makeover": 1900, "Crowns & Bridges": 1600, "Wisdom Tooth Extraction": 1300,
  "Gum Treatment": 880, "Cavity Filling": 720,
  "Hair Loss Treatment": 9900, "Acne Treatment": 8100, "Laser Treatment": 5400,
  "Skin Whitening": 4400, "PRP Therapy": 2900, "Anti-Aging Therapy": 1900,
  "LASIK": 12100, "Cataract Surgery": 6600, "Glaucoma Treatment": 2400,
  "Joint Replacement": 5400, "Fracture Treatment": 3600, "Sports Injury": 2900,
  "IVF": 14800, "Normal Delivery": 4400, "PCOS Treatment": 6600,
  "Vaccination": 8100, "Growth Monitoring": 1200,
  "General Check-up": 3600, "Health Screening": 2400,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (n >= 10000000) return `${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toLocaleString("en-IN");
}

function generateKeywords(treatments: string[], city: string): string[] {
  const keywords: string[] = [];
  for (const t of treatments) {
    const lower = t.toLowerCase();
    keywords.push(`${lower} ${city.toLowerCase()}`);
    keywords.push(`${lower} cost ${city.toLowerCase()}`);
    keywords.push(`best ${lower} ${city.toLowerCase()}`);
    keywords.push(`${lower} near me`);
  }
  return keywords;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CampaignWizardPage() {
  const router = useRouter();
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [launched, setLaunched] = useState(false);

  // Wizard state
  const [step, setStep] = useState(1);
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [selectedTreatments, setSelectedTreatments] = useState<string[]>([]);
  const [dailyBudget, setDailyBudget] = useState(500);

  useEffect(() => {
    (async () => {
      try {
        const data = await getMe();
        setDoctor(data);
        if (data.monthly_budget > 0) {
          setDailyBudget(Math.round(data.monthly_budget / 30.4));
        }
      } catch {
        // Not logged in
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const cpc = SPECIALTY_CPC[doctor?.specialty || "OTHER"] || 25;
  const estimatedClicks = Math.round((dailyBudget * 30) / cpc);
  const estimatedEnquiries = Math.round(estimatedClicks * 0.05);
  const keywords = useMemo(
    () => generateKeywords(selectedTreatments, doctor?.city || ""),
    [selectedTreatments, doctor?.city],
  );

  const campaignName = useMemo(() => {
    if (!doctor) return "";
    const treatment = selectedTreatments[0] || "Search";
    const platform = selectedPlatform === "GOOGLE" ? "Search" : selectedPlatform === "META" ? "Meta" : "WhatsApp";
    return `${doctor.clinic_name} | ${platform} | ${treatment} | ${doctor.city}`;
  }, [doctor, selectedTreatments, selectedPlatform]);

  function toggleTreatment(t: string) {
    setSelectedTreatments((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : prev.length < 3 ? [...prev, t] : prev
    );
  }

  async function handleLaunch() {
    if (!selectedPlatform) return;
    setLaunching(true);
    try {
      await launchCampaigns([selectedPlatform]);
      setLaunched(true);
      setTimeout(() => router.push("/dashboard/campaigns"), 2000);
    } catch {
      setLaunching(false);
    }
  }

  // ---- Loading / Success states ----

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (launched) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4 animate-bounce">
          <Rocket className="w-8 h-8 text-emerald-600" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Campaign Launched!</h2>
        <p className="text-slate-500">Redirecting to your campaigns...</p>
      </div>
    );
  }

  // ---- Step indicators ----

  const steps = ["Platform", "Treatments", "Budget", "Launch"];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => (step === 1 ? router.push("/dashboard/campaigns") : setStep(step - 1))}
          className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-slate-900">Create Campaign</h1>
          <p className="text-sm text-slate-500">Step {step} of 4 — {steps[step - 1]}</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="flex gap-1.5">
        {steps.map((s, i) => (
          <div
            key={s}
            className={`h-1.5 flex-1 rounded-full transition-colors ${
              i < step ? "bg-emerald-500" : "bg-slate-200"
            }`}
          />
        ))}
      </div>

      {/* ───── STEP 1: Choose Platform ───── */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Where do you want to advertise?</h2>
            <p className="text-sm text-slate-500">
              Start with Google Ads for fastest results — patients are already searching for your treatments.
            </p>
          </div>

          <div className="space-y-3">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPlatform(p.id)}
                className={`w-full text-left p-5 rounded-xl border-2 transition-all ${
                  selectedPlatform === p.id
                    ? "border-emerald-500 bg-emerald-50/50 shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-2.5 rounded-lg ${
                    selectedPlatform === p.id ? "bg-emerald-100 text-emerald-600" : "bg-slate-100 text-slate-500"
                  }`}>
                    {p.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-slate-900">{p.name}</span>
                      {p.badge && (
                        <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-emerald-100 text-emerald-700">
                          {p.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-600 mb-2">{p.description}</p>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Target className="w-3 h-3" />
                      {p.best_for}
                    </div>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 mt-1 ${
                    selectedPlatform === p.id ? "border-emerald-500 bg-emerald-500" : "border-slate-300"
                  }`}>
                    {selectedPlatform === p.id && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                  </div>
                </div>
              </button>
            ))}
          </div>

          <button
            onClick={() => selectedPlatform && setStep(2)}
            disabled={!selectedPlatform}
            className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            Continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ───── STEP 2: Choose Treatments ───── */}
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Which treatments do you want to promote?</h2>
            <p className="text-sm text-slate-500">
              Select 1–3 treatments. We'll create targeted campaigns with the right keywords and ad copy for each.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {(doctor?.services || []).map((service) => {
              const selected = selectedTreatments.includes(service);
              const volume = TREATMENT_SEARCH_VOLUME[service];
              return (
                <button
                  key={service}
                  onClick={() => toggleTreatment(service)}
                  disabled={!selected && selectedTreatments.length >= 3}
                  className={`text-left p-4 rounded-xl border-2 transition-all ${
                    selected
                      ? "border-emerald-500 bg-emerald-50/50"
                      : selectedTreatments.length >= 3
                        ? "border-slate-100 bg-slate-50 opacity-50 cursor-not-allowed"
                        : "border-slate-200 bg-white hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-900 text-sm">{service}</span>
                    <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                      selected ? "border-emerald-500 bg-emerald-500" : "border-slate-300"
                    }`}>
                      {selected && <CheckCircle2 className="w-3 h-3 text-white" />}
                    </div>
                  </div>
                  {volume && (
                    <div className="flex items-center gap-1 text-xs text-slate-400">
                      <Search className="w-3 h-3" />
                      {fmt(volume)} searches/month
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {selectedTreatments.length > 0 && (
            <div className="p-3 bg-emerald-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-emerald-700">
                <Sparkles className="w-4 h-4" />
                <span className="font-medium">{selectedTreatments.length} treatment{selectedTreatments.length > 1 ? "s" : ""} selected</span>
              </div>
              <p className="text-xs text-emerald-600 mt-1">
                We'll generate {selectedTreatments.length * 4} keywords targeting "{doctor?.city}" for these treatments.
              </p>
            </div>
          )}

          <button
            onClick={() => selectedTreatments.length > 0 && setStep(3)}
            disabled={selectedTreatments.length === 0}
            className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            Continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ───── STEP 3: Set Budget ───── */}
      {step === 3 && (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Set your daily budget</h2>
            <p className="text-sm text-slate-500">
              How much do you want to spend per day? You can change this anytime.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-slate-900 tabular-nums">
                ₹{dailyBudget.toLocaleString("en-IN")}
                <span className="text-base font-normal text-slate-400">/day</span>
              </div>
              <div className="text-sm text-slate-500 mt-1">
                ₹{fmt(dailyBudget * 30)}/month
              </div>
            </div>

            <input
              type="range"
              min={100}
              max={15000}
              step={100}
              value={dailyBudget}
              onChange={(e) => setDailyBudget(parseInt(e.target.value, 10))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>₹100/day</span>
              <span>₹15,000/day</span>
            </div>
          </div>

          {/* Estimates */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <MousePointerClick className="w-5 h-5 text-cyan-500 mx-auto mb-1.5" />
              <div className="text-xl font-bold text-slate-900 tabular-nums">{fmt(estimatedClicks)}</div>
              <div className="text-xs text-slate-500">Clicks/month</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <IndianRupee className="w-5 h-5 text-emerald-500 mx-auto mb-1.5" />
              <div className="text-xl font-bold text-slate-900 tabular-nums">₹{cpc}</div>
              <div className="text-xs text-slate-500">Est. per click</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <Calendar className="w-5 h-5 text-violet-500 mx-auto mb-1.5" />
              <div className="text-xl font-bold text-slate-900 tabular-nums">{estimatedEnquiries}</div>
              <div className="text-xs text-slate-500">Enquiries/month</div>
            </div>
          </div>

          <p className="text-xs text-slate-400 text-center">
            Estimates based on ₹{cpc} avg CPC for {doctor?.specialty?.replace("_", " ").toLowerCase() || "healthcare"} in {doctor?.city || "your city"}.
            Actual results depend on competition, ad quality, and landing page.
          </p>

          <button
            onClick={() => setStep(4)}
            className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2"
          >
            Review & Launch <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ───── STEP 4: Review & Launch ───── */}
      {step === 4 && (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Review your campaign</h2>
            <p className="text-sm text-slate-500">
              Everything looks good? Hit launch and your ads go live within 24 hours.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {/* Campaign name */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Campaign Name</div>
              <div className="font-semibold text-slate-900">{campaignName}</div>
            </div>

            {/* Platform */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Platform</div>
              <div className="font-medium text-slate-900">
                {PLATFORMS.find((p) => p.id === selectedPlatform)?.name || selectedPlatform}
              </div>
            </div>

            {/* Treatments */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Treatments</div>
              <div className="flex flex-wrap gap-2">
                {selectedTreatments.map((t) => (
                  <span key={t} className="px-2.5 py-1 text-xs font-medium bg-emerald-50 text-emerald-700 rounded-full">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Budget */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Budget</div>
              <div className="font-medium text-slate-900">
                ₹{dailyBudget.toLocaleString("en-IN")}/day (₹{fmt(dailyBudget * 30)}/month)
              </div>
            </div>

            {/* Targeting */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Targeting</div>
              <div className="font-medium text-slate-900">
                {doctor?.city}, {doctor?.state} — {doctor?.geo_radius_km || 5}km radius
              </div>
            </div>

            {/* Keywords preview */}
            <div className="p-4">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Auto-generated Keywords ({keywords.length})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {keywords.slice(0, 8).map((kw) => (
                  <span key={kw} className="px-2 py-0.5 text-xs bg-slate-100 text-slate-600 rounded">
                    {kw}
                  </span>
                ))}
                {keywords.length > 8 && (
                  <span className="px-2 py-0.5 text-xs text-slate-400">
                    +{keywords.length - 8} more
                  </span>
                )}
              </div>
            </div>

            {/* Estimated results */}
            <div className="p-4 bg-emerald-50/50">
              <div className="text-xs font-medium text-emerald-600 uppercase tracking-wider mb-2">
                <Zap className="w-3 h-3 inline mr-1" />
                Estimated Monthly Results
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-slate-900">{fmt(estimatedClicks)}</div>
                  <div className="text-xs text-slate-500">Clicks</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-900">{estimatedEnquiries}</div>
                  <div className="text-xs text-slate-500">Enquiries</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-900">
                    ₹{estimatedEnquiries > 0 ? fmt(Math.round((dailyBudget * 30) / estimatedEnquiries)) : "—"}
                  </div>
                  <div className="text-xs text-slate-500">Per enquiry</div>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleLaunch}
            disabled={launching}
            className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-base transition-colors disabled:opacity-60 flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
          >
            {launching ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Launching...
              </>
            ) : (
              <>
                <Rocket className="w-5 h-5" />
                Launch Campaign
              </>
            )}
          </button>

          <p className="text-xs text-slate-400 text-center">
            Your campaign will be reviewed by {selectedPlatform === "GOOGLE" ? "Google" : "Meta"} and typically goes live within 24 hours.
            You can pause or edit it anytime from the Campaigns page.
          </p>
        </div>
      )}
    </div>
  );
}
