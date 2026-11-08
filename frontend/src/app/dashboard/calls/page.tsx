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
      ANSWERED: "bg-emerald-500/10 text-emerald-400",
      MISSED: "bg-red-500/10 text-red-400",
      NO_ANSWER: "bg-amber-500/10 text-amber-400",
      BUSY: "bg-orange-500/10 text-orange-400",
      COMPLETED: "bg-emerald-500/10 text-emerald-400",
      FAILED: "bg-red-500/10 text-red-400",
    };
    return m[s] || "bg-white/5 text-slate-400";
  };

  const DirectionIcon = ({ direction }: { direction: string }) => {
    if (direction === "OUTBOUND") return <PhoneOutgoing className="w-4 h-4 text-cyan-400" />;
    return <PhoneIncoming className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-white">Call Log</h1>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Total Calls" value={stats.total_calls} icon={<Phone className="w-4 h-4 text-white" />} />
          <StatCard label="Answered" value={stats.answered} color="text-emerald-400" icon={<PhoneIncoming className="w-4 h-4 text-emerald-400" />} />
          <StatCard label="Missed" value={stats.missed} color="text-red-400" icon={<PhoneMissed className="w-4 h-4 text-red-400" />} />
          <StatCard label="Recovered" value={stats.recovered_via_whatsapp} color="text-cyan-400" icon={<MessageCircle className="w-4 h-4 text-cyan-400" />} />
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-500" />
        {STATUS_OPTIONS.map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === s ? "bg-emerald-500 text-[#0A0E1A]" : "bg-white/5 text-slate-400 border border-white/10 hover:border-white/20"
            }`}>
            {s === "ALL" ? "All" : s.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Call Log List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
        </div>
      ) : logs.length === 0 ? (
        <div className="bg-[#0F172A] rounded-xl p-8 text-center border border-white/5">
          <Phone className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-slate-400">No calls found.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((cl) => (
            <div key={cl.id} className="bg-[#0F172A] rounded-xl border border-white/5 p-4 hover:border-white/10 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-white/5 rounded-lg">
                    <DirectionIcon direction={cl.direction} />
                  </div>
                  <div>
                    <div className="font-medium text-white">{maskPhone(cl.caller_phone)}</div>
                    <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-2 flex-wrap">
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
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400">
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
    </div>
  );
}

function StatCard({ label, value, color, icon }: { label: string; value: number; color?: string; icon?: React.ReactNode }) {
  return (
    <div className="bg-[#0F172A] rounded-xl p-3 border border-white/5 text-center">
      {icon && <div className="flex justify-center mb-1">{icon}</div>}
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-xl font-bold ${color || "text-white"}`}>{value}</div>
    </div>
  );
}
