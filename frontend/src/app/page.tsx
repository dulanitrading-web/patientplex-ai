"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useTransform, animate } from "framer-motion";
import {
  ArrowRight, CheckCircle2, Star, Shield, Zap, BarChart3,
  MessageCircle, Calendar, Phone, Globe, Brain, TrendingUp,
  Users, IndianRupee, ChevronDown, ChevronRight, Play,
  Sparkles, Clock, Target, Award, Lock,
} from "lucide-react";

/* ─── Animated counter ─── */
function Counter({ target, suffix = "", prefix = "" }: { target: number; suffix?: string; prefix?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => `${prefix}${Math.round(v).toLocaleString("en-IN")}${suffix}`);
  const [display, setDisplay] = useState(`${prefix}0${suffix}`);

  useEffect(() => {
    if (!isInView) return;
    const controls = animate(count, target, { duration: 2, ease: "easeOut" });
    const unsub = rounded.on("change", (v) => setDisplay(v));
    return () => { controls.stop(); unsub(); };
  }, [isInView, target, count, rounded]);

  return <span ref={ref}>{display}</span>;
}

/* ─── Fade-in wrapper ─── */
function Reveal({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Data ─── */
const STATS = [
  { value: 4200, suffix: "+", label: "Patients booked" },
  { value: 89, suffix: "%", label: "WhatsApp response rate" },
  { value: 12, prefix: "₹", suffix: "", label: "Avg. cost per booking" },
  { value: 26, suffix: "x", label: "LTV to CAC ratio" },
];

const FEATURES = [
  {
    icon: Brain,
    title: "AI WhatsApp receptionist",
    desc: "Claude-powered conversations that qualify leads, answer treatment questions, and book appointments — in Hindi, English, or your patients' language.",
    color: "text-emerald-400",
    hoverColor: "group-hover:text-emerald-300",
    bg: "bg-emerald-500/10",
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    icon: BarChart3,
    title: "Google & Meta ad engine",
    desc: "Hyper-local campaigns that target patients within 5km of your clinic. Auto-optimized bids, A/B tested creatives, quality score tracking.",
    color: "text-cyan-400",
    hoverColor: "group-hover:text-cyan-300",
    bg: "bg-cyan-500/10",
    gradient: "from-cyan-500 to-blue-500",
  },
  {
    icon: Calendar,
    title: "Smart appointment booking",
    desc: "Syncs with Google Calendar. Sends WhatsApp reminders. Detects duplicate bookings. Reduces no-shows by 60% with automated follow-ups.",
    color: "text-violet-400",
    hoverColor: "group-hover:text-violet-300",
    bg: "bg-violet-500/10",
    gradient: "from-violet-500 to-purple-500",
  },
  {
    icon: Phone,
    title: "Call tracking & recovery",
    desc: "Every missed call becomes a WhatsApp follow-up. IVR routing, call recording, and conversion attribution — know which ad drove which patient.",
    color: "text-amber-400",
    hoverColor: "group-hover:text-amber-300",
    bg: "bg-amber-500/10",
    gradient: "from-amber-500 to-orange-500",
  },
  {
    icon: Globe,
    title: "SEO landing pages",
    desc: "Treatment-specific pages optimized for Google Ads quality score. Schema.org medical markup. Mobile-first. Generated from your clinic profile.",
    color: "text-rose-400",
    hoverColor: "group-hover:text-rose-300",
    bg: "bg-rose-500/10",
    gradient: "from-rose-500 to-pink-500",
  },
  {
    icon: TrendingUp,
    title: "Conversion analytics",
    desc: "Full-funnel visibility: ad click → WhatsApp enquiry → appointment → attended. See exactly which treatments and campaigns bring ROI.",
    color: "text-sky-400",
    hoverColor: "group-hover:text-sky-300",
    bg: "bg-sky-500/10",
    gradient: "from-sky-500 to-indigo-500",
  },
];

const TESTIMONIALS = [
  {
    name: "Dr. Priya Sharma",
    role: "Cosmetic Dentist, Mumbai",
    text: "We went from 3 new patients a week to 18. The WhatsApp AI handles enquiries at 2am better than my receptionist at 2pm. Our cost per patient dropped from ₹800 to ₹120.",
    avatar: "PS",
    metric: "6x more patients",
  },
  {
    name: "Dr. Rajesh Mehta",
    role: "Dermatologist, Delhi",
    text: "I was spending ₹50,000/month on agencies with zero transparency. PatientPlex shows me exactly where every rupee goes. My Google Ads quality score went from 4 to 9.",
    avatar: "RM",
    metric: "₹50K saved monthly",
  },
  {
    name: "Dr. Ananya Reddy",
    role: "Orthodontist, Bengaluru",
    text: "The no-show rate at my clinic dropped from 28% to 4%. The WhatsApp reminders and the AI follow-up system are genuinely better than anything I've tried.",
    avatar: "AR",
    metric: "4% no-show rate",
  },
];

const PRICING = [
  {
    name: "Starter",
    price: "4,999",
    period: "/mo",
    desc: "For solo practitioners starting with digital patient acquisition",
    features: ["Google Ads management", "WhatsApp AI (500 conversations)", "5 landing pages", "Basic analytics", "Email support"],
    cta: "Start free trial",
    highlight: false,
  },
  {
    name: "Growth",
    price: "14,999",
    period: "/mo",
    desc: "For clinics ready to scale patient volume predictably",
    features: ["Google + Meta Ads", "WhatsApp AI (unlimited)", "Unlimited landing pages", "Call tracking", "Conversion funnel analytics", "Priority WhatsApp support", "Google Calendar sync"],
    cta: "Start free trial",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "24,999",
    period: "/mo",
    desc: "For multi-location clinics and hospital chains",
    features: ["Everything in Growth", "Multi-location management", "Custom AI training", "Dedicated account manager", "API access", "HIPAA-grade audit logs", "Custom integrations"],
    cta: "Contact sales",
    highlight: false,
  },
];

const FAQS = [
  { q: "How quickly will I see new patients?", a: "Most clinics see their first AI-booked appointment within 48 hours of going live. Campaigns take 3–5 days to optimize fully, and you'll typically see consistent patient flow by week two." },
  { q: "Do I need to manage the ads myself?", a: "No. PatientPlex creates, launches, and optimizes your Google and Meta ad campaigns automatically. You set your budget and target treatments — the AI handles everything else." },
  { q: "What happens when a patient messages on WhatsApp?", a: "Our AI receptionist responds instantly in the patient's language. It answers treatment questions using your clinic's actual information, checks your calendar availability, and books the appointment — all without you lifting a finger." },
  { q: "Is my patient data secure?", a: "Yes. All data is encrypted at rest and in transit. We use Fernet symmetric encryption for OAuth tokens, HMAC-SHA256 for webhook verification, and maintain full audit logs. We're built for healthcare compliance from day one." },
  { q: "Can I try it before committing?", a: "Absolutely. Every plan starts with a 14-day free trial. No credit card required. You'll have a working campaign with real patient enquiries before you pay anything." },
  { q: "What if I already have a website?", a: "PatientPlex landing pages work alongside your existing website. They're specifically optimized for ad traffic — higher quality scores mean lower cost per click. Your main website stays exactly as it is." },
];

/* ─── Dashboard mockup data ─── */
const MOCK_METRICS = [
  { label: "Monthly ROAS", value: "4.2x", change: "+0.3" },
  { label: "Cost / booking", value: "₹12.40", change: "-₹2.10" },
  { label: "WhatsApp conv.", value: "89.4%", change: "+3.1%" },
  { label: "Booked this month", value: "1,848", change: "+312" },
];

const MOCK_QUEUE = [
  { name: "Priya S.", treatment: "Laser hair removal", time: "Just now", amount: "₹12,500" },
  { name: "Rajesh K.", treatment: "Root canal & crown", time: "2m ago", amount: "₹8,500" },
  { name: "Ananya R.", treatment: "Acne scar treatment", time: "5m ago", amount: "₹16,000" },
  { name: "Vikram P.", treatment: "Teeth whitening", time: "8m ago", amount: "₹5,500" },
];

/* ═══════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 80);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#0A0E1A] text-slate-100 overflow-x-hidden">
      {/* ─── Keyframes ─── */}
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -20px) scale(1.05); }
          66% { transform: translate(-20px, 15px) scale(0.95); }
        }
        @keyframes float-slower {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-40px, 25px) scale(1.08); }
        }
        @keyframes float-particle {
          0%, 100% { transform: translateY(0) scale(1); opacity: 0.4; }
          50% { transform: translateY(-20px) scale(1.2); opacity: 0.8; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .animate-float-slow { animation: float-slow 12s ease-in-out infinite; }
        .animate-float-slower { animation: float-slower 16s ease-in-out infinite; }
        .animate-float-particle-1 { animation: float-particle 4s ease-in-out infinite; }
        .animate-float-particle-2 { animation: float-particle 5s ease-in-out infinite 1s; }
        .animate-float-particle-3 { animation: float-particle 6s ease-in-out infinite 2s; }
        .animate-float-particle-4 { animation: float-particle 3.5s ease-in-out infinite 0.5s; }
        .badge-shimmer {
          background: linear-gradient(110deg, #10B981 0%, #10B981 40%, #34d399 50%, #10B981 60%, #10B981 100%);
          background-size: 200% 100%;
          animation: shimmer 3s ease-in-out infinite;
        }
        .hero-grid {
          background-image:
            repeating-linear-gradient(0deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 60px),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 60px);
        }
      `}</style>

      {/* ─── Nav ─── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 bg-[#0A0E1A]/80 backdrop-blur-xl transition-all duration-500 ${
        scrolled
          ? "border-b border-emerald-500/10 shadow-[0_1px_20px_rgba(16,185,129,0.06)]"
          : "border-b border-white/5"
      }`}>
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-400 flex items-center justify-center">
              <span className="text-[#0A0E1A] font-bold text-sm">P</span>
            </div>
            <span className="font-semibold text-lg tracking-tight">PatientPlex</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-slate-400 hover:text-white transition-colors hidden sm:block">
              Sign in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-medium px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] transition-colors"
            >
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* ─── Hero ─── */}
      <section className="pt-32 pb-20 px-6 relative">
        {/* Grid pattern */}
        <div className="absolute inset-0 hero-grid pointer-events-none" />

        {/* Floating gradient orbs */}
        <div className="absolute top-20 left-1/4 w-[600px] h-[500px] bg-emerald-500/[0.07] rounded-full blur-[120px] pointer-events-none animate-float-slow" />
        <div className="absolute top-40 right-1/4 w-[500px] h-[400px] bg-cyan-500/[0.05] rounded-full blur-[100px] pointer-events-none animate-float-slower" />
        <div className="absolute bottom-20 left-1/3 w-[400px] h-[300px] bg-violet-500/[0.04] rounded-full blur-[100px] pointer-events-none animate-float-slow" style={{ animationDelay: "4s" }} />

        <div className="max-w-6xl mx-auto relative">
          <div className="max-w-2xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm mb-6">
                <Sparkles className="w-3.5 h-3.5" />
                Built for Indian clinics
              </div>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] mb-6"
            >
              Stop paying agencies.
              <br />
              <span className="text-emerald-400">Start getting patients.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-lg text-slate-400 leading-relaxed mb-8 max-w-lg"
            >
              AI-powered Google & Meta ads, a WhatsApp receptionist that never sleeps,
              and appointment booking that fills your calendar — all for less than what
              you pay your current agency.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-3"
            >
              <Link
                href="/signup"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] font-semibold transition-colors"
              >
                Start free 14-day trial <ArrowRight className="w-4 h-4" />
              </Link>
              <button className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-white/10 hover:border-white/20 text-slate-300 hover:text-white transition-colors">
                <Play className="w-4 h-4" /> Watch 2-min demo
              </button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="flex items-center gap-6 mt-8 text-sm text-slate-500"
            >
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> No credit card</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Setup in 10 min</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Cancel anytime</span>
            </motion.div>
          </div>

          {/* Dashboard preview — interactive hover */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-16 rounded-xl border border-white/10 bg-[#0F172A] overflow-hidden shadow-2xl shadow-emerald-500/5 hover:border-emerald-500/20 hover:shadow-emerald-500/10 hover:shadow-2xl transition-all duration-500 hover:scale-[1.01]"
          >
            {/* Window chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                <div className="w-3 h-3 rounded-full bg-amber-500/60" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/60" />
              </div>
              <div className="flex-1 flex justify-center">
                <div className="px-4 py-1 rounded-md bg-white/5 text-xs text-slate-500 font-mono">
                  app.patientplex.ai/dashboard
                </div>
              </div>
            </div>

            {/* Dashboard content */}
            <div className="p-6">
              {/* Metrics row */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {MOCK_METRICS.map((m, i) => (
                  <div key={i} className="p-4 rounded-lg bg-white/[0.03] border border-white/5">
                    <div className="text-xs text-slate-500 mb-1">{m.label}</div>
                    <div className="text-xl font-bold text-white tabular-nums">{m.value}</div>
                    <div className="text-xs text-emerald-400 mt-1">↑ {m.change}</div>
                  </div>
                ))}
              </div>

              {/* Patient queue */}
              <div className="rounded-lg bg-white/[0.03] border border-white/5 overflow-hidden">
                <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-300">Live patient queue</span>
                  <span className="text-xs text-emerald-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Streaming
                  </span>
                </div>
                {MOCK_QUEUE.map((p, i) => (
                  <div key={i} className="px-4 py-3 flex items-center justify-between border-b border-white/[0.03] last:border-0">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center text-xs font-medium text-emerald-400">
                        {p.name[0]}
                      </div>
                      <div>
                        <div className="text-sm text-slate-200">{p.treatment}</div>
                        <div className="text-xs text-slate-500">{p.name} · {p.time}</div>
                      </div>
                    </div>
                    <span className="text-sm font-medium text-emerald-400 tabular-nums">{p.amount}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ─── Stats ─── */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent mb-16" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {STATS.map((s, i) => (
              <Reveal key={i} delay={i * 0.1} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-white mb-1 tabular-nums">
                  <Counter target={s.value} suffix={s.suffix} prefix={s.prefix} />
                </div>
                <div className="text-sm text-slate-500">{s.label}</div>
              </Reveal>
            ))}
          </div>
          <div className="h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent mt-16" />
        </div>
      </section>

      {/* ─── Problem → Solution ─── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <Reveal>
            <div className="max-w-2xl mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Your receptionist can{"'"}t answer at midnight.
                <br />
                <span className="text-slate-500">Your AI can.</span>
              </h2>
              <p className="text-slate-400 leading-relaxed">
                70% of patient enquiries come outside clinic hours. Every missed WhatsApp
                message is a patient who books with your competitor instead. PatientPlex
                makes sure that never happens.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Clock, title: "Before PatientPlex", items: ["Missed calls after hours", "₹800+ per new patient", "No idea which ads work", "Manual appointment reminders", "28% no-show rate"], bad: true },
              { icon: Zap, title: "After PatientPlex", items: ["24/7 AI WhatsApp receptionist", "₹12 per booking", "Full-funnel attribution", "Automated reminders", "4% no-show rate"], bad: false },
              { icon: Target, title: "The difference", items: ["6x more patients", "₹50K+ saved monthly", "90% less manual work", "Real-time patient pipeline", "Predictable growth"], bad: false, highlight: true },
            ].map((col, i) => (
              <Reveal key={i} delay={i * 0.15}>
                <div className={`p-6 rounded-xl border h-full ${
                  col.highlight
                    ? "border-emerald-500/30 bg-emerald-500/5"
                    : col.bad
                      ? "border-white/5 bg-white/[0.02]"
                      : "border-white/5 bg-white/[0.02]"
                }`}>
                  <div className={`inline-flex items-center gap-2 mb-4 ${col.highlight ? "text-emerald-400" : col.bad ? "text-red-400" : "text-cyan-400"}`}>
                    <col.icon className="w-5 h-5" />
                    <span className="font-semibold">{col.title}</span>
                  </div>
                  <ul className="space-y-3">
                    {col.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-slate-300">
                        {col.bad ? (
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500/60 mt-1.5 shrink-0" />
                        ) : (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                        )}
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features ─── */}
      <section id="features" className="py-24 px-6 bg-[#0C1020]">
        <div className="max-w-6xl mx-auto">
          <Reveal>
            <div className="max-w-2xl mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Everything your clinic needs to grow
              </h2>
              <p className="text-slate-400 leading-relaxed">
                From the first ad impression to the patient sitting in your chair —
                PatientPlex handles the entire journey.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((f, i) => (
              <Reveal key={i} delay={(i % 3) * 0.1}>
                <div className="group relative p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.04] transition-all duration-300 h-full overflow-hidden">
                  {/* Gradient top border on hover */}
                  <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${f.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                  <div className={`inline-flex p-2.5 rounded-lg ${f.bg} mb-4`}>
                    <f.icon className={`w-5 h-5 ${f.color} ${f.hoverColor} transition-colors duration-300`} />
                  </div>
                  <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How it works ─── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <Reveal>
            <div className="max-w-2xl mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Live in 10 minutes, not 10 weeks
              </h2>
              <p className="text-slate-400 leading-relaxed">
                No agencies, no contracts, no technical setup. Enter your clinic details
                and PatientPlex does the rest.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Tell us about your clinic", desc: "Specialty, location, treatments, budget. Takes about 3 minutes. We'll generate your landing pages and ad creatives automatically.", icon: Users },
              { step: "2", title: "Connect WhatsApp & Calendar", desc: "Link your clinic's WhatsApp Business number and Google Calendar. The AI receptionist starts handling enquiries immediately.", icon: MessageCircle },
              { step: "3", title: "Patients start booking", desc: "Campaigns go live within hours. The AI qualifies leads, books appointments, and sends reminders. You focus on patient care.", icon: Calendar },
            ].map((s, i) => (
              <Reveal key={i} delay={i * 0.15}>
                <div className="relative">
                  <div className="text-6xl font-bold text-white/[0.04] mb-4">{s.step}</div>
                  <div className="inline-flex p-2 rounded-lg bg-emerald-500/10 mb-3">
                    <s.icon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <h3 className="font-semibold text-white mb-2">{s.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Testimonials ─── */}
      <section className="py-24 px-6 bg-[#0C1020]">
        <div className="max-w-6xl mx-auto">
          <Reveal>
            <div className="max-w-2xl mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Trusted by clinics across India
              </h2>
              <p className="text-slate-400">
                Hear from doctors who switched from agencies to PatientPlex.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="relative p-6 rounded-xl border border-white/5 bg-white/[0.02] h-full flex flex-col overflow-hidden">
                  {/* Decorative quote mark */}
                  <span className="absolute top-4 left-5 text-6xl leading-none text-white/[0.04] font-serif pointer-events-none select-none">{"“"}</span>
                  <div className="flex items-center gap-1 mb-4 relative">
                    {[...Array(5)].map((_, j) => (
                      <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed flex-1 mb-6 relative">
                    {`"${t.text}"`}
                  </p>
                  <div className="flex items-center justify-between pt-4 border-t border-white/5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center text-sm font-semibold text-emerald-400">
                        {t.avatar}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white">{t.name}</div>
                        <div className="text-xs text-slate-500">{t.role}</div>
                      </div>
                    </div>
                    <div className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-xs font-medium text-emerald-400">
                      {t.metric}
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Pricing ─── */}
      <section id="pricing" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <Reveal>
            <div className="text-center max-w-2xl mx-auto mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Simple pricing, real results
              </h2>
              <p className="text-slate-400">
                Every plan includes a 14-day free trial. No credit card required.
                Your ad budget is separate and goes directly to Google/Meta.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PRICING.map((p, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className={`p-6 rounded-xl border h-full flex flex-col ${
                  p.highlight
                    ? "border-emerald-500/30 bg-emerald-500/[0.04] relative shadow-lg shadow-emerald-500/[0.06]"
                    : "border-white/5 bg-white/[0.02]"
                }`}>
                  {p.highlight && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full badge-shimmer text-[#0A0E1A] text-xs font-semibold">
                      Most popular
                    </div>
                  )}
                  <div className="mb-6">
                    <h3 className="font-semibold text-white mb-1">{p.name}</h3>
                    <p className="text-xs text-slate-500 mb-4">{p.desc}</p>
                    <div className="flex items-baseline gap-1">
                      <span className="text-sm text-slate-400">₹</span>
                      <span className="text-4xl font-bold text-white tabular-nums">{p.price}</span>
                      <span className="text-sm text-slate-500">{p.period}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-8 flex-1">
                    {p.features.map((f, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-slate-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Link
                    href="/signup"
                    className={`block text-center py-3 rounded-lg font-medium text-sm transition-colors ${
                      p.highlight
                        ? "bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A]"
                        : "border border-white/10 hover:border-white/20 text-slate-300 hover:text-white"
                    }`}
                  >
                    {p.cta}
                  </Link>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Security ─── */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent mb-16" />
          <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-slate-500">
            {[
              { icon: Shield, text: "End-to-end encryption" },
              { icon: Lock, text: "HMAC-SHA256 webhooks" },
              { icon: Award, text: "Healthcare-grade audit logs" },
              { icon: Shield, text: "SOC 2 aligned" },
            ].map((b, i) => (
              <div key={i} className="flex items-center gap-2">
                <b.icon className="w-4 h-4 text-emerald-500/60" />
                {b.text}
              </div>
            ))}
          </div>
          <div className="h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent mt-16" />
        </div>
      </section>

      {/* ─── FAQ ─── */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Reveal>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-12">
              Common questions
            </h2>
          </Reveal>

          <div className="space-y-2">
            {FAQS.map((faq, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full text-left p-5 rounded-xl border border-white/5 hover:border-white/10 bg-white/[0.02] transition-colors"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-medium text-white">{faq.q}</span>
                    <ChevronDown className={`w-5 h-5 text-slate-500 shrink-0 transition-transform duration-200 ${openFaq === i ? "rotate-180" : ""}`} />
                  </div>
                  {openFaq === i && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      transition={{ duration: 0.2 }}
                      className="mt-3 text-sm text-slate-400 leading-relaxed"
                    >
                      {faq.a}
                    </motion.div>
                  )}
                </button>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Final CTA ─── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="relative rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/[0.08] to-cyan-500/[0.04] p-12 sm:p-16 text-center overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.1),transparent_70%)]" />
            {/* Floating particles */}
            <div className="absolute top-8 left-[15%] w-2 h-2 rounded-full bg-emerald-400/30 animate-float-particle-1" />
            <div className="absolute top-16 right-[20%] w-1.5 h-1.5 rounded-full bg-cyan-400/25 animate-float-particle-2" />
            <div className="absolute bottom-12 left-[30%] w-2.5 h-2.5 rounded-full bg-emerald-400/20 animate-float-particle-3" />
            <div className="absolute bottom-20 right-[25%] w-1.5 h-1.5 rounded-full bg-cyan-400/30 animate-float-particle-4" />
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                Your competitor{"'"}s patients are looking
                <br className="hidden sm:block" /> for you right now
              </h2>
              <p className="text-slate-400 mb-8 max-w-lg mx-auto">
                Every day without PatientPlex is another day of missed enquiries,
                wasted ad spend, and patients going elsewhere.
              </p>
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 px-8 py-4 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] font-semibold text-lg transition-colors"
              >
                Start free trial <ArrowRight className="w-5 h-5" />
              </Link>
              <p className="text-sm text-slate-500 mt-4">
                14 days free · No credit card · Cancel anytime
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="py-12 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-400 flex items-center justify-center">
              <span className="text-[#0A0E1A] font-bold text-xs">P</span>
            </div>
            <span className="font-semibold text-sm">PatientPlex AI</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <a href="#" className="hover:text-slate-300 transition-colors">Privacy</a>
            <a href="#" className="hover:text-slate-300 transition-colors">Terms</a>
            <a href="#" className="hover:text-slate-300 transition-colors">Contact</a>
          </div>
          <p className="text-xs text-slate-600">
            © 2026 PatientPlex AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
