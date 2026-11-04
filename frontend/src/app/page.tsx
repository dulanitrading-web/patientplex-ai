"use client";

import Link from "next/link";
import {
  Zap,
  MessageCircle,
  CalendarCheck,
  ArrowRight,
  ChevronDown,
  Shield,
  TrendingUp,
  Clock,
} from "lucide-react";
import Button from "@/components/ui/Button";

const features = [
  {
    icon: Zap,
    title: "AI Ad Engine",
    description:
      "Automatically creates and optimizes Google & Meta ad campaigns tailored to your specialty. No marketing experience needed.",
    color: "text-electric",
    bg: "bg-electric/10",
  },
  {
    icon: MessageCircle,
    title: "24/7 AI Receptionist",
    description:
      "WhatsApp-based AI assistant handles patient inquiries, answers FAQs, and books appointments around the clock.",
    color: "text-teal",
    bg: "bg-teal/10",
  },
  {
    icon: CalendarCheck,
    title: "Direct Calendar Booking",
    description:
      "Patients are booked directly into your Google Calendar. No missed calls, no back-and-forth. Just confirmed appointments.",
    color: "text-amber",
    bg: "bg-amber/10",
  },
];

const stats = [
  { value: "3x", label: "More patient enquiries", icon: TrendingUp },
  { value: "70%", label: "Lower cost per lead", icon: Shield },
  { value: "24/7", label: "Always-on booking", icon: Clock },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 bg-navy/95 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-electric rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-white text-xl font-bold">PatientPlex AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-white hover:bg-white/10">
                Sign In
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="gradient-hero pt-32 pb-20 sm:pt-40 sm:pb-28 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-electric rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-teal rounded-full blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm text-white/90 mb-6 border border-white/10">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Built for Indian healthcare professionals
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Stop paying agencies.{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber to-coral">
                Start getting patients.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
              AI-powered ad automation built for doctors. PatientPlex AI runs your
              Google &amp; Meta campaigns, answers patient queries on WhatsApp,
              and books appointments directly into your calendar.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup">
                <Button size="lg" className="min-w-[200px]">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <a href="#features">
                <Button variant="ghost" size="lg" className="text-white hover:bg-white/10 min-w-[200px]">
                  See How It Works
                  <ChevronDown className="w-5 h-5 ml-2" />
                </Button>
              </a>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl mx-auto">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="text-center bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10"
              >
                <div className="text-3xl font-bold text-white">{stat.value}</div>
                <div className="text-sm text-gray-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 sm:py-28 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-navy mb-4">
              Everything you need to fill your clinic
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Three powerful tools working together to bring patients to your
              door — fully automated, fully managed by AI.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="card-elevated hover:shadow-xl transition-shadow duration-300 group"
              >
                <div
                  className={`w-14 h-14 rounded-xl ${feature.bg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
                >
                  <feature.icon className={`w-7 h-7 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-bold text-navy mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-bg">
        <div className="max-w-3xl mx-auto text-center px-4">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to grow your practice?
          </h2>
          <p className="text-gray-300 text-lg mb-8">
            Set up takes less than 5 minutes. No credit card required.
          </p>
          <Link href="/signup">
            <Button size="lg" className="bg-white text-navy hover:bg-gray-100 font-bold">
              Start Your Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-navy text-gray-400 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-7 h-7 bg-electric rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-bold text-lg">PatientPlex AI</span>
          </div>
          <p className="text-sm">
            &copy; {new Date().getFullYear()} PatientPlex AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
