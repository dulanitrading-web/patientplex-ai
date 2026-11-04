"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Calendar, CheckCircle2, Clock, XCircle, User,
  Loader2, Filter,
} from "lucide-react";
import Button from "@/components/ui/Button";
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
      CONFIRMED: "bg-blue-50 text-blue-700",
      REMINDED: "bg-yellow-50 text-yellow-700",
      ATTENDED: "bg-green-50 text-green-700",
      NO_SHOW: "bg-red-50 text-red-700",
      CANCELLED: "bg-gray-100 text-gray-500",
    };
    return m[s] || m.CONFIRMED;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <Link href="/dashboard" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-[#0B2545]">Appointments</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <StatCard label="Total" value={stats.total_booked} />
            <StatCard label="Attended" value={stats.attended} color="text-green-600" />
            <StatCard label="No-Show" value={stats.no_show} color="text-red-600" />
            <StatCard label="Cancelled" value={stats.cancelled} color="text-gray-500" />
            <StatCard label="Rate" value={`${stats.attendance_rate}%`} color="text-blue-600" />
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

        {/* Appointments List */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : appointments.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center border border-gray-200">
            <Calendar className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No appointments found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {appointments.map((a) => (
              <div key={a.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <User className="w-5 h-5 text-gray-400" />
                    </div>
                    <div>
                      <div className="font-medium text-[#0B2545]">{a.patient_name}</div>
                      <div className="text-sm text-gray-500">{a.treatment}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        📅 {a.date} · 🕐 {a.time} · 📞 {a.patient_phone}
                      </div>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(a.status)}`}>
                          {a.status}
                        </span>
                        {a.reminder_24h_sent && <span className="text-xs text-gray-400">24h ✓</span>}
                        {a.reminder_2h_sent && <span className="text-xs text-gray-400">2h ✓</span>}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  {(a.status === "CONFIRMED" || a.status === "REMINDED") && (
                    <div className="flex gap-2 shrink-0">
                      <Button variant="primary" size="sm" onClick={() => markStatus(a.id, "ATTENDED")}
                        loading={updating === a.id}>
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Attended
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => markStatus(a.id, "NO_SHOW")}>
                        <XCircle className="w-3.5 h-3.5 mr-1" /> No-Show
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="bg-white rounded-xl p-3 border border-gray-200 text-center">
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-xl font-bold ${color || "text-[#0B2545]"}`}>{value}</div>
    </div>
  );
}
