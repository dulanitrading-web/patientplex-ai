"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, ArrowRight } from "lucide-react";
import Logo from "@/components/Logo";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Pricing", href: "#pricing" },
  { label: "About", href: "/about" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-100">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5">
            <Logo size={32} />
            <span className="text-lg font-bold tracking-tight text-slate-900">
              PatientPlex
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors px-4 py-2"
            >
              Sign in
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-full transition-all shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40"
            >
              Start free trial
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {open && (
          <div className="md:hidden py-4 border-t border-slate-100 animate-fade-in">
            <div className="flex flex-col gap-1">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 px-3 py-2.5 rounded-lg transition-colors"
                >
                  {link.label}
                </a>
              ))}
              <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-slate-100">
                <Link
                  href="/login"
                  className="text-sm font-medium text-slate-600 text-center py-2.5 rounded-lg hover:bg-slate-50"
                >
                  Sign in
                </Link>
                <Link
                  href="/signup"
                  className="text-sm font-semibold bg-emerald-600 text-white text-center py-2.5 rounded-full"
                >
                  Start free trial
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
