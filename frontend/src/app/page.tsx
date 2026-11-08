"use client";

import { useState, useEffect, useRef, ReactNode } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useTransform, animate } from "framer-motion";
import {
  ArrowRight, CheckCircle2, Star, Shield, BarChart3,
  MessageCircle, Calendar, Phone, Globe, Brain, TrendingUp,
  Users, ChevronDown, Target, Award, Lock,
  Stethoscope, Activity, Instagram, Facebook, Search,
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

/* ─── Data ─── */
const STATS = [
  { value: 4200, suffix: "+", label: "Patients booked" },
  { value: 89, suffix: "%", label: "WhatsApp response rate" },
  { value: 12, prefix: "₹", suffix: "", label: "Avg. cost per booking" },
  { value: 26, suffix: "x", label: "LTV to CAC ratio" },
];

const TESTIMONIALS = [
  {
    name: "Dr. Priya Sharma", role: "Cosmetic Dentist, Mumbai",
    text: "We went from 3 new patients a week to 18. The WhatsApp AI handles enquiries at 2am better than my receptionist at 2pm. Our cost per patient dropped from ₹800 to ₹120.",
    avatar: "PS", metric: "6x more patients", rating: 5, platform: "google",
  },
  {
    name: "Dr. Rajesh Mehta", role: "Dermatologist, Delhi",
    text: "I was spending ₹50,000/month on agencies with zero transparency. PatientPlex shows me exactly where every rupee goes. My Google Ads quality score went from 4 to 9.",
    avatar: "RM", metric: "₹50K saved monthly", rating: 5, platform: "linkedin",
  },
  {
    name: "Dr. Ananya Reddy", role: "Orthodontist, Bengaluru",
    text: "The no-show rate at my clinic dropped from 28% to 4%. The WhatsApp reminders and the AI follow-up system are genuinely better than anything I have tried.",
    avatar: "AR", metric: "4% no-show rate", rating: 5, platform: "twitter",
  },
  {
    name: "Dr. Kavita Nair", role: "Pediatric Dentist, Chennai",
    text: "Setup took 10 minutes. Within a week I had 12 new patient bookings through WhatsApp alone. The ROI is insane compared to my old agency.",
    avatar: "KN", metric: "12 bookings in week 1", rating: 5, platform: "google",
  },
  {
    name: "Dr. Amit Patel", role: "Skin Specialist, Ahmedabad",
    text: "Our agency was charging ₹40K and I had no idea what they were doing. Now I see every rupee, every click, every booking. Transparency is everything.",
    avatar: "AP", metric: "Full transparency", rating: 5, platform: "linkedin",
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
  { q: "How quickly will I see new patients?", a: "Most clinics see their first AI-booked appointment within 48 hours of going live. Campaigns take 3–5 days to optimize fully, and you will typically see consistent patient flow by week two." },
  { q: "Do I need to manage the ads myself?", a: "No. PatientPlex creates, launches, and optimizes your Google and Meta ad campaigns automatically. You set your budget and target treatments — the AI handles everything else." },
  { q: "What happens when a patient messages on WhatsApp?", a: "Our AI receptionist responds instantly in the patient’s language. It answers treatment questions using your clinic’s actual information, checks your calendar availability, and books the appointment — all without you lifting a finger." },
  { q: "Is my patient data secure?", a: "Yes. All data is encrypted at rest and in transit. We use Fernet symmetric encryption for OAuth tokens, HMAC-SHA256 for webhook verification, and maintain full audit logs. We are built for healthcare compliance from day one." },
  { q: "Can I try it before committing?", a: "Absolutely. Every plan starts with a 14-day free trial. No credit card required. You will have a working campaign with real patient enquiries before you pay anything." },
  { q: "What if I already have a website?", a: "PatientPlex landing pages work alongside your existing website. They are specifically optimized for ad traffic — higher quality scores mean lower cost per click. Your main website stays exactly as it is." },
];

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

const PRESS = ["Economic Times", "YourStory", "Inc42", "Mint", "Business Standard"];

const CHANNELS = [
  { name: "WhatsApp", icon: MessageCircle, color: "text-green-600 bg-green-50" },
  { name: "Google Ads", icon: Search, color: "text-blue-600 bg-blue-50" },
  { name: "Instagram", icon: Instagram, color: "text-pink-600 bg-pink-50" },
  { name: "Facebook", icon: Facebook, color: "text-blue-700 bg-blue-50" },
  { name: "Phone", icon: Phone, color: "text-violet-600 bg-violet-50" },
  { name: "Website", icon: Globe, color: "text-emerald-600 bg-emerald-50" },
];

/* ═══════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-slate-900 overflow-x-hidden">

      {/* ─── Nav ─── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/90 backdrop-blur-xl border-b border-slate-200/60 shadow-sm"
          : "bg-transparent"
      }`}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center">
              <span className="text-white font-black text-sm">P</span>
            </div>
            <span className="font-black text-xl tracking-tight text-slate-900">PatientPlex</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-slate-900 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-slate-900 transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-slate-900 transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors hidden sm:block">
              Sign in
            </Link>
            <Link href="/signup"
              className="text-sm font-semibold px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white transition-colors"
            >
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══ HERO ═══ */}
      <section className="pt-28 pb-16 px-6 relative overflow-hidden">
        {/* Warm gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-50/80 via-[#FAFAF8] to-teal-50/60" />

        <div className="max-w-7xl mx-auto relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left — copy */}
            <div>
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-5xl sm:text-6xl lg:text-[4.25rem] font-black tracking-tight leading-[1.08] text-slate-900 mb-6"
              >
                AI runs your
                <br />
                patient
                <br />
                acquisition
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.15 }}
                className="text-lg text-slate-600 leading-relaxed mb-8 max-w-lg"
              >
                PatientPlex is an autonomous AI marketer for Indian clinics: it runs your
                Google and Meta ads, your WhatsApp receptionist and your appointment
                booking for a flat monthly fee. More patients on autopilot.
              </motion.p>

              {/* Email CTA — Ryze style */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.25 }}
                className="flex flex-col sm:flex-row gap-3 mb-8"
              >
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="flex-1 px-5 py-3.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all"
                />
                <Link href="/signup"
                  className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition-colors whitespace-nowrap"
                >
                  Get started <ArrowRight className="w-4 h-4" />
                </Link>
              </motion.div>

              {/* Platform icons */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="flex items-center gap-4"
              >
                {[
                  { label: "Google", bg: "bg-white", letter: "G", color: "text-blue-500" },
                  { label: "Meta", bg: "bg-white", letter: "M", color: "text-blue-600" },
                  { label: "WhatsApp", bg: "bg-white", letter: "W", color: "text-green-500" },
                  { label: "Instagram", bg: "bg-white", letter: "I", color: "text-pink-500" },
                  { label: "Calendar", bg: "bg-white", letter: "C", color: "text-red-500" },
                ].map((p, i) => (
                  <div key={i} className={`w-10 h-10 rounded-xl ${p.bg} border border-slate-200 shadow-sm flex items-center justify-center`}>
                    <span className={`font-black text-sm ${p.color}`}>{p.letter}</span>
                  </div>
                ))}
              </motion.div>
            </div>

            {/* Right — dashboard mockup (clean white card like Ryze) */}
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="hidden lg:block"
            >
              <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
                {/* Tab bar like Ryze */}
                <div className="border-b border-slate-100">
                  <div className="flex">
                    {["AI RECEPTIONIST", "AD CAMPAIGNS", "BOOKINGS"].map((tab, i) => (
                      <div key={i} className={`px-5 py-3 text-xs font-bold tracking-wider ${
                        i === 0 ? "text-emerald-600 border-b-2 border-emerald-500 bg-emerald-50/50" : "text-slate-400"
                      }`}>
                        {i === 0 && <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 align-middle" />}
                        {tab}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Chat UI mockup */}
                <div className="p-6">
                  <div className="flex items-start gap-3 mb-6">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                      <Brain className="w-4 h-4 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900 mb-1">PatientPlex AI</p>
                      <div className="bg-slate-50 rounded-xl rounded-tl-sm p-4 text-sm text-slate-700 leading-relaxed">
                        Got it. I have built a campaign for <strong>SmileCraft Dental</strong> to maximize bookings in Mumbai this month.
                      </div>
                    </div>
                  </div>

                  {/* Campaign card */}
                  <div className="bg-slate-50 rounded-xl p-5 border border-slate-100">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Campaign Setup</p>
                    <p className="font-bold text-slate-900 mb-4">SmileCraft Dental &mdash; Nov bookings</p>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-[10px] text-slate-400 mb-0.5">Daily budget</p>
                        <p className="text-lg font-black text-slate-900">{"₹"}2,500</p>
                        <p className="text-[10px] text-slate-400">{"₹"}75,000/mo</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-400 mb-0.5">Est. clicks/mo</p>
                        <p className="text-lg font-black text-slate-900">1,240</p>
                        <p className="text-[10px] text-slate-400">Based on local CPCs</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-400 mb-0.5">Est. bookings</p>
                        <p className="text-lg font-black text-slate-900">62&mdash;85</p>
                        <p className="text-[10px] text-slate-400">5&mdash;7% conv. rate</p>
                      </div>
                    </div>
                    <div className="space-y-2.5 text-sm">
                      {[
                        ["Platforms", "Google Search + Meta"],
                        ["Radius", "5 km from clinic"],
                        ["Schedule", "Mon—Sat, 7am—9pm"],
                        ["Bidding", "Maximize conversions"],
                      ].map(([k, v], i) => (
                        <div key={i} className="flex justify-between items-center">
                          <span className="text-slate-500">{k}</span>
                          <span className="font-semibold text-slate-900">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ═══ PRESS BAR ═══ */}
      <section className="py-8 border-y border-slate-200/60 bg-white/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col sm:flex-row items-center gap-6 sm:gap-0 justify-between">
            <p className="text-xs font-medium text-slate-400 uppercase tracking-widest whitespace-nowrap">
              Featured by the world{"'"}s most influential media
            </p>
            <div className="flex items-center gap-10">
              {PRESS.map((name, i) => (
                <span key={i} className="text-sm sm:text-base font-black text-slate-300 tracking-tight whitespace-nowrap">
                  {name}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ CHANNELS ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <Reveal>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight leading-tight mb-6">
                AI to manage patients across every channel
              </h2>
              <p className="text-lg text-slate-500 leading-relaxed">
                WhatsApp, Google, Instagram, phone calls &mdash; PatientPlex captures patients
                from every touchpoint and funnels them into your calendar.
              </p>
            </Reveal>
            <Reveal delay={0.15}>
              <div className="grid grid-cols-3 gap-4">
                {CHANNELS.map((ch, i) => (
                  <div key={i} className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col items-center gap-3 shadow-sm hover:shadow-md transition-shadow">
                    <div className={`w-12 h-12 rounded-xl ${ch.color} flex items-center justify-center`}>
                      <ch.icon className="w-6 h-6" />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">{ch.name}</span>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ═══ WALL OF LOVE ═══ */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">
              Wall of Love <span className="text-red-500">{"❤️"}</span>
            </h2>
            <p className="text-center text-slate-500 mb-16 text-lg">Hear from doctors who switched from agencies to PatientPlex.</p>
          </Reveal>

          {/* Masonry / bento grid */}
          <div className="columns-1 md:columns-2 lg:columns-3 gap-5 space-y-5">
            {TESTIMONIALS.map((t, i) => (
              <Reveal key={i} delay={i * 0.08}>
                <div className="break-inside-avoid bg-[#FAFAF8] rounded-2xl border border-slate-200 p-6 hover:shadow-lg transition-shadow">
                  {/* Platform icon */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-full bg-emerald-100 flex items-center justify-center text-sm font-black text-emerald-700">
                        {t.avatar}
                      </div>
                      <div>
                        <p className="font-bold text-slate-900 text-sm">{t.name}</p>
                        <p className="text-xs text-slate-500">{t.role}</p>
                      </div>
                    </div>
                    <div className="text-slate-300">
                      {t.platform === "google" && <span className="font-black text-lg text-slate-300">G</span>}
                      {t.platform === "linkedin" && <span className="font-black text-lg text-blue-300">in</span>}
                      {t.platform === "twitter" && <span className="font-black text-lg text-slate-300">X</span>}
                    </div>
                  </div>

                  <p className="text-sm text-slate-700 leading-relaxed mb-4">{t.text}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-0.5">
                      {[...Array(t.rating)].map((_, j) => (
                        <Star key={j} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                      ))}
                    </div>
                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                      {t.metric}
                    </span>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ STATS — Used by 200+ clinics ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-16">
              Used by 200+ clinics
            </h2>
          </Reveal>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {STATS.map((s, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="text-center p-8 bg-white rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-4xl sm:text-5xl font-black text-slate-900 mb-2 tabular-nums">
                    <Counter target={s.value} suffix={s.suffix} prefix={s.prefix} />
                  </div>
                  <p className="text-sm text-slate-500 font-medium">{s.label}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FEATURES — 3 column ═══ */}
      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">
              See what PatientPlex does inside your account
            </h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">
              Three autonomous AI agents working 24/7 to grow your clinic.
            </p>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Autonomous\nAI receptionist",
                bullets: ["24/7 WhatsApp responses", "Multi-language support", "Smart lead qualification", "Instant appointment booking"],
                icon: Brain,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6">
                    <div className="flex items-start gap-2 mb-3">
                      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center shrink-0 mt-0.5">
                        <MessageCircle className="w-3 h-3 text-green-600" />
                      </div>
                      <div className="bg-green-50 rounded-lg rounded-tl-sm p-2.5 text-xs text-slate-700">
                        Hi! I want to book a teeth whitening appointment.
                      </div>
                    </div>
                    <div className="flex items-start gap-2 justify-end">
                      <div className="bg-emerald-50 rounded-lg rounded-tr-sm p-2.5 text-xs text-slate-700">
                        Great choice! Dr. Sharma has slots on Tuesday at 10am and Thursday at 3pm. Which works better?
                      </div>
                      <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center shrink-0 mt-0.5">
                        <Brain className="w-3 h-3 text-emerald-600" />
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                title: "Autonomous\nad campaigns",
                bullets: ["Google + Meta on autopilot", "Geo-targeted within 5km", "A/B tested creatives", "Auto-optimized bids"],
                icon: BarChart3,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6">
                    <div className="space-y-2">
                      {[
                        { label: "Teeth whitening", cpc: "₹8.20", clicks: "342", status: "Active" },
                        { label: "Dental implants", cpc: "₹12.50", clicks: "189", status: "Active" },
                        { label: "Root canal", cpc: "₹10.80", clicks: "256", status: "Optimizing" },
                      ].map((ad, j) => (
                        <div key={j} className="flex items-center justify-between text-xs bg-white rounded-lg p-2.5 border border-slate-100">
                          <span className="font-medium text-slate-700">{ad.label}</span>
                          <span className="text-slate-400">{ad.cpc} CPC</span>
                          <span className="text-slate-400">{ad.clicks} clicks</span>
                          <span className={`font-semibold px-2 py-0.5 rounded text-[10px] ${
                            ad.status === "Active" ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"
                          }`}>{ad.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ),
              },
              {
                title: "Autonomous\npatient booking",
                bullets: ["Google Calendar sync", "WhatsApp reminders", "60% fewer no-shows", "Smart rescheduling"],
                icon: Calendar,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6">
                    <div className="space-y-2">
                      {MOCK_QUEUE.slice(0, 3).map((p, j) => (
                        <div key={j} className="flex items-center justify-between text-xs bg-white rounded-lg p-2.5 border border-slate-100">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center text-[9px] font-bold text-emerald-600">
                              {p.name[0]}
                            </div>
                            <div>
                              <p className="font-medium text-slate-700">{p.treatment}</p>
                              <p className="text-[10px] text-slate-400">{p.name} &middot; {p.time}</p>
                            </div>
                          </div>
                          <span className="font-semibold text-emerald-600">{p.amount}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ),
              },
            ].map((feat, i) => (
              <Reveal key={i} delay={i * 0.12}>
                <div className="h-full">
                  <feat.icon className="w-8 h-8 text-slate-900 mb-5" />
                  <h3 className="text-2xl font-black text-slate-900 mb-4 whitespace-pre-line leading-tight">
                    {feat.title}
                  </h3>
                  <ul className="space-y-2.5">
                    {feat.bullets.map((b, j) => (
                      <li key={j} className="flex items-center gap-2.5 text-sm text-slate-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-900 shrink-0" />
                        {b}
                      </li>
                    ))}
                  </ul>
                  {feat.mockup}
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ LIVE RESULTS + CTA ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-0 rounded-3xl overflow-hidden border border-slate-200 shadow-lg">
            {/* Left — live results (blue gradient like Ryze) */}
            <div className="bg-gradient-to-br from-sky-400 to-emerald-400 p-10 sm:p-14 text-white">
              <Reveal>
                <h3 className="text-sm font-bold uppercase tracking-widest opacity-80 mb-6">Live results across</h3>
                <p className="text-3xl sm:text-4xl font-black mb-10">200+ clinics</p>

                <div className="space-y-8">
                  {[
                    { category: "PAID ADS", items: [["Avg. client ROAS", "4.2x"], ["Revenue driven", "₹4.2Cr"]] },
                    { category: "WHATSAPP AI", items: [["Messages handled", "1.2M+"], ["Response rate", "89%"]] },
                    { category: "BOOKINGS", items: [["Patients booked", "4,200+"], ["No-show reduction", "-60%"]] },
                  ].map((group, i) => (
                    <div key={i}>
                      <p className="text-xs font-bold uppercase tracking-widest opacity-60 mb-3">
                        <span className="inline-block w-1.5 h-1.5 rounded-full bg-white mr-1.5 align-middle opacity-80" />
                        {group.category}
                      </p>
                      {group.items.map(([label, val], j) => (
                        <div key={j} className="flex items-center justify-between py-1.5">
                          <span className="text-sm opacity-80">{label}</span>
                          <span className="font-mono font-black text-lg">{val}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>

                <p className="mt-8 text-xs opacity-60 font-mono">Last updated: Nov 2026</p>
                <p className="text-xs opacity-60 font-mono flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-300" /> All systems ok
                </p>
              </Reveal>
            </div>

            {/* Right — CTA card */}
            <div className="bg-white p-10 sm:p-14 flex flex-col justify-center">
              <Reveal delay={0.15}>
                <h3 className="text-3xl sm:text-4xl font-black text-slate-900 mb-4 leading-tight">
                  Let AI Run
                  <br />
                  Your Clinic
                </h3>
                <p className="text-slate-500 mb-8">
                  Autonomous agents that acquire patients, book appointments and
                  optimize your ads &mdash; around the clock.
                </p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="email"
                    placeholder="work@email.com"
                    className="flex-1 px-5 py-3.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all"
                  />
                  <Link href="/signup"
                    className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition-colors whitespace-nowrap"
                  >
                    Get started <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </Reveal>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ PRICING ═══ */}
      <section id="pricing" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">
              Simple pricing, real results
            </h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">
              Every plan includes a 14-day free trial. No credit card required.
              Your ad budget is separate and goes directly to Google/Meta.
            </p>
          </Reveal>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PRICING.map((p, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className={`relative p-7 rounded-2xl border h-full flex flex-col transition-shadow ${
                  p.highlight
                    ? "border-emerald-500 bg-emerald-50/30 shadow-lg shadow-emerald-500/10"
                    : "border-slate-200 bg-[#FAFAF8] hover:shadow-md"
                }`}>
                  {p.badge && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-emerald-500 text-white text-xs font-bold">
                      {p.badge}
                    </div>
                  )}
                  <div className="mb-6">
                    <h3 className="font-black text-xl text-slate-900 mb-1">{p.name}</h3>
                    <p className="text-xs text-slate-500 mb-5">{p.desc}</p>
                    <div className="flex items-baseline gap-1">
                      <span className="text-lg text-slate-400">{"₹"}</span>
                      <span className="text-5xl font-black text-slate-900 tabular-nums">{p.price}</span>
                      <span className="text-sm text-slate-400">{p.period}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-8 flex-1">
                    {p.features.map((f, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-slate-600">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Link href="/signup"
                    className={`block text-center py-3.5 rounded-lg font-semibold text-sm transition-colors ${
                      p.highlight
                        ? "bg-slate-900 hover:bg-slate-800 text-white"
                        : "bg-white border border-slate-300 hover:border-slate-400 text-slate-700 hover:text-slate-900"
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

      {/* ═══ SECURITY ═══ */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-wrap items-center justify-center gap-10 text-sm text-slate-400">
            {[
              { icon: Shield, text: "End-to-end encryption" },
              { icon: Lock, text: "HMAC-SHA256 webhooks" },
              { icon: Award, text: "Healthcare-grade audit logs" },
              { icon: Shield, text: "SOC 2 aligned" },
            ].map((b, i) => (
              <div key={i} className="flex items-center gap-2">
                <b.icon className="w-4 h-4 text-emerald-500/60" />
                <span className="font-medium">{b.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">
              Common questions
            </h2>
            <p className="text-center text-slate-500 mb-12">Everything you need to know about PatientPlex.</p>
          </Reveal>

          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full text-left p-6 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 transition-all"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-bold text-slate-900">{faq.q}</span>
                    <ChevronDown className={`w-5 h-5 text-slate-400 shrink-0 transition-transform duration-200 ${openFaq === i ? "rotate-180" : ""}`} />
                  </div>
                  {openFaq === i && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      transition={{ duration: 0.2 }}
                      className="mt-4 text-sm text-slate-500 leading-relaxed"
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

      {/* ═══ FOOTER ═══ */}
      <footer className="py-16 px-6 border-t border-slate-200">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-10 mb-12">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center">
                  <span className="text-white font-black text-xs">P</span>
                </div>
                <span className="font-black text-lg text-slate-900">PatientPlex</span>
              </Link>
              <p className="text-sm text-slate-500 leading-relaxed mb-4">
                AI-powered patient acquisition for Indian clinics.
              </p>
              <div className="inline-flex items-center gap-1.5 text-xs text-slate-400">
                <span>{"🇮🇳"}</span> Made in India
              </div>
            </div>

            {[
              { title: "Product", links: ["Features", "Pricing", "Integrations", "API"] },
              { title: "Company", links: ["About", "Blog", "Careers", "Contact"] },
              { title: "Legal", links: ["Privacy Policy", "Terms of Service", "Security", "HIPAA"] },
              { title: "Connect", links: ["Twitter", "LinkedIn", "YouTube", "hello@patientplex.ai"] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-sm font-bold text-slate-900 mb-4">{col.title}</h4>
                <ul className="space-y-2.5">
                  {col.links.map((link, j) => (
                    <li key={j}>
                      <a href="#" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-slate-200 text-center">
            <p className="text-xs text-slate-400">{"©"} 2026 PatientPlex AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
