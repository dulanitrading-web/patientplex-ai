import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import HowItWorks from "@/components/landing/HowItWorks";
import Features from "@/components/landing/Features";
import Pricing from "@/components/landing/Pricing";
import Footer from "@/components/landing/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />

        {/* Social proof strip */}
        <section className="py-12 border-y border-slate-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <Stat value="15+" label="Specialties supported" />
              <Stat value="30s" label="Missed call follow-up" />
              <Stat value="24/7" label="AI receptionist uptime" />
              <Stat value="40%" label="No-show reduction" />
            </div>
          </div>
        </section>

        <HowItWorks />
        <Features />
        <Pricing />

        {/* CTA */}
        <section className="py-24">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Ready to stop losing patients to missed calls?
            </h2>
            <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
              Join the pilot program. Set up in 30 minutes. See your first
              AI-booked appointment within a week.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
              <a
                href="/signup"
                className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-8 py-3.5 rounded-full text-base transition-all shadow-xl shadow-emerald-500/25"
              >
                Start free trial
              </a>
              <a
                href="https://wa.me/918447804080?text=Hi%2C%20I%27d%20like%20a%20demo"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 bg-white text-slate-700 font-semibold px-8 py-3.5 rounded-full text-base border border-slate-200 hover:bg-slate-50 transition-all"
              >
                WhatsApp us
              </a>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <p className="text-3xl font-extrabold text-emerald-600">{value}</p>
      <p className="text-sm text-slate-500 mt-1">{label}</p>
    </div>
  );
}
