export default function DashboardLoading() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div className="flex items-end justify-between">
        <div>
          <div className="h-7 w-64 bg-slate-200 rounded-lg" />
          <div className="h-4 w-40 bg-slate-100 rounded mt-2" />
        </div>
        <div className="h-3 w-24 bg-slate-100 rounded" />
      </div>

      {/* KPI Cards skeleton */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl p-4 border border-slate-200">
            <div className="h-4 w-20 bg-slate-100 rounded mb-3" />
            <div className="h-8 w-16 bg-slate-200 rounded mb-2" />
            <div className="h-3 w-28 bg-slate-100 rounded" />
          </div>
        ))}
      </div>

      {/* Content skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-5 border border-slate-200">
          <div className="h-5 w-36 bg-slate-200 rounded mb-4" />
          <div className="h-10 w-24 bg-slate-100 rounded mb-2" />
          <div className="h-3 w-48 bg-slate-100 rounded" />
        </div>
        <div className="bg-white rounded-xl p-5 border border-slate-200">
          <div className="h-5 w-36 bg-slate-200 rounded mb-4" />
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="h-4 w-20 bg-slate-100 rounded" />
                <div className="flex-1 h-2 bg-slate-100 rounded-full" />
                <div className="h-4 w-8 bg-slate-100 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
