"use client";

import {
  Megaphone, MessageCircle, Calendar, Shield, BarChart3,
  Globe, Smartphone, BrainCircuit, Bell, Users,
} from "lucide-react";

const FEATURES = [
  {
    icon: <Megaphone className="w-5 h-5" />,
    title: "Autonomous Ads",
    desc: "AI manages Google, Meta, and LinkedIn campaigns. Optimizes budgets and creatives daily.",
  },
  {
    icon: <MessageCircle className="w-5 h-5" />,
    title: "WhatsApp AI Receptionist",
    desc: "Responds to patient enquiries 24/7 in English, Hindi, and regional languages.",
  },
  {
    icon: <Calendar className="w-5 h-5" />,
    title: "Smart Booking",
    desc: "Patients book directly into your calendar. Auto-reminders reduce no-shows by 40%.",
  },
  {
    icon: <BrainCircuit className="w-5 h-5" />,
    title: "Marketing Brain",
    desc: "ML engine learns from every campaign and patient interaction to improve ROI over time.",
  },
  {
    icon: <BarChart3 className="w-5 h-5" />,
    title: "Conversion Tracking",
    desc: "17-stage funnel from ad impression to completed appointment. Know your true cost per patient.",
  },
  {
    icon: <Globe className="w-5 h-5" />,
    title: "Landing Pages",
    desc: "Auto-generated treatment pages with Schema.org markup for better Google visibility.",
  },
  {
    icon: <Smartphone className="w-5 h-5" />,
    title: "Missed Call Recovery",
    desc: "Every missed call gets a WhatsApp follow-up in 30 seconds. No patient lost.",
  },
  {
    icon: <Shield className="w-5 h-5" />,
    title: "DPDP Compliant",
    desc: "Patient data encrypted at rest. Audit logs. India-based data residency under DPDP Act 2023.",
  },
  {
    icon: <Bell className="w-5 h-5" />,
    title: "Doctor Notifications",
    desc: "Daily digest of new bookings, campaign performance, and revenue attribution.",
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: "Multi-Location",
    desc: "Manage multiple clinic locations from one dashboard. Separate budgets and campaigns.",
  },
];

export default function Features() {
  return (
    <section id="features" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-sm font-semibold text-emerald-600 uppercase tracking-wider mb-3">
            Features
          </p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Everything a clinic needs to grow
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            One platform replaces your marketing agency, receptionist follow-ups, and scattered booking tools.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-emerald-200 hover:shadow-md transition-all"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center text-emerald-600 mb-3 transition-colors">
                {f.icon}
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mb-1.5">
                {f.title}
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
