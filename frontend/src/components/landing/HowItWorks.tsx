"use client";

import { Phone, MessageCircle, Calendar, BarChart3 } from "lucide-react";

const STEPS = [
  {
    num: "01",
    icon: <Phone className="w-6 h-6" />,
    title: "Patient calls your clinic",
    desc: "A patient sees your Google or Meta ad and calls. If you're busy or the clinic is closed, the call is marked as missed.",
    color: "text-blue-600",
    bg: "bg-blue-50",
  },
  {
    num: "02",
    icon: <MessageCircle className="w-6 h-6" />,
    title: "AI follows up in 30 seconds",
    desc: "PatientPlex sends a WhatsApp message within 30 seconds. The AI receptionist greets the patient, asks about their concern, and offers appointment slots.",
    color: "text-emerald-600",
    bg: "bg-emerald-50",
  },
  {
    num: "03",
    icon: <Calendar className="w-6 h-6" />,
    title: "Appointment booked automatically",
    desc: "The patient picks a slot. The booking goes straight into your calendar. Reminders are sent 24 hours and 2 hours before the appointment.",
    color: "text-violet-600",
    bg: "bg-violet-50",
  },
  {
    num: "04",
    icon: <BarChart3 className="w-6 h-6" />,
    title: "You see what works",
    desc: "Every booking traces back to the ad that brought it. You see exactly which campaigns bring patients and what each patient costs.",
    color: "text-amber-600",
    bg: "bg-amber-50",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-sm font-semibold text-emerald-600 uppercase tracking-wider mb-3">
            How it works
          </p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            From missed call to booked patient in under a minute
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STEPS.map((step) => (
            <div
              key={step.num}
              className="relative bg-white rounded-2xl border border-slate-100 p-6 hover:shadow-lg transition-all group"
            >
              <span className="text-5xl font-black text-slate-100 group-hover:text-emerald-100 transition-colors absolute top-4 right-4">
                {step.num}
              </span>
              <div className={`w-12 h-12 rounded-xl ${step.bg} flex items-center justify-center mb-4 ${step.color}`}>
                {step.icon}
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
