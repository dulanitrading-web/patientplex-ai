"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";

/* ═══════════════════════════════════════════════════
   PatientPlex AI v3.0 — World-Class Landing Page
   Design: Deep Slate #070a12, Emerald #10B981, Violet #8B5CF6
   Style:  Stripe / Linear / Vercel-tier glassmorphism SaaS
   ═══════════════════════════════════════════════════ */

// ── Data ──────────────────────────────────────────

const whatsappChat = [
  { from: "patient", text: "Hi, I saw your ad for dental implants. What's the cost?" },
  { from: "ai", text: "Hello! Thanks for reaching out to SmileCare Dental.\n\nDental implant costs range from Rs.25,000 to Rs.45,000 per tooth depending on type.\n\nWould you like to book a free consultation?" },
  { from: "patient", text: "Yes, do you have slots tomorrow afternoon?" },
  { from: "ai", text: "Let me check the calendar... Found 2 slots:\n\n2:30 PM - 3:00 PM\n4:00 PM - 4:30 PM\n\nTap a time to book instantly:" },
  { from: "patient", text: "4 PM please" },
  { from: "ai", text: "Booked!\n\nTomorrow, 4:00 PM\nDr. Sharma\nSmileCare Dental, Ameerpet, Hyderabad\n\nYou will get a reminder 2 hours before. See you!" },
];

const queueItems = [
  { init: "P", treatment: "Laser Hair Removal", doc: "Dr. Priya Sharma, Mumbai", price: "Rs.12,500", time: "Just now", color: "#a855f7" },
  { init: "R", treatment: "Root Canal & Crown", doc: "Dr. Rajesh Mehta, Delhi NCR", price: "Rs.8,500", time: "2m ago", color: "#3b82f6" },
  { init: "A", treatment: "Acne Scar Treatment", doc: "Dr. Ananya Reddy, Bengaluru", price: "Rs.16,000", time: "5m ago", color: "#10b981" },
  { init: "S", treatment: "Invisalign Consultation", doc: "Dr. Kiran Patel, Pune", price: "Rs.55,000", time: "8m ago", color: "#f59e0b" },
];

const specialties: Record<string, { label: string; icon: string; cards: { title: string; desc: string; icon: string }[]; keywords: string[]; treatments: string[] }> = {
  dental: {
    label: "Dental & Orthodontics",
    icon: "D",
    cards: [
      { title: "Emergency Implant & Invisalign Ads", icon: "1", desc: "Auto-launch high-intent Google Search campaigns targeting dental implants, invisible braces and orthodontic keywords in your city." },
      { title: "24/7 Late-Night Toothache Booking", icon: "2", desc: "AI WhatsApp receptionist triages emergency calls at 2 AM and books the first morning slot automatically." },
      { title: "1-Tap Slot Reminders & Recall", icon: "3", desc: "Automated 24h + 2h WhatsApp reminders. No-show rate drops 60%. Recall lapsed patients every 6 months." },
    ],
    keywords: ["Dental Implants Near Me", "Invisible Braces Cost [City]", "Root Canal Treatment Price", "Best Dentist in [City]", "Teeth Whitening Near Me"],
    treatments: ["Dental Implants - Rs.25K-45K", "Invisible Aligners - Rs.50K-1.5L", "Root Canal - Rs.3K-8K", "Teeth Whitening - Rs.5K-15K"],
  },
  derma: {
    label: "Dermatology & Cosmetology",
    icon: "S",
    cards: [
      { title: "Laser & Acne Search Ads", icon: "1", desc: "Target laser hair removal cost, acne scar treatment, fractional CO2 laser with city-level precision." },
      { title: "Skin Assessment AI Triage", icon: "2", desc: "Patients describe their concern on WhatsApp. AI qualifies intent, screens price shoppers, books serious leads." },
      { title: "Repeat Package Session Recall", icon: "3", desc: "Automated follow-ups for multi-session treatments (laser, PRP, chemical peels). Revenue on autopilot." },
    ],
    keywords: ["Laser Hair Removal Cost [City]", "Acne Scar Treatment Near Me", "Fractional CO2 Laser Price", "PRP Hair Treatment Cost", "Best Dermatologist in [City]"],
    treatments: ["Laser Hair Removal - Rs.2K-8K/session", "Fractional CO2 - Rs.8K-20K", "Chemical Peel - Rs.2K-5K", "PRP Therapy - Rs.5K-12K"],
  },
};

const adCopies: Record<string, Record<string, { headline: string; desc: string; whatsapp: string }>> = {
  dental: {
    Hyderabad: { headline: "Dental Implants in Hyderabad - Rs.25,000 | Book Free Consult", desc: "Experienced implantologist . Same-day assessment . 0% EMI available . 4.9 Google Rating . Book on WhatsApp now", whatsapp: "Hi! Thanks for reaching out about dental implants. Our prices start at Rs.25,000 with 0% EMI. Would you like to book a free consultation? I can check tomorrow's slots for you right now!" },
    Mumbai: { headline: "Best Dental Implants Mumbai - Free Consultation", desc: "Top-rated implant centre . German implants . 10-year warranty . Book instantly on WhatsApp", whatsapp: "Hello! Welcome to SmileCare Mumbai. We specialize in German dental implants starting Rs.30,000. Want me to find a slot for your free consultation?" },
    Bengaluru: { headline: "Dental Implants Bengaluru - Same Day Assessment", desc: "MDS Prosthodontist . Digital smile design . Rs.25K-45K . EMI from Rs.2,083/mo", whatsapp: "Hi there! Interested in dental implants? Our Bengaluru clinic offers same-day assessment. Shall I check available slots?" },
  },
  derma: {
    Hyderabad: { headline: "Laser Hair Removal Hyderabad - Rs.1,999/Session", desc: "US FDA approved laser . Pain-free . 6-session package . Free patch test . Book on WhatsApp", whatsapp: "Hi! Interested in laser hair removal? We use US FDA approved diode laser. Sessions start at Rs.1,999. Want to book a free patch test?" },
    Mumbai: { headline: "Acne Scar Treatment Mumbai - See Results in 3 Sessions", desc: "Fractional CO2 + PRP combo . Board-certified dermatologist . Before/after gallery . EMI available", whatsapp: "Hello! Looking for acne scar treatment? Our CO2 laser + PRP combo shows visible results in 3 sessions. Shall I book a consultation?" },
    Bengaluru: { headline: "Best Dermatologist Bengaluru - Book Online", desc: "Laser . Acne . PRP . Chemical Peels . 15+ years experience . WhatsApp booking", whatsapp: "Hi! Welcome to SkinGlow Bengaluru. Which treatment are you interested in? I can check availability for you." },
  },
};

const faqs = [
  { q: "How does PatientPlex AI provision Google Ads automatically?", a: "Once you complete the 5-minute onboarding (specialty, city, budget), our AI generates optimized Google Search campaigns with high-intent medical keywords, negative keyword filters, geo-targeting, and ad copy specific to your specialty. You approve and it goes live." },
  { q: "Is the WhatsApp integration compliant with Meta's policies?", a: "Yes. We use the official Meta WhatsApp Business Cloud API. All message templates are pre-approved. Patient conversations are encrypted end-to-end. We only message patients who contacted you first." },
  { q: "How does 2-way Google Calendar sync work?", a: "PatientPlex connects via Google Calendar OAuth. When the AI books a slot, it creates an event in your calendar. If you block time manually, the AI sees it and won't double-book. Works with Cal.com and Outlook too." },
  { q: "What happens during a medical emergency inquiry?", a: "The AI never gives medical advice. For emergencies, it immediately responds with: Please call emergency services (108/112) or visit your nearest hospital. It then notifies you via WhatsApp about the urgent inquiry." },
  { q: "Is patient data secure?", a: "All data is encrypted at rest (AES-256) and in transit (TLS 1.3). We store data on SOC 2 certified infrastructure following HIPAA-equivalent practices and India's DPDP Act 2023 guidelines." },
  { q: "Can I use my existing clinic phone number?", a: "Yes. You get a virtual number that forwards calls to your existing number. When a call is missed, the AI triggers a WhatsApp message to the patient within 30 seconds." },
  { q: "How quickly can I get started?", a: "5 minutes. Sign up, select specialty, set your schedule, connect calendar, launch. Your first campaign can be live the same day. No contracts, cancel anytime." },
  { q: "Does the AI learn and improve over time?", a: "Yes. Our Conversion Neural Engine analyzes every interaction - which ad copies convert best, which time slots fill fastest, which WhatsApp scripts book the most patients. It auto-optimizes daily without any manual input." },
];

const compareRows = [
  ["Monthly Retainer Fee", "Rs.40K-80K/mo", "Rs.0 (subscription only)"],
  ["Inquiry Response Time", "2-12 Hours (Manual)", "< 3 Seconds (24/7 AI)"],
  ["After-Hours Coverage", "Zero - leads lost at night", "100% Automated WhatsApp"],
  ["Calendar Integration", "Manual callbacks & Excel", "Direct Calendar + PMS Sync"],
  ["Setup Turnaround", "2-3 Weeks onboarding", "5-Minute 1-Click Launch"],
  ["Learning & Optimization", "Monthly review meetings", "Self-learning AI, daily auto-optimize"],
  ["Attribution & Tracking", "Monthly PDF reports", "17-Stage Real-Time Funnel"],
];

// ── AI Brain Data ──────────────────────────────────
const brainNodes = [
  { label: "Ad Performance", metric: "CTR 4.8%", status: "optimizing" },
  { label: "WhatsApp Conversion", metric: "89.4%", status: "learning" },
  { label: "Slot Utilization", metric: "94%", status: "stable" },
  { label: "Cost Per Lead", metric: "Rs.280", status: "improving" },
  { label: "No-Show Prediction", metric: "92% acc", status: "learning" },
  { label: "Keyword Bidding", metric: "Auto CPC", status: "optimizing" },
];

// ── Component ─────────────────────────────────────

export default function LandingPage() {
  const [chatIdx, setChatIdx] = useState(0);
  const [typing, setTyping] = useState(false);
  const [specTab, setSpecTab] = useState<"dental" | "derma">("dental");
  const [adSpec, setAdSpec] = useState("dental");
  const [adCity, setAdCity] = useState("Hyderabad");
  const [spend, setSpend] = useState(50000);
  const [procVal, setProcVal] = useState(15000);
  const [roiSpec, setRoiSpec] = useState("dental");
  const [annual, setAnnual] = useState(false);
  const [faqOpen, setFaqOpen] = useState<number | null>(null);
  const [modal, setModal] = useState(false);
  const [modalSent, setModalSent] = useState(false);
  const [liveCount, setLiveCount] = useState(1847);
  const [brainPulse, setBrainPulse] = useState(0);
  const [dataPoints, setDataPoints] = useState(234891);

  // Chat auto-play
  useEffect(() => {
    if (chatIdx >= whatsappChat.length) return;
    const isAi = whatsappChat[chatIdx]?.from === "ai";
    const delay = chatIdx === 0 ? 1200 : isAi ? 2200 : 1600;
    if (isAi) setTyping(true);
    const t = setTimeout(() => { setTyping(false); setChatIdx((c) => c + 1); }, delay);
    return () => clearTimeout(t);
  }, [chatIdx]);

  // Live counters
  useEffect(() => {
    const t1 = setInterval(() => setLiveCount((c) => c + 1), 12000);
    const t2 = setInterval(() => setBrainPulse((c) => (c + 1) % brainNodes.length), 2500);
    const t3 = setInterval(() => setDataPoints((c) => c + Math.floor(Math.random() * 5) + 1), 3000);
    return () => { clearInterval(t1); clearInterval(t2); clearInterval(t3); };
  }, []);

  // ROI calc
  const inquiries = Math.round(spend / 350);
  const booked = Math.round(inquiries * 0.42);
  const revenue = booked * procVal;
  const roi = spend > 0 ? (revenue / spend).toFixed(1) : "0";

  const spec = specialties[specTab];
  const adKey = adSpec as "dental" | "derma";
  const ad = adCopies[adKey]?.[adCity] ?? adCopies[adKey]?.Hyderabad;

  const tierPrice = (base: number) => annual ? Math.round(base * 0.8) : base;

  return (
    <div className="min-h-screen bg-[#070a12] text-white selection:bg-emerald-500/30 overflow-x-hidden">

      {/* ═══ GLOBAL AMBIENT EFFECTS ═══ */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/3 w-[800px] h-[800px] bg-emerald-500/[0.03] rounded-full blur-[200px]" />
        <div className="absolute bottom-1/4 right-0 w-[600px] h-[600px] bg-violet-500/[0.03] rounded-full blur-[200px]" />
        <div className="absolute top-1/2 left-0 w-[400px] h-[400px] bg-cyan-500/[0.02] rounded-full blur-[150px]" />
      </div>

      {/* ═══ 1. TOP BAR ═══ */}
      <div className="relative z-10 bg-gradient-to-r from-emerald-600/10 via-transparent to-violet-600/10 border-b border-slate-800/40 py-2 px-4 text-center text-sm">
        <span className="inline-flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold px-2.5 py-0.5 rounded-full mr-2 uppercase tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />Live
        </span>
        <span className="text-slate-500 text-xs">{dataPoints.toLocaleString("en-IN")} data points processed today</span>
        <span className="text-slate-800 mx-2">|</span>
        <Link href="/signup" className="text-emerald-400 hover:text-emerald-300 text-xs font-medium transition">Start Free &rarr;</Link>
      </div>

      {/* ═══ STICKY NAV ═══ */}
      <nav className="sticky top-0 z-50 bg-[#070a12]/80 backdrop-blur-2xl border-b border-slate-800/30 relative">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/25">
                <span className="text-white font-black text-sm">P</span>
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#070a12] animate-pulse" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight">PatientPlex</span>
              <span className="text-[9px] text-emerald-400/60 ml-1 font-mono">AI</span>
            </div>
          </div>
          <div className="hidden lg:flex items-center gap-6 text-[11px] text-slate-600 font-medium tracking-[2px] uppercase">
            <a href="#brain" className="hover:text-emerald-400 transition">AI Brain</a>
            <a href="#specialties" className="hover:text-emerald-400 transition">Specialties</a>
            <a href="#demo" className="hover:text-emerald-400 transition">Demo</a>
            <a href="#roi" className="hover:text-emerald-400 transition">ROI</a>
            <a href="#pricing" className="hover:text-emerald-400 transition">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-xs text-slate-500 hover:text-white transition hidden sm:block">Sign In</Link>
            <Link href="/signup" className="relative group bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl hover:shadow-xl hover:shadow-emerald-500/25 transition-all">
              <span className="relative z-10">Start Free Trial</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══ 2. HERO ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-24 grid lg:grid-cols-2 gap-16 items-start">
        {/* Left column */}
        <div className="pt-4">
          <div className="inline-flex items-center gap-2 bg-slate-900/60 backdrop-blur border border-slate-800 rounded-full px-4 py-1.5 mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-semibold">#1 AI Patient Flow Engine</span>
            <span className="text-slate-800">|</span>
            <span className="text-slate-600 text-xs">Self-Learning</span>
          </div>

          <h1 className="text-[2.6rem] lg:text-[3.6rem] font-extrabold leading-[1.06] tracking-tight mb-6">
            Your Clinic&apos;s AI Brain That{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Never Stops Learning.</span>
          </h1>

          <p className="text-base lg:text-lg text-slate-400 leading-relaxed mb-4 max-w-xl">
            PatientPlex AI autonomously runs your Google Ads, triages patients on WhatsApp 24/7, and books confirmed appointments - all while learning from every single interaction to get you more patients at lower cost.
          </p>

          <div className="flex items-center gap-6 mb-10 text-sm">
            <div className="flex items-center gap-2 text-emerald-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-mono text-xs">{liveCount.toLocaleString()} patients booked this month</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 mb-12">
            <Link href="/signup" className="group bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-8 py-4 rounded-2xl text-base hover:shadow-2xl hover:shadow-emerald-500/30 transition-all inline-flex items-center gap-2">
              Start 14-Day Free Trial <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
            </Link>
            <a href="#demo" className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition border border-slate-800 hover:border-slate-700 px-6 py-4 rounded-2xl hover:bg-slate-900/50 text-base group">
              <span className="text-emerald-400 group-hover:scale-110 transition-transform">&#9654;</span> Watch AI Demo
            </a>
          </div>

          <div className="grid grid-cols-4 gap-4">
            {[
              { v: "4.2x", l: "Avg Ad ROI" },
              { v: "70%", l: "Lower Cost" },
              { v: "< 3s", l: "AI Response" },
              { v: "89%", l: "Book Rate" },
            ].map((s, i) => (
              <div key={i} className="text-center">
                <p className="text-xl lg:text-2xl font-bold bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent">{s.v}</p>
                <p className="text-[9px] text-slate-700 mt-1 tracking-wide uppercase">{s.l}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right - Live Dashboard */}
        <div className="relative">
          <div className="absolute -inset-4 bg-gradient-to-br from-emerald-500/10 via-transparent to-violet-500/10 rounded-3xl blur-xl" />
          <div className="relative bg-[#0c1220]/90 backdrop-blur-2xl border border-slate-800/60 rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
            {/* Dashboard header */}
            <div className="px-5 py-3.5 border-b border-slate-800/40 flex items-center justify-between bg-gradient-to-r from-slate-900/50 to-transparent">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm font-mono">AI</div>
                <div>
                  <p className="font-semibold text-xs">Live Command Dashboard</p>
                  <p className="text-[10px] text-slate-700">Powered by Conversion Neural Engine</p>
                </div>
              </div>
              <span className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-emerald-400 text-[10px] font-semibold">Live</span>
              </span>
            </div>

            {/* 4 metric cards */}
            <div className="p-3 grid grid-cols-2 gap-2">
              {[
                { label: "Monthly Google Ad ROI", val: "4.2x", sub: "+0.3x this week", hl: true },
                { label: "Avg Cost / Confirmed Slot", val: "Rs.340", sub: "Industry: Rs.1,200", hl: false },
                { label: "WhatsApp Triage Rate", val: "89.4%", sub: "AI learning: active", hl: true },
                { label: "Appointments Booked", val: String(liveCount), sub: "This month (live)", hl: false },
              ].map((m, i) => (
                <div key={i} className="bg-[#070a12]/80 rounded-xl p-3 border border-slate-800/40 hover:border-emerald-500/10 transition group">
                  <p className="text-[9px] text-slate-700 uppercase tracking-wider mb-1">{m.label}</p>
                  <p className={`text-lg font-bold ${m.hl ? "text-emerald-400" : "text-white"}`}>{m.val}</p>
                  <p className={`text-[9px] mt-0.5 ${m.hl ? "text-emerald-600" : "text-slate-800"}`}>{m.sub}</p>
                </div>
              ))}
            </div>

            {/* Patient queue */}
            <div className="px-3 pb-3">
              <div className="flex items-center justify-between mb-2 px-1">
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Real-Time Patient Queue</p>
                <p className="text-[9px] text-emerald-600 font-mono">streaming...</p>
              </div>
              <div className="space-y-1">
                {queueItems.map((p, i) => (
                  <div key={i} className={`flex items-center justify-between bg-[#070a12]/60 rounded-xl px-3 py-2 border border-slate-800/30 hover:border-slate-700/50 transition ${i === 0 ? "animate-pulse" : ""}`} style={i === 0 ? { animationDuration: "3s" } : {}}>
                    <div className="flex items-center gap-2.5">
                      <div className="w-6 h-6 rounded-lg flex items-center justify-center text-white text-[10px] font-bold" style={{ backgroundColor: p.color + "30", color: p.color }}>{p.init}</div>
                      <div>
                        <p className="text-[11px] font-medium">{p.treatment}</p>
                        <p className="text-[9px] text-slate-700">{p.doc}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[11px] font-semibold text-emerald-400">{p.price}</p>
                      <p className="text-[9px] text-slate-800">{p.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ TRUSTED BY BAR ═══ */}
      <section className="relative z-10 border-y border-slate-800/30 py-8 px-6">
        <div className="max-w-5xl mx-auto flex flex-wrap items-center justify-center gap-8 lg:gap-16">
          {["140+ Indian Clinics", "Rs.2.4Cr Revenue Generated", "47,000+ Patients Booked", "8 Cities Live"].map((t, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="w-1 h-1 rounded-full bg-emerald-500/40" />
              <span className="text-[11px] text-slate-600 font-medium tracking-wide">{t}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 3. AI BRAIN SECTION ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-24" id="brain">
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-1.5 mb-5">
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            <span className="text-violet-400 text-xs font-semibold">Conversion Neural Engine</span>
          </div>
          <h2 className="text-3xl lg:text-5xl font-bold mb-4">An AI Brain That Gets<br /><span className="bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">Smarter Every Day</span></h2>
          <p className="text-slate-500 max-w-2xl mx-auto">Every patient interaction, every ad click, every booking teaches PatientPlex how to get you more patients at lower cost. It never stops optimizing.</p>
        </div>

        {/* Brain visualization */}
        <div className="max-w-4xl mx-auto mb-14">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {brainNodes.map((node, i) => (
              <div key={i} className={`relative bg-[#0c1220]/80 backdrop-blur border rounded-2xl p-5 transition-all duration-700 ${brainPulse === i ? "border-violet-500/40 shadow-lg shadow-violet-500/10 scale-[1.02]" : "border-slate-800/40"}`}>
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-[9px] font-bold uppercase tracking-wider ${node.status === "optimizing" ? "text-emerald-400" : node.status === "learning" ? "text-violet-400" : "text-slate-600"}`}>
                    {node.status === "optimizing" ? "Optimizing" : node.status === "learning" ? "Learning" : "Stable"}
                  </span>
                  <span className={`w-2 h-2 rounded-full ${brainPulse === i ? "animate-ping" : ""} ${node.status === "optimizing" ? "bg-emerald-400" : node.status === "learning" ? "bg-violet-400" : "bg-slate-700"}`} />
                </div>
                <p className="text-sm font-medium text-slate-300 mb-1">{node.label}</p>
                <p className={`text-2xl font-bold ${brainPulse === i ? "text-white" : "text-slate-400"}`}>{node.metric}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How AI learns */}
        <div className="grid md:grid-cols-3 gap-5 max-w-5xl mx-auto">
          {[
            { step: "01", title: "Ingest & Analyze", desc: "Every click, message, booking and no-show feeds into the neural engine. We process 200K+ data points daily across all clinics.", gradient: "from-emerald-400 to-teal-400" },
            { step: "02", title: "Pattern Recognition", desc: "AI identifies what ad copy converts best for your city + specialty, which time slots fill fastest, and which patients are likely to show up.", gradient: "from-violet-400 to-purple-400" },
            { step: "03", title: "Auto-Optimize", desc: "Without any manual input, the engine adjusts ad bids, rewrites WhatsApp scripts, shifts budget to top-performing campaigns, and predicts no-shows.", gradient: "from-cyan-400 to-blue-400" },
          ].map((s, i) => (
            <div key={i} className="bg-[#0c1220]/60 backdrop-blur border border-slate-800/40 rounded-2xl p-6 hover:border-slate-700/50 transition group">
              <div className={`text-xs font-black bg-gradient-to-r ${s.gradient} bg-clip-text text-transparent mb-4`}>{s.step}</div>
              <h3 className="font-bold text-base mb-2">{s.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 4. SPECIALTY TABS ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="specialties">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Specialties</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Pre-Built for High-Ticket Medical Practices</h2>
          <p className="text-slate-500 mt-2">Ready-to-launch AI workflows trained on your exact specialty</p>
        </div>

        <div className="flex justify-center gap-3 mb-10">
          {(["dental", "derma"] as const).map((t) => (
            <button key={t} onClick={() => setSpecTab(t)} className={`px-6 py-3 rounded-2xl text-sm font-semibold transition-all ${specTab === t ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20" : "bg-slate-900/50 text-slate-500 border border-slate-800 hover:border-slate-700"}`}>
              {specialties[t].label}
            </button>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {spec.cards.map((c, i) => (
            <div key={i} className="bg-[#0c1220]/60 backdrop-blur border border-slate-800/40 rounded-2xl p-6 hover:border-emerald-500/20 transition group">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 text-sm font-bold group-hover:shadow-lg group-hover:shadow-emerald-500/10 transition">{c.icon}</div>
              <h3 className="font-bold mb-2">{c.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-5 max-w-4xl mx-auto">
          <div className="bg-[#0c1220]/40 border border-slate-800/40 rounded-2xl p-5">
            <h4 className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-3">Auto-Generated Keywords</h4>
            <div className="space-y-1.5">{spec.keywords.map((k, i) => (
              <div key={i} className="bg-[#070a12]/60 rounded-lg px-3.5 py-2 border border-slate-800/30 text-sm text-slate-400 flex items-center gap-2"><span className="text-emerald-500 text-[10px]">&#9656;</span>{k}</div>
            ))}</div>
          </div>
          <div className="bg-[#0c1220]/40 border border-slate-800/40 rounded-2xl p-5">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">Treatment Pricing Engine</h4>
            <div className="space-y-1.5">{spec.treatments.map((t, i) => {
              const parts = t.split(" - ");
              return <div key={i} className="bg-[#070a12]/60 rounded-lg px-3.5 py-2 border border-slate-800/30 text-sm flex items-center justify-between"><span className="text-slate-400">{parts[0]}</span><span className="text-emerald-400 font-semibold">{parts[1]}</span></div>;
            })}</div>
          </div>
        </div>
      </section>

      {/* ═══ 5. WHATSAPP AI SIMULATOR ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="demo">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Live Demo</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Watch the AI Receptionist in Action</h2>
          <p className="text-slate-500 mt-2">This is exactly what your patients experience - instant, intelligent, 24/7</p>
        </div>

        <div className="max-w-md mx-auto">
          <div className="relative">
            <div className="absolute -inset-3 bg-gradient-to-b from-emerald-500/10 to-violet-500/10 rounded-[2rem] blur-xl" />
            <div className="relative bg-[#0c1220] border border-slate-800/60 rounded-[1.8rem] overflow-hidden shadow-2xl shadow-black/60">
              {/* WhatsApp header */}
              <div className="bg-gradient-to-r from-[#075e54] to-[#128C7E] px-4 py-3 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold text-white">SC</div>
                <div className="flex-1">
                  <p className="font-semibold text-sm text-white">SmileCare Dental</p>
                  <p className="text-[10px] text-emerald-200 flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-300 inline-block" /> AI Receptionist &bull; Online</p>
                </div>
              </div>
              {/* Chat area */}
              <div className="p-3 space-y-2.5 min-h-[380px] bg-[#0b1622]">
                <div className="space-y-2.5">
                  {whatsappChat.slice(0, chatIdx).map((m, i) => (
                    <div key={i} className={`flex ${m.from === "patient" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[82%] rounded-2xl px-3.5 py-2 text-[13px] whitespace-pre-line leading-relaxed shadow-sm ${
                        m.from === "patient"
                          ? "bg-emerald-600 text-white rounded-br-sm"
                          : "bg-[#1e293b] text-slate-200 border border-slate-700/50 rounded-bl-sm"
                      }`}>
                        {m.text}
                        <p className={`text-[9px] mt-1 text-right ${m.from === "patient" ? "text-emerald-200/60" : "text-slate-600"}`}>
                          {m.from === "ai" && <span className="text-violet-400 mr-1">AI</span>}
                          {new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {typing && (
                    <div className="flex justify-start">
                      <div className="bg-[#1e293b] border border-slate-700/50 rounded-2xl rounded-bl-sm px-4 py-3">
                        <div className="flex gap-1">
                          <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" />
                          <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "0.15s" }} />
                          <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "0.3s" }} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ 6. ROI CALCULATOR ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="roi">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">ROI Calculator</p>
          <h2 className="text-3xl lg:text-4xl font-bold">See Your Returns Before You Start</h2>
        </div>
        <div className="max-w-2xl mx-auto bg-[#0c1220]/60 backdrop-blur border border-slate-800/40 rounded-2xl p-8">
          <div className="flex gap-3 mb-6">
            {["dental", "derma"].map((s) => (
              <button key={s} onClick={() => setRoiSpec(s)} className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${roiSpec === s ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-slate-900/50 text-slate-500 border border-slate-800"}`}>
                {s === "dental" ? "Dental" : "Dermatology"}
              </button>
            ))}
          </div>
          <div className="space-y-6 mb-8">
            <div>
              <div className="flex justify-between text-sm mb-2"><span className="text-slate-400">Monthly Ad Spend</span><span className="text-emerald-400 font-bold font-mono">Rs.{spend.toLocaleString("en-IN")}</span></div>
              <input type="range" min={10000} max={200000} step={5000} value={spend} onChange={(e) => setSpend(+e.target.value)} className="w-full accent-emerald-500 h-1.5 rounded-full" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2"><span className="text-slate-400">Avg Procedure Value</span><span className="text-violet-400 font-bold font-mono">Rs.{procVal.toLocaleString("en-IN")}</span></div>
              <input type="range" min={3000} max={50000} step={1000} value={procVal} onChange={(e) => setProcVal(+e.target.value)} className="w-full accent-violet-500 h-1.5 rounded-full" />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { v: String(inquiries), l: "High-Intent Inquiries", c: "text-white" },
              { v: String(booked), l: "Confirmed Slots (42%)", c: "text-emerald-400" },
              { v: `Rs.${revenue.toLocaleString("en-IN")}`, l: "Monthly Revenue", c: "text-emerald-400" },
              { v: `${roi}x`, l: "Net ROI", c: "text-violet-400" },
            ].map((r, i) => (
              <div key={i} className="bg-[#070a12]/80 rounded-xl p-4 border border-slate-800/30 text-center">
                <p className={`text-xl font-bold font-mono ${r.c}`}>{r.v}</p>
                <p className="text-[9px] text-slate-700 mt-1">{r.l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ 7. AD COPY GENERATOR ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="adgen">
        <div className="text-center mb-10">
          <p className="text-violet-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Free Tool</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Instant Campaign & Ad Copy Generator</h2>
          <p className="text-slate-500 mt-2">Select your specialty and city - get a ready-to-run Google Ad + WhatsApp script</p>
        </div>
        <div className="max-w-3xl mx-auto bg-[#0c1220]/60 backdrop-blur border border-slate-800/40 rounded-2xl p-8">
          <div className="flex flex-wrap gap-3 mb-6">
            <select value={adSpec} onChange={(e) => setAdSpec(e.target.value)} className="bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-300 focus:border-emerald-500 outline-none">
              <option value="dental">Dental & Orthodontics</option>
              <option value="derma">Dermatology & Cosmetology</option>
            </select>
            <select value={adCity} onChange={(e) => setAdCity(e.target.value)} className="bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-300 focus:border-emerald-500 outline-none">
              {["Hyderabad", "Mumbai", "Bengaluru"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          {ad && (
            <div className="grid md:grid-cols-2 gap-5">
              <div className="bg-[#070a12]/80 border border-slate-800/30 rounded-xl p-5">
                <p className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider mb-3">Google Search Ad Preview</p>
                <p className="text-blue-400 text-sm font-medium mb-1">{ad.headline}</p>
                <p className="text-[11px] text-emerald-700 mb-1">Ad &bull; patientplex.ai/{adCity.toLowerCase()}</p>
                <p className="text-xs text-slate-500 leading-relaxed">{ad.desc}</p>
              </div>
              <div className="bg-[#070a12]/80 border border-slate-800/30 rounded-xl p-5">
                <p className="text-[10px] text-violet-400 font-semibold uppercase tracking-wider mb-3">WhatsApp Auto-Reply Script</p>
                <div className="bg-[#1e293b]/80 rounded-xl px-3.5 py-3 text-xs text-slate-300 leading-relaxed border border-slate-700/30">
                  {ad.whatsapp}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ═══ 8. AGENCY VS AI COMPARISON ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="compare">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Comparison</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Traditional Agency vs. PatientPlex AI</h2>
        </div>
        <div className="max-w-3xl mx-auto overflow-hidden rounded-2xl border border-slate-800/40">
          <table className="w-full text-sm">
            <thead><tr className="bg-[#0c1220]">
              <th className="text-left px-5 py-3 text-slate-600 font-medium text-xs">Feature</th>
              <th className="text-left px-5 py-3 text-red-400/60 font-medium text-xs">Traditional Agency</th>
              <th className="text-left px-5 py-3 text-emerald-400 font-medium text-xs">PatientPlex AI</th>
            </tr></thead>
            <tbody>
              {compareRows.map(([feat, agency, ai], i) => (
                <tr key={i} className={`${i % 2 === 0 ? "bg-[#070a12]/50" : "bg-[#0c1220]/30"} border-t border-slate-800/20`}>
                  <td className="px-5 py-3 text-slate-300 text-xs font-medium">{feat}</td>
                  <td className="px-5 py-3 text-slate-600 text-xs">{agency}</td>
                  <td className="px-5 py-3 text-emerald-400 text-xs font-semibold">{ai}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ═══ 9. PRICING ═══ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-20" id="pricing">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Pricing</p>
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">Transparent Pricing. No Agency Lock-Ins.</h2>
          <div className="inline-flex items-center gap-3 bg-slate-900/50 border border-slate-800 rounded-full p-1">
            <button onClick={() => setAnnual(false)} className={`px-4 py-1.5 rounded-full text-xs font-semibold transition ${!annual ? "bg-emerald-500 text-black" : "text-slate-500"}`}>Monthly</button>
            <button onClick={() => setAnnual(true)} className={`px-4 py-1.5 rounded-full text-xs font-semibold transition ${annual ? "bg-emerald-500 text-black" : "text-slate-500"}`}>Annual <span className="text-emerald-400 ml-1">-20%</span></button>
          </div>
        </div>
        <div className="grid md:grid-cols-3 gap-5 max-w-4xl mx-auto">
          {[
            { name: "Starter Flow", price: tierPrice(4999), features: ["100 AI conversations/mo", "2 campaigns (Google + Meta)", "WhatsApp AI receptionist", "Basic conversion tracking", "Email support"], pop: false },
            { name: "Pro Patient Engine", price: tierPrice(9999), features: ["Unlimited conversations", "10 campaigns, all platforms", "Full 17-stage funnel", "AI self-learning engine", "Priority support", "ROI dashboard"], pop: true },
            { name: "Clinic Network", price: tierPrice(18999), features: ["Everything in Pro", "Multi-location support", "White-label branding", "Dedicated account manager", "API access", "Custom integrations"], pop: false },
          ].map((p, i) => (
            <div key={i} className={`rounded-2xl p-6 transition relative ${p.pop ? "bg-gradient-to-b from-emerald-500/[0.07] to-transparent border-2 border-emerald-500/30 scale-[1.02]" : "bg-[#0c1220]/40 border border-slate-800/40 hover:border-slate-700/50"}`}>
              {p.pop && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-teal-500 text-black text-[10px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">Most Popular</div>}
              <p className="text-xs text-slate-500 mb-1">{p.name}</p>
              <p className="text-3xl font-bold mb-0.5 font-mono">Rs.{p.price.toLocaleString("en-IN")}</p>
              <p className="text-[10px] text-slate-700 mb-5">/{annual ? "mo (billed annually)" : "month"}</p>
              <ul className="space-y-2 mb-6">{p.features.map((f, j) => <li key={j} className="text-xs text-slate-400 flex items-start gap-2"><span className="text-emerald-400 mt-0.5">&#10003;</span>{f}</li>)}</ul>
              <button onClick={() => setModal(true)} className={`w-full text-center py-3 rounded-xl text-sm font-semibold transition ${p.pop ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20" : "bg-slate-900/50 hover:bg-slate-800/50 text-white border border-slate-800"}`}>
                {p.pop ? "Start Free Trial" : "Choose Plan"}
              </button>
            </div>
          ))}
        </div>
        <p className="text-center text-slate-800 text-xs mt-6">All plans include: 14-day free trial &bull; No credit card required &bull; Cancel anytime</p>
      </section>

      {/* ═══ 10. FAQ ═══ */}
      <section className="relative z-10 max-w-3xl mx-auto px-6 py-20" id="faq">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">FAQ</p>
          <h2 className="text-3xl font-bold">Frequently Asked Questions</h2>
        </div>
        <div className="space-y-0">
          {faqs.map((f, i) => (
            <div key={i} className="border-b border-slate-800/30">
              <button onClick={() => setFaqOpen(faqOpen === i ? null : i)} className="w-full text-left py-5 flex justify-between items-center hover:text-emerald-400 transition gap-4">
                <span className="text-sm font-medium">{f.q}</span>
                <span className={`text-slate-600 text-lg flex-shrink-0 transition-transform ${faqOpen === i ? "rotate-45" : ""}`}>+</span>
              </button>
              <div className={`overflow-hidden transition-all duration-300 ${faqOpen === i ? "max-h-40 pb-4" : "max-h-0"}`}>
                <p className="text-slate-500 text-sm leading-relaxed">{f.a}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 11. FINAL CTA ═══ */}
      <section className="relative z-10 py-24 px-6 text-center">
        <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/[0.04] via-violet-500/[0.02] to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-semibold">{dataPoints.toLocaleString("en-IN")} interactions learned from today</span>
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">Every Missed Call Is a{" "}<span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Patient Lost Forever.</span></h2>
          <p className="text-slate-500 text-lg mb-8">Your AI brain is ready. It will start learning from day one.</p>
          <button onClick={() => setModal(true)} className="group bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-10 py-4 rounded-2xl text-lg shadow-2xl shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all inline-flex items-center gap-2">
            Start Free - No Credit Card <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
          </button>
          <p className="text-slate-800 text-xs mt-4">14-day free trial &middot; No contracts &middot; Cancel anytime</p>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="relative z-10 border-t border-slate-800/30 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-[10px] font-bold">P</div>
            <span className="font-semibold text-sm">PatientPlex AI</span>
            <span className="text-[9px] text-slate-800 font-mono ml-1">v3.0</span>
          </div>
          <p className="text-slate-700 text-xs">Self-learning AI for Indian healthcare. Replace your agency.</p>
          <p className="text-slate-800 text-[10px]">&copy; 2026 PatientPlex AI. All rights reserved.</p>
        </div>
      </footer>

      {/* ═══ TRIAL MODAL ═══ */}
      {modal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => { setModal(false); setModalSent(false); }} />
          <div className="relative bg-[#0c1220] border border-slate-800/60 rounded-2xl p-8 max-w-md w-full shadow-2xl shadow-black/60">
            <button onClick={() => { setModal(false); setModalSent(false); }} className="absolute top-4 right-4 text-slate-600 hover:text-white transition text-lg">&times;</button>
            {!modalSent ? (
              <>
                <h3 className="text-xl font-bold mb-1">Start Your 14-Day Free Trial</h3>
                <p className="text-sm text-slate-500 mb-6">No credit card required. Your AI brain starts learning immediately.</p>
                <form onSubmit={(e) => { e.preventDefault(); setModalSent(true); }} className="space-y-3">
                  <input required placeholder="Doctor Name" className="w-full bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none transition" />
                  <input required placeholder="Clinic Name" className="w-full bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none transition" />
                  <select required className="w-full bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-400 focus:border-emerald-500 outline-none transition">
                    <option value="">Select Specialty</option>
                    <option>Dental & Orthodontics</option>
                    <option>Dermatology & Cosmetology</option>
                    <option>Orthopedics</option>
                    <option>Gynecology</option>
                    <option>Other</option>
                  </select>
                  <input required type="tel" placeholder="Phone / WhatsApp Number" className="w-full bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none transition" />
                  <select required className="w-full bg-[#070a12] border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-400 focus:border-emerald-500 outline-none transition">
                    <option value="">Select City</option>
                    {["Hyderabad", "Mumbai", "Delhi NCR", "Bengaluru", "Pune", "Chennai", "Kolkata", "Ahmedabad"].map(c => <option key={c}>{c}</option>)}
                  </select>
                  <button type="submit" className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold py-3 rounded-xl text-sm shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition mt-2">
                    Activate AI Brain &rarr;
                  </button>
                </form>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4">&#10003;</div>
                <h3 className="text-xl font-bold mb-2 text-emerald-400">You&apos;re In!</h3>
                <p className="text-sm text-slate-400 mb-6">Your AI brain is initializing. Check your WhatsApp - our AI will message you in under 30 seconds.</p>
                <Link href="/signup" className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-8 py-3 rounded-xl text-sm inline-block">Go to Dashboard</Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
