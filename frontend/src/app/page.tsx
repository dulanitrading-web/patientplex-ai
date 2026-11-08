"use client";

import { useState, useEffect, useRef, ReactNode } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useTransform, animate, useScroll, useSpring } from "framer-motion";
import {
  ArrowRight, CheckCircle2, Star, Shield, Zap, BarChart3,
  MessageCircle, Calendar, Phone, Globe, Brain, TrendingUp,
  Users, ChevronDown, Play, Sparkles, Clock, Target, Award, Lock,
  ArrowUpRight, Stethoscope, Activity, HeartPulse, MousePointerClick,
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
    const controls = animate(count, target, { duration: 2.2, ease: [0.16, 1, 0.3, 1] });
    const unsub = rounded.on("change", (v) => setDisplay(v));
    return () => { controls.stop(); unsub(); };
  }, [isInView, target, count, rounded]);

  return <span ref={ref}>{display}</span>;
}

/* ─── Reveal wrapper ─── */
function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Marquee for social proof ─── */
function Marquee({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`overflow-hidden ${className}`}>
      <div className="flex animate-marquee whitespace-nowrap">
        {children}
        {children}
      </div>
    </div>
  );
}

/* ─── Data ─── */
const STATS = [
  { value: 4200, suffix: "+", label: "Patients booked", icon: Users },
  { value: 89, suffix: "%", label: "WhatsApp response rate", icon: MessageCircle },
  { value: 12, prefix: "₹", suffix: "", label: "Avg. cost per booking", icon: Target },
  { value: 26, suffix: "x", label: "LTV to CAC ratio", icon: TrendingUp },
];

const FEATURES = [
  {
    icon: Brain, title: "AI WhatsApp Receptionist",
    desc: "Claude-powered conversations that qualify leads, answer treatment questions, and book appointments — in Hindi, English, or your patients' language. Never misses an enquiry.",
    color: "emerald", gradient: "from-emerald-500 to-teal-400",
    details: ["24/7 multilingual responses", "Smart lead qualification", "Instant appointment booking", "Treatment FAQ automation"],
  },
  {
    icon: BarChart3, title: "Google & Meta Ad Engine",
    desc: "Hyper-local campaigns that target patients within 5km of your clinic. Auto-optimized bids, A/B tested creatives, and quality score tracking — all on autopilot.",
    color: "cyan", gradient: "from-cyan-500 to-blue-400",
    details: ["Geo-targeted patient ads", "Auto-optimized bidding", "A/B tested creatives", "Quality score tracking"],
  },
  {
    icon: Calendar, title: "Smart Appointment Booking",
    desc: "Syncs with Google Calendar. Sends WhatsApp reminders. Detects duplicate bookings. Reduces no-shows by 60% with automated follow-ups and rescheduling.",
    color: "violet", gradient: "from-violet-500 to-purple-400",
    details: ["Google Calendar sync", "WhatsApp reminders", "60% fewer no-shows", "Auto rescheduling"],
  },
  {
    icon: Phone, title: "Call Tracking & Recovery",
    desc: "Every missed call becomes a WhatsApp follow-up. IVR routing, call recording, and conversion attribution — know which ad drove which patient.",
    color: "amber", gradient: "from-amber-500 to-orange-400",
    details: ["Missed call recovery", "IVR call routing", "Full call recording", "Ad attribution"],
  },
  {
    icon: Globe, title: "SEO Landing Pages",
    desc: "Treatment-specific pages optimized for Google Ads quality score. Medical schema markup. Mobile-first design. Auto-generated from your clinic profile.",
    color: "rose", gradient: "from-rose-500 to-pink-400",
    details: ["Treatment-specific pages", "Medical schema markup", "Mobile-first design", "Auto-generated content"],
  },
  {
    icon: TrendingUp, title: "Conversion Analytics",
    desc: "Full-funnel visibility: ad click → WhatsApp enquiry → appointment → attended. See exactly which treatments and campaigns bring the highest ROI.",
    color: "sky", gradient: "from-sky-500 to-indigo-400",
    details: ["Full-funnel tracking", "Treatment-level ROI", "Campaign attribution", "Revenue forecasting"],
  },
];

const TESTIMONIALS = [
  {
    name: "Dr. Priya Sharma", role: "Cosmetic Dentist, Mumbai",
    text: "We went from 3 new patients a week to 18. The WhatsApp AI handles enquiries at 2am better than my receptionist at 2pm. Our cost per patient dropped from ₹800 to ₹120.",
    avatar: "PS", metric: "6x more patients", rating: 5,
  },
  {
    name: "Dr. Rajesh Mehta", role: "Dermatologist, Delhi",
    text: "I was spending ₹50,000/month on agencies with zero transparency. PatientPlex shows me exactly where every rupee goes. My Google Ads quality score went from 4 to 9.",
    avatar: "RM", metric: "₹50K saved monthly", rating: 5,
  },
  {
    name: "Dr. Ananya Reddy", role: "Orthodontist, Bengaluru",
    text: "The no-show rate at my clinic dropped from 28% to 4%. The WhatsApp reminders and the AI follow-up system are genuinely better than anything I've tried.",
    avatar: "AR", metric: "4% no-show rate", rating: 5,
  },
];

const PRICING = [
  {
    name: "Starter", price: "4,999", period: "/mo",
    desc: "For solo practitioners starting with digital patient acquisition",
    features: ["Google Ads management", "WhatsApp AI (500 conversations)", "5 landing pages", "Basic analytics", "Email support"],
    cta: "Start free trial", highlight: false,
  },
  {
    name: "Growth", price: "14,999", period: "/mo",
    desc: "For clinics ready to scale patient volume predictably",
    features: ["Google + Meta Ads", "WhatsApp AI (unlimited)", "Unlimited landing pages", "Call tracking", "Conversion funnel analytics", "Priority WhatsApp support", "Google Calendar sync"],
    cta: "Start free trial", highlight: true, badge: "Most popular",
  },
  {
    name: "Enterprise", price: "24,999", period: "/mo",
    desc: "For multi-location clinics and hospital chains",
    features: ["Everything in Growth", "Multi-location management", "Custom AI training", "Dedicated account manager", "API access", "HIPAA-grade audit logs", "Custom integrations"],
    cta: "Contact sales", highlight: false,
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

const MOCK_METRICS = [
  { label: "Monthly ROAS", value: "4.2x", change: "+0.3", icon: TrendingUp },
  { label: "Cost / booking", value: "₹12.40", change: "-₹2.10", icon: Target },
  { label: "WhatsApp conv.", value: "89.4%", change: "+3.1%", icon: MessageCircle },
  { label: "Booked this month", value: "1,848", change: "+312", icon: Calendar },
];

const MOCK_QUEUE = [
  { name: "Priya S.", treatment: "Laser hair removal", time: "Just now", amount: "₹12,500", status: "confirmed" },
  { name: "Rajesh K.", treatment: "Root canal & crown", time: "2m ago", amount: "₹8,500", status: "confirmed" },
  { name: "Ananya R.", treatment: "Acne scar treatment", time: "5m ago", amount: "₹16,000", status: "pending" },
  { name: "Vikram P.", treatment: "Teeth whitening", time: "8m ago", amount: "₹5,500", status: "confirmed" },
];

const CLINIC_NAMES = [
  "SmileCraft Dental", "DermGlow Clinic", "OrthoElite", "SkinFirst Dermatology",
  "PearlSmile Dental", "ClearSkin Clinic", "BrightBite Orthodontics", "RadiantDerm",
  "GentleCare Dental", "SkinRevive Clinic", "PrimeDent", "GlowUp Dermatology",
];

/* ═══════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [activeFeature, setActiveFeature] = useState(0);
  const [scrolled, setScrolled] = useState(false);
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, 60]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 80);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Auto-rotate features
  useEffect(() => {
    const timer = setInterval(() => setActiveFeature((p) => (p + 1) % FEATURES.length), 5000);
    return () => clearInterval(timer);
  }, []);

  const f = FEATURES[activeFeature];

  return (
    <div className="min-h-screen bg-[#060910] text-slate-100 overflow-x-hidden">
      {/* ─── Global styles ─── */}
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
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(16,185,129,0.1); }
          50% { box-shadow: 0 0 40px rgba(16,185,129,0.2); }
        }
        @keyframes gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .animate-float-slow { animation: float-slow 12s ease-in-out infinite; }
        .animate-float-slower { animation: float-slower 16s ease-in-out infinite; }
        .animate-marquee { animation: marquee 40s linear infinite; }
        .animate-pulse-glow { animation: pulse-glow 3s ease-in-out infinite; }
        .animate-gradient { animation: gradient-shift 8s ease infinite; background-size: 200% 200%; }
        .badge-shimmer {
          background: linear-gradient(110deg, #10B981 0%, #10B981 40%, #34d399 50%, #10B981 60%, #10B981 100%);
          background-size: 200% 100%;
          animation: shimmer 3s ease-in-out infinite;
        }
        .noise-overlay {
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        }
        .hero-mesh {
          background:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(16,185,129,0.12), transparent),
            radial-gradient(ellipse 60% 40% at 80% 50%, rgba(6,182,212,0.08), transparent),
            radial-gradient(ellipse 50% 60% at 20% 80%, rgba(139,92,246,0.06), transparent);
        }
        .text-gradient {
          background: linear-gradient(135deg, #10B981, #06B6D4, #8B5CF6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .card-3d {
          transform-style: preserve-3d;
          perspective: 1000px;
        }
        .glass {
          background: rgba(15,23,42,0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
        }
        .border-glow {
          position: relative;
        }
        .border-glow::before {
          content: '';
          position: absolute;
          inset: -1px;
          border-radius: inherit;
          padding: 1px;
          background: linear-gradient(135deg, rgba(16,185,129,0.3), transparent, rgba(6,182,212,0.3));
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          pointer-events: none;
        }
      `}</style>

      {/* ─── Noise texture overlay ─── */}
      <div className="fixed inset-0 noise-overlay pointer-events-none z-[1]" />

      {/* ─── Nav ─── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "glass border-b border-white/[0.06] shadow-xl shadow-black/20"
          : "bg-transparent"
      }`}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-400 to-cyan-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:shadow-emerald-500/40 transition-shadow">
              <span className="text-[#060910] font-black text-sm">P</span>
            </div>
            <span className="font-bold text-lg tracking-tight">PatientPlex</span>
          </Link>
          <div className="hidden md:flex items-center gap-1 text-sm">
            {["Features", "Pricing", "FAQ"].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all">{item}</a>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-slate-400 hover:text-white transition-colors hidden sm:block px-3 py-2">
              Sign in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-semibold px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-[#060910] transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98]"
            >
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══ HERO ═══ */}
      <section ref={heroRef} className="relative min-h-screen flex items-center pt-16">
        {/* Mesh gradient background */}
        <div className="absolute inset-0 hero-mesh" />
        {/* Animated orbs */}
        <div className="absolute top-20 left-1/4 w-[700px] h-[600px] bg-emerald-500/[0.07] rounded-full blur-[150px] pointer-events-none animate-float-slow" />
        <div className="absolute top-60 right-1/4 w-[600px] h-[500px] bg-cyan-500/[0.05] rounded-full blur-[120px] pointer-events-none animate-float-slower" />
        <div className="absolute bottom-40 left-1/3 w-[500px] h-[400px] bg-violet-500/[0.04] rounded-full blur-[120px] pointer-events-none animate-float-slow" style={{ animationDelay: "4s" }} />

        <motion.div style={{ opacity: heroOpacity, scale: heroScale, y: heroY }} className="max-w-7xl mx-auto px-6 w-full relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left column — copy */}
            <div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-emerald-500/20 text-emerald-400 text-sm mb-8">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="font-medium">AI-powered patient acquisition for Indian clinics</span>
                </div>
              </motion.div>

              <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
                className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.05] mb-8"
              >
                Stop paying
                <br />
                agencies.
                <br />
                <span className="text-gradient">Start getting</span>
                <br />
                <span className="text-gradient">patients.</span>
              </motion.h1>

              <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
                className="text-lg sm:text-xl text-slate-400 leading-relaxed mb-10 max-w-lg"
              >
                AI-powered ads, a WhatsApp receptionist that never sleeps, and
                appointment booking that fills your calendar — for less than your agency costs.
              </motion.p>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.3 }}
                className="flex flex-col sm:flex-row gap-4"
              >
                <Link href="/signup"
                  className="group inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-[#060910] font-bold text-lg transition-all shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98]"
                >
                  Start free 14-day trial
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="group inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl glass border border-white/10 hover:border-white/20 text-slate-300 hover:text-white transition-all">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-white/20 transition-colors">
                    <Play className="w-3.5 h-3.5 ml-0.5" />
                  </div>
                  Watch demo
                </button>
              </motion.div>

              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.5 }}
                className="flex flex-wrap items-center gap-x-6 gap-y-2 mt-8 text-sm text-slate-500"
              >
                {["No credit card required", "Setup in 10 minutes", "Cancel anytime"].map((t, i) => (
                  <span key={i} className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500/70" /> {t}
                  </span>
                ))}
              </motion.div>
            </div>

            {/* Right column — dashboard mockup */}
            <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.4 }}
              className="hidden lg:block"
            >
              <div className="relative">
                {/* Glow behind card */}
                <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-violet-500/10 rounded-3xl blur-2xl" />

                <div className="relative rounded-2xl border border-white/10 glass overflow-hidden shadow-2xl animate-pulse-glow">
                  {/* Window chrome */}
                  <div className="flex items-center gap-2 px-5 py-3.5 border-b border-white/[0.06]">
                    <div className="flex gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500/70" />
                      <div className="w-3 h-3 rounded-full bg-amber-500/70" />
                      <div className="w-3 h-3 rounded-full bg-emerald-500/70" />
                    </div>
                    <div className="flex-1 flex justify-center">
                      <div className="px-4 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs text-slate-500 font-mono flex items-center gap-2">
                        <Lock className="w-3 h-3" />
                        app.patientplex.ai/dashboard
                      </div>
                    </div>
                  </div>

                  {/* Dashboard content */}
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-5">
                      <div>
                        <p className="text-xs text-slate-500">Good evening, Dr. Sharma</p>
                        <p className="text-sm font-semibold text-white">Dashboard Overview</p>
                      </div>
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                        <Activity className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-xs font-medium text-emerald-400">Live</span>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-3 mb-5">
                      {MOCK_METRICS.map((m, i) => (
                        <div key={i} className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-emerald-500/20 transition-colors">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[11px] text-slate-500 uppercase tracking-wider">{m.label}</span>
                            <m.icon className="w-3.5 h-3.5 text-slate-600" />
                          </div>
                          <div className="text-lg font-bold text-white tabular-nums">{m.value}</div>
                          <div className="text-[11px] text-emerald-400 mt-0.5 font-medium">↑ {m.change}</div>
                        </div>
                      ))}
                    </div>

                    {/* Patient queue */}
                    <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] overflow-hidden">
                      <div className="px-4 py-2.5 border-b border-white/[0.06] flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Live Patient Queue</span>
                        <span className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Streaming
                        </span>
                      </div>
                      {MOCK_QUEUE.map((p, i) => (
                        <div key={i} className="px-4 py-2.5 flex items-center justify-between border-b border-white/[0.03] last:border-0 hover:bg-white/[0.02] transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center text-[10px] font-bold text-emerald-400">
                              {p.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <div>
                              <div className="text-xs font-medium text-slate-200">{p.treatment}</div>
                              <div className="text-[10px] text-slate-500">{p.name} · {p.time}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold text-emerald-400 tabular-nums">{p.amount}</span>
                            <div className={`text-[9px] mt-0.5 font-medium ${p.status === 'confirmed' ? 'text-emerald-500' : 'text-amber-500'}`}>
                              {p.status === 'confirmed' ? '✓ Confirmed' : '● Pending'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* ═══ SOCIAL PROOF MARQUEE ═══ */}
      <section className="py-12 border-y border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-6 mb-6">
          <p className="text-center text-xs text-slate-500 uppercase tracking-widest font-medium">Trusted by 200+ clinics across India</p>
        </div>
        <Marquee>
          {CLINIC_NAMES.map((name, i) => (
            <div key={i} className="flex items-center gap-2.5 mx-8 text-slate-600 whitespace-nowrap">
              <div className="w-8 h-8 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center">
                <Stethoscope className="w-4 h-4 text-slate-500" />
              </div>
              <span className="text-sm font-medium">{name}</span>
            </div>
          ))}
        </Marquee>
      </section>

      {/* ═══ STATS ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {STATS.map((s, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="relative p-6 rounded-2xl glass border border-white/[0.06] text-center group hover:border-emerald-500/20 transition-all duration-300">
                  <div className="inline-flex p-2.5 rounded-xl bg-emerald-500/10 mb-4">
                    <s.icon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div className="text-3xl sm:text-4xl font-black text-white mb-1 tabular-nums">
                    <Counter target={s.value} suffix={s.suffix} prefix={s.prefix} />
                  </div>
                  <div className="text-sm text-slate-500">{s.label}</div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ PROBLEM → SOLUTION ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-slate-400 text-xs font-medium mb-6 uppercase tracking-widest">
                <HeartPulse className="w-3.5 h-3.5 text-emerald-400" /> The Problem
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                Your receptionist can{"'"}t answer at midnight.
                <br />
                <span className="text-slate-500">Your AI can.</span>
              </h2>
              <p className="text-lg text-slate-400 leading-relaxed">
                70% of patient enquiries come outside clinic hours. Every missed WhatsApp
                message is a patient who books with your competitor instead.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Clock, title: "Before PatientPlex", items: ["Missed calls after hours", "₹800+ per new patient", "No idea which ads work", "Manual appointment reminders", "28% no-show rate"], bad: true },
              { icon: Zap, title: "After PatientPlex", items: ["24/7 AI WhatsApp receptionist", "₹12 per booking", "Full-funnel attribution", "Automated reminders", "4% no-show rate"], bad: false },
              { icon: Target, title: "The Difference", items: ["6x more patients", "₹50K+ saved monthly", "90% less manual work", "Real-time patient pipeline", "Predictable growth"], bad: false, highlight: true },
            ].map((col, i) => (
              <Reveal key={i} delay={i * 0.15}>
                <div className={`p-7 rounded-2xl border h-full transition-all duration-300 ${
                  col.highlight
                    ? "border-emerald-500/30 bg-emerald-500/[0.06] border-glow"
                    : "border-white/[0.06] glass hover:border-white/10"
                }`}>
                  <div className={`inline-flex items-center gap-2.5 mb-5 font-bold text-lg ${
                    col.highlight ? "text-emerald-400" : col.bad ? "text-red-400" : "text-cyan-400"
                  }`}>
                    <col.icon className="w-5 h-5" />
                    {col.title}
                  </div>
                  <ul className="space-y-3.5">
                    {col.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-3 text-sm text-slate-300">
                        {col.bad ? (
                          <span className="w-2 h-2 rounded-full bg-red-500/60 mt-1.5 shrink-0" />
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

      {/* ═══ FEATURES — Interactive tabs ═══ */}
      <section id="features" className="py-24 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-[#060910] via-[#0A0F1A] to-[#060910]" />
        <div className="max-w-7xl mx-auto relative">
          <Reveal>
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-slate-400 text-xs font-medium mb-6 uppercase tracking-widest">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Platform
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                Everything your clinic needs
                <br />
                <span className="text-gradient">to grow predictably</span>
              </h2>
              <p className="text-lg text-slate-400">
                From the first ad impression to the patient sitting in your chair.
              </p>
            </div>
          </Reveal>

          {/* Feature tabs */}
          <div className="grid lg:grid-cols-[1fr_1.3fr] gap-8 items-start">
            {/* Tab list */}
            <div className="space-y-2">
              {FEATURES.map((feat, i) => (
                <Reveal key={i} delay={i * 0.05}>
                  <button
                    onClick={() => setActiveFeature(i)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-300 group ${
                      activeFeature === i
                        ? `border-${feat.color}-500/30 bg-${feat.color}-500/[0.06]`
                        : "border-white/[0.04] hover:border-white/10 bg-white/[0.02]"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg transition-colors ${
                        activeFeature === i ? `bg-${feat.color}-500/20` : "bg-white/[0.04]"
                      }`}>
                        <feat.icon className={`w-5 h-5 ${
                          activeFeature === i ? `text-${feat.color}-400` : "text-slate-500"
                        }`} />
                      </div>
                      <div>
                        <h3 className={`font-semibold text-sm ${activeFeature === i ? "text-white" : "text-slate-400"}`}>
                          {feat.title}
                        </h3>
                      </div>
                      {activeFeature === i && (
                        <ArrowRight className="w-4 h-4 ml-auto text-slate-500" />
                      )}
                    </div>
                  </button>
                </Reveal>
              ))}
            </div>

            {/* Active feature detail */}
            <motion.div
              key={activeFeature}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="p-8 rounded-2xl glass border border-white/[0.06] border-glow"
            >
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${f.gradient} mb-6`}>
                <f.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">{f.title}</h3>
              <p className="text-slate-400 leading-relaxed mb-8">{f.desc}</p>

              <div className="grid grid-cols-2 gap-3">
                {f.details.map((d, i) => (
                  <div key={i} className="flex items-center gap-2.5 p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <CheckCircle2 className={`w-4 h-4 text-${f.color}-400 shrink-0`} />
                    <span className="text-sm text-slate-300">{d}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-slate-400 text-xs font-medium mb-6 uppercase tracking-widest">
                <MousePointerClick className="w-3.5 h-3.5 text-emerald-400" /> How it works
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                Live in <span className="text-gradient">10 minutes</span>, not 10 weeks
              </h2>
              <p className="text-lg text-slate-400">
                No agencies, no contracts, no technical setup. Enter your clinic details
                and PatientPlex does the rest.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-16 left-[20%] right-[20%] h-px bg-gradient-to-r from-emerald-500/30 via-cyan-500/30 to-violet-500/30" />

            {[
              { step: "01", title: "Tell us about your clinic", desc: "Specialty, location, treatments, budget. Takes about 3 minutes. We generate landing pages and ad creatives automatically.", icon: Users, color: "emerald" },
              { step: "02", title: "Connect WhatsApp & Calendar", desc: "Link your clinic's WhatsApp Business number and Google Calendar. The AI receptionist starts handling enquiries immediately.", icon: MessageCircle, color: "cyan" },
              { step: "03", title: "Patients start booking", desc: "Campaigns go live within hours. The AI qualifies leads, books appointments, and sends reminders. You focus on care.", icon: Calendar, color: "violet" },
            ].map((s, i) => (
              <Reveal key={i} delay={i * 0.15}>
                <div className="relative text-center">
                  <div className={`w-14 h-14 rounded-2xl bg-${s.color}-500/10 border border-${s.color}-500/20 flex items-center justify-center mx-auto mb-6 relative z-10`}>
                    <s.icon className={`w-6 h-6 text-${s.color}-400`} />
                  </div>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Step {s.step}</div>
                  <h3 className="text-lg font-bold text-white mb-3">{s.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ TESTIMONIALS ═══ */}
      <section className="py-24 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-[#060910] via-[#0A0F1A] to-[#060910]" />
        <div className="max-w-7xl mx-auto relative">
          <Reveal>
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-slate-400 text-xs font-medium mb-6 uppercase tracking-widest">
                <Star className="w-3.5 h-3.5 text-amber-400" /> Testimonials
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                Doctors who switched
                <br />
                <span className="text-gradient">never went back</span>
              </h2>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="relative p-7 rounded-2xl glass border border-white/[0.06] h-full flex flex-col group hover:border-emerald-500/20 transition-all duration-300">
                  {/* Quote mark */}
                  <span className="absolute top-5 right-6 text-7xl leading-none text-white/[0.03] font-serif pointer-events-none select-none">{"“"}</span>

                  {/* Stars */}
                  <div className="flex items-center gap-1 mb-5">
                    {[...Array(t.rating)].map((_, j) => (
                      <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>

                  <p className="text-sm text-slate-300 leading-relaxed flex-1 mb-6">{`"${t.text}"`}</p>

                  <div className="flex items-center justify-between pt-5 border-t border-white/[0.06]">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/10 flex items-center justify-center text-sm font-bold text-emerald-400">
                        {t.avatar}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white">{t.name}</div>
                        <div className="text-xs text-slate-500">{t.role}</div>
                      </div>
                    </div>
                    <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400">
                      {t.metric}
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ PRICING ═══ */}
      <section id="pricing" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-slate-400 text-xs font-medium mb-6 uppercase tracking-widest">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Pricing
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                Simple pricing,
                <br />
                <span className="text-gradient">real results</span>
              </h2>
              <p className="text-lg text-slate-400">
                Every plan includes a 14-day free trial. No credit card required.
                Ad budget goes directly to Google/Meta.
              </p>
            </div>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PRICING.map((p, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className={`relative p-7 rounded-2xl border h-full flex flex-col transition-all duration-300 ${
                  p.highlight
                    ? "border-emerald-500/30 bg-emerald-500/[0.04] border-glow shadow-xl shadow-emerald-500/[0.08] scale-[1.02]"
                    : "border-white/[0.06] glass hover:border-white/10"
                }`}>
                  {p.badge && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full badge-shimmer text-[#060910] text-xs font-bold">
                      {p.badge}
                    </div>
                  )}
                  <div className="mb-6">
                    <h3 className="font-bold text-white text-lg mb-1">{p.name}</h3>
                    <p className="text-xs text-slate-500 mb-5">{p.desc}</p>
                    <div className="flex items-baseline gap-1">
                      <span className="text-lg text-slate-400">₹</span>
                      <span className="text-5xl font-black text-white tabular-nums">{p.price}</span>
                      <span className="text-sm text-slate-500">{p.period}</span>
                    </div>
                  </div>
                  <ul className="space-y-3.5 mb-8 flex-1">
                    {p.features.map((feat, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-slate-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                        {feat}
                      </li>
                    ))}
                  </ul>
                  <Link href="/signup"
                    className={`block text-center py-3.5 rounded-xl font-semibold text-sm transition-all ${
                      p.highlight
                        ? "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-[#060910] shadow-lg shadow-emerald-500/20"
                        : "glass border border-white/10 hover:border-white/20 text-slate-300 hover:text-white"
                    }`}
                  >
                    {p.cta} <ArrowRight className="w-4 h-4 inline ml-1" />
                  </Link>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ SECURITY BADGES ═══ */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="p-8 rounded-2xl glass border border-white/[0.06]">
            <div className="flex flex-wrap items-center justify-center gap-10 text-sm text-slate-500">
              {[
                { icon: Shield, text: "End-to-end encryption" },
                { icon: Lock, text: "HMAC-SHA256 webhooks" },
                { icon: Award, text: "Healthcare-grade audit logs" },
                { icon: Shield, text: "SOC 2 aligned" },
              ].map((b, i) => (
                <div key={i} className="flex items-center gap-2.5">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10">
                    <b.icon className="w-4 h-4 text-emerald-500/60" />
                  </div>
                  <span className="font-medium">{b.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Reveal>
            <div className="text-center mb-12">
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-4">
                Common questions
              </h2>
              <p className="text-slate-400">Everything you need to know about PatientPlex.</p>
            </div>
          </Reveal>

          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full text-left p-6 rounded-2xl glass border border-white/[0.06] hover:border-white/10 transition-all"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-semibold text-white">{faq.q}</span>
                    <div className={`p-1 rounded-lg bg-white/[0.04] transition-transform duration-200 ${openFaq === i ? "rotate-180" : ""}`}>
                      <ChevronDown className="w-4 h-4 text-slate-500" />
                    </div>
                  </div>
                  {openFaq === i && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      transition={{ duration: 0.2 }}
                      className="mt-4 text-sm text-slate-400 leading-relaxed"
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

      {/* ═══ FINAL CTA ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.15] via-cyan-500/[0.08] to-violet-500/[0.1]" />
            <div className="absolute inset-0 glass" />
            <div className="absolute inset-0 border border-emerald-500/20 rounded-3xl" />

            {/* Orbs */}
            <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-emerald-500/[0.08] rounded-full blur-[100px]" />
            <div className="absolute bottom-0 right-1/4 w-[400px] h-[250px] bg-cyan-500/[0.06] rounded-full blur-[80px]" />

            <div className="relative p-12 sm:p-20 text-center">
              <Reveal>
                <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
                  Your competitor{"'"}s patients
                  <br />
                  <span className="text-gradient">are looking for you right now</span>
                </h2>
                <p className="text-lg text-slate-400 mb-10 max-w-xl mx-auto">
                  Every day without PatientPlex is another day of missed enquiries,
                  wasted ad spend, and patients going elsewhere.
                </p>
                <Link href="/signup"
                  className="group inline-flex items-center gap-2.5 px-10 py-5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-[#060910] font-bold text-lg transition-all shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98]"
                >
                  Start free trial
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <p className="text-sm text-slate-500 mt-5">
                  14 days free · No credit card · Cancel anytime
                </p>
              </Reveal>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="py-16 px-6 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-400 to-cyan-400 flex items-center justify-center">
                  <span className="text-[#060910] font-black text-sm">P</span>
                </div>
                <span className="font-bold text-lg">PatientPlex</span>
              </Link>
              <p className="text-sm text-slate-500 leading-relaxed mb-4">
                AI-powered patient acquisition for Indian dental and dermatology clinics.
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] text-xs text-slate-500">
                🇮🇳 Made in India
              </div>
            </div>

            {/* Links */}
            {[
              { title: "Product", links: ["Features", "Pricing", "Integrations", "API"] },
              { title: "Company", links: ["About", "Blog", "Careers", "Contact"] },
              { title: "Legal", links: ["Privacy Policy", "Terms of Service", "Security", "HIPAA"] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-sm font-semibold text-white mb-4">{col.title}</h4>
                <ul className="space-y-2.5">
                  {col.links.map((link, j) => (
                    <li key={j}>
                      <a href="#" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-600">© 2026 PatientPlex AI. All rights reserved.</p>
            <div className="flex items-center gap-4">
              {["Twitter", "LinkedIn", "YouTube"].map((social, i) => (
                <a key={i} href="#" className="text-xs text-slate-600 hover:text-slate-400 transition-colors">{social}</a>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
