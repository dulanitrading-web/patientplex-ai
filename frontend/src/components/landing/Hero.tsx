"use client";

import Link from "next/link";
import { ArrowRight, Phone, MessageCircle, Calendar, TrendingUp } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 gradient-bg" />
      <div className="absolute top-20 right-0 w-96 h-96 bg-emerald-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-teal-200/20 rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left — Copy */}
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-full px-4 py-1.5 mb-6">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-emerald-700 tracking-wide uppercase">
                Now in pilot — 1 clinic live
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 leading-[1.1] tracking-tight">
              Your clinic&apos;s
              <br />
              <span className="gradient-text">AI marketing</span>
              <br />
              engine
            </h1>

            <p className="mt-6 text-lg text-slate-600 leading-relaxed">
              PatientPlex catches every missed call, follows up on WhatsApp in
              30 seconds, and books the appointment — while you treat patients.
              No agencies, no manual work.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <Link
                href="/signup"
                className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-8 py-3.5 rounded-full text-base transition-all shadow-xl shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5"
              >
                Start free for 14 days
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="https://wa.me/918447804080?text=Hi%2C%20I%27d%20like%20a%20demo%20of%20PatientPlex"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 font-semibold px-8 py-3.5 rounded-full text-base border border-slate-200 transition-all hover:-translate-y-0.5"
              >
                <MessageCircle className="w-5 h-5 text-emerald-600" />
                WhatsApp us for demo
              </a>
            </div>

            <p className="mt-4 text-sm text-slate-500">
              No credit card needed. Cancel anytime.
            </p>
          </div>

          {/* Right — Feature cards */}
          <div className="relative lg:pl-8">
            <div className="grid grid-cols-2 gap-3">
              <FeatureCard
                icon={<Phone className="w-5 h-5 text-emerald-600" />}
                title="Missed call recovery"
                desc="30-second WhatsApp follow-up"
                className="animate-fade-in"
                style={{ animationDelay: "0.1s" }}
              />
              <FeatureCard
                icon={<MessageCircle className="w-5 h-5 text-emerald-600" />}
                title="AI receptionist"
                desc="24/7 WhatsApp conversations"
                className="animate-fade-in mt-6"
                style={{ animationDelay: "0.2s" }}
              />
              <FeatureCard
                icon={<Calendar className="w-5 h-5 text-emerald-600" />}
                title="Smart booking"
                desc="Auto-schedule appointments"
                className="animate-fade-in"
                style={{ animationDelay: "0.3s" }}
              />
              <FeatureCard
                icon={<TrendingUp className="w-5 h-5 text-emerald-600" />}
                title="Conversion tracking"
                desc="Ad spend to booking ROI"
                className="animate-fade-in mt-6"
                style={{ animationDelay: "0.4s" }}
              />
            </div>

            {/* Floating stats */}
            <div className="absolute -bottom-4 -left-4 glass rounded-2xl px-5 py-3 shadow-xl animate-float">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Cost per lead</p>
                  <p className="text-lg font-bold text-slate-900">&#8377;5-8</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function FeatureCard({
  icon,
  title,
  desc,
  className = "",
  style,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className={`bg-white rounded-2xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5 ${className}`}
      style={style}
    >
      <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mb-3">
        {icon}
      </div>
      <h3 className="font-semibold text-slate-900 text-sm">{title}</h3>
      <p className="text-xs text-slate-500 mt-1">{desc}</p>
    </div>
  );
}
