"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

/* ═══════════════════════════════════════════════════
   PatientPlex AI — Premium Landing Page
   Design: Deep Slate #070a12, Emerald #10B981, Violet #8B5CF6
   Style:  Stripe / Vercel glassmorphism dark-mode SaaS
   ═══════════════════════════════════════════════════ */

// ── Data ──────────────────────────────────────────

const whatsappChat = [
  { from: "patient", text: "Hi, I saw your ad for dental implants. What’s the cost?" },
  { from: "ai", text: "Hello! 👋 Thanks for reaching out to SmileCare Dental.\n\nDental implant costs range from ₹25,000 to ₹45,000 per tooth depending on type.\n\nWould you like to book a free consultation?" },
  { from: "patient", text: "Yes, do you have slots tomorrow afternoon?" },
  { from: "ai", text: "Let me check Dr. Bhardwaj’s calendar… ✅ Found 2 slots:\n\n🕐 2:30 PM – 3:00 PM\n🕐 4:00 PM – 4:30 PM\n\nTap a time to book instantly:" },
  { from: "patient", text: "4 PM please" },
  { from: "ai", text: "✅ Booked!\n\n📅 Tomorrow, 4:00 PM\n👨‍⚕️ Dr. Bhardwaj\n📍 SmileCare Dental, Ameerpet, Hyderabad\n\nYou’ll get a reminder 2 hours before. See you! 😊" },
];

const queueItems = [
  { init: "P", treatment: "Laser Hair Removal", doc: "Dr. Priya Sharma • Mumbai", price: "₹12,500", time: "Just now", bg: "bg-purple-500" },
  { init: "R", treatment: "Root Canal & Crown", doc: "Dr. Rajesh Mehta • Delhi NCR", price: "₹8,500", time: "2m ago", bg: "bg-blue-500" },
  { init: "A", treatment: "Acne Scar Treatment", doc: "Dr. Ananya Reddy • Bengaluru", price: "₹16,000", time: "5m ago", bg: "bg-emerald-500" },
];

const specialties: Record<string, { label: string; cards: { title: string; desc: string }[]; keywords: string[]; treatments: string[] }> = {
  dental: {
    label: "🦷 Dental & Orthodontics",
    cards: [
      { title: "Emergency Implant & Invisalign Ads", desc: "Auto-launch high-intent Google Search campaigns targeting “dental implants near me” and “invisible braces cost” in your city." },
      { title: "24/7 Late-Night Toothache Booking", desc: "AI WhatsApp receptionist triages emergency calls at 2 AM and books the first morning slot automatically." },
      { title: "1-Tap Slot Reminders & Recall", desc: "Automated 24h + 2h WhatsApp reminders. No-show rate drops 60%. Recall lapsed patients every 6 months." },
    ],
    keywords: ["Dental Implants Near Me", "Invisible Braces Cost [City]", "Root Canal Treatment Price", "Best Dentist in [City]", "Teeth Whitening Near Me"],
    treatments: ["Dental Implants — ₹25K–45K", "Invisible Aligners — ₹50K–1.5L", "Root Canal — ₹3K–8K", "Teeth Whitening — ₹5K–15K"],
  },
  derma: {
    label: "✨ Dermatology & Cosmetology",
    cards: [
      { title: "Laser & Acne Search Ads", desc: "Target “laser hair removal cost”, “acne scar treatment”, “fractional CO2 laser” with city-level precision." },
      { title: "Skin Assessment AI Triage", desc: "Patients describe their concern on WhatsApp. AI qualifies intent, screens price shoppers, books serious leads." },
      { title: "Repeat Package Session Recall", desc: "Automated follow-ups for multi-session treatments (laser, PRP, chemical peels). Revenue on autopilot." },
    ],
    keywords: ["Laser Hair Removal Cost [City]", "Acne Scar Treatment Near Me", "Fractional CO2 Laser Price", "PRP Hair Treatment Cost", "Best Dermatologist in [City]"],
    treatments: ["Laser Hair Removal — ₹2K–8K/session", "Fractional CO2 — ₹8K–20K", "Chemical Peel — ₹2K–5K", "PRP Therapy — ₹5K–12K"],
  },
};

const adCopies: Record<string, Record<string, { headline: string; desc: string; whatsapp: string }>> = {
  dental: {
    Hyderabad: { headline: "Dental Implants in Hyderabad — ₹25,000 | Book Free Consult", desc: "Experienced implantologist • Same-day assessment • 0% EMI available • 4.9★ Google Rating • Book on WhatsApp now", whatsapp: "Hi! 👋 Thanks for reaching out about dental implants. Our prices start at ₹25,000 with 0% EMI. Would you like to book a free consultation with Dr. Bhardwaj? I can check tomorrow’s slots for you right now!" },
    Mumbai: { headline: "Best Dental Implants Mumbai — Free Consultation", desc: "Top-rated implant centre • German implants • 10-year warranty • Book instantly on WhatsApp", whatsapp: "Hello! 😊 Welcome to SmileCare Mumbai. We specialize in German dental implants starting ₹30,000. Want me to find a slot for your free consultation?" },
    Bengaluru: { headline: "Dental Implants Bengaluru — Same Day Assessment", desc: "MDS Prosthodontist • Digital smile design • ₹25K–45K • EMI from ₹2,083/mo", whatsapp: "Hi there! 👋 Interested in dental implants? Our Bengaluru clinic offers same-day assessment with Dr. Nair. Shall I check available slots?" },
  },
  derma: {
    Hyderabad: { headline: "Laser Hair Removal Hyderabad — ₹1,999/Session", desc: "US FDA approved laser • Pain-free • 6-session package • Free patch test • Book on WhatsApp", whatsapp: "Hi! 👋 Interested in laser hair removal? We use US FDA approved diode laser. Sessions start at ₹1,999. Want to book a free patch test?" },
    Mumbai: { headline: "Acne Scar Treatment Mumbai — See Results in 3 Sessions", desc: "Fractional CO2 + PRP combo • Board-certified dermatologist • Before/after gallery • EMI available", whatsapp: "Hello! 😊 Looking for acne scar treatment? Our CO2 laser + PRP combo shows visible results in 3 sessions. Shall I book a consultation?" },
    Bengaluru: { headline: "Best Dermatologist Bengaluru — Book Online", desc: "Laser • Acne • PRP • Chemical Peels • 15+ years experience • WhatsApp booking", whatsapp: "Hi! 👋 Welcome to SkinGlow Bengaluru. Which treatment are you interested in? I can check Dr. Reddy’s availability for you." },
  },
};

const faqs = [
  { q: "How does PatientPlex AI provision Google Ads automatically?", a: "Once you complete the 5-minute onboarding (specialty, city, budget), our AI generates optimized Google Search campaigns with high-intent medical keywords, negative keyword filters, geo-targeting, and ad copy — all specific to your specialty. You approve and it goes live." },
  { q: "Is the WhatsApp integration compliant with Meta’s policies?", a: "Yes. We use the official Meta WhatsApp Business Cloud API. All message templates are pre-approved. Patient conversations are encrypted end-to-end. No spam — we only message patients who contacted you first or missed a call." },
  { q: "How does 2-way Google Calendar sync work?", a: "PatientPlex connects via Google Calendar OAuth. When the AI books a slot, it creates an event in your calendar. If you block time manually, the AI sees it and won’t double-book. Works with Cal.com and Outlook too." },
  { q: "What happens during a medical emergency inquiry?", a: "The AI is trained to never give medical advice. For emergencies, it immediately responds with: “Please call emergency services (108/112) or visit your nearest hospital.” It then notifies you via WhatsApp about the urgent inquiry." },
  { q: "Is patient data secure? Are you HIPAA compliant?", a: "All data is encrypted at rest (AES-256) and in transit (TLS 1.3). We store data on SOC 2 certified infrastructure. We follow HIPAA-equivalent data handling practices and India’s DPDP Act 2023 guidelines." },
  { q: "Will the AI give medical advice to patients?", a: "Never. PatientPlex AI is trained exclusively for scheduling. It checks availability, shows slots, books appointments, and sends confirmations. Any medical question is deflected to “Please discuss this with the doctor during your consultation.”" },
  { q: "Can I use my existing clinic phone number?", a: "Yes. You get a virtual number that forwards calls to your existing number. When a call is missed, the AI triggers a WhatsApp message to the patient within 30 seconds. Your existing number stays the same." },
  { q: "How quickly can I get started?", a: "5 minutes. Sign up → select specialty → set your schedule → connect calendar → launch. Your first campaign can be live the same day. No contracts, cancel anytime." },
];

const compareRows = [
  ["Monthly Retainer Fee", "₹40,000 – ₹80,000/mo", "₹0 Retainer (subscription only)"],
  ["Inquiry Response Time", "2–12 Hours (Manual sheet)", "Instant (< 3 Seconds, 24/7)"],
  ["After-Hours Coverage", "None — leads drop off at night", "100% Automated WhatsApp Triage"],
  ["Calendar Integration", "Manual callbacks & Excel tracking", "Direct Google Calendar + PMS Sync"],
  ["Setup Turnaround", "2–3 Weeks onboarding", "5-Minute 1-Click Launch"],
  ["Attribution & Tracking", "Monthly PDF reports", "17-Stage Real-Time Conversion Funnel"],
  ["Ad Optimization", "Monthly review meetings", "AI auto-optimizes daily"],
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
  const [liveCount, setLiveCount] = useState(118);

  // Chat auto-play
  useEffect(() => {
    if (chatIdx >= whatsappChat.length) return;
    const isAi = whatsappChat[chatIdx]?.from === "ai";
    const delay = chatIdx === 0 ? 1200 : isAi ? 2200 : 1600;
    if (isAi) { setTyping(true); }
    const t = setTimeout(() => { setTyping(false); setChatIdx((c) => c + 1); }, delay);
    return () => clearTimeout(t);
  }, [chatIdx]);

  // Live counter tick
  useEffect(() => {
    const t = setInterval(() => setLiveCount((c) => c + 1), 18000);
    return () => clearInterval(t);
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
    <div className="min-h-screen bg-[#070a12] text-white selection:bg-emerald-500/30">

      {/* ═══ 1. ANNOUNCEMENT BAR ═══ */}
      <div className="bg-gradient-to-r from-emerald-600/10 via-transparent to-violet-600/10 border-b border-slate-800/60 py-2 px-4 text-center text-sm">
        <span className="bg-emerald-500 text-black text-[10px] font-bold px-2 py-0.5 rounded mr-2 uppercase tracking-wider">New</span>
        <span className="text-slate-400">Built for Indian Clinics: Automate Google Search Ads & 24/7 WhatsApp Bookings</span>
        <Link href="/signup" className="text-emerald-400 hover:text-emerald-300 ml-2 font-medium transition">Get Started Free &rarr;</Link>
      </div>

      {/* ═══ STICKY NAV ═══ */}
      <nav className="sticky top-0 z-50 bg-[#070a12]/80 backdrop-blur-xl border-b border-slate-800/40">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <span className="text-white font-black text-sm">P</span>
            </div>
            <span className="font-bold text-lg tracking-tight">PatientPlex</span>
            <span className="hidden sm:inline bg-emerald-500/10 text-emerald-400 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-emerald-500/20">v2.4 Active</span>
          </div>
          <div className="hidden lg:flex items-center gap-5 text-[11px] text-slate-500 font-medium tracking-widest uppercase">
            <a href="#specialties" className="hover:text-white transition">Specialties</a>
            <a href="#demo" className="hover:text-white transition">Demo</a>
            <a href="#roi" className="hover:text-white transition">ROI Calculator</a>
            <a href="#compare" className="hover:text-white transition">Agencies vs AI</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
            <a href="#faq" className="hover:text-white transition">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-slate-400 hover:text-white transition hidden sm:block">Sign In</Link>
            <Link href="/signup" className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-xs px-4 py-2 rounded-lg hover:shadow-lg hover:shadow-emerald-500/25 transition-all">Start 14-Day Free Trial</Link>
          </div>
        </div>
      </nav>

      {/* ═══ 2. HERO ═══ */}
      <section className="relative max-w-7xl mx-auto px-6 pt-16 pb-20 grid lg:grid-cols-2 gap-14 items-start overflow-hidden">
        {/* Ambient glows */}
        <div className="absolute -top-20 left-1/4 w-[600px] h-[600px] bg-emerald-500/[0.04] rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-40 right-0 w-[500px] h-[500px] bg-violet-500/[0.04] rounded-full blur-[140px] pointer-events-none" />

        {/* Left column */}
        <div className="relative z-10 pt-4">
          <div className="inline-flex items-center gap-2 bg-slate-900/60 backdrop-blur border border-slate-800 rounded-full px-4 py-1.5 mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-semibold">#1 AI Patient Flow Engine</span>
            <span className="text-slate-700">|</span>
            <span className="text-slate-500 text-xs">Dermatology & Dental Clinics</span>
          </div>

          <h1 className="text-[2.8rem] lg:text-[3.4rem] font-extrabold leading-[1.08] tracking-tight mb-6">
            Stop Paying Agency{" "}Retainers.{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Book Patients 24/7 on Autopilot.</span>
          </h1>

          <p className="text-base lg:text-lg text-slate-400 leading-relaxed mb-8 max-w-xl">
            PatientPlex AI automatically creates high-converting Google & Meta campaigns, triages late-night patient queries instantly on WhatsApp, and locks confirmed slots directly into your calendar.
          </p>

          <div className="flex flex-wrap items-center gap-4 mb-14">
            <Link href="/signup" className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-7 py-3.5 rounded-xl text-base hover:shadow-xl hover:shadow-emerald-500/25 transition-all inline-flex items-center gap-2">
              Start 14-Day Free Trial <span>&rarr;</span>
            </Link>
            <a href="#demo" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition border border-slate-800 hover:border-slate-700 px-6 py-3.5 rounded-xl hover:bg-slate-900/50 text-base">
              <span className="text-emerald-400">&#9654;</span> Try WhatsApp Demo
            </a>
          </div>

          <div className="grid grid-cols-4 gap-5">
            {[
              { v: "3.8x", l: "Avg Google Ad ROI" },
              { v: "70%", l: "Lower Cost/Booking" },
              { v: "< 3s", l: "WhatsApp AI Speed" },
              { v: "140+", l: "Indian Clinics" },
            ].map((s, i) => (
              <div key={i}>
                <p className="text-xl lg:text-2xl font-bold">{s.v}</p>
                <p className="text-[10px] text-slate-600 mt-1">{s.l}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right — Live Dashboard */}
        <div className="relative z-10 bg-[#0f172a]/70 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
          {/* Dashboard header */}
          <div className="px-5 py-3.5 border-b border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm">&#9783;</div>
              <div>
                <p className="font-semibold text-xs">Live Practice Command Dashboard</p>
                <p className="text-[10px] text-slate-600">Apex Derma & Dental Center, Bangalore</p>
              </div>
            </div>
            <span className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-emerald-400 text-[10px] font-semibold">Live</span>
            </span>
          </div>

          {/* 4 metric cards */}
          <div className="p-3 grid grid-cols-2 gap-2.5">
            {[
              { label: "Monthly Google Ad ROI", val: "4.2x", sub: "Spend: ₹35,000", hl: true },
              { label: "Avg Cost / Confirmed Slot", val: "₹340", sub: "Industry: ₹1,200", hl: false },
              { label: "WhatsApp Triage Rate", val: "89.4%", sub: "Zero human delay", hl: true },
              { label: "Appointments Booked", val: String(liveCount), sub: "This month", hl: false },
            ].map((m, i) => (
              <div key={i} className="bg-[#070a12] rounded-xl p-3.5 border border-slate-800/50 hover:border-emerald-500/20 transition">
                <p className="text-[9px] text-slate-600 uppercase tracking-wider mb-0.5">{m.label}</p>
                <p className={`text-xl font-bold ${m.hl ? "text-emerald-400" : "text-white"}`}>{m.val}</p>
                <p className={`text-[9px] mt-0.5 ${i === 3 ? "text-emerald-500" : "text-slate-700"}`}>{m.sub}</p>
              </div>
            ))}
          </div>

          {/* Patient queue */}
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold">Real-Time Patient Queue</p>
              <p className="text-[9px] text-slate-600">Updated Live</p>
            </div>
            <div className="space-y-1.5">
              {queueItems.map((p, i) => (
                <div key={i} className="flex items-center justify-between bg-[#070a12] rounded-xl px-3.5 py-2.5 border border-slate-800/50 hover:border-slate-700 transition">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-7 h-7 rounded-lg ${p.bg} flex items-center justify-center text-white text-[10px] font-bold`}>{p.init}</div>
                    <div>
                      <p className="text-xs font-medium">{p.treatment}</p>
                      <p className="text-[9px] text-slate-600">{p.doc}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-semibold text-emerald-400">{p.price}</p>
                    <p className="text-[9px] text-slate-700">{p.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ 3. SPECIALTY TABS ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="specialties">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Specialties</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Pre-Built for High-Ticket Medical Practices</h2>
          <p className="text-slate-500 mt-2">Ready-to-launch workflows for your exact specialty</p>
        </div>

        <div className="flex justify-center gap-3 mb-10">
          {(["dental", "derma"] as const).map((t) => (
            <button key={t} onClick={() => setSpecTab(t)} className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition ${specTab === t ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20" : "bg-slate-900/50 text-slate-400 border border-slate-800 hover:border-slate-700"}`}>
              {specialties[t].label}
            </button>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {spec.cards.map((c, i) => (
            <div key={i} className="bg-[#0f172a]/60 backdrop-blur border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/20 transition group">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-4 text-lg group-hover:shadow-lg group-hover:shadow-violet-500/10 transition">&#10024;</div>
              <h3 className="font-bold mb-2">{c.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-5 max-w-4xl mx-auto">
          <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-5">
            <h4 className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-3">Auto-Generated Keywords</h4>
            <div className="space-y-1.5">{spec.keywords.map((k, i) => (
              <div key={i} className="bg-[#070a12] rounded-lg px-3.5 py-2 border border-slate-800/50 text-sm text-slate-400 flex items-center gap-2"><span className="text-emerald-500 text-[10px]">&#9656;</span>{k}</div>
            ))}</div>
          </div>
          <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-5">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">Treatment Pricing Engine</h4>
            <div className="space-y-1.5">{spec.treatments.map((t, i) => {
              const [name, price] = t.split(" — ");
              return <div key={i} className="bg-[#070a12] rounded-lg px-3.5 py-2 border border-slate-800/50 text-sm flex items-center justify-between"><span className="text-slate-400">{name}</span><span className="text-emerald-400 font-semibold">{price}</span></div>;
            })}</div>
          </div>
        </div>
      </section>

      {/* ═══ 4. WHATSAPP AI SIMULATOR ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="demo">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Live Demo</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Watch the AI Receptionist in Action</h2>
          <p className="text-slate-500 mt-2">This is exactly what your patients experience — instant, intelligent, 24/7</p>
        </div>

        <div className="max-w-md mx-auto">
          {/* Phone frame */}
          <div className="bg-[#0f172a] border border-slate-800 rounded-[1.6rem] overflow-hidden shadow-2xl shadow-black/60">
            {/* WhatsApp header */}
            <div className="bg-[#075e54] px-4 py-3 flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-base">🏥</div>
              <div className="flex-1">
                <p className="font-semibold text-sm text-white">SmileCare Dental</p>
                <p className="text-[10px] text-emerald-200 flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-300 inline-block" /> AI Receptionist • Online</p>
              </div>
              <span className="text-white/60 text-xs">&#128222;</span>
            </div>
            {/* Chat area */}
            <div className="p-3 space-y-2.5 min-h-[380px] bg-[#0b1622] relative">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMGg0MHY0MEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0wIDBoMXYxSDB6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDEpIi8+PC9zdmc+')] opacity-50 pointer-events-none" />
              <div className="relative z-10 space-y-2.5">
                {whatsappChat.slice(0, chatIdx).map((m, i) => (
                  <div key={i} className={`flex ${m.from === "patient" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[82%] rounded-2xl px-3.5 py-2 text-[13px] whitespace-pre-line leading-relaxed shadow-sm ${
                      m.from === "patient"
                        ? "bg-emerald-600 text-white rounded-br-sm"
                        : "bg-[#1e293b] text-slate-200 border border-slate-700/50 rounded-bl-sm"
                    }`}>
                      {m.text}
                      <p className={`text-[9px] mt-1 text-right ${m.from === "patient" ? "text-emerald-200/60" : "text-slate-600"}`}>
                        {m.from === "ai" && <span className="text-violet-400 mr-1">🤖</span>}
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
      </section>

      {/* ═══ 5. ROI CALCULATOR ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="roi">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">ROI Calculator</p>
          <h2 className="text-3xl lg:text-4xl font-bold">See Your Returns Before You Start</h2>
        </div>
        <div className="max-w-2xl mx-auto bg-[#0f172a]/60 backdrop-blur border border-slate-800 rounded-2xl p-7">
          <div className="flex gap-3 mb-6">
            {["dental", "derma"].map((s) => (
              <button key={s} onClick={() => setRoiSpec(s)} className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${roiSpec === s ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-slate-900/50 text-slate-500 border border-slate-800"}`}>
                {s === "dental" ? "🦷 Dental" : "✨ Dermatology"}
              </button>
            ))}
          </div>
          <div className="space-y-5 mb-8">
            <div>
              <div className="flex justify-between text-sm mb-1"><span className="text-slate-400">Monthly Ad Spend</span><span className="text-emerald-400 font-bold">₹{spend.toLocaleString("en-IN")}</span></div>
              <input type="range" min={10000} max={200000} step={5000} value={spend} onChange={(e) => setSpend(+e.target.value)} className="w-full accent-emerald-500 h-1.5" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1"><span className="text-slate-400">Avg Procedure Value</span><span className="text-violet-400 font-bold">₹{procVal.toLocaleString("en-IN")}</span></div>
              <input type="range" min={3000} max={50000} step={1000} value={procVal} onChange={(e) => setProcVal(+e.target.value)} className="w-full accent-violet-500 h-1.5" />
            </div>
          </div>
          <div className="grid grid-cols-4 gap-3">
            {[
              { v: String(inquiries), l: "High-Intent Inquiries", c: "text-white" },
              { v: String(booked), l: "Confirmed Slots (42%)", c: "text-emerald-400" },
              { v: `₹${revenue.toLocaleString("en-IN")}`, l: "Monthly Revenue", c: "text-emerald-400" },
              { v: `${roi}x`, l: "Net ROI Multiplier", c: "text-violet-400" },
            ].map((r, i) => (
              <div key={i} className="bg-[#070a12] rounded-xl p-4 border border-slate-800/50 text-center">
                <p className={`text-xl lg:text-2xl font-bold ${r.c}`}>{r.v}</p>
                <p className="text-[9px] text-slate-600 mt-1">{r.l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ 6. AD COPY GENERATOR ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="adgen">
        <div className="text-center mb-10">
          <p className="text-violet-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Free Tool</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Instant Campaign & Ad Copy Generator</h2>
          <p className="text-slate-500 mt-2">Select your specialty and city — get a ready-to-run Google Ad + WhatsApp script</p>
        </div>
        <div className="max-w-3xl mx-auto bg-[#0f172a]/60 backdrop-blur border border-slate-800 rounded-2xl p-7">
          <div className="flex flex-wrap gap-3 mb-6">
            <select value={adSpec} onChange={(e) => setAdSpec(e.target.value)} className="bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2 text-sm text-slate-300 focus:border-emerald-500 outline-none">
              <option value="dental">Dental & Orthodontics</option>
              <option value="derma">Dermatology & Cosmetology</option>
            </select>
            <select value={adCity} onChange={(e) => setAdCity(e.target.value)} className="bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2 text-sm text-slate-300 focus:border-emerald-500 outline-none">
              {["Hyderabad", "Mumbai", "Bengaluru"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          {ad && (
            <div className="grid md:grid-cols-2 gap-5">
              <div className="bg-[#070a12] border border-slate-800/50 rounded-xl p-5">
                <p className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider mb-3">Google Search Ad Preview</p>
                <p className="text-blue-400 text-sm font-medium mb-1 underline">{ad.headline}</p>
                <p className="text-[11px] text-emerald-600 mb-1">Ad • patientplex.ai/{adCity.toLowerCase()}</p>
                <p className="text-xs text-slate-500 leading-relaxed">{ad.desc}</p>
              </div>
              <div className="bg-[#070a12] border border-slate-800/50 rounded-xl p-5">
                <p className="text-[10px] text-violet-400 font-semibold uppercase tracking-wider mb-3">WhatsApp Auto-Reply Script</p>
                <div className="bg-[#1e293b] rounded-xl px-3.5 py-3 text-xs text-slate-300 leading-relaxed border border-slate-700/50">
                  {ad.whatsapp}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ═══ 7. AGENCY VS AI COMPARISON ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="compare">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Comparison</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Traditional Agency vs. PatientPlex AI</h2>
        </div>
        <div className="max-w-3xl mx-auto overflow-hidden rounded-2xl border border-slate-800">
          <table className="w-full text-sm">
            <thead><tr className="bg-[#0f172a]">
              <th className="text-left px-5 py-3 text-slate-500 font-medium text-xs">Feature</th>
              <th className="text-left px-5 py-3 text-red-400/70 font-medium text-xs">Traditional Agency</th>
              <th className="text-left px-5 py-3 text-emerald-400 font-medium text-xs">PatientPlex AI</th>
            </tr></thead>
            <tbody>
              {compareRows.map(([feat, agency, ai], i) => (
                <tr key={i} className={`${i % 2 === 0 ? "bg-[#070a12]" : "bg-[#0f172a]/40"} border-t border-slate-800/30`}>
                  <td className="px-5 py-3 text-slate-300 text-xs font-medium">{feat}</td>
                  <td className="px-5 py-3 text-slate-600 text-xs">{agency}</td>
                  <td className="px-5 py-3 text-emerald-400 text-xs font-semibold">{ai}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ═══ 11. CASE STUDY ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">Case Study</p>
          <h2 className="text-3xl lg:text-4xl font-bold">Bhardwaj Dental Clinic, Hyderabad</h2>
          <p className="text-slate-500 mt-2">From losing 12 patients/week to filling every chair</p>
        </div>
        <div className="grid md:grid-cols-2 gap-5 max-w-4xl mx-auto mb-8">
          <div className="bg-red-500/[0.03] border border-red-500/10 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-red-400 mb-4 flex items-center gap-2"><span className="w-7 h-7 rounded-full bg-red-500/10 flex items-center justify-center text-xs">&times;</span>Before</h3>
            {[["Missed calls/week", "12–15"], ["Agency cost/month", "₹40,000"], ["Patient tracking", "None"], ["After-hours response", "0"], ["Revenue lost/month", "₹2.4L+"]].map(([l, v], i) => (
              <div key={i} className="flex justify-between border-b border-red-500/5 py-2"><span className="text-xs text-slate-500">{l}</span><span className="text-sm font-bold text-red-400">{v}</span></div>
            ))}
          </div>
          <div className="bg-emerald-500/[0.03] border border-emerald-500/10 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-emerald-400 mb-4 flex items-center gap-2"><span className="w-7 h-7 rounded-full bg-emerald-500/10 flex items-center justify-center text-xs">&#10003;</span>After</h3>
            {[["Calls recovered", "47/month"], ["AI-booked appointments", "19/month"], ["Revenue recovered", "₹1.9L/mo"], ["PatientPlex cost", "₹7,999/mo"], ["Saved vs agency", "₹32,001/mo"]].map(([l, v], i) => (
              <div key={i} className="flex justify-between border-b border-emerald-500/5 py-2"><span className="text-xs text-slate-500">{l}</span><span className="text-sm font-bold text-emerald-400">{v}</span></div>
            ))}
          </div>
        </div>
        <div className="bg-[#0f172a]/40 border border-slate-800 rounded-2xl p-8 text-center max-w-2xl mx-auto">
          <p className="text-base text-slate-300 leading-relaxed italic mb-4">&ldquo;I was paying ₹40,000 to an agency and had no idea if it worked. PatientPlex costs ₹7,999 and I can see every patient it brought me. Last month it booked 19 appointments I would have lost.&rdquo;</p>
          <div className="flex items-center justify-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-black text-xs font-bold">DB</div>
            <div className="text-left"><p className="text-sm font-semibold">Dr. Bhardwaj</p><p className="text-[10px] text-slate-600">Bhardwaj Dental Clinic, Hyderabad</p></div>
          </div>
        </div>
      </section>

      {/* ═══ 8. PRICING ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="pricing">
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
            { name: "Pro Patient Engine", price: tierPrice(9999), features: ["Unlimited conversations", "10 campaigns, all platforms", "Full 17-stage funnel", "SEO landing pages", "Priority support", "ROI dashboard"], pop: true },
            { name: "Clinic Network", price: tierPrice(18999), features: ["Everything in Pro", "Multi-location support", "White-label branding", "Dedicated account manager", "API access", "Custom integrations"], pop: false },
          ].map((p, i) => (
            <div key={i} className={`rounded-2xl p-6 transition relative ${p.pop ? "bg-gradient-to-b from-emerald-500/[0.07] to-transparent border-2 border-emerald-500/30 scale-[1.02]" : "bg-[#0f172a]/40 border border-slate-800 hover:border-slate-700"}`}>
              {p.pop && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-teal-500 text-black text-[10px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">Most Popular</div>}
              <p className="text-xs text-slate-500 mb-1">{p.name}</p>
              <p className="text-3xl font-bold mb-0.5">₹{p.price.toLocaleString("en-IN")}</p>
              <p className="text-[10px] text-slate-600 mb-5">/{annual ? "mo (billed annually)" : "month"}</p>
              <ul className="space-y-2 mb-6">{p.features.map((f, j) => <li key={j} className="text-xs text-slate-400 flex items-start gap-2"><span className="text-emerald-400 mt-0.5">&#10003;</span>{f}</li>)}</ul>
              <button onClick={() => setShowTrialModal(true)} className={`w-full text-center py-2.5 rounded-xl text-sm font-semibold transition ${p.pop ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20" : "bg-slate-900/50 hover:bg-slate-800/50 text-white border border-slate-800"}`}>
                {p.pop ? "Start Free Trial" : "Choose Plan"}
              </button>
            </div>
          ))}
        </div>
        <p className="text-center text-slate-700 text-xs mt-6">All plans include: 14-day free trial &bull; No credit card required &bull; Cancel anytime</p>
      </section>

      {/* ═══ 9. FAQ ═══ */}
      <section className="max-w-3xl mx-auto px-6 py-20" id="faq">
        <div className="text-center mb-10">
          <p className="text-emerald-400 text-xs font-semibold tracking-[3px] uppercase mb-3">FAQ</p>
          <h2 className="text-3xl font-bold">Frequently Asked Questions</h2>
        </div>
        <div className="space-y-0">
          {faqs.map((f, i) => (
            <div key={i} className="border-b border-slate-800/50">
              <button onClick={() => setFaqOpen(faqOpen === i ? null : i)} className="w-full text-left py-4 flex justify-between items-center hover:text-emerald-400 transition gap-4">
                <span className="text-sm font-medium">{f.q}</span>
                <span className="text-slate-600 text-lg flex-shrink-0">{faqOpen === i ? "−" : "+"}</span>
              </button>
              {faqOpen === i && <p className="text-slate-500 text-sm pb-4 leading-relaxed">{f.a}</p>}
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 12. FINAL CTA ═══ */}
      <section className="py-20 px-6 text-center relative">
        <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/[0.03] to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-2xl mx-auto">
          <h2 className="text-4xl font-bold mb-4">Every missed call is a{" "}<span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">patient lost forever.</span></h2>
          <p className="text-slate-500 text-lg mb-8">Start your free trial. Book patients on autopilot. Replace your agency today.</p>
          <button onClick={() => setShowTrialModal(true)} className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-10 py-4 rounded-xl text-lg shadow-2xl shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all inline-flex items-center gap-2">
            Start Free — No Credit Card <span>&rarr;</span>
          </button>
          <p className="text-slate-700 text-xs mt-4">14-day free trial &middot; No contracts &middot; Cancel anytime</p>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="border-t border-slate-800/40 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-[10px] font-bold">P</div>
            <span className="font-semibold text-sm">PatientPlex AI</span>
          </div>
          <p className="text-slate-700 text-xs">Built for Indian healthcare. Replace your agency today.</p>
          <p className="text-slate-800 text-[10px]">&copy; 2026 PatientPlex AI. All rights reserved.</p>
        </div>
      </footer>

      {/* ═══ 10. TRIAL MODAL ═══ */}
      {showTrialModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => { setShowTrialModal(false); setModalSent(false); }} />
          <div className="relative bg-[#0f172a] border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl shadow-black/60">
            <button onClick={() => { setShowTrialModal(false); setModalSent(false); }} className="absolute top-4 right-4 text-slate-600 hover:text-white transition text-lg">&times;</button>
            {!modalSent ? (
              <>
                <h3 className="text-xl font-bold mb-1">Start Your 14-Day Free Trial</h3>
                <p className="text-sm text-slate-500 mb-6">No credit card required. Set up in 5 minutes.</p>
                <form onSubmit={(e) => { e.preventDefault(); setModalSent(true); }} className="space-y-3">
                  <input required placeholder="Doctor Name" className="w-full bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none" />
                  <input required placeholder="Clinic Name" className="w-full bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none" />
                  <select required className="w-full bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-400 focus:border-emerald-500 outline-none">
                    <option value="">Select Specialty</option>
                    <option>Dental & Orthodontics</option>
                    <option>Dermatology & Cosmetology</option>
                    <option>Orthopedics</option>
                    <option>Gynecology</option>
                    <option>Other</option>
                  </select>
                  <input required type="tel" placeholder="Phone / WhatsApp Number" className="w-full bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-slate-700 focus:border-emerald-500 outline-none" />
                  <select required className="w-full bg-[#070a12] border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-400 focus:border-emerald-500 outline-none">
                    <option value="">Select City</option>
                    {["Hyderabad", "Mumbai", "Delhi NCR", "Bengaluru", "Pune", "Chennai", "Kolkata", "Ahmedabad"].map(c => <option key={c}>{c}</option>)}
                  </select>
                  <button type="submit" className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold py-3 rounded-xl text-sm shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition">
                    Start Free Trial &rarr;
                  </button>
                </form>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-3xl mx-auto mb-4">&#10003;</div>
                <h3 className="text-xl font-bold mb-2 text-emerald-400">You&apos;re In!</h3>
                <p className="text-sm text-slate-400 mb-6">Check your WhatsApp — our AI will message you in under 30 seconds to get started.</p>
                <Link href="/signup" className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-8 py-3 rounded-xl text-sm inline-block">Go to Dashboard</Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
