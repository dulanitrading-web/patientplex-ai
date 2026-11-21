import Link from "next/link";
import Logo from "@/components/Logo";

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <Logo size={28} />
              <span className="text-lg font-bold text-white">PatientPlex</span>
            </div>
            <p className="text-sm leading-relaxed max-w-sm">
              AI-powered patient acquisition for healthcare clinics across India.
              Replace your marketing agency with autonomous ads, an AI receptionist,
              and smart booking.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
            <ul className="space-y-2.5">
              <li><a href="#features" className="text-sm hover:text-white transition-colors">Features</a></li>
              <li><a href="#pricing" className="text-sm hover:text-white transition-colors">Pricing</a></li>
              <li><a href="#how-it-works" className="text-sm hover:text-white transition-colors">How it works</a></li>
              <li><Link href="/about" className="text-sm hover:text-white transition-colors">About</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Legal</h4>
            <ul className="space-y-2.5">
              <li><Link href="/privacy" className="text-sm hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="text-sm hover:text-white transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs">&copy; {new Date().getFullYear()} PatientPlex AI. All rights reserved.</p>
          <p className="text-xs">Made in India for Indian clinics</p>
        </div>
      </div>
    </footer>
  );
}
