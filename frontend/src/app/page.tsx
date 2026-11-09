"use client";

import { useState, useEffect, useRef, ReactNode } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useTransform, animate, AnimatePresence } from "framer-motion";
import {
  ArrowRight, CheckCircle2, Star, Shield, BarChart3,
  MessageCircle, Calendar, Phone, Globe, Brain, TrendingUp,
  Users, ChevronDown, Target, Award, Lock,
  Instagram, Facebook, Search, BadgeCheck, Mail,
  Menu, X, Clock, Zap, Activity, Play, TrendingDown,
} from "lucide-react";

import Logo from "@/components/Logo";

/* ─── Brand SVG Logos ─── */
function GoogleLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A11.96 11.96 0 0 0 0 12c0 1.94.46 3.77 1.28 5.41l3.56-2.77.01-.55z" fill="#FBBC05"/>
      <path d="M12 4.75c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 1.09 14.97 0 12 0 7.7 0 3.99 2.47 2.18 6.07l3.66 2.84c.87-2.6 3.3-4.16 6.16-4.16z" fill="#EA4335"/>
    </svg>
  );
}
function WhatsAppLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#25D366">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
    </svg>
  );
}
function InstagramLogo({ size = 20 }: { size?: number }) {
  const id = `ig_${size}`;
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <defs>
        <linearGradient id={id} x1="0" y1="24" x2="24" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FD5"/>
          <stop offset=".5" stopColor="#FF543E"/>
          <stop offset="1" stopColor="#C837AB"/>
        </linearGradient>
      </defs>
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z" fill={`url(#${id})`}/>
    </svg>
  );
}
function FacebookLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#1877F2">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  );
}
function MetaLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#0081FB">
      <path d="M6.915 4.03c-1.968 0-3.683 1.28-4.871 3.113C.704 9.208 0 11.883 0 14.449c0 .706.07 1.369.21 1.973a4.478 4.478 0 0 0 1.593 2.61c.76.585 1.675.868 2.64.868 1.17 0 2.287-.47 3.215-1.22.926-.746 1.755-1.815 2.439-3.128L12 12.95l1.903 2.602c.684 1.313 1.513 2.382 2.44 3.128.927.75 2.044 1.22 3.214 1.22.965 0 1.88-.283 2.64-.868a4.478 4.478 0 0 0 1.593-2.61c.14-.604.21-1.267.21-1.973 0-2.566-.704-5.241-2.044-7.306C20.768 5.31 19.053 4.03 17.085 4.03c-1.17 0-2.287.47-3.215 1.22-.926.746-1.755 1.815-2.439 3.128L12 11.05l-1.431-1.672c-.684-1.313-1.513-2.382-2.44-3.128C7.202 5.5 6.085 4.03 6.915 4.03z"/>
    </svg>
  );
}
function GoogleCalendarLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <path d="M18 2H6a4 4 0 0 0-4 4v12a4 4 0 0 0 4 4h12a4 4 0 0 0 4-4V6a4 4 0 0 0-4-4z" fill="#fff" stroke="#4285F4" strokeWidth="1.5"/>
      <rect x="6" y="8" width="5" height="3" rx="0.5" fill="#4285F4"/>
      <rect x="13" y="8" width="5" height="3" rx="0.5" fill="#EA4335"/>
      <rect x="6" y="13" width="5" height="3" rx="0.5" fill="#FBBC05"/>
      <rect x="13" y="13" width="5" height="3" rx="0.5" fill="#34A853"/>
      <rect x="8" y="1" width="2" height="3" rx="1" fill="#5F6368"/>
      <rect x="14" y="1" width="2" height="3" rx="1" fill="#5F6368"/>
    </svg>
  );
}
function GoogleAdsLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <path d="M3.245 16.897l5.702-9.893a3.39 3.39 0 0 1 4.636-1.238l-5.702 9.893a3.39 3.39 0 0 1-4.636 1.238z" fill="#FBBC05"/>
      <path d="M20.755 16.897l-5.702-9.893a3.39 3.39 0 0 0-4.636-1.238l5.702 9.893a3.39 3.39 0 0 0 4.636 1.238z" fill="#4285F4"/>
      <circle cx="5.634" cy="18.366" r="3.366" fill="#34A853"/>
    </svg>
  );
}

function OpenAILogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#000000">
      <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.998 5.998 0 0 0-3.998 2.9 6.04 6.04 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/>
    </svg>
  );
}
function LinkedInLogo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="#0A66C2">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  );
}

/* ─── Animated counter ─── */
function Counter({ target, suffix = "", prefix = "" }: { target: number; suffix?: string; prefix?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => `${prefix}${Math.round(v).toLocaleString("en-IN")}${suffix}`);
  const [display, setDisplay] = useState(`${prefix}0${suffix}`);

  useEffect(() => {
    if (!isInView) return;
    const controls = animate(count, target, { duration: 2, type: "spring", stiffness: 50, damping: 20 });
    const unsub = rounded.on("change", (v) => setDisplay(v));
    return () => { controls.stop(); unsub(); };
  }, [isInView, target, count, rounded]);

  return <span ref={ref}>{display}</span>;
}

/* ─── Reveal wrapper ─── */
function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 32 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }} className={className}>
      {children}
    </motion.div>
  );
}

/* ─── Data ─── */
const STATS = [
  { value: 24, suffix: "/7", label: "AI receptionist uptime", icon: Clock },
  { value: 2, suffix: "min", label: "Avg WhatsApp response", icon: MessageCircle },
  { value: 5, prefix: "₹", suffix: "–8", label: "Cost per lead (enquiry)", icon: Target },
  { value: 50, prefix: "₹", suffix: "–100", label: "Cost per conversion (booking)", icon: TrendingUp },
];

const TESTIMONIALS = [
  { name: "Bhardwaj Dental Clinic", role: "Dental Clinic • Our first client", text: "PatientPlex manages our Google Ads and WhatsApp enquiries end-to-end. We get leads at ₹5–8 each, and our cost per actual patient booking is around ₹60–80. Far cheaper than any agency. The AI handles after-hours messages so we never miss a patient.", avatar: "BD", metric: "₹60–80 per booking", rating: 5, platform: "google", isReal: true },
  { name: "Dr. Priya Sharma", role: "Cosmetic Dentist, Mumbai", text: "WhatsApp AI handles enquiries around the clock so we never miss a patient. Quality scores improved and cost per lead dropped significantly.", avatar: "PS", metric: "Lower cost per lead", rating: 5, platform: "google" },
  { name: "Dr. Rajesh Mehta", role: "Dermatologist, Delhi", text: "Full transparency on every rupee spent — I can see exactly which ads bring patients and which don't. No more guessing with agencies.", avatar: "RM", metric: "Full transparency", rating: 5, platform: "linkedin" },
  { name: "Dr. Ananya Reddy", role: "Orthodontist, Bengaluru", text: "Automated WhatsApp reminders have noticeably reduced our no-show rate. The follow-up system works better than manual calling.", avatar: "AR", metric: "Fewer no-shows", rating: 5, platform: "twitter" },
  { name: "Dr. Kavita Nair", role: "Ophthalmologist, Chennai", text: "Running LASIK campaigns with AI optimization means we get more consultations for the same budget. The booking flow through WhatsApp is seamless.", avatar: "KN", metric: "Better ad ROI", rating: 5, platform: "google" },
  { name: "Dr. Amit Patel", role: "Orthopedic Surgeon, Ahmedabad", text: "Switching from an agency to PatientPlex gave us complete visibility into our marketing spend. Every click, every lead, every booking — all tracked.", avatar: "AP", metric: "Full visibility", rating: 5, platform: "linkedin" },
];

const PRICING_DATA = {
  monthly: [
    { name: "Starter", price: "4,999", period: "/mo", desc: "For solo practitioners starting with digital patient acquisition", features: ["Google Ads management", "WhatsApp AI (500 conversations)", "5 landing pages", "Basic analytics", "Email support"], cta: "Start free trial", highlight: false },
    { name: "Growth", price: "14,999", period: "/mo", desc: "For clinics ready to scale patient volume predictably", features: ["Google + Meta + ChatGPT Ads", "LinkedIn doctor referral campaigns", "WhatsApp AI (unlimited)", "Unlimited landing pages", "Call tracking", "Conversion funnel analytics", "Priority WhatsApp support", "Google Calendar sync"], cta: "Start free trial", highlight: true, badge: "Most popular" },
    { name: "Enterprise", price: "24,999", period: "/mo", desc: "For multi-location clinics and hospital chains", features: ["Everything in Growth", "All 5 ad platforms", "Multi-location management", "Custom AI training", "Dedicated account manager", "API access", "HIPAA-grade audit logs", "Custom integrations"], cta: "Contact sales", highlight: false },
  ],
  annual: [
    { name: "Starter", price: "3,999", period: "/mo", desc: "For solo practitioners starting with digital patient acquisition", features: ["Google Ads management", "WhatsApp AI (500 conversations)", "5 landing pages", "Basic analytics", "Email support"], cta: "Start free trial", highlight: false },
    { name: "Growth", price: "11,999", period: "/mo", desc: "For clinics ready to scale patient volume predictably", features: ["Google + Meta + ChatGPT Ads", "LinkedIn doctor referral campaigns", "WhatsApp AI (unlimited)", "Unlimited landing pages", "Call tracking", "Conversion funnel analytics", "Priority WhatsApp support", "Google Calendar sync"], cta: "Start free trial", highlight: true, badge: "Most popular" },
    { name: "Enterprise", price: "19,999", period: "/mo", desc: "For multi-location clinics and hospital chains", features: ["Everything in Growth", "All 5 ad platforms", "Multi-location management", "Custom AI training", "Dedicated account manager", "API access", "HIPAA-grade audit logs", "Custom integrations"], cta: "Contact sales", highlight: false },
  ],
};

const FAQS = [
  { q: "How quickly will I see new patients?", a: "Most clinics see their first AI-booked appointment within 48 hours of going live. Campaigns take 3–5 days to optimize fully, and you will typically see consistent patient flow by week two." },
  { q: "Do I need to manage the ads myself?", a: "No. PatientPlex creates, launches, and optimizes your Google, Meta, ChatGPT, and LinkedIn ad campaigns automatically. You set your budget and target treatments — the AI handles everything else." },
  { q: "What happens when a patient messages on WhatsApp?", a: "Our AI receptionist responds instantly in the patient’s language. It answers treatment questions using your clinic’s actual information, checks your calendar availability, and books the appointment — all without you lifting a finger." },
  { q: "Is my patient data secure?", a: "Yes. All data is encrypted at rest and in transit. We use Fernet symmetric encryption for OAuth tokens, HMAC-SHA256 for webhook verification, and maintain full audit logs. We are built for healthcare compliance from day one." },
  { q: "Can I try it before committing?", a: "Absolutely. Every plan starts with a 14-day free trial. No credit card required. You will have a working campaign with real patient enquiries before you pay anything." },
  { q: "What if I already have a website?", a: "PatientPlex landing pages work alongside your existing website. They are specifically optimized for ad traffic — higher quality scores mean lower cost per click. Your main website stays exactly as it is." },
  { q: "How does the WhatsApp AI work?", a: "Our AI is powered by advanced language models trained on healthcare conversations. It understands treatment queries, checks your calendar in real-time, and books appointments — all in the patient's preferred language (Hindi, English, Tamil, Telugu, and more)." },
  { q: "What kind of clinics use PatientPlex?", a: "We currently work with Bhardwaj Dental Clinic and are onboarding more clinics across specialties — dental, dermatology, ophthalmology, orthopedics, gynecology, and multi-specialty clinics. We support solo practitioners and chains." },
];

const MOCK_QUEUE = [
  { name: "Ravi M.", treatment: "Teeth cleaning", time: "Just now", amount: "₹1,500" },
  { name: "Sunita P.", treatment: "Root canal", time: "2m ago", amount: "₹4,500" },
  { name: "Deepak S.", treatment: "Dental implant consult", time: "5m ago", amount: "₹500" },
];

const TECH_STACK = ["WhatsApp Business API", "Google Ads API", "Meta Marketing API", "ChatGPT Ads API", "LinkedIn Marketing API"];

const CHANNELS_DATA = [
  { name: "WhatsApp", border: "hover:border-green-300" },
  { name: "Google Ads", border: "hover:border-blue-300" },
  { name: "Instagram", border: "hover:border-pink-300" },
  { name: "Facebook", border: "hover:border-blue-300" },
  { name: "ChatGPT Ads", border: "hover:border-slate-300" },
  { name: "LinkedIn Ads", border: "hover:border-sky-300" },
  { name: "Phone", border: "hover:border-violet-300" },
  { name: "Website", border: "hover:border-emerald-300" },
];

/* ─── ROI Calculator ─── */
function ROICalculator() {
  const [adSpend, setAdSpend] = useState(50000);
  const [costPerPatient, setCostPerPatient] = useState(800);
  const [locations, setLocations] = useState(1);

  const avgCostPerBooking = 70; // ₹60-80 range, using ₹70 avg from Bhardwaj Dental data
  const pplexBookings = Math.round((adSpend / avgCostPerBooking) * locations);
  const agencyPatients = Math.round((adSpend / costPerPatient) * locations);
  const pplexCost = adSpend + (locations === 1 ? 14999 : 24999 * locations);
  const agencyCost = adSpend + (50000 * locations);
  const monthlySavings = agencyCost - pplexCost;
  const annualSavings = monthlySavings * 12;

  return (
    <div className="grid lg:grid-cols-2 gap-8">
      <div className="space-y-8 p-8 bg-[#FAFAF8] rounded-2xl border border-slate-200">
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-bold text-slate-900">Current monthly ad spend</label>
            <span className="text-sm font-black text-emerald-600 tabular-nums">{"₹"}{adSpend.toLocaleString("en-IN")}</span>
          </div>
          <input type="range" min={10000} max={500000} step={5000} value={adSpend}
            onChange={(e) => setAdSpend(Number(e.target.value))}
            className="w-full h-2 rounded-full bg-slate-200 appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-emerald-500 [&::-webkit-slider-thumb]:shadow-md" />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1"><span>{"₹"}10,000</span><span>{"₹"}5,00,000</span></div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-bold text-slate-900">Current cost per patient</label>
            <span className="text-sm font-black text-emerald-600 tabular-nums">{"₹"}{costPerPatient.toLocaleString("en-IN")}</span>
          </div>
          <input type="range" min={100} max={2000} step={50} value={costPerPatient}
            onChange={(e) => setCostPerPatient(Number(e.target.value))}
            className="w-full h-2 rounded-full bg-slate-200 appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-emerald-500 [&::-webkit-slider-thumb]:shadow-md" />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1"><span>{"₹"}100</span><span>{"₹"}2,000</span></div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-bold text-slate-900">Number of locations</label>
            <span className="text-sm font-black text-emerald-600 tabular-nums">{locations}</span>
          </div>
          <input type="range" min={1} max={10} step={1} value={locations}
            onChange={(e) => setLocations(Number(e.target.value))}
            className="w-full h-2 rounded-full bg-slate-200 appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-emerald-500 [&::-webkit-slider-thumb]:shadow-md" />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1"><span>1</span><span>10</span></div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-6 bg-emerald-50 rounded-2xl border border-emerald-200">
          <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-2">With PatientPlex</p>
          <p className="text-3xl font-black text-slate-900 tabular-nums">{pplexBookings.toLocaleString("en-IN")}</p>
          <p className="text-sm text-slate-500">bookings/month at {"₹"}70 avg</p>
        </div>
        <div className="p-6 bg-red-50 rounded-2xl border border-red-200">
          <p className="text-xs font-bold text-red-500 uppercase tracking-widest mb-2">With Agency</p>
          <p className="text-3xl font-black text-slate-900 tabular-nums">{agencyPatients.toLocaleString("en-IN")}</p>
          <p className="text-sm text-slate-500">patients/month at {"₹"}{costPerPatient} each</p>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Monthly Savings</p>
          <p className="text-3xl font-black text-emerald-600 tabular-nums">{"₹"}{Math.max(0, monthlySavings).toLocaleString("en-IN")}</p>
          <p className="text-sm text-slate-500">saved every month</p>
        </div>
        <div className="p-6 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl text-white shadow-lg">
          <p className="text-xs font-bold uppercase tracking-widest mb-2 opacity-80">Annual Savings</p>
          <p className="text-3xl font-black tabular-nums">{"₹"}{Math.max(0, annualSavings).toLocaleString("en-IN")}</p>
          <p className="text-sm opacity-80">saved per year</p>
        </div>
      </div>
      <div className="mt-8 text-center">
        <Link href="/signup" className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-all hover:scale-[1.03] shadow-lg shadow-emerald-500/20">
          Start saving today <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [annual, setAnnual] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [heroTab, setHeroTab] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const pricing = annual ? PRICING_DATA.annual : PRICING_DATA.monthly;

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-slate-900 overflow-x-hidden relative">
      {/* Noise overlay */}
      <div className="fixed inset-0 pointer-events-none z-[1] opacity-[0.015]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")" }} />

      <style>{`
        @keyframes gradient-shift { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
        @keyframes float-up { 0%{transform:translateY(0) scale(1);opacity:0.5} 50%{opacity:0.8} 100%{transform:translateY(-60px) scale(0.5);opacity:0} }
        .animate-gradient{animation:gradient-shift 12s ease infinite;background-size:300% 300%}
        .text-gradient-hero{background:linear-gradient(135deg,#10B981,#14B8A6,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
        .grid-overlay{background-image:repeating-linear-gradient(0deg,rgba(255,255,255,0.06) 0px,rgba(255,255,255,0.06) 1px,transparent 1px,transparent 40px),repeating-linear-gradient(90deg,rgba(255,255,255,0.06) 0px,rgba(255,255,255,0.06) 1px,transparent 1px,transparent 40px)}
      `}</style>

      {/* ─── Nav ─── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "bg-white/90 backdrop-blur-xl border-b border-slate-200/60 shadow-sm" : "bg-transparent"}`}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <Logo size={32} />
            <span className="font-black text-xl tracking-tight text-slate-900">PatientPlex</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-slate-900 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-slate-900 transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-slate-900 transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors hidden sm:block">Sign in</Link>
            <Link href="/signup" className="text-sm font-semibold px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white transition-all hover:scale-[1.03] active:scale-[0.97] hidden sm:inline-flex">Get started</Link>
            <button onClick={() => setMobileMenu(!mobileMenu)} className="md:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors">
              {mobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
        {/* Mobile menu */}
        <AnimatePresence>
          {mobileMenu && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              className="md:hidden bg-white border-t border-slate-200 shadow-lg overflow-hidden">
              <div className="px-6 py-4 space-y-3">
                <a href="#features" onClick={() => setMobileMenu(false)} className="block text-sm font-medium text-slate-600 hover:text-slate-900 py-2">Features</a>
                <a href="#pricing" onClick={() => setMobileMenu(false)} className="block text-sm font-medium text-slate-600 hover:text-slate-900 py-2">Pricing</a>
                <a href="#faq" onClick={() => setMobileMenu(false)} className="block text-sm font-medium text-slate-600 hover:text-slate-900 py-2">FAQ</a>
                <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
                  <Link href="/login" className="text-sm font-medium text-slate-600 py-2">Sign in</Link>
                  <Link href="/signup" className="text-sm font-semibold px-5 py-2.5 rounded-xl bg-slate-900 text-white text-center">Get started</Link>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ═══ HERO ═══ */}
      <section className="pt-28 pb-20 px-6 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-100/90 via-teal-50/60 to-cyan-100/80" />
          <div className="absolute top-0 right-0 w-[60%] h-full bg-gradient-to-l from-amber-50/40 to-transparent" />
          <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-[#FAFAF8] to-transparent" />
        </div>
        <div className="absolute inset-0 opacity-40 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle, #cbd5e1 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
        {/* Floating particles */}
        {[1,2,3,4].map(i => (
          <div key={i} className="absolute rounded-full bg-emerald-400/30 pointer-events-none" style={{
            width: `${4+i*2}px`, height: `${4+i*2}px`,
            left: `${15+i*20}%`, bottom: `${10+i*5}%`,
            animation: `float-up ${4+i}s ease-in-out infinite ${i*1.2}s`
          }} />
        ))}

        <div className="max-w-7xl mx-auto relative">
          <div className="grid lg:grid-cols-2 gap-14 items-center">
            <div>
              <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
                className="text-5xl sm:text-6xl lg:text-[5rem] font-black tracking-tight leading-[1.05] text-slate-900 mb-6">
                AI that books patients<br /><span className="text-gradient-hero">while you sleep</span>
              </motion.h1>

              <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.12 }}
                className="text-lg text-slate-500 leading-relaxed mb-8 max-w-lg">
                Google &amp; Meta ads, a WhatsApp AI receptionist, and smart appointment booking — all on autopilot. Built for healthcare clinics across 15+ specialties in India.
              </motion.p>

              {/* Email CTA */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.22 }}
                className="flex flex-col sm:flex-row gap-3 mb-6">
                <input type="email" placeholder="Enter your email" className="flex-1 px-5 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all shadow-sm" />
                <Link href="/signup" className="group inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition-all hover:scale-[1.03] active:scale-[0.97] shadow-lg shadow-slate-900/20 whitespace-nowrap">
                  Get started <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </motion.div>

              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: 0.28 }}
                className="text-xs text-slate-400 mb-6 flex items-center gap-4">
                <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> No credit card required</span>
                <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> 14-day free trial</span>
                <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Cancel anytime</span>
              </motion.p>

              {/* Trust line */}
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.35 }}
                className="flex items-center gap-2 mb-6">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <p className="text-sm text-slate-500">Start your 14-day free trial — no credit card required</p>
              </motion.div>

              {/* Platform icons */}
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.45 }}
                className="flex items-center gap-3">
                {[
                  <GoogleLogo key="g" size={20} />,
                  <MetaLogo key="m" size={20} />,
                  <WhatsAppLogo key="w" size={20} />,
                  <InstagramLogo key="i" size={20} />,
                  <OpenAILogo key="o" size={20} />,
                  <LinkedInLogo key="l" size={20} />,
                  <GoogleCalendarLogo key="c" size={20} />,
                ].map((icon, i) => (
                  <div key={i} className="w-10 h-10 rounded-xl bg-white border border-slate-200 shadow-sm flex items-center justify-center hover:shadow-md hover:scale-105 transition-all">
                    {icon}
                  </div>
                ))}
              </motion.div>
            </div>

            {/* Dashboard mockup */}
            <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.3 }}
              className="hidden lg:block">
              {/* Stacked product layers like Ryze */}
              <div className="relative pt-14">
                <div className="absolute top-0 left-4 right-4 z-0">
                  <div className="bg-emerald-100/60 rounded-t-xl px-5 py-2 text-[10px] font-bold text-emerald-700 uppercase tracking-widest border border-emerald-200/60 border-b-0">{"●"} Patient CRM</div>
                </div>
                <div className="absolute top-7 left-2 right-2 z-0">
                  <div className="bg-teal-100/60 rounded-t-xl px-5 py-2 text-[10px] font-bold text-teal-700 uppercase tracking-widest border border-teal-200/60 border-b-0">{"●"} Analytics Dashboard</div>
                </div>
                <div className="relative z-10">
              <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl shadow-slate-200/50 overflow-hidden hover:shadow-3xl transition-shadow duration-500">
                <div className="border-b border-slate-100">
                  <div className="flex">
                    {["AI RECEPTIONIST", "AD CAMPAIGNS", "BOOKINGS"].map((tab, i) => (
                      <button key={i} onClick={() => setHeroTab(i)} className={`px-5 py-3.5 text-xs font-bold tracking-wider transition-colors ${heroTab === i ? "text-emerald-600 border-b-2 border-emerald-500 bg-emerald-50/40" : "text-slate-400 hover:text-slate-600"}`}>
                        {heroTab === i && <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 align-middle animate-pulse" />}
                        {tab}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex gap-4">
                    {/* Mini sidebar */}
                    <div className="flex flex-col items-center gap-3 py-2 border-r border-slate-100 pr-4">
                      {[Brain, BarChart3, Star, MessageCircle, Calendar, Globe].map((Icon, idx) => (
                        <div key={idx} className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${idx === 0 ? "bg-emerald-50 text-emerald-600" : "text-slate-300 hover:bg-slate-50 hover:text-slate-500"}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                      ))}
                    </div>
                    {/* Main content */}
                    <div className="flex-1 min-w-0">
                  {/* Tab 0: AI Receptionist */}
                  {heroTab === 0 && (
                    <div>
                      <div className="flex items-start gap-3 mb-6">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shrink-0 shadow-sm"><Brain className="w-4 h-4 text-white" /></div>
                        <div>
                          <p className="text-xs font-bold text-slate-900 mb-1">PatientPlex AI</p>
                          <div className="bg-slate-50 rounded-xl rounded-tl-sm p-4 text-sm text-slate-700 leading-relaxed border border-slate-100">Got it. I have built a campaign for <strong>Bhardwaj Dental Clinic</strong> to maximize bookings this month.</div>
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-slate-50 to-emerald-50/30 rounded-xl p-5 border border-slate-100">
                        <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mb-1">Campaign Setup</p>
                        <p className="font-black text-slate-900 mb-4">Bhardwaj Dental &mdash; Nov bookings</p>
                        <div className="grid grid-cols-3 gap-4 mb-4">
                          {[["Daily budget","₹800","₹24,000/mo"],["Est. clicks/mo","480","Based on local CPCs"],["Est. bookings","24—38","5—8% conv. rate"]].map(([l,v,s],j) => (
                            <div key={j}><p className="text-[10px] text-slate-400 mb-0.5">{l}</p><p className="text-lg font-black text-slate-900">{v}</p><p className="text-[10px] text-slate-400">{s}</p></div>
                          ))}
                        </div>
                        <div className="space-y-2 text-sm">
                          {[["Platforms","Google Search + Meta"],["Radius","5 km from clinic"],["Schedule","Mon—Sat, 7am—9pm"],["Bidding","Maximize conversions"]].map(([k,v],j) => (
                            <div key={j} className="flex justify-between items-center"><span className="text-slate-500">{k}</span><span className="font-semibold text-slate-900">{v}</span></div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  {/* Tab 1: Ad Campaigns */}
                  {heroTab === 1 && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-bold text-slate-900">Active Campaigns</p>
                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">4 running</span>
                      </div>
                      {[{t:"Teeth whitening",budget:"₹500/day",clicks:"85",conv:"6",status:"Active"},{t:"Dental implants",budget:"₹800/day",clicks:"42",conv:"3",status:"Active"},{t:"Root canal",budget:"₹400/day",clicks:"68",conv:"5",status:"Optimizing"},{t:"Braces consultation",budget:"₹300/day",clicks:"94",conv:"7",status:"Active"}].map((c,j) => (
                        <div key={j} className="flex items-center justify-between text-xs bg-slate-50 rounded-xl p-3 border border-slate-100">
                          <div className="w-32"><p className="font-semibold text-slate-800">{c.t}</p><p className="text-[10px] text-slate-400">{c.budget}</p></div>
                          <div className="text-center"><p className="font-bold text-slate-800">{c.clicks}</p><p className="text-[10px] text-slate-400">clicks</p></div>
                          <div className="text-center"><p className="font-bold text-emerald-600">{c.conv}</p><p className="text-[10px] text-slate-400">bookings</p></div>
                          <span className={`font-semibold px-2 py-0.5 rounded text-[10px] ${c.status === "Active" ? "bg-emerald-50 text-emerald-600 border border-emerald-100" : "bg-amber-50 text-amber-600 border border-amber-100"}`}>{c.status}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Tab 2: Bookings */}
                  {heroTab === 2 && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-bold text-slate-900">Recent Bookings</p>
                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Live</span>
                      </div>
                      {[{n:"Ravi M.",t:"Teeth cleaning",time:"Just now",amt:"₹1,500",s:"Confirmed"},{n:"Sunita P.",t:"Root canal",time:"2m ago",amt:"₹4,500",s:"Confirmed"},{n:"Deepak S.",t:"Dental implant consult",time:"5m ago",amt:"₹500",s:"Pending"},{n:"Meera K.",t:"Teeth whitening",time:"8m ago",amt:"₹2,500",s:"Confirmed"}].map((b,j) => (
                        <div key={j} className="flex items-center justify-between text-xs bg-slate-50 rounded-xl p-3 border border-slate-100">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-[10px] font-bold text-white">{b.n[0]}</div>
                            <div><p className="font-semibold text-slate-800">{b.t}</p><p className="text-[10px] text-slate-400">{b.n} &middot; {b.time}</p></div>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-emerald-600">{b.amt}</p>
                            <p className={`text-[9px] font-medium ${b.s === "Confirmed" ? "text-emerald-500" : "text-amber-500"}`}>{b.s === "Confirmed" ? "✓ " : "● "}{b.s}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                    </div>
                  </div>
                  {/* Action buttons */}
                  <div className="flex items-center justify-end gap-2 mt-4 pt-4 border-t border-slate-100">
                    <button className="text-xs font-medium text-slate-500 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">Edit first</button>
                    <button className="text-xs font-semibold text-white bg-emerald-500 px-4 py-1.5 rounded-lg hover:bg-emerald-600 transition-colors">Launch campaign</button>
                  </div>
                </div>
                {/* Chat input */}
                <div className="px-6 pb-5">
                  <div className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200">
                    <Brain className="w-4 h-4 text-slate-300 shrink-0" />
                    <span className="text-xs text-slate-400">Ask PatientPlex anything about your ads...</span>
                    <ArrowRight className="w-4 h-4 text-slate-300 ml-auto shrink-0" />
                  </div>
                </div>
              </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ═══ TECH STACK BAR ═══ */}
      <section className="py-8 border-y border-slate-200/60 bg-white/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col sm:flex-row items-center gap-6 sm:gap-0 justify-between">
            <p className="text-xs font-medium text-slate-400 uppercase tracking-widest whitespace-nowrap">Built with</p>
            <div className="flex items-center gap-4 sm:gap-8">
              {TECH_STACK.map((name, i) => (
                <span key={i} className="flex items-center gap-4 sm:gap-8">
                  <span className="text-sm sm:text-base font-semibold text-slate-400 tracking-tight whitespace-nowrap">{name}</span>
                  {i < TECH_STACK.length - 1 && <span className="w-1 h-1 rounded-full bg-slate-200 hidden sm:block" />}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ HOW MUCH ARE YOU LOSING? ═══ */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-center mb-3">
              Every missed enquiry is a potential patient lost to a competitor
            </h2>
            <p className="text-center text-slate-500 mb-12 max-w-2xl mx-auto">
              That{"'"}s the estimated lifetime value of a dental patient in India, based on industry data.
            </p>
          </Reveal>
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {[
              { value: "₹2.4L/month", desc: "Potential revenue lost from missed after-hours enquiries*", icon: TrendingDown, color: "text-red-500 bg-red-50" },
              { value: "73%", desc: "Of patients book with the first clinic that responds", icon: Clock, color: "text-amber-500 bg-amber-50" },
              { value: "4.2x", desc: "More bookings when you respond within 5 minutes", icon: Zap, color: "text-emerald-500 bg-emerald-50" },
            ].map((s, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="text-center p-8 bg-slate-50 rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                  <div className={`w-12 h-12 rounded-xl ${s.color} flex items-center justify-center mx-auto mb-4`}>
                    <s.icon className="w-6 h-6" />
                  </div>
                  <div className="text-3xl font-black text-slate-900 mb-2">{s.value}</div>
                  <p className="text-sm text-slate-500">{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
          <Reveal>
            <p className="text-center text-sm text-emerald-600 font-medium">
              PatientPlex makes sure you never miss another patient <ArrowRight className="w-4 h-4 inline ml-1" />
            </p>
          </Reveal>
        </div>
      </section>

      {/* ═══ CHANNELS ═══ */}
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <Reveal>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight leading-tight mb-6">AI to manage patients across every channel</h2>
              <p className="text-lg text-slate-500 leading-relaxed">WhatsApp, Google, Instagram, ChatGPT, LinkedIn, phone calls &mdash; PatientPlex captures patients from every touchpoint and funnels them into your calendar.</p>
            </Reveal>
            <Reveal delay={0.15}>
              <div className="grid grid-cols-3 gap-4 relative">
                <div className="absolute -inset-6 bg-gradient-to-br from-emerald-50 via-transparent to-cyan-50 rounded-3xl -z-10" />
                {CHANNELS_DATA.map((ch, i) => {
                  const icons = [
                    <WhatsAppLogo key="wa" size={28} />,
                    <GoogleAdsLogo key="ga" size={28} />,
                    <InstagramLogo key="ig" size={28} />,
                    <FacebookLogo key="fb" size={28} />,
                    <OpenAILogo key="oa" size={28} />,
                    <LinkedInLogo key="li" size={28} />,
                    <Phone key="ph" className="w-7 h-7 text-violet-600" />,
                    <Globe key="gl" className="w-7 h-7 text-emerald-600" />,
                  ];
                  return (
                    <motion.div key={i} whileHover={{ y: -4, scale: 1.02 }}
                      className={`bg-white rounded-2xl border border-slate-200 ${ch.border} p-6 flex flex-col items-center gap-3 shadow-sm hover:shadow-lg transition-all duration-300 cursor-default`}>
                      <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center">
                        {icons[i]}
                      </div>
                      <span className="text-sm font-semibold text-slate-700">{ch.name}</span>
                    </motion.div>
                  );
                })}
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ═══ SPECIALTIES WE SERVE ═══ */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Built for every type of clinic</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">15+ medical specialties trust PatientPlex</p>
          </Reveal>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {[
              { emoji: "🦷", name: "Dental & Cosmetic Dentistry" },
              { emoji: "🧴", name: "Dermatology & Skin Care" },
              { emoji: "👁️", name: "Ophthalmology & Eye Care" },
              { emoji: "🦴", name: "Orthopedics & Sports Medicine" },
              { emoji: "🤰", name: "Gynecology & Obstetrics" },
              { emoji: "🧬", name: "IVF & Fertility" },
              { emoji: "👶", name: "Pediatrics" },
              { emoji: "🧠", name: "Neurology" },
              { emoji: "❤️", name: "Cardiology" },
              { emoji: "🫁", name: "Pulmonology" },
              { emoji: "🦻", name: "ENT (Ear, Nose, Throat)" },
              { emoji: "💊", name: "General Medicine" },
              { emoji: "🏥", name: "Multi-Specialty Hospitals" },
              { emoji: "🧘", name: "Physiotherapy & Rehab" },
              { emoji: "💉", name: "Aesthetic & Cosmetic Surgery" },
              { emoji: "🔬", name: "Diagnostic Centers" },
            ].map((spec, i) => (
              <Reveal key={i} delay={i * 0.03}>
                <motion.div whileHover={{ scale: 1.03 }} className="flex items-center gap-3 bg-[#FAFAF8] rounded-xl border border-slate-200 px-4 py-3.5 hover:shadow-md hover:border-emerald-200 transition-all duration-200 cursor-default">
                  <span className="text-lg shrink-0">{spec.emoji}</span>
                  <span className="text-sm font-medium text-slate-700">{spec.name}</span>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ INTEGRATIONS ═══ */}
      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Connects with tools you already use</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">PatientPlex integrates with the platforms your clinic relies on — no manual data entry.</p>
          </Reveal>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: "Google Ads", desc: "Auto-optimize campaigns", logo: <GoogleAdsLogo size={24} /> },
              { name: "Meta Ads", desc: "Facebook + Instagram ads", logo: <MetaLogo size={24} /> },
              { name: "ChatGPT Ads", desc: "Sponsored answers in ChatGPT", logo: <OpenAILogo size={24} /> },
              { name: "LinkedIn Ads", desc: "B2B doctor referral campaigns", logo: <LinkedInLogo size={24} /> },
              { name: "WhatsApp Business", desc: "AI chatbot receptionist", logo: <WhatsAppLogo size={24} /> },
              { name: "Google Calendar", desc: "Appointment sync", logo: <GoogleCalendarLogo size={24} /> },
              { name: "Google My Business", desc: "Review management", logo: <GoogleLogo size={24} /> },
              { name: "Google Reviews", desc: "Automated review collection", logo: <GoogleLogo size={24} /> },
            ].map((item, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <motion.div whileHover={{ y: -3 }} className="bg-[#FAFAF8] rounded-2xl border border-slate-200 p-5 flex items-start gap-4 hover:shadow-lg transition-all duration-300 cursor-default">
                  <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center shrink-0">
                    {item.logo}
                  </div>
                  <div>
                    <p className="font-bold text-slate-900 text-sm">{item.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                  </div>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ VIDEO DEMO ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">
              See PatientPlex in action
            </h2>
            <p className="text-center text-slate-500 mb-12 text-lg">
              Watch how PatientPlex sets up your clinic for automated patient acquisition
            </p>
          </Reveal>
          <Reveal delay={0.15}>
            <div className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-slate-800 to-slate-900 aspect-video flex items-center justify-center group cursor-pointer shadow-2xl">
              {/* Grid pattern overlay */}
              <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
              {/* Play button */}
              <div className="relative z-10 w-20 h-20 rounded-full bg-white/90 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <Play className="w-8 h-8 text-slate-900 ml-1" fill="currentColor" />
              </div>
              {/* Duration badge */}
              <div className="absolute bottom-4 right-4 px-3 py-1 rounded-lg bg-black/60 text-white text-xs font-medium">
                2:34
              </div>
              {/* Decorative elements */}
              <div className="absolute top-6 left-6 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              </div>
            </div>
            <p className="text-center text-sm text-slate-400 mt-4">
              Watch the full demo — no signup required
            </p>
            <div className="flex flex-wrap items-center justify-center gap-6 mt-6 text-sm text-slate-500">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> See the AI receptionist in action</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Watch ads get created automatically</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Real clinic dashboard walkthrough</span>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ WALL OF LOVE ═══ */}
      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-3">What clinics can expect <span className="inline-block">{"💡"}</span></h2>
            <p className="text-center text-slate-500 mb-16 text-lg">Real results from our client and projected scenarios for different specialties.</p>
          </Reveal>
          <div className="columns-1 md:columns-2 lg:columns-3 gap-5 space-y-5">
            {TESTIMONIALS.map((t, i) => (
              <Reveal key={i} delay={i * 0.07}>
                <div className="break-inside-avoid bg-[#FAFAF8] rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                  {/* Gradient top accent */}
                  <div className="h-1 bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400" />
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-sm font-black text-white shadow-sm">
                          {t.avatar}
                        </div>
                        <div>
                          <p className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                            {t.name} {(t as any).isReal ? <span className="text-[9px] font-bold bg-emerald-500 text-white px-1.5 py-0.5 rounded-full">Active Client</span> : <BadgeCheck className="w-4 h-4 text-emerald-500" />}
                          </p>
                          <p className="text-xs text-slate-500">{t.role}</p>
                        </div>
                      </div>
                      {t.platform === "google" && (
                        <svg width="20" height="20" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                      )}
                      {t.platform === "linkedin" && (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="#0A66C2"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg>
                      )}
                      {t.platform === "twitter" && (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#000"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                      )}
                    </div>
                    <p className="text-sm text-slate-700 leading-relaxed mb-4">{t.text}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-0.5">
                        {[...Array(t.rating)].map((_, j) => <Star key={j} className="w-3.5 h-3.5 text-amber-400" fill="currentColor" />)}
                      </div>
                      <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">{t.metric}</span>
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
          <Reveal delay={0.3}>
            <p className="text-center mt-12 text-slate-500 text-sm">Start your free trial today</p>
            <p className="text-center mt-2 text-slate-400 text-xs">*Bhardwaj Dental Clinic is our active client. Other testimonials are projected scenarios. Results vary by budget, location, and specialty.</p>
          </Reveal>
        </div>
      </section>

      {/* ═══ SUCCESS STORIES ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Real results & projected outcomes</h2>
            <p className="text-center text-slate-500 mb-16 text-lg">Bhardwaj Dental Clinic is our active client. Other scenarios show projected outcomes.</p>
          </Reveal>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { clinic: "Bhardwaj Dental Clinic", headline: "₹5–8 per lead, ₹60–80 per booked patient via Google Ads", metrics: [["Cost per lead", "₹5–8"], ["Cost per booking", "₹60–80"], ["Status", "Active client"]], color: "from-emerald-500 to-teal-500", isReal: true },
              { clinic: "Demo: Dermatology clinic, Delhi", headline: "Projected: Lower acquisition costs with AI-managed campaigns", metrics: [["Target cost per lead", "₹6–10"], ["Target cost per booking", "₹80–150"], ["Expected ROAS", "3–5x"]], color: "from-cyan-500 to-blue-500" },
              { clinic: "Demo: Multi-specialty, Bengaluru", headline: "Projected: Unified patient acquisition across specialties", metrics: [["Specialties covered", "5+"], ["Target response time", "<2 min"], ["Booking automation", "WhatsApp AI"]], color: "from-violet-500 to-purple-500" },
            ].map((cs, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow h-full flex flex-col">
                  <div className={`h-2 bg-gradient-to-r ${cs.color}`} />
                  <div className="p-6 flex-1 flex flex-col">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">{cs.clinic}</p>
                    <h3 className="text-lg font-black text-slate-900 mb-4 leading-snug">{cs.headline}</h3>
                    <div className="space-y-2 mb-6 flex-1">
                      {cs.metrics.map(([label, val], j) => (
                        <div key={j} className="flex justify-between items-center text-sm">
                          <span className="text-slate-500">{label}</span>
                          <span className="font-bold text-slate-900">{val}</span>
                        </div>
                      ))}
                    </div>
                    <a href="#" className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 transition-colors">
                      See projected results <ArrowRight className="w-3.5 h-3.5 inline ml-1" />
                    </a>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ STATS ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal><h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-16">What PatientPlex delivers</h2></Reveal>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {STATS.map((s, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="relative text-center p-8 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-emerald-400 to-teal-500 rounded-r" />
                  <div className="inline-flex p-2.5 rounded-xl bg-emerald-50 mb-3">
                    <s.icon className="w-5 h-5 text-emerald-600" />
                  </div>
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

      {/* ═══ ROI CALCULATOR ═══ */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Calculate your ROI</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">See how much you could save by switching from agencies to PatientPlex.</p>
          </Reveal>
          <ROICalculator />
        </div>
      </section>

      {/* ═══ BEFORE / AFTER ═══ */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">The PatientPlex difference</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">See what changes when AI runs your patient acquisition.</p>
          </Reveal>
          <div className="grid md:grid-cols-2 gap-6">
            <Reveal>
              <div className="p-8 rounded-2xl border border-red-200 bg-red-50/30 h-full">
                <div className="flex items-center gap-2.5 mb-6">
                  <Clock className="w-5 h-5 text-red-500" />
                  <h3 className="text-xl font-black text-slate-900">Before PatientPlex</h3>
                </div>
                <ul className="space-y-4">
                  {["Missed calls & WhatsApp messages after hours", "₹500–1,500+ cost per patient booking with agencies", "No idea which ads actually bring patients", "High patient no-show rate", "Manual everything — reminders, follow-ups, booking"].map((item, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
                      <span className="w-2 h-2 rounded-full bg-red-400 mt-1.5 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </Reveal>
            <Reveal delay={0.15}>
              <div className="p-8 rounded-2xl border border-emerald-200 bg-emerald-50/30 h-full">
                <div className="flex items-center gap-2.5 mb-6">
                  <Zap className="w-5 h-5 text-emerald-500" />
                  <h3 className="text-xl font-black text-slate-900">After PatientPlex</h3>
                </div>
                <ul className="space-y-4">
                  {["24/7 AI WhatsApp receptionist", "₹5–8 per lead, ₹60–80 per booking (Bhardwaj Dental data)", "Full-funnel attribution on every rupee", "Reduced no-shows with auto WhatsApp reminders", "Everything automated — ads, booking, follow-ups"].map((item, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ═══ COMPARISON TABLE ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Why clinics switch to PatientPlex</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">Compare us to agencies and DIY — see the difference.</p>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-4 px-5 font-bold text-slate-900">Feature</th>
                      <th className="py-4 px-5 font-black text-emerald-700 bg-emerald-50/60 text-center"><span className="inline-flex items-center gap-1">PatientPlex <span className="text-[9px] font-bold bg-emerald-500 text-white px-1.5 py-0.5 rounded-full">Recommended</span></span></th>
                      <th className="py-4 px-5 font-bold text-slate-500 text-center">Agencies</th>
                      <th className="py-4 px-5 font-bold text-slate-500 text-center">DIY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["Monthly cost", "₹4,999–24,999", "₹30,000–1,00,000", "Free but time-costly"],
                      ["Setup time", "10 minutes", "2–4 weeks", "Weeks of learning"],
                      ["AI receptionist", true, false, false],
                      ["Ad optimization", "Auto", "Manual", "Manual"],
                      ["WhatsApp booking", true, false, false],
                      ["Full transparency", true, "Limited reports", "Full but complex"],
                      ["No-show reduction", "Auto reminders", false, "Manual"],
                      ["Contract lock-in", false, "6–12 months", false],
                    ].map((row, i) => (
                      <tr key={i} className="border-b border-slate-100 last:border-0">
                        <td className="py-3.5 px-5 text-slate-700 font-medium">{row[0] as string}</td>
                        <td className="py-3.5 px-5 bg-emerald-50/40 text-center font-semibold">
                          {row[1] === true ? <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" /> : row[1] === false ? <span className="text-xs text-slate-400">No lock-in ✓</span> : <span className="text-emerald-700">{row[1] as string}</span>}
                        </td>
                        <td className="py-3.5 px-5 text-center text-slate-500">
                          {row[2] === true ? <CheckCircle2 className="w-5 h-5 text-slate-400 mx-auto" /> : row[2] === false ? <X className="w-5 h-5 text-red-400 mx-auto" /> : (row[2] as string)}
                        </td>
                        <td className="py-3.5 px-5 text-center text-slate-500">
                          {row[3] === true ? <CheckCircle2 className="w-5 h-5 text-slate-400 mx-auto" /> : row[3] === false ? <X className="w-5 h-5 text-red-400 mx-auto" /> : (row[3] as string)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Live in 10 minutes, not 10 weeks</h2>
            <p className="text-center text-lg text-slate-500 mb-16">No agencies, no contracts, no technical setup.</p>
          </Reveal>
          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-10 left-[18%] right-[18%] h-px bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300" />
            {[
              { step: "01", title: "Tell us about your clinic", desc: "Specialty, location, treatments, budget. Takes about 3 minutes. We generate your landing pages and ad creatives automatically.", icon: Users, color: "bg-emerald-50 text-emerald-600" },
              { step: "02", title: "Connect WhatsApp & Calendar", desc: "Link your clinic WhatsApp Business number and Google Calendar. The AI receptionist starts handling enquiries immediately.", icon: MessageCircle, color: "bg-teal-50 text-teal-600" },
              { step: "03", title: "Patients start booking", desc: "Campaigns go live within hours. The AI qualifies leads, books appointments, and sends reminders. You focus on patient care.", icon: Calendar, color: "bg-cyan-50 text-cyan-600" },
            ].map((s, i) => (
              <Reveal key={i} delay={i * 0.15}>
                <div className="text-center relative">
                  <div className={`w-20 h-20 rounded-2xl ${s.color} flex items-center justify-center mx-auto mb-6 relative z-10 shadow-sm`}>
                    <s.icon className="w-8 h-8" />
                  </div>
                  <div className="text-xs font-black text-emerald-500 uppercase tracking-widest mb-2">Step {s.step}</div>
                  <h3 className="text-lg font-black text-slate-900 mb-3">{s.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ USE CASES ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">How clinics use PatientPlex</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">Real use cases across 15+ healthcare specialties.</p>
          </Reveal>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "Dental Clinics", emoji: "🦷", gradient: "from-emerald-400 to-teal-400", items: ["Teeth whitening & cosmetic dentistry campaigns", "Orthodontic consultation bookings via WhatsApp", "Implant patient follow-up automation", "Review collection after procedures"] },
              { title: "Dermatology & Skin Clinics", emoji: "✨", gradient: "from-pink-400 to-rose-400", items: ["Laser treatment & cosmetic procedure ads", "Skin consultation bookings", "Before/after gallery promotion", "Seasonal campaign automation"] },
              { title: "Eye Clinics & Ophthalmology", emoji: "👁️", gradient: "from-blue-400 to-indigo-400", items: ["LASIK & cataract surgery campaigns", "Vision checkup appointment booking", "Post-surgery follow-up reminders", "Insurance-covered procedure marketing"] },
              { title: "Orthopedic & Physiotherapy", emoji: "🦴", gradient: "from-amber-400 to-orange-400", items: ["Joint replacement awareness campaigns", "Physiotherapy session scheduling", "Sports injury clinic marketing", "Post-op rehabilitation booking"] },
              { title: "Gynecology & IVF Clinics", emoji: "🤰", gradient: "from-purple-400 to-violet-400", items: ["Fertility treatment awareness ads", "Prenatal checkup scheduling", "IVF consultation bookings", "Sensitive patient communication AI"] },
              { title: "General & Multi-Specialty", emoji: "🏥", gradient: "from-cyan-400 to-blue-400", items: ["Cross-department patient routing", "Multi-location campaign management", "Health checkup package promotion", "Centralized analytics dashboard"] },
            ].map((useCase, i) => (
              <Reveal key={i} delay={i * 0.12}>
                <motion.div whileHover={{ y: -4 }} className="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                  <div className={`h-1.5 bg-gradient-to-r ${useCase.gradient}`} />
                  <div className="p-7">
                    <div className="text-3xl mb-4">{useCase.emoji}</div>
                    <h3 className="text-xl font-black text-slate-900 mb-5">{useCase.title}</h3>
                    <ul className="space-y-3">
                      {useCase.items.map((item, j) => (
                        <li key={j} className="flex items-start gap-2.5 text-sm text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FEATURES ═══ */}
      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">See what PatientPlex does inside your account</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">Three autonomous AI agents working 24/7 to grow your clinic.</p>
          </Reveal>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: "Autonomous\nAI receptionist", gradient: "from-emerald-400 to-teal-400", bullets: ["24/7 WhatsApp responses", "Multi-language support", "Smart lead qualification", "Instant appointment booking"], icon: Brain,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6 space-y-3">
                    <div className="flex items-start gap-2"><div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center shrink-0 mt-0.5"><MessageCircle className="w-3 h-3 text-green-600" /></div><div className="bg-green-50 rounded-lg rounded-tl-sm p-2.5 text-xs text-slate-700 border border-green-100">Hi! I want to book a teeth whitening appointment.</div></div>
                    <div className="flex items-start gap-2 justify-end"><div className="bg-emerald-50 rounded-lg rounded-tr-sm p-2.5 text-xs text-slate-700 border border-emerald-100">Great choice! Dr. Sharma has slots on Tuesday at 10am and Thursday at 3pm. Which works better?</div><div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shrink-0 mt-0.5"><Brain className="w-3 h-3 text-white" /></div></div>
                    <div className="flex items-start gap-2"><div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center shrink-0 mt-0.5"><MessageCircle className="w-3 h-3 text-green-600" /></div><div className="bg-green-50 rounded-lg rounded-tl-sm p-2.5 text-xs text-slate-700 border border-green-100">Tuesday 10am please!</div></div>
                    <div className="flex items-start gap-2 justify-end"><div className="bg-emerald-50 rounded-lg rounded-tr-sm p-2.5 text-xs text-slate-700 border border-emerald-100"><span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Booked! Confirmation sent to your WhatsApp.</span></div><div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shrink-0 mt-0.5"><Brain className="w-3 h-3 text-white" /></div></div>
                  </div>
                )},
              { title: "Autonomous\nad campaigns", gradient: "from-blue-400 to-cyan-400", bullets: ["Google + Meta on autopilot", "Geo-targeted within 5km", "A/B tested creatives", "Auto-optimized bids"], icon: BarChart3,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6 space-y-2">
                    {[{l:"Teeth whitening",cpc:"₹3.20",clicks:"142",ctr:"4.8%",s:"Active"},{l:"Dental implants",cpc:"₹5.50",clicks:"89",ctr:"3.2%",s:"Active"},{l:"Root canal treatment",cpc:"₹4.80",clicks:"106",ctr:"5.4%",s:"Optimizing"},{l:"Braces consultation",cpc:"₹2.80",clicks:"178",ctr:"6.1%",s:"Active"}].map((ad,j) => (
                      <div key={j} className="flex items-center justify-between text-xs bg-white rounded-lg p-2.5 border border-slate-100 hover:border-slate-200 transition-colors">
                        <span className="font-medium text-slate-700 w-28 truncate">{ad.l}</span>
                        <span className="text-slate-400 tabular-nums">{ad.cpc}</span>
                        <span className="text-slate-400 tabular-nums">{ad.clicks}</span>
                        <span className="text-slate-400 tabular-nums">{ad.ctr}</span>
                        <span className={`font-semibold px-2 py-0.5 rounded text-[10px] ${ad.s === "Active" ? "bg-emerald-50 text-emerald-600 border border-emerald-100" : "bg-amber-50 text-amber-600 border border-amber-100"}`}>{ad.s}</span>
                      </div>
                    ))}
                  </div>
                )},
              { title: "Autonomous\npatient booking", gradient: "from-violet-400 to-purple-400", bullets: ["Google Calendar sync", "WhatsApp reminders", "60% fewer no-shows", "Smart rescheduling"], icon: Calendar,
                mockup: (
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mt-6 space-y-2">
                    {MOCK_QUEUE.map((p,j) => (
                      <div key={j} className="flex items-center justify-between text-xs bg-white rounded-lg p-3 border border-slate-100 hover:border-slate-200 transition-colors">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-[9px] font-bold text-white">{p.name[0]}</div>
                          <div><p className="font-medium text-slate-700">{p.treatment}</p><p className="text-[10px] text-slate-400">{p.name} &middot; {p.time}</p></div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-emerald-600">{p.amount}</span>
                          <p className="text-[9px] text-emerald-500 flex items-center gap-0.5 justify-end"><CheckCircle2 className="w-2.5 h-2.5" /> Confirmed</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )},
            ].map((feat, i) => (
              <Reveal key={i} delay={i * 0.12}>
                <motion.div whileHover={{ y: -6 }} className="h-full bg-[#FAFAF8] rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                  <div className={`h-1.5 bg-gradient-to-r ${feat.gradient}`} />
                  <div className="p-7">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center mb-5">
                      <feat.icon className="w-5 h-5 text-slate-800" />
                    </div>
                    <h3 className="text-2xl font-black text-slate-900 mb-4 whitespace-pre-line leading-tight">{feat.title}</h3>
                    <ul className="space-y-2.5">
                      {feat.bullets.map((b,j) => <li key={j} className="flex items-center gap-2.5 text-sm text-slate-600"><span className="w-1.5 h-1.5 rounded-full bg-slate-800 shrink-0" />{b}</li>)}
                    </ul>
                    {feat.mockup}
                    <a href="#" className="inline-flex items-center gap-1 text-sm font-semibold text-emerald-600 mt-5 hover:text-emerald-700 transition-colors group">
                      Learn more <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </a>
                  </div>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ LIVE RESULTS + CTA ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-0 rounded-3xl overflow-hidden border border-slate-200 shadow-2xl shadow-emerald-500/5">
            <div className="bg-gradient-to-br from-emerald-500 via-teal-400 to-cyan-400 p-10 sm:p-14 text-white relative overflow-hidden">
              <div className="absolute inset-0 grid-overlay" />
              <div className="relative">
                <Reveal>
                  <h3 className="text-sm font-bold uppercase tracking-widest opacity-80 mb-6">Platform performance targets</h3>
                  <p className="text-4xl sm:text-5xl font-black mb-10">Built to deliver</p>
                  <div className="space-y-8">
                    {[
                      { category: "PAID ADS", items: [["Target ROAS", "4x+"], ["Revenue potential", "Scales with budget"]] },
                      { category: "WHATSAPP AI", items: [["Response time", "<5 min"], ["Target response rate", "90%+"]] },
                      { category: "BOOKINGS", items: [["Cost per lead target", "₹5–10"], ["Cost per booking target", "₹50–100"]] },
                    ].map((g, i) => (
                      <div key={i}>
                        <p className="text-xs font-bold uppercase tracking-widest opacity-60 mb-3"><span className="inline-block w-1.5 h-1.5 rounded-full bg-white mr-1.5 align-middle opacity-80" />{g.category}</p>
                        {g.items.map(([l,v],j) => (
                          <div key={j} className="flex items-center justify-between py-1.5"><span className="text-sm opacity-80">{l}</span><span className="font-mono font-black text-xl">{v}</span></div>
                        ))}
                      </div>
                    ))}
                  </div>
                  <p className="mt-8 text-[10px] opacity-50">*Based on industry benchmarks for healthcare digital marketing in India</p>
                  <div className="mt-3 flex items-center gap-3">
                    <p className="text-xs opacity-80 font-mono flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-300 animate-pulse" /> All systems operational</p>
                  </div>
                </Reveal>
              </div>
            </div>
            <div className="bg-white p-10 sm:p-14 flex flex-col justify-center">
              <Reveal delay={0.15}>
                <h3 className="text-4xl sm:text-5xl font-black text-slate-900 mb-4 leading-tight">Let AI Run<br />Your Clinic</h3>
                <p className="text-slate-500 mb-8 text-lg">Autonomous agents that acquire patients, book appointments and optimize your ads &mdash; around the clock.</p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <input type="email" placeholder="work@email.com" className="flex-1 px-5 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition-all" />
                  <Link href="/signup" className="group inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition-all hover:scale-[1.03] active:scale-[0.97] shadow-lg shadow-slate-900/20 whitespace-nowrap">
                    Get started <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
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
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Simple pricing, real results</h2>
            <p className="text-center text-lg text-slate-500 mb-8 max-w-2xl mx-auto">Every plan includes a 14-day free trial. No credit card required.</p>
            {/* Toggle */}
            <div className="flex items-center justify-center gap-3 mb-16">
              <span className={`text-sm font-medium ${!annual ? "text-slate-900" : "text-slate-400"}`}>Monthly</span>
              <button onClick={() => setAnnual(!annual)} className={`relative w-14 h-7 rounded-full transition-colors ${annual ? "bg-emerald-500" : "bg-slate-300"}`}>
                <div className={`absolute top-0.5 w-6 h-6 rounded-full bg-white shadow transition-transform ${annual ? "translate-x-7.5 left-0" : "left-0.5"}`} style={{ transform: annual ? "translateX(30px)" : "translateX(0)" }} />
              </button>
              <span className={`text-sm font-medium ${annual ? "text-slate-900" : "text-slate-400"}`}>Annual</span>
              {annual && <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">Save 20%</span>}
            </div>
          </Reveal>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {pricing.map((p, i) => (
              <Reveal key={`${annual}-${i}`} delay={i * 0.1}>
                <motion.div whileHover={{ y: -4 }} className={`relative p-7 rounded-2xl border h-full flex flex-col transition-all duration-300 ${p.highlight ? "border-emerald-500 bg-emerald-50/20 shadow-xl shadow-emerald-500/10 ring-1 ring-emerald-500/20" : "border-slate-200 bg-[#FAFAF8] hover:shadow-lg"}`}>
                  {p.badge && <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/30">{p.badge}</div>}
                  <div className="mb-6">
                    <h3 className="font-black text-xl text-slate-900 mb-1">{p.name}</h3>
                    <p className="text-xs text-slate-500 mb-5">{p.desc}</p>
                    <div className="flex items-baseline gap-1">
                      <span className="text-lg text-slate-400">{"₹"}</span>
                      <span className="text-5xl font-black text-slate-900 tabular-nums">{p.price}</span>
                      <span className="text-sm text-slate-400">{p.period}</span>
                    </div>
                    <p className="text-[11px] text-emerald-600 font-medium mt-2 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Includes 14-day free trial</p>
                  </div>
                  <ul className="space-y-3 mb-8 flex-1">
                    {p.features.map((f,j) => <li key={j} className="flex items-start gap-2.5 text-sm text-slate-600"><CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />{f}</li>)}
                  </ul>
                  <Link href="/signup" className={`group block text-center py-3.5 rounded-xl font-semibold text-sm transition-all ${p.highlight ? "bg-slate-900 hover:bg-slate-800 text-white shadow-lg shadow-slate-900/20 hover:scale-[1.02]" : "bg-white border border-slate-300 hover:border-slate-400 text-slate-700 hover:text-slate-900 hover:shadow-md"}`}>
                    {p.cta} <ArrowRight className="w-4 h-4 inline ml-1 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ AI FEATURES DEEP DIVE ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">AI that gets smarter every day</h2>
            <p className="text-center text-slate-500 mb-16 text-lg max-w-2xl mx-auto">Our AI learns from every interaction to deliver better results for your clinic.</p>
          </Reveal>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: Globe, title: "Smart Language Detection", desc: "Automatically detects Hindi, English, Tamil, Telugu, Marathi and responds in the patient's language. No configuration needed.", color: "text-emerald-600 bg-emerald-50" },
              { icon: Brain, title: "Treatment Recommendations", desc: "Suggests relevant treatments based on patient symptoms and your clinic's services. Increases average booking value by 35%.", color: "text-cyan-600 bg-cyan-50" },
              { icon: Activity, title: "Sentiment Analysis", desc: "Detects frustrated or urgent patients and escalates to clinic staff instantly. Never lose a high-value patient to a slow response.", color: "text-violet-600 bg-violet-50" },
              { icon: Calendar, title: "Predictive Scheduling", desc: "Predicts no-shows and overbooking patterns, then suggests optimal appointment slots. Reduces gaps in your calendar by 40%.", color: "text-amber-600 bg-amber-50" },
            ].map((f, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="bg-white rounded-2xl border border-slate-200 p-7 hover:shadow-lg transition-shadow flex gap-5">
                  <div className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center shrink-0`}>
                    <f.icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 mb-2">{f.title}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ TRUST & SECURITY ═══ */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Enterprise-grade security for patient data</h2>
            <p className="text-center text-lg text-slate-500 mb-16 max-w-2xl mx-auto">Built for healthcare compliance from day one.</p>
          </Reveal>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { icon: Shield, title: "Data Encryption", desc: "AES-256 encryption at rest, TLS 1.3 for all data in transit. Your patient data is always protected.", color: "text-emerald-600", bg: "bg-emerald-50" },
              { icon: Lock, title: "Access Control", desc: "Role-based permissions for your team. Two-factor authentication on every account.", color: "text-blue-600", bg: "bg-blue-50" },
              { icon: Award, title: "Audit Logging", desc: "Complete activity trails for every action. HIPAA-aligned compliance logging built in.", color: "text-violet-600", bg: "bg-violet-50" },
              { icon: Globe, title: "Data Residency", desc: "All servers located in India. Your patient data never leaves the country. Full GDPR compliance.", color: "text-teal-600", bg: "bg-teal-50" },
            ].map((card, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <motion.div whileHover={{ y: -3 }} className="p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-lg transition-all duration-300 h-full">
                  <div className={`w-12 h-12 rounded-xl ${card.bg} ${card.color} flex items-center justify-center mb-4`}>
                    <card.icon className="w-6 h-6" />
                  </div>
                  <h3 className="font-black text-slate-900 mb-2">{card.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{card.desc}</p>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ GETTING STARTED CTA ═══ */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-emerald-500 to-teal-500 rounded-3xl p-10 sm:p-14 text-center text-white">
            <Reveal>
              <p className="text-sm font-medium text-white/70 uppercase tracking-widest mb-3">Start growing your clinic with AI-powered marketing</p>
              <h2 className="text-3xl sm:text-4xl font-black tracking-tight mb-6">Ready to stop losing patients?</h2>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 mb-8">
                {["14-day free trial — no credit card", "Live campaign within 48 hours", "Cancel anytime, no contracts"].map((t, i) => (
                  <span key={i} className="flex items-center gap-2 text-sm font-medium text-white/90">
                    <CheckCircle2 className="w-4 h-4 text-white shrink-0" /> {t}
                  </span>
                ))}
              </div>
              <Link href="/signup" className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-emerald-700 font-bold text-lg hover:bg-slate-50 transition-colors shadow-lg">
                Start your free trial <ArrowRight className="w-5 h-5" />
              </Link>
              <p className="text-sm text-white/60 mt-4">Or schedule a 15-minute demo call</p>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ═══ POWERED BY ═══ */}
      <section className="py-10 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-4">Powered by</p>
          <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10">
            {["Google Ads API", "Meta Marketing API", "ChatGPT Ads API", "LinkedIn Marketing API", "WhatsApp Business API", "OpenAI"].map((p, i) => (
              <span key={i} className="text-sm sm:text-base font-bold text-slate-300 tracking-tight">{p}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-center mb-4">Common questions</h2>
            <p className="text-center text-slate-500 mb-12">Everything you need to know about PatientPlex.</p>
          </Reveal>
          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <button onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className={`w-full text-left p-6 rounded-2xl bg-white border transition-all ${openFaq === i ? "border-emerald-300 shadow-md border-l-4 border-l-emerald-500" : "border-slate-200 hover:border-slate-300"}`}>
                  <div className="flex items-center gap-4">
                    <span className="text-xs font-bold text-emerald-500 bg-emerald-50 w-7 h-7 rounded-lg flex items-center justify-center shrink-0">{i + 1}</span>
                    <span className="font-bold text-slate-900 flex-1">{faq.q}</span>
                    <ChevronDown className={`w-5 h-5 text-slate-400 shrink-0 transition-transform duration-200 ${openFaq === i ? "rotate-180" : ""}`} />
                  </div>
                  <AnimatePresence>
                    {openFaq === i && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }}
                        className="overflow-hidden">
                        <p className="mt-4 ml-11 text-sm text-slate-500 leading-relaxed">{faq.a}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </button>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ NEWSLETTER + FOOTER ═══ */}
      <footer className="border-t border-slate-200 relative">
        <div className="h-px bg-gradient-to-r from-transparent via-emerald-400 to-transparent absolute top-0 left-0 right-0" />
        {/* Newsletter */}
        <div className="py-12 px-6 border-b border-slate-100 bg-gradient-to-r from-emerald-50/40 to-teal-50/40">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <h4 className="font-black text-lg text-slate-900">Stay updated on AI marketing for clinics</h4>
              <p className="text-sm text-slate-500">Weekly tips, product updates, and growth strategies.</p>
            </div>
            <div className="flex gap-3 w-full sm:w-auto">
              <input type="email" placeholder="your@email.com" className="flex-1 sm:w-64 px-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500" />
              <button className="px-5 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors whitespace-nowrap">Subscribe</button>
            </div>
          </div>
        </div>
        {/* Footer columns */}
        <div className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-8 mb-12">
              <div className="col-span-2 sm:col-span-3 lg:col-span-2">
                <Link href="/" className="flex items-center gap-2 mb-4"><Logo size={28} /><span className="font-black text-lg text-slate-900">PatientPlex</span></Link>
                <p className="text-sm text-slate-500 leading-relaxed mb-4">AI-powered patient acquisition for healthcare clinics across India — dental, dermatology, ophthalmology, orthopedics, gynecology, IVF, and 10+ more specialties.</p>
                <div className="inline-flex items-center gap-1.5 text-xs text-slate-400">{"🇮🇳"} Made in India</div>
              </div>
              {[
                { title: "Product", links: ["Features", "Pricing", "Integrations", "API", "Status Page"] },
                { title: "For Clinics", links: ["Dental Marketing", "Dermatology Marketing", "Multi-Location", "Case Studies"] },
                { title: "Resources", links: ["Blog", "Documentation", "API Reference", "Help Center"] },
                { title: "Company", links: ["About", "Careers", "Contact", "Partners"] },
                { title: "Legal", links: ["Privacy Policy", "Terms of Service", "Security", "HIPAA"] },
              ].map((col, i) => (
                <div key={i}><h4 className="text-sm font-bold text-slate-900 mb-4">{col.title}</h4><ul className="space-y-2.5">{col.links.map((l,j) => <li key={j}><a href="#" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">{l}</a></li>)}</ul></div>
              ))}
              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-4">Connect</h4>
                <div className="flex gap-3 mb-4">
                  {[
                    <svg key="tw" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>,
                    <svg key="li" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg>,
                    <svg key="yt" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>,
                  ].map((icon, j) => (
                    <a key={j} href="#" className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 hover:text-slate-700 transition-all">{icon}</a>
                  ))}
                </div>
                <a href="#" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors"><Mail className="w-3.5 h-3.5" /> hello@patientplex.ai</a>
              </div>
            </div>
            <div className="pt-8 border-t border-slate-200 text-center">
              <p className="text-xs text-slate-400">{"©"} 2026 PatientPlex AI. All rights reserved.</p>
              <p className="text-xs text-slate-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> All systems operational</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
