import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h1 className="text-7xl font-black text-emerald-500/30 mb-4">404</h1>
        <p className="text-xl text-slate-900 font-bold mb-2">Page not found</p>
        <p className="text-slate-500 mb-8">The page you&apos;re looking for doesn&apos;t exist or has been moved.</p>
        <Link href="/dashboard" className="inline-flex items-center gap-2 bg-slate-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-slate-800 transition-colors">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
