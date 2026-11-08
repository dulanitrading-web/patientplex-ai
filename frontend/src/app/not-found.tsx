import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-[#0B2545] mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-2">Page not found</p>
        <p className="text-gray-400 mb-8">The page you&apos;re looking for doesn&apos;t exist or has been moved.</p>
        <Link href="/dashboard" className="inline-flex items-center gap-2 bg-[#13838C] text-white px-6 py-3 rounded-xl font-semibold hover:bg-[#0f6d75] transition">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
