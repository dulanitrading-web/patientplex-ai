"use client";

import Link from "next/link";
import { Check, ArrowRight } from "lucide-react";

const PLANS = [
  {
    name: "Starter",
    price: "9,999",
    desc: "For solo practitioners starting with AI marketing",
    features: [
      "1 doctor, 1 location",
      "Google Ads management",
      "WhatsApp AI receptionist",
      "Smart appointment booking",
      "Automated reminders",
      "1 treatment landing page",
      "Basic analytics",
    ],
    cta: "Start free trial",
    popular: false,
  },
  {
    name: "Growth",
    price: "24,999",
    desc: "For clinics ready to scale patient acquisition",
    features: [
      "Up to 3 doctors",
      "Google + Meta Ads",
      "WhatsApp AI receptionist",
      "Smart booking + reminders",
      "Treatment landing pages",
      "Conversion tracking",
      "Competitive intelligence",
      "Missed call recovery",
      "Daily performance reports",
    ],
    cta: "Start free trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "49,999",
    desc: "For multi-location clinics and hospital chains",
    features: [
      "Unlimited doctors",
      "All ad platforms (Google, Meta, LinkedIn)",
      "Everything in Growth",
      "Multi-location support",
      "Revenue attribution",
      "Custom templates",
      "API access",
      "Priority support",
      "Dedicated account manager",
    ],
    cta: "Contact sales",
    popular: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-sm font-semibold text-emerald-600 uppercase tracking-wider mb-3">
            Pricing
          </p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Less than what agencies charge per month
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            14-day free trial on all plans. No credit card required. Cancel anytime.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`relative bg-white rounded-2xl p-6 flex flex-col ${
                plan.popular
                  ? "border-2 border-emerald-500 shadow-xl shadow-emerald-500/10 scale-[1.02]"
                  : "border border-slate-200"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-emerald-600 text-white text-xs font-bold px-4 py-1 rounded-full">
                  Most popular
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg font-bold text-slate-900">{plan.name}</h3>
                <p className="text-sm text-slate-500 mt-1">{plan.desc}</p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-sm text-slate-500">&#8377;</span>
                  <span className="text-4xl font-extrabold text-slate-900">
                    {plan.price}
                  </span>
                  <span className="text-sm text-slate-500">/month</span>
                </div>
              </div>

              <ul className="flex-1 space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5">
                    <Check className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-slate-600">{f}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.name === "Enterprise" ? "https://wa.me/918447804080?text=Hi%2C%20I%27m%20interested%20in%20PatientPlex%20Enterprise" : "/signup"}
                className={`inline-flex items-center justify-center gap-2 py-3 rounded-full text-sm font-semibold transition-all ${
                  plan.popular
                    ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/25"
                    : "bg-slate-900 hover:bg-slate-800 text-white"
                }`}
              >
                {plan.cta}
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
