"use client";
import Link from "next/link";
import { useState, useEffect, useRef, useCallback } from "react";

/* PatientPlex AI v4.0 — Production-Ready SPA
   10 Breakthrough Features + Full Landing Engine
   Design: Slate-950, Teal #0EA5E9, Emerald #10B981, Indigo gradients */

// ══════════ DATA ══════════

const locations = [
  { id: "aus-n", name: "Austin North", type: "Dental", doc: "Dr. Pamnani" },
  { id: "dal-s", name: "Dallas South", type: "Derm", doc: "Dr. Smith" },
  { id: "hou-w", name: "Houston West", type: "Dental", doc: "Dr. Kapoor" },
];

const geoEngines = [
  { name: "ChatGPT", score: 88, trend: "+5", color: "#10B981" },
  { name: "Perplexity", score: 74, trend: "+12", color: "#0EA5E9" },
  { name: "Claude", score: 91, trend: "+3", color: "#8B5CF6" },
  { name: "Google AI", score: 69, trend: "+8", color: "#F59E0B" },
];

const ehrSystems = [
  { name: "Dentrix", status: "synced", records: "2,847" },
  { name: "Open Dental", status: "synced", records: "1,203" },
  { name: "Nextech", status: "pending", records: "--" },
  { name: "AthenaHealth", status: "synced", records: "4,102" },
];

const noShowPatients = [
  { name: "R. Mehta", time: "Tomorrow 2:30 PM", risk: 84, treatment: "Root Canal", action: "SMS Deposit Sent" },
  { name: "P. Sharma", time: "Tomorrow 4:00 PM", risk: 67, treatment: "Teeth Whitening", action: "Reminder Queued" },
  { name: "A. Reddy", time: "Wed 11:00 AM", risk: 42, treatment: "Cleaning", action: "Low Risk" },
];

const wastedSpend = [
  { placement: "Mobile Game: Candy Crush", type: "Display", saved: 142, status: "pruned" },
  { placement: "Search: dental assistant salary", type: "Search", saved: 89, status: "pruned" },
  { placement: "YouTube: kids dental cartoon", type: "Video", saved: 67, status: "pending" },
  { placement: "Search: dental college admission", type: "Search", saved: 114, status: "pruned" },
];

const competitors = [
  { name: "SmileCare Dental", action: "Raised Invisalign bids +12%", counter: "Auto-countered with negative keyword layer", time: "2h ago" },
  { name: "DermGlow Clinic", action: "New Botox campaign launched", counter: "Increased impression share to 78%", time: "5h ago" },
  { name: "City Dental Hub", action: "Bid on your brand keywords", counter: "Brand defense campaign activated", time: "1d ago" },
];

const ltvData = {
  dental: [
    { proc: "Invisalign", cac: 250, ltv: 6500, ratio: "26x", volume: 34 },
    { proc: "Implants", cac: 180, ltv: 4500, ratio: "25x", volume: 28 },
    { proc: "Veneers", cac: 320, ltv: 8200, ratio: "25.6x", volume: 12 },
    { proc: "Root Canal", cac: 90, ltv: 850, ratio: "9.4x", volume: 67 },
  ],
  derm: [
    { proc: "Botox", cac: 120, ltv: 3800, ratio: "31.7x", volume: 89 },
    { proc: "Laser Hair", cac: 85, ltv: 2400, ratio: "28.2x", volume: 142 },
    { proc: "CoolSculpting", cac: 280, ltv: 5500, ratio: "19.6x", volume: 18 },
    { proc: "Chemical Peel", cac: 60, ltv: 1200, ratio: "20x", volume: 56 },
  ],
};

const mcpCommands = [
  { cmd: 'patientplex.query("get_todays_cpa")', res: '{ "cpa": "$12.40", "leads": 47, "booked": 19 }' },
  { cmd: 'patientplex.query("top_keywords")', res: '{ "keywords": ["dental implants near me", "invisalign cost", "emergency dentist"] }' },
  { cmd: 'patientplex.action("pause_campaign", { id: "camp_042" })', res: '{ "status": "paused", "saved_budget": "$84.20" }' },
  { cmd: 'patientplex.query("no_show_risk", { date: "tomorrow" })', res: '{ "high_risk": 2, "patients": ["R. Mehta (84%)", "P. Sharma (67%)"] }' },
];

const launchSteps = [
  { label: "Select Service", options: ["Teeth Whitening", "Dental Implants", "Invisalign", "Laser Hair Removal", "Botox", "Acne Treatment"] },
  { label: "Set Budget", range: [500, 5000] },
  { label: "Choose Channels", options: ["Google Search", "Google Call-Only", "Meta Video", "Local Schema"] },
  { label: "Launch" },
];

const whatsappChat = [
  { from: "patient", text: "Hi, I saw your ad for dental implants. What is the cost?" },
  { from: "ai", text: "Hello! Thanks for reaching out to SmileCare Dental.\n\nDental implant costs range from $2,500 to $4,500 per tooth.\n\nWould you like to book a free consultation?" },
  { from: "patient", text: "Yes, do you have slots tomorrow?" },
  { from: "ai", text: "Let me check... Found 2 slots:\n\n2:30 PM - 3:00 PM\n4:00 PM - 4:30 PM\n\nTap to book:" },
  { from: "patient", text: "4 PM please" },
  { from: "ai", text: "Booked!\n\nTomorrow, 4:00 PM\nDr. Pamnani\nSmileCare Dental, Austin\n\nReminder sent 2 hours before." },
];

const faqs = [
  { q: "How does PatientPlex provision Google Ads automatically?", a: "5-minute onboarding generates optimized campaigns with high-intent keywords, geo-targeting, and AI-written ad copy specific to your specialty." },
  { q: "Is the WhatsApp integration Meta-compliant?", a: "Yes. Official WhatsApp Business Cloud API with pre-approved templates and end-to-end encryption." },
  { q: "How does the AI Brain learn?", a: "Our Conversion Neural Engine analyzes every interaction - ad performance, WhatsApp scripts, booking patterns - and auto-optimizes daily." },
  { q: "Is it HIPAA compliant?", a: "Yes. AES-256 encryption, SOC 2 infrastructure, signed BAA, PHI scrubbing before AI processing, and full audit trail." },
  { q: "What about GEO (AI Search Optimization)?", a: "We monitor how often LLMs like ChatGPT, Perplexity, and Claude recommend your practice and optimize your content to increase AI brand visibility." },
  { q: "Can it integrate with my EHR/PMS?", a: "Direct integrations with Dentrix, Open Dental, Nextech, AthenaHealth, and more. Real-time appointment sync and patient data flow." },
];

const compareRows = [
  ["Monthly Retainer", "$4K-8K/mo", "$0 (subscription only)"],
  ["Response Time", "2-12 Hours", "< 3 Seconds (24/7)"],
  ["AI Search (GEO)", "Not offered", "Full LLM optimization"],
  ["No-Show Prevention", "Manual calls", "AI prediction + auto-SMS"],
  ["Wasted Spend Detection", "Monthly review", "Real-time auto-pruning"],
  ["HIPAA Compliance", "Varies", "Built-in BAA + audit trail"],
  ["Competitor Monitoring", "Quarterly report", "Live counter-bidding"],
];

const brainNodes = [
  { label: "Ad Performance", metric: "CTR 4.8%", status: "optimizing" },
  { label: "WhatsApp Conv.", metric: "89.4%", status: "learning" },
  { label: "GEO Score", metric: "88/100", status: "optimizing" },
  { label: "No-Show Pred.", metric: "92% acc", status: "learning" },
  { label: "Cost Per Lead", metric: "$12.40", status: "improving" },
  { label: "LTV Prediction", metric: "$4,200", status: "stable" },
];

// ══════════ COMPONENT ══════════

export default function PatientPlexApp() {
  // State
  const [loc, setLoc] = useState(locations[0]);
  const [locOpen, setLocOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [chatIdx, setChatIdx] = useState(0);
  const [typing, setTyping] = useState(false);
  const [liveCount, setLiveCount] = useState(1847);
  const [dataPoints, setDataPoints] = useState(234891);
  const [brainPulse, setBrainPulse] = useState(0);
  const [geoScores, setGeoScores] = useState(geoEngines);
  const [ltvTab, setLtvTab] = useState<"dental"|"derm">("dental");
  const [mcpIdx, setMcpIdx] = useState(0);
  const [mcpTyping, setMcpTyping] = useState(false);
  const [mcpHistory, setMcpHistory] = useState<{cmd:string;res:string}[]>([]);
  const [launchStep, setLaunchStep] = useState(0);
  const [launchService, setLaunchService] = useState("");
  const [launchBudget, setLaunchBudget] = useState(1500);
  const [launchChannels, setLaunchChannels] = useState<string[]>([]);
  const [launched, setLaunched] = useState(false);
  const [spend, setSpend] = useState(2000);
  const [procVal, setProcVal] = useState(3500);
  const [annual, setAnnual] = useState(false);
  const [faqOpen, setFaqOpen] = useState<number|null>(null);
  const [modal, setModal] = useState(false);
  const [modalSent, setModalSent] = useState(false);
  const [wavePos, setWavePos] = useState(0);
  const [callPlaying, setCallPlaying] = useState(false);
  const [specTab, setSpecTab] = useState<"dental"|"derm">("dental");
  const [pruneActions, setPruneActions] = useState<Record<number,string>>({});
  const [hipaaExpanded, setHipaaExpanded] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Effects
  useEffect(() => {
    if (chatIdx >= whatsappChat.length) return;
    const isAi = whatsappChat[chatIdx]?.from === "ai";
    if (isAi) setTyping(true);
    const t = setTimeout(() => { setTyping(false); setChatIdx(c => c + 1); }, chatIdx === 0 ? 1200 : isAi ? 2200 : 1600);
    return () => clearTimeout(t);
  }, [chatIdx]);

  useEffect(() => {
    const t1 = setInterval(() => setLiveCount(c => c + 1), 12000);
    const t2 = setInterval(() => setBrainPulse(c => (c + 1) % brainNodes.length), 2500);
    const t3 = setInterval(() => setDataPoints(c => c + Math.floor(Math.random() * 5) + 1), 3000);
    return () => { clearInterval(t1); clearInterval(t2); clearInterval(t3); };
  }, []);

  // Voice AI waveform
  useEffect(() => {
    if (!callPlaying) return;
    const t = setInterval(() => setWavePos(c => c + 1), 80);
    return () => clearInterval(t);
  }, [callPlaying]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = "#0EA5E9";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.sin((x + wavePos * 3) * 0.05) * (callPlaying ? 20 + Math.sin(x * 0.02) * 15 : 2);
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    // Second wave
    ctx.strokeStyle = "#10B981";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.cos((x + wavePos * 2) * 0.04) * (callPlaying ? 15 + Math.cos(x * 0.03) * 10 : 1);
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
  }, [wavePos, callPlaying]);

  const inquiries = Math.round(spend / 42);
  const booked = Math.round(inquiries * 0.42);
  const revenue = booked * procVal;
  const roi = spend > 0 ? (revenue / spend).toFixed(1) : "0";
  const tierPrice = (b: number) => annual ? Math.round(b * 0.8) : b;

  const callTranscript = [
    { t: 0, speaker: "Patient", text: "Hi, I'd like to schedule a teeth whitening appointment." },
    { t: 8, speaker: "AI", text: "Of course! I have availability tomorrow at 2 PM or Thursday at 10 AM. Which works better?" },
    { t: 18, speaker: "Patient", text: "Thursday at 10 works." },
    { t: 24, speaker: "AI", text: "Perfect. Booked with Dr. Pamnani for Thursday 10 AM. You'll receive a confirmation text shortly." },
  ];

  const navTabs = [
    { id: "dashboard", label: "Dashboard" },
    { id: "geo", label: "GEO Tracker" },
    { id: "ehr", label: "EHR / No-Show" },
    { id: "pruner", label: "Spend Pruner" },
    { id: "competitors", label: "Competitors" },
    { id: "voice", label: "Voice AI" },
    { id: "ltv", label: "LTV Analyzer" },
    { id: "mcp", label: "MCP Console" },
    { id: "launcher", label: "Campaign Launch" },
    { id: "site", label: "Full Site" },
  ];

  // ══════════ RENDER ══════════
  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-teal-500/30 overflow-x-hidden">
      {/* Ambient */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-teal-500/[0.03] rounded-full blur-[200px]" />
        <div className="absolute bottom-1/4 right-0 w-[600px] h-[600px] bg-indigo-500/[0.03] rounded-full blur-[200px]" />
        <div className="absolute top-1/2 left-0 w-[400px] h-[400px] bg-emerald-500/[0.02] rounded-full blur-[150px]" />
      </div>

      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-2xl border-b border-slate-800/40">
        <div className="max-w-[1400px] mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-500/25">
                <span className="text-white font-black text-xs">P</span>
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-pulse" />
            </div>
            <span className="font-bold text-sm tracking-tight">PatientPlex<span className="text-teal-400 font-mono text-[10px] ml-0.5">AI</span></span>

            {/* Multi-Location Switcher */}
            <div className="relative ml-3">
              <button onClick={() => setLocOpen(!locOpen)} className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-[11px] hover:border-slate-700 transition">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-slate-300">{loc.name}</span>
                <span className="text-slate-600">|</span>
                <span className="text-teal-400">{loc.type}</span>
                <span className="text-slate-700 text-[10px]">&#9662;</span>
              </button>
              {locOpen && (
                <div className="absolute top-full left-0 mt-1 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl shadow-black/50 py-1 min-w-[220px] z-50">
                  {locations.map(l => (
                    <button key={l.id} onClick={() => { setLoc(l); setLocOpen(false); }} className={`w-full text-left px-4 py-2 text-xs hover:bg-slate-800 transition flex items-center justify-between ${loc.id === l.id ? "text-teal-400" : "text-slate-400"}`}>
                      <span>{l.name} - {l.type}</span>
                      <span className="text-slate-600">{l.doc}</span>
                    </button>
                  ))}
                  <div className="border-t border-slate-800 mt-1 pt-1 px-4 py-2">
                    <span className="text-[10px] text-teal-500 font-semibold">View Aggregated (All Locations)</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* HIPAA Badge */}
          <div className="hidden md:flex items-center gap-2">
            <button onClick={() => setHipaaExpanded(!hipaaExpanded)} className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full hover:bg-emerald-500/15 transition">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span className="text-emerald-400 text-[9px] font-bold tracking-wider">HIPAA</span>
              <span className="text-emerald-600 text-[9px]">BAA Active</span>
            </button>
            <span className="text-[9px] text-slate-700 font-mono">AES-256 | Log #9942</span>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/login" className="text-[11px] text-slate-500 hover:text-white transition hidden sm:block">Sign In</Link>
            <button onClick={() => setModal(true)} className="bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-semibold text-[11px] px-4 py-2 rounded-lg hover:shadow-lg hover:shadow-teal-500/25 transition-all">Start Free Trial</button>
          </div>
        </div>

        {/* HIPAA Expanded Panel */}
        {hipaaExpanded && (
          <div className="border-t border-slate-800/40 bg-slate-900/50 px-4 py-3">
            <div className="max-w-[1400px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "BAA Status", val: "Active & Signed", c: "text-emerald-400" },
                { label: "PHI Encryption", val: "AES-256 at rest, TLS 1.3 in transit", c: "text-teal-400" },
                { label: "AI Data Scrubbing", val: "PHI removed before LLM processing", c: "text-indigo-400" },
                { label: "Audit Trail", val: "Log #9942 | 14,203 events tracked", c: "text-amber-400" },
              ].map((h, i) => (
                <div key={i} className="bg-slate-950/50 rounded-lg p-3 border border-slate-800/30">
                  <p className="text-[9px] text-slate-600 uppercase tracking-wider mb-1">{h.label}</p>
                  <p className={`text-[11px] font-medium ${h.c}`}>{h.val}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </header>

      {/* ═══ TAB NAV ═══ */}
      <div className="sticky top-14 z-40 bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/30">
        <div className="max-w-[1400px] mx-auto px-4 flex gap-1 overflow-x-auto py-2 scrollbar-hide">
          {navTabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`whitespace-nowrap px-3 py-1.5 rounded-lg text-[11px] font-medium transition ${activeTab === tab.id ? "bg-teal-500/10 text-teal-400 border border-teal-500/20" : "text-slate-500 hover:text-slate-300 hover:bg-slate-900/50"}`}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="relative z-10 max-w-[1400px] mx-auto px-4 py-6">

        {/* ═══════════════════════════════════
            TAB: DASHBOARD
        ═══════════════════════════════════ */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Top stats */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">{loc.name} <span className="text-teal-400">{loc.type}</span></h1>
                <p className="text-xs text-slate-600">{loc.doc} | {dataPoints.toLocaleString()} data points processed</p>
              </div>
              <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-emerald-400 text-xs font-mono">{liveCount.toLocaleString()} booked this month</span>
              </div>
            </div>

            {/* Metric cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Monthly ROAS", val: "4.2x", sub: "+0.3x this week", c: "text-emerald-400" },
                { label: "Cost / Booking", val: "$12.40", sub: "Industry: $48", c: "text-teal-400" },
                { label: "WhatsApp Conv.", val: "89.4%", sub: "AI learning: active", c: "text-emerald-400" },
                { label: "GEO AI Score", val: "88/100", sub: "Top 5% visibility", c: "text-indigo-400" },
                { label: "No-Show Rate", val: "4.2%", sub: "Industry avg: 18%", c: "text-teal-400" },
                { label: "LTV / CAC Ratio", val: "26x", sub: "Dental Implants lead", c: "text-emerald-400" },
                { label: "Wasted Spend Saved", val: "$412/mo", sub: "Auto-pruned", c: "text-amber-400" },
                { label: "Competitor Wins", val: "14/18", sub: "78% impression share", c: "text-indigo-400" },
              ].map((m, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-4 hover:border-teal-500/20 transition">
                  <p className="text-[9px] text-slate-600 uppercase tracking-wider mb-1">{m.label}</p>
                  <p className={`text-xl font-bold font-mono ${m.c}`}>{m.val}</p>
                  <p className="text-[9px] text-slate-700 mt-0.5">{m.sub}</p>
                </div>
              ))}
            </div>

            {/* AI Brain */}
            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                  <h3 className="text-sm font-bold">Conversion Neural Engine</h3>
                </div>
                <span className="text-[9px] text-indigo-400 font-mono">6 models active</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                {brainNodes.map((n, i) => (
                  <div key={i} className={`rounded-xl p-3 border transition-all duration-700 ${brainPulse === i ? "border-indigo-500/40 bg-indigo-500/5 shadow-lg shadow-indigo-500/10" : "border-slate-800/40 bg-slate-950/50"}`}>
                    <span className={`text-[8px] font-bold uppercase tracking-wider ${n.status === "optimizing" ? "text-emerald-400" : n.status === "learning" ? "text-indigo-400" : n.status === "improving" ? "text-teal-400" : "text-slate-600"}`}>{n.status}</span>
                    <p className="text-[10px] text-slate-400 mt-1">{n.label}</p>
                    <p className={`text-sm font-bold font-mono ${brainPulse === i ? "text-white" : "text-slate-500"}`}>{n.metric}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Patient Queue */}
            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold">Real-Time Patient Queue</h3>
                <span className="text-[9px] text-emerald-500 font-mono animate-pulse">streaming...</span>
              </div>
              <div className="space-y-1.5">
                {[
                  { init: "P", treatment: "Laser Hair Removal", doc: "Dr. Priya Sharma, Mumbai", price: "$125", time: "Just now", color: "#a855f7" },
                  { init: "R", treatment: "Root Canal & Crown", doc: "Dr. Rajesh Mehta, Delhi", price: "$85", time: "2m ago", color: "#3b82f6" },
                  { init: "A", treatment: "Acne Scar Treatment", doc: "Dr. Ananya Reddy, Bengaluru", price: "$160", time: "5m ago", color: "#10b981" },
                ].map((p, i) => (
                  <div key={i} className={`flex items-center justify-between bg-slate-950/60 rounded-xl px-3 py-2.5 border border-slate-800/30 hover:border-slate-700/50 transition ${i === 0 ? "animate-pulse" : ""}`} style={i === 0 ? { animationDuration: "3s" } : {}}>
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold" style={{ backgroundColor: p.color + "25", color: p.color }}>{p.init}</div>
                      <div><p className="text-xs font-medium">{p.treatment}</p><p className="text-[9px] text-slate-700">{p.doc}</p></div>
                    </div>
                    <div className="text-right"><p className="text-xs font-semibold text-emerald-400">{p.price}</p><p className="text-[9px] text-slate-800">{p.time}</p></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: GEO TRACKER
        ═══════════════════════════════════ */}
        {activeTab === "geo" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold mb-1">GEO <span className="text-teal-400">(Generative Engine Optimization)</span></h2>
              <p className="text-xs text-slate-500">Track how often AI assistants recommend your practice</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {geoScores.map((e, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5 text-center hover:border-teal-500/20 transition">
                  <p className="text-xs text-slate-500 mb-2">{e.name}</p>
                  <div className="relative w-20 h-20 mx-auto mb-3">
                    <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                      <circle cx="40" cy="40" r="34" stroke="#1e293b" strokeWidth="6" fill="none" />
                      <circle cx="40" cy="40" r="34" stroke={e.color} strokeWidth="6" fill="none" strokeDasharray={`${e.score * 2.14} 214`} strokeLinecap="round" />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-lg font-bold font-mono">{e.score}</span>
                  </div>
                  <span className="text-emerald-400 text-xs font-mono">{e.trend} this week</span>
                </div>
              ))}
            </div>

            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-bold mb-3">AI Optimization Suggestions</h3>
              <div className="space-y-2">
                {[
                  { priority: "High", suggestion: "Add structured FAQ schema for 'best dentist near me' queries", impact: "+8 pts on ChatGPT" },
                  { priority: "Med", suggestion: "Create treatment-specific landing pages with medical schema markup", impact: "+5 pts on Google AI" },
                  { priority: "High", suggestion: "Publish 3 authoritative blog posts on Invisalign process", impact: "+12 pts on Perplexity" },
                  { priority: "Low", suggestion: "Update Google Business Profile with latest reviews and photos", impact: "+3 pts all engines" },
                ].map((s, i) => (
                  <div key={i} className="flex items-start gap-3 bg-slate-950/50 rounded-lg p-3 border border-slate-800/30">
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${s.priority === "High" ? "bg-red-500/10 text-red-400" : s.priority === "Med" ? "bg-amber-500/10 text-amber-400" : "bg-slate-800 text-slate-500"}`}>{s.priority}</span>
                    <div className="flex-1">
                      <p className="text-xs text-slate-300">{s.suggestion}</p>
                      <p className="text-[10px] text-teal-500 mt-0.5">{s.impact}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: EHR / NO-SHOW
        ═══════════════════════════════════ */}
        {activeTab === "ehr" && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">EHR Integration & <span className="text-teal-400">No-Show Predictor</span></h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {ehrSystems.map((e, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-4 hover:border-teal-500/20 transition">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-semibold">{e.name}</p>
                    <span className={`w-2 h-2 rounded-full ${e.status === "synced" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
                  </div>
                  <p className={`text-[10px] ${e.status === "synced" ? "text-emerald-400" : "text-amber-400"}`}>{e.status === "synced" ? "Active Sync" : "Setup Pending"}</p>
                  <p className="text-lg font-bold font-mono mt-1">{e.records}</p>
                  <p className="text-[9px] text-slate-700">records synced</p>
                </div>
              ))}
            </div>

            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />AI No-Show Predictor</h3>
                <span className="text-[9px] text-slate-600 font-mono">Model accuracy: 92%</span>
              </div>
              <div className="space-y-2">
                {noShowPatients.map((p, i) => (
                  <div key={i} className="flex items-center justify-between bg-slate-950/50 rounded-xl p-4 border border-slate-800/30">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm ${p.risk > 70 ? "bg-red-500/10 text-red-400" : p.risk > 50 ? "bg-amber-500/10 text-amber-400" : "bg-emerald-500/10 text-emerald-400"}`}>{p.risk}%</div>
                      <div>
                        <p className="text-sm font-medium">{p.name}</p>
                        <p className="text-[10px] text-slate-600">{p.treatment} - {p.time}</p>
                      </div>
                    </div>
                    <span className={`text-[10px] font-semibold px-3 py-1 rounded-full ${p.risk > 70 ? "bg-red-500/10 text-red-400 border border-red-500/20" : p.risk > 50 ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"}`}>{p.action}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: WASTED SPEND PRUNER
        ═══════════════════════════════════ */}
        {activeTab === "pruner" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">Wasted Spend <span className="text-amber-400">Pruner</span></h2>
                <p className="text-xs text-slate-500">AI auto-detects and pauses junk ad placements</p>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-2 text-center">
                <p className="text-lg font-bold text-emerald-400 font-mono">${wastedSpend.reduce((a, w) => a + w.saved, 0)}/mo</p>
                <p className="text-[9px] text-emerald-600">Total Saved</p>
              </div>
            </div>

            <div className="space-y-2">
              {wastedSpend.map((w, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold ${w.status === "pruned" ? "bg-red-500/10 text-red-400" : "bg-amber-500/10 text-amber-400"}`}>{w.status === "pruned" ? "X" : "?"}</div>
                    <div>
                      <p className="text-sm font-medium">{w.placement}</p>
                      <p className="text-[10px] text-slate-600">{w.type} Placement | ${w.saved}/mo wasted</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {pruneActions[i] ? (
                      <span className={`text-[10px] font-semibold px-3 py-1.5 rounded-lg ${pruneActions[i] === "approved" ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-500"}`}>{pruneActions[i] === "approved" ? "Approved" : "Declined"}</span>
                    ) : w.status === "pending" ? (
                      <>
                        <button onClick={() => setPruneActions(p => ({...p, [i]: "approved"}))} className="text-[10px] font-semibold px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition">Approve</button>
                        <button onClick={() => setPruneActions(p => ({...p, [i]: "declined"}))} className="text-[10px] font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-500 hover:bg-slate-700 transition">Decline</button>
                      </>
                    ) : (
                      <span className="text-[10px] text-emerald-400 font-semibold px-3 py-1.5 rounded-lg bg-emerald-500/10">Auto-Pruned</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: COMPETITORS
        ═══════════════════════════════════ */}
        {activeTab === "competitors" && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">Competitor <span className="text-indigo-400">Conquesting Monitor</span></h2>
            <div className="space-y-3">
              {competitors.map((c, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400 text-xs font-bold">{c.name[0]}</div>
                      <div><p className="text-sm font-bold">{c.name}</p><p className="text-[10px] text-slate-600">{c.time}</p></div>
                    </div>
                    <span className="text-[9px] text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full">Competitor Move</span>
                  </div>
                  <div className="grid md:grid-cols-2 gap-3">
                    <div className="bg-red-500/5 border border-red-500/10 rounded-lg p-3">
                      <p className="text-[9px] text-red-400 uppercase tracking-wider mb-1">Their Action</p>
                      <p className="text-xs text-slate-300">{c.action}</p>
                    </div>
                    <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-lg p-3">
                      <p className="text-[9px] text-emerald-400 uppercase tracking-wider mb-1">AI Counter-Response</p>
                      <p className="text-xs text-slate-300">{c.counter}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: VOICE AI
        ═══════════════════════════════════ */}
        {activeTab === "voice" && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">Voice AI <span className="text-teal-400">Call Handler</span></h2>

            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-xs text-slate-400">Inbound Call Simulation — AI Receptionist</p>
                <button onClick={() => setCallPlaying(!callPlaying)} className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${callPlaying ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-teal-500/10 text-teal-400 border border-teal-500/20"}`}>
                  {callPlaying ? "Stop" : "Play Demo Call"}
                </button>
              </div>

              <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800/30 mb-4">
                <canvas ref={canvasRef} width={800} height={80} className="w-full h-20" />
              </div>

              <div className="space-y-2">
                {callTranscript.map((line, i) => (
                  <div key={i} className={`flex gap-3 transition-all duration-500 ${callPlaying && wavePos > line.t * 12 ? "opacity-100" : callPlaying ? "opacity-20" : "opacity-100"}`}>
                    <span className={`text-[10px] font-bold w-16 shrink-0 ${line.speaker === "AI" ? "text-teal-400" : "text-slate-400"}`}>{line.speaker}</span>
                    <p className="text-xs text-slate-300">{line.text}</p>
                  </div>
                ))}
              </div>

              {callPlaying && wavePos > 300 && (
                <div className="mt-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-center">
                  <p className="text-emerald-400 text-sm font-bold">Appointment Auto-Created in EHR</p>
                  <p className="text-xs text-slate-400">Thursday 10:00 AM - Teeth Whitening - Dr. Pamnani</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: LTV ANALYZER
        ═══════════════════════════════════ */}
        {activeTab === "ltv" && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">Patient LTV <span className="text-emerald-400">Analyzer</span></h2>

            <div className="flex gap-2 mb-4">
              {(["dental","derm"] as const).map(t => (
                <button key={t} onClick={() => setLtvTab(t)} className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${ltvTab === t ? "bg-teal-500/10 text-teal-400 border border-teal-500/20" : "text-slate-500 border border-slate-800"}`}>
                  {t === "dental" ? "Dental" : "Dermatology"}
                </button>
              ))}
            </div>

            <div className="space-y-2">
              {ltvData[ltvTab].map((p, i) => (
                <div key={i} className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-bold">{p.proc}</p>
                    <span className="text-emerald-400 text-sm font-bold font-mono">{p.ratio} ROI</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div><p className="text-[9px] text-slate-600 uppercase">CAC</p><p className="text-sm font-mono text-red-400">${p.cac}</p></div>
                    <div><p className="text-[9px] text-slate-600 uppercase">LTV</p><p className="text-sm font-mono text-emerald-400">${p.ltv.toLocaleString()}</p></div>
                    <div><p className="text-[9px] text-slate-600 uppercase">Volume/mo</p><p className="text-sm font-mono text-teal-400">{p.volume}</p></div>
                  </div>
                  <div className="mt-3 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-teal-500 to-emerald-500 rounded-full" style={{ width: `${Math.min((p.ltv / 8200) * 100, 100)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: MCP CONSOLE
        ═══════════════════════════════════ */}
        {activeTab === "mcp" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">MCP <span className="text-indigo-400">Developer Console</span></h2>
              <p className="text-xs text-slate-500">Connect PatientPlex to Claude or custom workflows via Model Context Protocol</p>
            </div>

            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800/40 bg-slate-950/50">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                </div>
                <span className="text-[10px] text-slate-600 font-mono">patientplex-mcp-server v2.1</span>
              </div>

              <div className="p-4 font-mono text-xs min-h-[300px] space-y-3">
                <div className="text-slate-600">{"// PatientPlex MCP Server — Connect your clinic's AI brain to any workflow"}</div>
                <div className="text-slate-600">{"// Endpoint: mcp://patientplex.ai/{loc.id}/v2"}</div>
                <div className="text-slate-600">{"// ---"}</div>

                {mcpHistory.map((h, i) => (
                  <div key={i}>
                    <div className="text-teal-400"><span className="text-slate-600">$</span> {h.cmd}</div>
                    <div className="text-emerald-400 pl-4 mt-1">{h.res}</div>
                  </div>
                ))}

                {mcpTyping && <div className="text-teal-400 animate-pulse"><span className="text-slate-600">$</span> {mcpCommands[mcpIdx]?.cmd}<span className="animate-ping">_</span></div>}

                <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800/30">
                  <span className="text-slate-600">$</span>
                  <span className="text-teal-400 flex-1">Try a command:</span>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {mcpCommands.map((c, i) => (
                    <button key={i} onClick={() => {
                      setMcpTyping(true);
                      setMcpIdx(i);
                      setTimeout(() => {
                        setMcpTyping(false);
                        setMcpHistory(h => [...h, { cmd: c.cmd, res: c.res }]);
                      }, 1500);
                    }} className="text-[10px] text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 rounded-lg hover:bg-indigo-500/20 transition">
                      {c.cmd.split("(")[0]}()
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: CAMPAIGN LAUNCHER
        ═══════════════════════════════════ */}
        {activeTab === "launcher" && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">60-Second <span className="text-teal-400">Campaign Launcher</span></h2>

            {/* Progress */}
            <div className="flex items-center gap-1 mb-6">
              {launchSteps.map((s, i) => (
                <div key={i} className="flex-1 flex items-center gap-1">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border transition ${i <= launchStep ? "bg-teal-500/20 border-teal-500 text-teal-400" : "border-slate-800 text-slate-700"}`}>{i + 1}</div>
                  {i < launchSteps.length - 1 && <div className={`flex-1 h-0.5 ${i < launchStep ? "bg-teal-500" : "bg-slate-800"}`} />}
                </div>
              ))}
            </div>

            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-6">
              {!launched ? (
                <>
                  {launchStep === 0 && (
                    <div>
                      <h3 className="text-sm font-bold mb-4">Select Service to Promote</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {launchSteps[0].options?.map(opt => (
                          <button key={opt} onClick={() => { setLaunchService(opt); setLaunchStep(1); }} className={`p-3 rounded-xl text-xs font-medium border transition ${launchService === opt ? "border-teal-500 bg-teal-500/10 text-teal-400" : "border-slate-800 text-slate-400 hover:border-slate-700"}`}>{opt}</button>
                        ))}
                      </div>
                    </div>
                  )}
                  {launchStep === 1 && (
                    <div>
                      <h3 className="text-sm font-bold mb-4">Set Monthly Budget for &ldquo;{launchService}&rdquo;</h3>
                      <div className="flex justify-between text-sm mb-2"><span className="text-slate-400">Budget</span><span className="text-teal-400 font-bold font-mono">${launchBudget.toLocaleString()}/mo</span></div>
                      <input type="range" min={500} max={5000} step={100} value={launchBudget} onChange={e => setLaunchBudget(+e.target.value)} className="w-full accent-teal-500 h-2 rounded-full mb-4" />
                      <button onClick={() => setLaunchStep(2)} className="bg-teal-500/10 text-teal-400 border border-teal-500/20 px-6 py-2 rounded-xl text-xs font-semibold hover:bg-teal-500/20 transition">Next &rarr;</button>
                    </div>
                  )}
                  {launchStep === 2 && (
                    <div>
                      <h3 className="text-sm font-bold mb-4">Choose Ad Channels</h3>
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        {launchSteps[2].options?.map(ch => (
                          <button key={ch} onClick={() => setLaunchChannels(c => c.includes(ch) ? c.filter(x => x !== ch) : [...c, ch])} className={`p-3 rounded-xl text-xs font-medium border transition ${launchChannels.includes(ch) ? "border-teal-500 bg-teal-500/10 text-teal-400" : "border-slate-800 text-slate-400 hover:border-slate-700"}`}>
                            {launchChannels.includes(ch) && <span className="mr-1">&#10003;</span>}{ch}
                          </button>
                        ))}
                      </div>
                      <button onClick={() => setLaunchStep(3)} className="bg-teal-500/10 text-teal-400 border border-teal-500/20 px-6 py-2 rounded-xl text-xs font-semibold hover:bg-teal-500/20 transition">Next &rarr;</button>
                    </div>
                  )}
                  {launchStep === 3 && (
                    <div className="text-center">
                      <h3 className="text-sm font-bold mb-2">Ready to Launch</h3>
                      <p className="text-xs text-slate-500 mb-1">{launchService} | ${launchBudget}/mo | {launchChannels.join(", ")}</p>
                      <p className="text-xs text-slate-600 mb-6">AI will generate ad copy, keywords, and targeting automatically</p>
                      <button onClick={() => setLaunched(true)} className="bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold px-8 py-3 rounded-xl text-sm shadow-xl shadow-teal-500/25 hover:shadow-teal-500/40 transition-all">Launch Campaign</button>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-6">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4">&#10003;</div>
                  <h3 className="text-lg font-bold text-emerald-400 mb-2">Campaign Launched!</h3>
                  <p className="text-xs text-slate-400 mb-4">4 channels activated for &ldquo;{launchService}&rdquo;</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-w-2xl mx-auto">
                    {["Google Search Ad", "Call-Only Ad", "Meta Video Hook", "Local Schema JSON-LD"].map((ch, i) => (
                      <div key={i} className="bg-slate-950/50 border border-emerald-500/10 rounded-lg p-3">
                        <p className="text-[9px] text-emerald-400 font-semibold">{ch}</p>
                        <p className="text-[10px] text-slate-600 mt-1">Generated & Live</p>
                      </div>
                    ))}
                  </div>
                  <button onClick={() => { setLaunched(false); setLaunchStep(0); setLaunchService(""); setLaunchChannels([]); }} className="mt-4 text-xs text-teal-400 hover:text-teal-300 transition">Launch Another &rarr;</button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════
            TAB: FULL SITE (Landing Page)
        ═══════════════════════════════════ */}
        {activeTab === "site" && (
          <div className="space-y-16">
            {/* Hero */}
            <section className="grid lg:grid-cols-2 gap-12 items-start pt-8">
              <div>
                <div className="inline-flex items-center gap-2 bg-slate-900/60 border border-slate-800 rounded-full px-4 py-1.5 mb-6">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-teal-400 text-xs font-semibold">#1 AI Patient Acquisition Engine</span>
                </div>
                <h1 className="text-4xl lg:text-5xl font-extrabold leading-[1.08] tracking-tight mb-6">
                  Your Practice&apos;s<br /><span className="bg-gradient-to-r from-teal-400 via-emerald-400 to-indigo-400 bg-clip-text text-transparent">Autonomous AI Brain.</span>
                </h1>
                <p className="text-slate-400 leading-relaxed mb-8 max-w-xl">PatientPlex AI runs your Google Ads, answers patient calls, triages WhatsApp 24/7, predicts no-shows, and optimizes for AI search — all while getting smarter every day.</p>
                <div className="flex flex-wrap gap-3 mb-8">
                  <button onClick={() => setModal(true)} className="group bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold px-8 py-4 rounded-2xl hover:shadow-2xl hover:shadow-teal-500/30 transition-all inline-flex items-center gap-2">
                    Start 14-Day Free Trial <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
                  </button>
                  <button onClick={() => setActiveTab("voice")} className="border border-slate-800 hover:border-slate-700 px-6 py-4 rounded-2xl hover:bg-slate-900/50 inline-flex items-center gap-2 text-slate-400 hover:text-white transition">
                    <span className="text-teal-400">&#9654;</span> Hear Voice AI Demo
                  </button>
                </div>
                <div className="grid grid-cols-4 gap-4">
                  {[{ v: "4.2x", l: "Avg ROAS" },{ v: "88", l: "GEO Score" },{ v: "< 3s", l: "AI Response" },{ v: "92%", l: "No-Show Acc" }].map((s,i) => (
                    <div key={i} className="text-center"><p className="text-xl font-bold bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent">{s.v}</p><p className="text-[9px] text-slate-700 mt-1 uppercase tracking-wide">{s.l}</p></div>
                  ))}
                </div>
              </div>
              <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-800/40 flex items-center justify-between">
                  <span className="text-xs font-semibold">Live Command Dashboard</span>
                  <span className="flex items-center gap-1.5 bg-emerald-500/10 px-2 py-0.5 rounded-full"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /><span className="text-emerald-400 text-[10px]">Live</span></span>
                </div>
                <div className="p-3 grid grid-cols-2 gap-2">
                  {[{ l: "ROAS", v: "4.2x", c: "text-emerald-400" },{ l: "Cost/Booking", v: "$12.40", c: "text-teal-400" },{ l: "WhatsApp Rate", v: "89.4%", c: "text-emerald-400" },{ l: "Booked", v: String(liveCount), c: "text-white" }].map((m,i) => (
                    <div key={i} className="bg-slate-950/60 rounded-xl p-3 border border-slate-800/30">
                      <p className="text-[9px] text-slate-700 uppercase tracking-wider">{m.l}</p>
                      <p className={`text-lg font-bold ${m.c}`}>{m.v}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* WhatsApp Demo */}
            <section>
              <div className="text-center mb-8">
                <p className="text-teal-400 text-xs font-semibold tracking-[3px] uppercase mb-2">Live Demo</p>
                <h2 className="text-3xl font-bold">AI Receptionist in Action</h2>
              </div>
              <div className="max-w-md mx-auto bg-slate-900 border border-slate-800 rounded-[1.8rem] overflow-hidden">
                <div className="bg-gradient-to-r from-[#075e54] to-[#128C7E] px-4 py-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-xs font-bold">SC</div>
                  <div><p className="text-sm font-semibold text-white">SmileCare Dental</p><p className="text-[10px] text-emerald-200">AI Receptionist &bull; Online</p></div>
                </div>
                <div className="p-3 min-h-[320px] bg-slate-950/80 space-y-2">
                  {whatsappChat.slice(0, chatIdx).map((m, i) => (
                    <div key={i} className={`flex ${m.from === "patient" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[82%] rounded-2xl px-3 py-2 text-[12px] whitespace-pre-line leading-relaxed ${m.from === "patient" ? "bg-teal-600 text-white rounded-br-sm" : "bg-slate-800 text-slate-200 rounded-bl-sm"}`}>{m.text}</div>
                    </div>
                  ))}
                  {typing && <div className="flex justify-start"><div className="bg-slate-800 rounded-2xl rounded-bl-sm px-4 py-3"><div className="flex gap-1"><span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" /><span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{animationDelay:"0.15s"}} /><span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{animationDelay:"0.3s"}} /></div></div></div>}
                </div>
              </div>
            </section>

            {/* ROI Calculator */}
            <section>
              <div className="text-center mb-8">
                <p className="text-teal-400 text-xs font-semibold tracking-[3px] uppercase mb-2">ROI Calculator</p>
                <h2 className="text-3xl font-bold">See Your Returns</h2>
              </div>
              <div className="max-w-2xl mx-auto bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <div className="space-y-5 mb-6">
                  <div>
                    <div className="flex justify-between text-sm mb-2"><span className="text-slate-400">Monthly Ad Spend</span><span className="text-teal-400 font-bold font-mono">${spend.toLocaleString()}</span></div>
                    <input type="range" min={500} max={10000} step={100} value={spend} onChange={e => setSpend(+e.target.value)} className="w-full accent-teal-500 h-1.5" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2"><span className="text-slate-400">Avg Procedure Value</span><span className="text-indigo-400 font-bold font-mono">${procVal.toLocaleString()}</span></div>
                    <input type="range" min={200} max={8000} step={100} value={procVal} onChange={e => setProcVal(+e.target.value)} className="w-full accent-indigo-500 h-1.5" />
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {[{ v: String(inquiries), l: "Inquiries", c: "text-white" },{ v: String(booked), l: "Booked (42%)", c: "text-emerald-400" },{ v: `$${revenue.toLocaleString()}`, l: "Revenue", c: "text-emerald-400" },{ v: `${roi}x`, l: "ROI", c: "text-indigo-400" }].map((r,i) => (
                    <div key={i} className="bg-slate-950/80 rounded-xl p-3 border border-slate-800/30 text-center">
                      <p className={`text-xl font-bold font-mono ${r.c}`}>{r.v}</p><p className="text-[9px] text-slate-700 mt-1">{r.l}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Comparison Table */}
            <section>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold">Agency vs. <span className="text-teal-400">PatientPlex AI</span></h2>
              </div>
              <div className="max-w-3xl mx-auto overflow-hidden rounded-2xl border border-slate-800">
                <table className="w-full text-sm">
                  <thead><tr className="bg-slate-900"><th className="text-left px-5 py-3 text-slate-600 text-xs">Feature</th><th className="text-left px-5 py-3 text-red-400/60 text-xs">Agency</th><th className="text-left px-5 py-3 text-emerald-400 text-xs">PatientPlex</th></tr></thead>
                  <tbody>{compareRows.map(([f,a,p],i) => (<tr key={i} className={`${i%2===0?"bg-slate-950/50":"bg-slate-900/30"} border-t border-slate-800/20`}><td className="px-5 py-3 text-slate-300 text-xs">{f}</td><td className="px-5 py-3 text-slate-600 text-xs">{a}</td><td className="px-5 py-3 text-emerald-400 text-xs font-semibold">{p}</td></tr>))}</tbody>
                </table>
              </div>
            </section>

            {/* Pricing */}
            <section>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold mb-4">Pricing</h2>
                <div className="inline-flex bg-slate-900/50 border border-slate-800 rounded-full p-1">
                  <button onClick={() => setAnnual(false)} className={`px-4 py-1.5 rounded-full text-xs font-semibold transition ${!annual?"bg-teal-500 text-black":"text-slate-500"}`}>Monthly</button>
                  <button onClick={() => setAnnual(true)} className={`px-4 py-1.5 rounded-full text-xs font-semibold transition ${annual?"bg-teal-500 text-black":"text-slate-500"}`}>Annual -20%</button>
                </div>
              </div>
              <div className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto">
                {[
                  { name: "Starter", price: tierPrice(299), features: ["100 AI conversations","2 campaigns","WhatsApp AI","Basic tracking"], pop: false },
                  { name: "Pro Engine", price: tierPrice(599), features: ["Unlimited convos","10 campaigns","GEO Tracker","No-Show AI","Voice AI","Full dashboard"], pop: true },
                  { name: "Network", price: tierPrice(1199), features: ["Everything in Pro","Multi-location","White-label","API + MCP","Dedicated manager"], pop: false },
                ].map((p,i) => (
                  <div key={i} className={`rounded-2xl p-6 relative ${p.pop?"bg-gradient-to-b from-teal-500/[0.07] to-transparent border-2 border-teal-500/30":"bg-slate-900/40 border border-slate-800"}`}>
                    {p.pop && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-teal-500 to-emerald-500 text-black text-[10px] font-bold px-3 py-0.5 rounded-full">Most Popular</div>}
                    <p className="text-xs text-slate-500 mb-1">{p.name}</p>
                    <p className="text-3xl font-bold font-mono">${p.price}</p>
                    <p className="text-[10px] text-slate-700 mb-5">/{annual?"mo (annual)":"month"}</p>
                    <ul className="space-y-2 mb-6">{p.features.map((f,j) => <li key={j} className="text-xs text-slate-400 flex items-start gap-2"><span className="text-emerald-400 mt-0.5">&#10003;</span>{f}</li>)}</ul>
                    <button onClick={() => setModal(true)} className={`w-full py-3 rounded-xl text-sm font-semibold transition ${p.pop?"bg-gradient-to-r from-teal-500 to-emerald-500 text-white shadow-lg shadow-teal-500/20":"bg-slate-900/50 hover:bg-slate-800/50 text-white border border-slate-800"}`}>{p.pop?"Start Free Trial":"Choose Plan"}</button>
                  </div>
                ))}
              </div>
            </section>

            {/* FAQ */}
            <section className="max-w-3xl mx-auto">
              <div className="text-center mb-8"><h2 className="text-3xl font-bold">FAQ</h2></div>
              {faqs.map((f,i) => (
                <div key={i} className="border-b border-slate-800/30">
                  <button onClick={() => setFaqOpen(faqOpen===i?null:i)} className="w-full text-left py-4 flex justify-between items-center hover:text-teal-400 transition">
                    <span className="text-sm font-medium">{f.q}</span>
                    <span className={`text-slate-600 transition-transform ${faqOpen===i?"rotate-45":""}`}>+</span>
                  </button>
                  <div className={`overflow-hidden transition-all duration-300 ${faqOpen===i?"max-h-40 pb-4":"max-h-0"}`}><p className="text-slate-500 text-sm">{f.a}</p></div>
                </div>
              ))}
            </section>

            {/* CTA */}
            <section className="text-center py-12">
              <h2 className="text-4xl font-bold mb-4">Every Missed Call Is a <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">Patient Lost.</span></h2>
              <p className="text-slate-500 mb-8">Your AI brain is ready. It starts learning from day one.</p>
              <button onClick={() => setModal(true)} className="group bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold px-10 py-4 rounded-2xl text-lg shadow-2xl shadow-teal-500/25 hover:shadow-teal-500/40 transition-all inline-flex items-center gap-2">
                Start Free — No Credit Card <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </button>
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/30 py-8 px-4">
        <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2"><div className="w-6 h-6 rounded-md bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center text-white text-[10px] font-bold">P</div><span className="font-semibold text-sm">PatientPlex AI</span><span className="text-[9px] text-slate-800 font-mono">v4.0</span></div>
          <p className="text-slate-700 text-xs">HIPAA Compliant | Self-Learning AI for Healthcare</p>
          <p className="text-slate-800 text-[10px]">&copy; 2026 PatientPlex AI. All rights reserved.</p>
        </div>
      </footer>

      {/* Trial Modal */}
      {modal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => { setModal(false); setModalSent(false); }} />
          <div className="relative bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl">
            <button onClick={() => { setModal(false); setModalSent(false); }} className="absolute top-4 right-4 text-slate-600 hover:text-white transition">&times;</button>
            {!modalSent ? (
              <>
                <h3 className="text-xl font-bold mb-1">Start Your 14-Day Free Trial</h3>
                <p className="text-sm text-slate-500 mb-6">No credit card required. AI brain activates immediately.</p>
                <form onSubmit={e => { e.preventDefault(); setModalSent(true); }} className="space-y-3">
                  <input required placeholder="Practice Name" className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-teal-500 outline-none" />
                  <input required placeholder="Doctor Name" className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-teal-500 outline-none" />
                  <select required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-400 focus:border-teal-500 outline-none">
                    <option value="">Select Specialty</option>
                    <option>Dental & Orthodontics</option>
                    <option>Dermatology & Cosmetology</option>
                    <option>Ophthalmology (LASIK)</option>
                    <option>Plastic Surgery</option>
                    <option>ENT</option>
                    <option>Orthopedics</option>
                    <option>Gynecology</option>
                    <option>Other</option>
                  </select>
                  <input required type="tel" placeholder="Phone Number" className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-teal-500 outline-none" />
                  <button type="submit" className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold py-3 rounded-xl text-sm shadow-lg shadow-teal-500/20 mt-2">Activate AI Brain &rarr;</button>
                </form>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4">&#10003;</div>
                <h3 className="text-xl font-bold mb-2 text-emerald-400">You&apos;re In!</h3>
                <p className="text-sm text-slate-400 mb-6">Your AI brain is initializing. Check your phone for setup instructions.</p>
                <Link href="/signup" className="bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold px-8 py-3 rounded-xl text-sm inline-block">Go to Dashboard</Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
