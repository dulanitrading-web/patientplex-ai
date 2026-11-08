import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#0A0E1A] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h1 className="text-7xl font-bold text-emerald-500/20 mb-4">404</h1>
        <p className="text-xl text-white mb-2">Page not found</p>
        <p className="text-slate-500 mb-8">The page you&apos;re looking for doesn&apos;t exist or has been moved.</p>
        <Link href="/dashboard" className="inline-flex items-center gap-2 bg-emerald-500 text-[#0A0E1A] px-6 py-3 rounded-lg font-semibold hover:bg-emerald-400 transition-colors">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
