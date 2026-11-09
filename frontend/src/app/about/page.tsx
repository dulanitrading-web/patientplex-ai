"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Logo from "@/components/Logo";
import {
  ArrowLeft,
  Linkedin,
  Twitter,
  Mail,
  Globe,
  Target,
  Brain,
  Users,
  Rocket,
  Heart,
  Award,
  TrendingUp,
  MessageCircle,
  Zap,
  Shield,
  ChevronRight,
} from "lucide-react";

const Reveal = ({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
  >
    {children}
  </motion.div>
);

const JOURNEY = [
  { year: "The Problem", text: "Saw Indian clinics losing patients every day — missed calls, expensive agencies charging ₹50K+ with zero transparency, and no way to track which ads actually work." },
  { year: "The Idea", text: "What if AI could handle everything — run ads, answer WhatsApp messages, book appointments, and optimize budgets — all for a fraction of what agencies charge?" },
  { year: "Building", text: "Built PatientPlex AI from scratch — a full-stack platform combining Google Ads, Meta, ChatGPT Ads, LinkedIn, WhatsApp, and Twilio into one autonomous marketing engine." },
  { year: "First Client", text: "Bhardwaj Dental Clinic became our first client. Results: ₹5–8 per lead, ₹60–80 per booking — far cheaper than any agency in the market." },
  { year: "The Vision", text: "Scaling to make world-class performance marketing accessible to every healthcare clinic in India — from solo practitioners to 50-location hospital chains." },
];

const VALUES = [
  { icon: Heart, title: "Doctors First", desc: "Every feature we build starts with one question: does this help a doctor get more patients?" },
  { icon: Shield, title: "Radical Transparency", desc: "Every rupee tracked. Every click visible. No hidden fees, no black-box algorithms." },
  { icon: Zap, title: "AI-Native", desc: "Not a dashboard with a chatbot bolted on. AI is the core — it runs the ads, answers patients, and optimizes spend." },
  { icon: TrendingUp, title: "Results Over Revenue", desc: "We grow when our clinics grow. If our AI doesn't deliver patients, we haven't earned our fee." },
];

const SKILLS = [
  "Performance Marketing",
  "Google Ads",
  "Meta Ads",
  "AI & Machine Learning",
  "Healthcare Marketing",
  "Full-Stack Development",
  "WhatsApp Business API",
  "Patient Acquisition",
  "Marketing Automation",
  "Data Analytics",
];

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-[#FAFAF8]/80 backdrop-blur-xl border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-16 px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2.5 group">
            <ArrowLeft className="w-4 h-4 text-slate-400 group-hover:text-emerald-500 transition-colors" />
            <Logo size={32} />
            <span className="font-black text-lg text-slate-900">PatientPlex</span>
          </Link>
          <Link
            href="/"
            className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
          >
            Back to home
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-teal-50/50 to-transparent" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 pt-20 pb-16">
          <Reveal>
            <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
              {/* Founder avatar */}
              <div className="flex-shrink-0">
                <div className="relative">
                  <div className="w-56 h-56 sm:w-64 sm:h-64 rounded-3xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-2xl shadow-emerald-500/20">
                    <span className="text-8xl sm:text-9xl font-black text-white/90">PD</span>
                  </div>
                  {/* Floating badge */}
                  <div className="absolute -bottom-3 -right-3 bg-white rounded-2xl px-4 py-2 shadow-lg border border-slate-200">
                    <div className="flex items-center gap-2">
                      <Rocket className="w-4 h-4 text-emerald-500" />
                      <span className="text-sm font-bold text-slate-900">Founder & CEO</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Info */}
              <div className="text-center lg:text-left">
                <p className="text-emerald-600 font-bold text-sm tracking-widest uppercase mb-3">Meet the Founder</p>
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black text-slate-900 tracking-tight mb-4">
                  Prakash Dulani
                </h1>
                <p className="text-xl sm:text-2xl text-slate-500 font-medium mb-6 max-w-xl">
                  Founder & CEO of PatientPlex AI — building the future of healthcare marketing in India.
                </p>
                <p className="text-lg text-slate-600 leading-relaxed max-w-2xl mb-8">
                  Performance marketer turned entrepreneur. Prakash saw firsthand how Indian healthcare clinics
                  struggle with patient acquisition — overpaying agencies, missing after-hours enquiries, and having
                  zero visibility into their ad spend. He built PatientPlex AI to solve this: an autonomous
                  AI-powered performance marketing engine that handles everything from Google Ads to WhatsApp booking,
                  so doctors can focus on treating patients.
                </p>

                {/* Social links */}
                <div className="flex items-center gap-3 justify-center lg:justify-start">
                  <a href="mailto:prakash@patientplex.ai" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors">
                    <Mail className="w-4 h-4" /> Get in touch
                  </a>
                  <a href="https://www.linkedin.com/in/prakashdulani" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-500 hover:text-blue-600 hover:border-blue-200 transition-all">
                    <Linkedin className="w-4 h-4" />
                  </a>
                  <a href="https://twitter.com/prakashdulani" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-500 hover:text-sky-500 hover:border-sky-200 transition-all">
                    <Twitter className="w-4 h-4" />
                  </a>
                  <a href="https://patientplex-ai.vercel.app" className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-500 hover:text-emerald-600 hover:border-emerald-200 transition-all">
                    <Globe className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Skills / Expertise */}
      <section className="py-12 border-y border-slate-200/60 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex flex-wrap items-center justify-center gap-3">
            {SKILLS.map((skill) => (
              <span
                key={skill}
                className="px-4 py-2 rounded-full bg-slate-50 border border-slate-200 text-sm font-semibold text-slate-700"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* The Journey */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black text-slate-900 text-center mb-4">The Journey</h2>
            <p className="text-center text-slate-500 text-lg mb-16">From identifying the problem to building the solution</p>
          </Reveal>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-emerald-500 via-teal-500 to-cyan-500 hidden sm:block" />

            <div className="space-y-10">
              {JOURNEY.map((item, i) => (
                <Reveal key={i} delay={i * 0.1}>
                  <div className="flex gap-6 sm:gap-10">
                    {/* Dot */}
                    <div className="flex-shrink-0 hidden sm:flex flex-col items-center">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-black text-sm shadow-lg shadow-emerald-500/20">
                        {i + 1}
                      </div>
                    </div>

                    {/* Card */}
                    <div className="flex-1 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 hover:shadow-lg hover:border-emerald-200 transition-all">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="sm:hidden w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-black text-xs">
                          {i + 1}
                        </span>
                        <h3 className="text-xl font-black text-slate-900">{item.year}</h3>
                      </div>
                      <p className="text-slate-600 leading-relaxed">{item.text}</p>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* What Drives Us */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black text-white text-center mb-4">What Drives Us</h2>
            <p className="text-center text-slate-400 text-lg mb-16">The principles behind every line of code</p>
          </Reveal>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {VALUES.map((v, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
                  <v.icon className="w-10 h-10 text-emerald-400 mb-4" />
                  <h3 className="text-xl font-black text-white mb-2">{v.title}</h3>
                  <p className="text-slate-400 leading-relaxed">{v.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* The Product */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black text-slate-900 mb-6">What We{"’"}re Building</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-12">
              PatientPlex AI is an all-in-one autonomous marketing engine for healthcare clinics.
              One platform that handles everything — so doctors never have to think about marketing again.
            </p>
          </Reveal>

          <Reveal delay={0.2}>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                { icon: Target, label: "5 Ad Platforms", sub: "Google, Meta, ChatGPT, LinkedIn, WhatsApp" },
                { icon: MessageCircle, label: "AI Receptionist", sub: "WhatsApp + Phone (Twilio) — 24/7" },
                { icon: Brain, label: "ML Marketing Brain", sub: "RL bidding, conversion prediction, LTV" },
                { icon: Users, label: "15+ Specialties", sub: "Dental to cardiology, solo to chains" },
                { icon: Award, label: "Real Results", sub: "₹5–8 per lead, ₹60–80 per booking" },
                { icon: Globe, label: "Multilingual AI", sub: "Hindi, English, Tamil, Telugu & more" },
              ].map((item, i) => (
                <div key={i} className="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-md hover:border-emerald-200 transition-all text-left">
                  <item.icon className="w-8 h-8 text-emerald-500 mb-3" />
                  <h4 className="font-bold text-slate-900 mb-1">{item.label}</h4>
                  <p className="text-sm text-slate-500">{item.sub}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <Reveal>
            <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
              Let{"’"}s grow your clinic together
            </h2>
            <p className="text-xl text-white/80 mb-8">
              Start your 14-day free trial. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/"
                className="px-8 py-4 rounded-xl bg-white text-emerald-600 font-bold text-lg hover:bg-emerald-50 transition-colors shadow-lg flex items-center gap-2"
              >
                Get started free <ChevronRight className="w-5 h-5" />
              </Link>
              <a
                href="mailto:prakash@patientplex.ai"
                className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur-sm text-white font-bold text-lg hover:bg-white/20 transition-colors border border-white/20"
              >
                Talk to Prakash
              </a>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-slate-900 text-center">
        <p className="text-slate-500 text-sm">
          © {new Date().getFullYear()} PatientPlex AI — Founded by Prakash Dulani
        </p>
      </footer>
    </div>
  );
}
