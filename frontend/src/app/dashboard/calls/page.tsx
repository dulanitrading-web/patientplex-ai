"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Phone, PhoneIncoming, PhoneOutgoing, PhoneMissed,
  Loader2, Filter, MessageCircle, Clock,
} from "lucide-react";
import { getCallStats, getCallLogs } from "@/lib/api";

interface CallLog {
  id: string;
  caller_phone: string;
  direction: string;
  status: string;
  duration_seconds: number;
  recording_url: string | null;
  whatsapp_followup_sent: boolean;
  started_at: string;
  created_at: string;
}

interface CallStats {
  period_days: number;
  total_calls: number;
  answered: number;
  missed: number;
  recovered_via_whatsapp: number;
  recovery_rate: number;
  answer_rate: number;
}

const STATUS_OPTIONS = ["ALL", "ANSWERED", "MISSED", "NO_ANSWER", "BUSY"];

function maskPhone(phone: string): string {
  if (!phone || phone.length < 4) return phone;
  return phone.slice(0, -4).replace(/\d/g, "*") + phone.slice(-4);
}

function formatDuration(seconds: number): string {
  if (!seconds || seconds === 0) return "-";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function CallsPage() {
  const [logs, setLogs] = useState<CallLog[]>([]);
  const [stats, setStats] = useState<CallStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");

  useEffect(() => { load(); }, [filter]);

  async function load() {
    setLoading(true);
    try {
      const [logsData, statsData] = await Promise.allSettled([
        getCallLogs(filter),
        getCallStats(),
      ]);
      if (logsData.status === "fulfilled") setLogs(logsData.value.call_logs || []);
      if (statsData.status === "fulfilled") setStats(statsData.value);
    } finally {
      setLoading(false);
    }
  }

  const statusBadge = (s: string) => {
    const m: Record<string, string> = {
      ANSWERED: "bg-green-50 text-green-700",
      MISSED: "bg-red-50 text-red-700",
      NO_ANSWER: "bg-yellow-50 text-yellow-700",
      BUSY: "bg-orange-50 text-orange-700",
      COMPLETED: "bg-green-50 text-green-700",
      FAILED: "bg-red-50 text-red-700",
    };
    return m[s] || "bg-gray-100 text-gray-600";
  };

  const DirectionIcon = ({ direction }: { direction: string }) => {
    if (direction === "OUTBOUND") return <PhoneOutgoing className="w-4 h-4 text-blue-500" />;
    return <PhoneIncoming className="w-4 h-4 text-teal-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <Link href="/dashboard" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-[#0B2545]">Call Log</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <StatCard label="Total Calls" value={stats.total_calls} icon={<Phone className="w-4 h-4 text-[#0B2545]" />} />
            <StatCard label="Answered" value={stats.answered} color="text-green-600" icon={<PhoneIncoming className="w-4 h-4 text-green-500" />} />
            <StatCard label="Missed" value={stats.missed} color="text-red-600" icon={<PhoneMissed className="w-4 h-4 text-red-500" />} />
            <StatCard label="Recovered" value={stats.recovered_via_whatsapp} color="text-teal-600" icon={<MessageCircle className="w-4 h-4 text-teal-500" />} />
          </div>
        )}

        {/* Filter */}
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-4 h-4 text-gray-400" />
          {STATUS_OPTIONS.map((s) => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filter === s ? "bg-[#0B2545] text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              }`}>
              {s === "ALL" ? "All" : s.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* Call Log List */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : logs.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center border border-gray-200">
            <Phone className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No calls found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((cl) => (
              <div key={cl.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <DirectionIcon direction={cl.direction} />
                    </div>
                    <div>
                      <div className="font-medium text-[#0B2545]">{maskPhone(cl.caller_phone)}</div>
                      <div className="text-xs text-gray-400 mt-0.5 flex items-center gap-2 flex-wrap">
                        <span className="capitalize">{cl.direction.toLowerCase()}</span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {formatDuration(cl.duration_seconds)}
                        </span>
                        <span>·</span>
                        <span>{formatTime(cl.started_at)}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(cl.status)}`}>
                          {cl.status.replace("_", " ")}
                        </span>
                        {cl.whatsapp_followup_sent && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700">
                            <MessageCircle className="w-3 h-3" /> WhatsApp sent
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ label, value, color, icon }: { label: string; value: number; color?: string; icon?: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl p-3 border border-gray-200 text-center">
      {icon && <div className="flex justify-center mb-1">{icon}</div>}
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-xl font-bold ${color || "text-[#0B2545]"}`}>{value}</div>
    </div>
  );
}
