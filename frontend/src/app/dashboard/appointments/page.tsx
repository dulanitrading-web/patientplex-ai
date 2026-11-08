"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Calendar, CheckCircle2, Clock, XCircle, User,
  Loader2, Filter,
} from "lucide-react";
import { getAppointments, updateAppointmentStatus, getAppointmentStats } from "@/lib/api";

interface Appointment {
  id: string;
  patient_name: string;
  patient_phone: string;
  treatment: string;
  date: string;
  time: string;
  duration_minutes: number;
  status: string;
  reminder_24h_sent: boolean;
  reminder_2h_sent: boolean;
  notes: string | null;
  created_at: string;
}

interface Stats {
  total_booked: number;
  attended: number;
  no_show: number;
  cancelled: number;
  upcoming: number;
  attendance_rate: number;
}

const STATUS_OPTIONS = ["ALL", "CONFIRMED", "REMINDED", "ATTENDED", "NO_SHOW", "CANCELLED"];

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => { load(); }, [filter]);

  async function load() {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filter !== "ALL") params.status = filter;
      const [apptData, statsData] = await Promise.allSettled([
        getAppointments(params),
        getAppointmentStats(30),
      ]);
      if (apptData.status === "fulfilled") setAppointments(apptData.value.appointments || []);
      if (statsData.status === "fulfilled") setStats(statsData.value);
    } finally {
      setLoading(false);
    }
  }

  async function markStatus(id: string, status: string) {
    setUpdating(id);
    try {
      await updateAppointmentStatus(id, status);
      await load();
    } finally {
      setUpdating(null);
    }
  }

  const statusBadge = (s: string) => {
    const m: Record<string, string> = {
      CONFIRMED: "bg-cyan-500/10 text-cyan-400",
      REMINDED: "bg-amber-500/10 text-amber-400",
      ATTENDED: "bg-emerald-500/10 text-emerald-400",
      NO_SHOW: "bg-red-500/10 text-red-400",
      CANCELLED: "bg-white/5 text-slate-500",
    };
    return m[s] || m.CONFIRMED;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="text-slate-500 hover:text-slate-300">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-lg font-bold text-white">Appointments</h1>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <StatCard label="Total" value={stats.total_booked} />
          <StatCard label="Attended" value={stats.attended} color="text-emerald-400" />
          <StatCard label="No-Show" value={stats.no_show} color="text-red-400" />
          <StatCard label="Cancelled" value={stats.cancelled} color="text-slate-500" />
          <StatCard label="Rate" value={`${stats.attendance_rate}%`} color="text-cyan-400" />
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-500" />
        {STATUS_OPTIONS.map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === s
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                : "text-slate-400 border border-white/10 hover:border-white/20 hover:text-slate-300"
            }`}>
            {s === "ALL" ? "All" : s.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Appointments List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
        </div>
      ) : appointments.length === 0 ? (
        <div className="bg-[#0F172A] rounded-xl p-8 text-center border border-white/5">
          <Calendar className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-slate-500">No appointments found.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((a) => (
            <div key={a.id} className="bg-[#0F172A] rounded-xl border border-white/5 p-4 hover:border-white/10 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-white/5 rounded-lg">
                    <User className="w-5 h-5 text-slate-400" />
                  </div>
                  <div>
                    <div className="font-medium text-white">{a.patient_name}</div>
                    <div className="text-sm text-slate-400">{a.treatment}</div>
                    <div className="text-xs text-slate-500 mt-1">
                      {a.date} · {a.time} · {a.patient_phone}
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(a.status)}`}>
                        {a.status}
                      </span>
                      {a.reminder_24h_sent && <span className="text-xs text-slate-500">24h ✓</span>}
                      {a.reminder_2h_sent && <span className="text-xs text-slate-500">2h ✓</span>}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                {(a.status === "CONFIRMED" || a.status === "REMINDED") && (
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => markStatus(a.id, "ATTENDED")}
                      disabled={updating === a.id}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500 hover:bg-emerald-400 text-[#0A0E1A] transition-colors disabled:opacity-50"
                    >
                      {updating === a.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                      Attended
                    </button>
                    <button
                      onClick={() => markStatus(a.id, "NO_SHOW")}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-white/10 hover:border-red-500/30 text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <XCircle className="w-3.5 h-3.5" /> No-Show
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="bg-[#0F172A] rounded-xl p-3 border border-white/5 text-center">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-xl font-bold ${color || "text-white"}`}>{value}</div>
    </div>
  );
}
