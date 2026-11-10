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
  ExternalLink,
} from "lucide-react";

const Reveal = ({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-40px" }}
    transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
  >
    {children}
  </motion.div>
);

const JOURNEY = [
  { step: "01", title: "The Problem", text: "Indian clinics losing patients daily — missed calls, agencies charging ₹50K+ with zero transparency, no ad tracking." },
  { step: "02", title: "The Idea", text: "What if AI handled everything — ads, WhatsApp, bookings, optimization — at a fraction of agency cost?" },
  { step: "03", title: "Building", text: "Full-stack platform from scratch: Google Ads, Meta, ChatGPT Ads, LinkedIn, WhatsApp, Twilio — one engine." },
  { step: "04", title: "First Client", text: "Bhardwaj Dental Clinic — our first pilot. Real campaigns, real data, real patients." },
  { step: "05", title: "The Vision", text: "World-class performance marketing for every healthcare clinic in India." },
];

const VALUES = [
  { icon: Heart, title: "Doctors First", desc: "Every feature starts with: does this help a doctor get more patients?" },
  { icon: Shield, title: "Radical Transparency", desc: "Every rupee tracked. Every click visible. No hidden fees." },
  { icon: Zap, title: "AI-Native", desc: "AI is the core — it runs ads, answers patients, optimizes spend." },
  { icon: TrendingUp, title: "Results Over Revenue", desc: "We grow when clinics grow. No patients, no fee earned." },
];

const SKILLS = [
  "Performance Marketing", "Google Ads", "Meta Ads", "AI & ML",
  "Healthcare", "Full-Stack Dev", "WhatsApp API", "Patient Acquisition",
  "Marketing Automation", "Data Analytics",
];

const CAPABILITIES = [
  { icon: Target, label: "5 Ad Platforms", sub: "Google, Meta, ChatGPT, LinkedIn, WhatsApp" },
  { icon: MessageCircle, label: "AI Receptionist", sub: "WhatsApp + Phone — 24/7" },
  { icon: Brain, label: "ML Brain", sub: "RL bidding, conversion prediction" },
  { icon: Users, label: "15+ Specialties", sub: "Dental to cardiology" },
  { icon: Award, label: "Pilot Active", sub: "Bhardwaj Dental Clinic" },
  { icon: Globe, label: "Multilingual", sub: "Hindi, English, Tamil & more" },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-[#FAFAF8]/80 backdrop-blur-xl border-b border-slate-200/60">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-14 px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 group">
            <ArrowLeft className="w-3.5 h-3.5 text-slate-400 group-hover:text-emerald-500 transition-colors" />
            <Logo size={28} />
            <span className="font-bold text-base text-slate-900">PatientPlex</span>
          </Link>
          <Link href="/" className="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors flex items-center gap-1">
            Home <ExternalLink className="w-3 h-3" />
          </Link>
        </div>
      </header>

      {/* Founder Hero — clean, refined */}
      <section className="relative">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-50/60 to-transparent h-[50vh]" />
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 pt-16 pb-12">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              {/* Avatar */}
              <div className="relative mb-6">
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/15">
                  <span className="text-4xl font-black text-white">P</span>
                </div>
                <div className="absolute -bottom-1.5 -right-1.5 bg-white rounded-lg px-2 py-0.5 shadow border border-slate-100">
                  <span className="text-[10px] font-bold text-emerald-600 tracking-wide uppercase">Founder</span>
                </div>
              </div>

              {/* Name + title */}
              <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mb-2">
                Prakash Dulani
              </h1>
              <p className="text-base text-slate-500 font-medium mb-6">
                Founder & CEO, PatientPlex AI
              </p>

              {/* Social row */}
              <div className="flex items-center gap-2 mb-8">
                <a href="mailto:prakash@patientplex.ai" className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition-colors">
                  <Mail className="w-3.5 h-3.5" /> Email
                </a>
                <a href="https://www.linkedin.com/in/prakashdulani" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-9 h-9 rounded-lg bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200 transition-all">
                  <Linkedin className="w-3.5 h-3.5" />
                </a>
                <a href="https://twitter.com/prakashdulani" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-9 h-9 rounded-lg bg-white border border-slate-200 text-slate-400 hover:text-sky-500 hover:border-sky-200 transition-all">
                  <Twitter className="w-3.5 h-3.5" />
                </a>
                <a href="https://patientplex-ai.vercel.app" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-9 h-9 rounded-lg bg-white border border-slate-200 text-slate-400 hover:text-emerald-600 hover:border-emerald-200 transition-all">
                  <Globe className="w-3.5 h-3.5" />
                </a>
              </div>

              {/* Bio — first person, compelling */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 text-left max-w-2xl">
                <p className="text-[15px] text-slate-600 leading-relaxed mb-4">
                  I spent years in performance marketing and watched the same story repeat: clinics in India pouring money into agencies that charge ₹30K–₹1L per month, with zero transparency on where the money goes. Doctors would ask me, {"“"}Which ad brought that patient?{"”"} and the agency couldn{"’"}t answer.
                </p>
                <p className="text-[15px] text-slate-600 leading-relaxed mb-4">
                  Meanwhile, patients were messaging on WhatsApp at 10pm and nobody was there to respond. Calls went unanswered on Sundays. Every missed enquiry was a patient who booked with the competitor who picked up first.
                </p>
                <p className="text-[15px] text-slate-600 leading-relaxed">
                  So I built PatientPlex AI — an autonomous marketing engine that runs Google Ads, answers WhatsApp and phone calls 24/7, books appointments, and optimizes every rupee. All for a fraction of what an agency charges. Built for every healthcare clinic in India — dental, derma, ortho, eye, gynec, and 15+ more specialties.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Skills — subtle tags */}
      <section className="py-6 border-y border-slate-100">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <div className="flex flex-wrap items-center justify-center gap-2">
            {SKILLS.map((skill) => (
              <span key={skill} className="px-3 py-1 rounded-md bg-slate-50 border border-slate-150 text-xs font-medium text-slate-500">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Journey — compact timeline */}
      <section className="py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <Reveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 text-center mb-2">The Journey</h2>
            <p className="text-center text-slate-400 text-sm mb-10">From problem to product</p>
          </Reveal>

          <div className="space-y-4">
            {JOURNEY.map((item, i) => (
              <Reveal key={i} delay={i * 0.06}>
                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-emerald-600">{item.step}</span>
                  </div>
                  <div className="flex-1 pb-4 border-b border-slate-100 last:border-0">
                    <h3 className="text-sm font-bold text-slate-900 mb-0.5">{item.title}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">{item.text}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Values — refined dark section */}
      <section className="py-14 bg-slate-900">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <Reveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-white text-center mb-2">What Drives Us</h2>
            <p className="text-center text-slate-500 text-sm mb-10">The principles behind every line of code</p>
          </Reveal>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {VALUES.map((v, i) => (
              <Reveal key={i} delay={i * 0.06}>
                <div className="bg-white/[0.04] border border-white/[0.06] rounded-xl p-5 hover:bg-white/[0.07] transition-colors">
                  <v.icon className="w-5 h-5 text-emerald-400 mb-3" />
                  <h3 className="text-sm font-bold text-white mb-1">{v.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{v.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Product capabilities */}
      <section className="py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <Reveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 text-center mb-2">What We{"’"}re Building</h2>
            <p className="text-center text-slate-400 text-sm mb-10">One platform, every clinic need</p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {CAPABILITIES.map((item, i) => (
                <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-sm hover:border-emerald-200 transition-all">
                  <item.icon className="w-5 h-5 text-emerald-500 mb-2" />
                  <h4 className="text-sm font-bold text-slate-900 mb-0.5">{item.label}</h4>
                  <p className="text-xs text-slate-400">{item.sub}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* CTA — subtle */}
      <section className="py-14 bg-gradient-to-br from-emerald-500 to-teal-500">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <Reveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
              Let{"’"}s grow your clinic together
            </h2>
            <p className="text-base text-white/75 mb-6">
              14-day free trial. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link href="/" className="px-6 py-3 rounded-lg bg-white text-emerald-600 font-semibold text-sm hover:bg-emerald-50 transition-colors shadow-md flex items-center gap-1.5">
                Get started <ChevronRight className="w-4 h-4" />
              </Link>
              <a href="mailto:prakash@patientplex.ai" className="px-6 py-3 rounded-lg bg-white/10 text-white font-semibold text-sm hover:bg-white/20 transition-colors border border-white/20">
                Talk to Prakash
              </a>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 bg-slate-900 text-center">
        <p className="text-slate-500 text-xs">
          © {new Date().getFullYear()} PatientPlex AI — Founded by Prakash Dulani
        </p>
      </footer>
    </div>
  );
}
