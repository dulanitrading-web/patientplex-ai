"use client";
import Link from "next/link";
import { useState, useEffect } from "react";

const patients = [
  { init: "P", name: "Laser Hair Removal", doc: "Dr. Priya Sharma • Mumbai", price: "₹12,500", time: "Just now", color: "bg-purple-500" },
  { init: "R", name: "Root Canal & Crown", doc: "Dr. Rajesh Mehta • Delhi NCR", price: "₹8,500", time: "2m ago", color: "bg-blue-500" },
  { init: "A", name: "Acne Scar Treatment", doc: "Dr. Ananya Reddy • Bengaluru", price: "₹16,000", time: "5m ago", color: "bg-emerald-500" },
  { init: "S", name: "Dental Implants", doc: "Dr. Suresh Patel • Hyderabad", price: "₹22,000", time: "8m ago", color: "bg-orange-500" },
];

export default function LandingPage() {
  const [count, setCount] = useState(118);
  useEffect(() => { const t = setInterval(() => setCount(c => c + 1), 12000); return () => clearInterval(t); }, []);

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white">
      {/* Top Bar */}
      <div className="bg-gradient-to-r from-emerald-600/20 via-[#0a0f1a] to-emerald-600/20 border-b border-emerald-500/10 py-2 px-4 text-center text-sm">
        <span className="bg-emerald-500 text-black text-xs font-bold px-2 py-0.5 rounded mr-2">NEW</span>
        <span className="text-gray-300">Built for Indian Clinics: Automate Google Search Ads & 24/7 WhatsApp Bookings</span>
        <Link href="/signup" className="text-emerald-400 hover:text-emerald-300 ml-2 font-medium">Get Started Free →</Link>
      </div>

      {/* Navbar */}
      <nav className="border-b border-white/5 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <span className="font-bold text-xl">PatientPlex</span>
            <span className="bg-emerald-500/10 text-emerald-400 text-xs font-semibold px-2 py-1 rounded-full border border-emerald-500/20">v2.4 Active</span>
          </div>
          <div className="hidden lg:flex items-center gap-6 text-sm text-gray-400">
            <a href="#demo" className="hover:text-white transition">WHATSAPP AI DEMO</a>
            <a href="#features" className="hover:text-white transition">FEATURES</a>
            <a href="#roi" className="hover:text-white transition">ROI CALCULATOR</a>
            <a href="#agencies" className="hover:text-white transition">AGENCIES VS AI</a>
            <a href="#pricing" className="hover:text-white transition">PRICING</a>
            <a href="#faq" className="hover:text-white transition">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-gray-400 hover:text-white transition">Sign In</Link>
            <Link href="/signup" className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm px-5 py-2.5 rounded-xl hover:shadow-lg hover:shadow-emerald-500/20 transition-all">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              Start 14-Day Free Trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-16 grid lg:grid-cols-2 gap-12 items-start">
        {/* Left */}
        <div className="pt-8">
          <div className="inline-flex items-center gap-2 bg-emerald-500/5 border border-emerald-500/15 rounded-full px-4 py-1.5 mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-sm font-medium">#1 AI Patient Flow Engine</span>
            <span className="text-gray-500">|</span>
            <span className="text-gray-400 text-sm">Dermatology & Dental Clinics</span>
          </div>

          <h1 className="text-5xl lg:text-6xl font-bold leading-[1.1] mb-6">
            Stop Paying Agency Retainers.{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">Book Patients 24/7 on Autopilot.</span>
          </h1>

          <p className="text-lg text-gray-400 mb-8 leading-relaxed max-w-xl">
            PatientPlex AI automatically creates high-converting Google & Meta campaigns, triages late-night patient queries instantly on WhatsApp, and locks confirmed slots directly into your calendar.
          </p>

          <div className="flex flex-wrap items-center gap-4 mb-12">
            <Link href="/signup" className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-8 py-4 rounded-xl text-lg hover:shadow-xl hover:shadow-emerald-500/25 transition-all flex items-center gap-2">
              Start 14-Day Free Trial
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </Link>
            <button className="flex items-center gap-2 text-gray-300 hover:text-white transition text-lg border border-white/10 px-6 py-4 rounded-xl hover:bg-white/5">
              <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              Try WhatsApp Demo
            </button>
          </div>

          <div className="grid grid-cols-4 gap-6">
            {[
              { value: "3.8x", label: "Avg Google Ad ROI" },
              { value: "70%", label: "Lower Cost/Booking" },
              { value: "< 3s", label: "WhatsApp AI Speed" },
              { value: "140+", label: "Indian Clinics" },
            ].map((s, i) => (
              <div key={i}>
                <p className="text-2xl font-bold text-white">{s.value}</p>
                <p className="text-xs text-gray-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right - Live Dashboard */}
        <div className="bg-[#111827] border border-white/[0.06] rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
          <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              </div>
              <div>
                <p className="font-semibold text-sm">Live Practice Command Dashboard</p>
                <p className="text-xs text-gray-500">Apex Derma & Dental Center, Bangalore</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 bg-emerald-500/10 px-3 py-1 rounded-full">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-emerald-400 text-xs font-medium">Live</span>
            </div>
          </div>

          <div className="p-4 grid grid-cols-2 gap-3">
            <div className="bg-[#0a0f1a] rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 mb-1">Monthly Google Ad ROI</p>
              <p className="text-2xl font-bold text-emerald-400">4.2x</p>
              <p className="text-xs text-gray-600 mt-1">Spend: ₹35,000</p>
            </div>
            <div className="bg-[#0a0f1a] rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 mb-1">Avg Cost / Confirmed Slot</p>
              <p className="text-2xl font-bold text-white">₹340</p>
              <p className="text-xs text-gray-600 mt-1">Industry: ₹1,200</p>
            </div>
            <div className="bg-[#0a0f1a] rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 mb-1">WhatsApp Triage Rate</p>
              <p className="text-2xl font-bold text-emerald-400">89.4%</p>
              <p className="text-xs text-gray-600 mt-1">Zero human delay</p>
            </div>
            <div className="bg-[#0a0f1a] rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 mb-1">Appointments Booked</p>
              <p className="text-2xl font-bold text-white">{count}</p>
              <p className="text-xs text-emerald-500 mt-1">This month</p>
            </div>
          </div>

          <div className="px-4 pb-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-semibold">Real-Time Patient Queue</p>
              <p className="text-xs text-gray-500">Updated Live</p>
            </div>
            <div className="space-y-2">
              {patients.slice(0, 3).map((p, i) => (
                <div key={i} className="flex items-center justify-between bg-[#0a0f1a] rounded-xl px-4 py-3 border border-white/5">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg ${p.color} flex items-center justify-center text-white text-xs font-bold`}>{p.init}</div>
                    <div>
                      <p className="text-sm font-medium">{p.name}</p>
                      <p className="text-xs text-gray-500">{p.doc}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-emerald-400">{p.price}</p>
                    <p className="text-xs text-gray-600">{p.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Case Study */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="roi">
        <div className="text-center mb-12">
          <p className="text-emerald-400 text-sm font-semibold tracking-[2px] uppercase mb-4">CASE STUDY</p>
          <h2 className="text-4xl font-bold mb-4">Bhardwaj Dental Clinic, Hyderabad</h2>
          <p className="text-gray-400">From losing 12 patients/week to filling every chair</p>
        </div>
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <div className="bg-red-500/[0.04] border border-red-500/10 rounded-2xl p-8">
            <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2"><span className="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center text-sm">✕</span> Before</h3>
            <div className="space-y-3">
              {[["Missed calls/week","12-15"],["Agency cost/month","₹40,000"],["Patient tracking","None"],["After-hours response","0"],["Revenue lost/month","₹2.4L+"]].map(([l,v],i) => (
                <div key={i} className="flex justify-between border-b border-red-500/5 pb-2"><span className="text-sm text-gray-400">{l}</span><span className="font-bold text-red-400">{v}</span></div>
              ))}
            </div>
          </div>
          <div className="bg-emerald-500/[0.04] border border-emerald-500/10 rounded-2xl p-8">
            <h3 className="text-lg font-bold text-emerald-400 mb-4 flex items-center gap-2"><span className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-sm">✓</span> After</h3>
            <div className="space-y-3">
              {[["Calls recovered","47/month"],["Appointments booked","19/month"],["Revenue recovered","₹1.9L/mo"],["PatientPlex cost","₹7,999/mo"],["Saved vs agency","₹32,001/mo"]].map(([l,v],i) => (
                <div key={i} className="flex justify-between border-b border-emerald-500/5 pb-2"><span className="text-sm text-gray-400">{l}</span><span className="font-bold text-emerald-400">{v}</span></div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-7xl mx-auto px-6 py-20" id="pricing">
        <div className="text-center mb-12">
          <p className="text-emerald-400 text-sm font-semibold tracking-[2px] uppercase mb-4">PRICING</p>
          <h2 className="text-4xl font-bold mb-4">Start free. Pay only when it works.</h2>
        </div>
        <div className="grid md:grid-cols-4 gap-4 max-w-5xl mx-auto">
          {[
            { plan:"Free Trial", price:"₹0", period:"14 days", features:["50 conversations","1 campaign","WhatsApp AI","Basic dashboard"], hl:false },
            { plan:"Starter", price:"₹2,999", period:"/month", features:["100 conversations","2 campaigns","Tracking","Email support"], hl:false },
            { plan:"Growth", price:"₹7,999", period:"/month", features:["Unlimited chats","10 campaigns","Full funnel","Landing pages","Priority support"], hl:true },
            { plan:"Enterprise", price:"₹19,999", period:"/month", features:["Everything","White-label","Dedicated manager","API access","Multi-location"], hl:false },
          ].map((p,i) => (
            <div key={i} className={`rounded-2xl p-6 ${p.hl ? "bg-gradient-to-b from-emerald-500/10 to-transparent border-2 border-emerald-500/30 relative" : "bg-white/[0.02] border border-white/[0.06]"}`}>
              {p.hl && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-teal-500 text-black text-xs font-bold px-3 py-1 rounded-full">POPULAR</div>}
              <p className="text-sm text-gray-400">{p.plan}</p>
              <p className="text-3xl font-bold my-1">{p.price}</p>
              <p className="text-xs text-gray-600 mb-4">{p.period}</p>
              <ul className="space-y-2 mb-6">{p.features.map((f,j) => <li key={j} className="text-sm text-gray-400 flex gap-2"><span className="text-emerald-400">✓</span>{f}</li>)}</ul>
              <Link href="/signup" className={`block text-center py-2.5 rounded-xl text-sm font-semibold ${p.hl ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white" : "bg-white/5 hover:bg-white/10"}`}>{p.hl ? "Get Started" : "Choose"}</Link>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="text-4xl font-bold mb-4">Every missed call is a <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">patient lost forever.</span></h2>
        <p className="text-gray-400 text-lg mb-8">Start your free trial. Book patients on autopilot.</p>
        <Link href="/signup" className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold px-10 py-4 rounded-xl text-lg shadow-2xl shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all">Start Free — No Credit Card</Link>
      </section>

      <footer className="border-t border-white/5 py-8 px-6 text-center text-gray-600 text-sm">
        © 2026 PatientPlex AI. Built for Indian healthcare.
      </footer>
    </div>
  );
}
