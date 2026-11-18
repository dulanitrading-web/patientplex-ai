"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, Calendar, CheckCircle2, Clock, XCircle, User, Plus,
  Loader2, Filter, Phone, X, Stethoscope, LayoutGrid, List, IndianRupee, Download,
} from "lucide-react";
import { getAppointments, updateAppointmentStatus, getAppointmentStats, bookAppointment, getMe } from "@/lib/api";
import CalendarView from "@/components/ui/CalendarView";
import WalkInQueue from "@/components/ui/WalkInQueue";

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
const SOURCE_OPTIONS = ["Google Ads", "WhatsApp", "Walk-in", "Phone Call", "Referral"];

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  const [updating, setUpdating] = useState<string | null>(null);

  // View mode: list or calendar
  const [viewMode, setViewMode] = useState<"list" | "calendar">("calendar");

  // Detail modal
  const [selectedAppt, setSelectedAppt] = useState<Appointment | null>(null);
  const [revenueInput, setRevenueInput] = useState("");
  const [treatmentDoneInput, setTreatmentDoneInput] = useState("");

  // Booking form
  const [showBooking, setShowBooking] = useState(false);
  const [booking, setBooking] = useState(false);
  const [services, setServices] = useState<string[]>([]);
  const [form, setForm] = useState({
    patient_name: "",
    patient_phone: "",
    treatment: "",
    date: new Date().toISOString().split("T")[0],
    time: "10:00",
    source: "Walk-in",
    notes: "",
  });

  useEffect(() => { load(); loadServices(); }, []);
  useEffect(() => { load(); }, [filter]);

  async function loadServices() {
    try {
      const me = await getMe();
      setServices(me.services || []);
      if (me.services?.length > 0) {
        setForm((f) => ({ ...f, treatment: me.services[0] }));
      }
    } catch { /* ignore */ }
  }

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

  async function handleBook() {
    if (!form.patient_name.trim() || !form.patient_phone.trim() || !form.treatment) return;
    setBooking(true);
    try {
      await bookAppointment(form);
      setShowBooking(false);
      setForm({ patient_name: "", patient_phone: "", treatment: services[0] || "", date: new Date().toISOString().split("T")[0], time: "10:00", source: "Walk-in", notes: "" });
      await load();
    } catch (err) {
      console.error("Booking failed:", err);
    } finally {
      setBooking(false);
    }
  }

  async function markStatus(id: string, status: string, options?: { revenue_amount?: number; treatment_done?: string }) {
    setUpdating(id);
    try {
      await updateAppointmentStatus(id, status, options);
      setSelectedAppt(null);
      setRevenueInput("");
      setTreatmentDoneInput("");
      await load();
    } finally {
      setUpdating(null);
    }
  }

  function exportCSV() {
    if (appointments.length === 0) return;
    const headers = ["Patient Name", "Phone", "Treatment", "Date", "Time", "Status", "Notes"];
    const rows = appointments.map((a) => [
      a.patient_name, a.patient_phone, a.treatment, a.date, a.time, a.status, a.notes || "",
    ]);
    const csv = [headers.join(","), ...rows.map((r) => r.map((v) => `"${v}"`).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `appointments_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const statusBadge = (s: string) => {
    const m: Record<string, string> = {
      CONFIRMED: "bg-cyan-50 text-cyan-600",
      REMINDED: "bg-amber-50 text-amber-600",
      ATTENDED: "bg-emerald-50 text-emerald-600",
      NO_SHOW: "bg-red-50 text-red-600",
      CANCELLED: "bg-slate-100 text-slate-500",
    };
    return m[s] || m.CONFIRMED;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/dashboard" className="text-slate-400 hover:text-slate-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-slate-900">Appointments</h1>
        </div>
        <div className="flex items-center gap-2">
          {/* Export */}
          <button
            onClick={exportCSV}
            disabled={appointments.length === 0}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition disabled:opacity-30"
            title="Export CSV"
          >
            <Download className="w-4 h-4" />
          </button>
          {/* View Toggle */}
          <div className="flex gap-0.5 bg-slate-100 rounded-lg p-0.5">
            <button
              onClick={() => setViewMode("calendar")}
              className={`p-2 rounded-md transition ${viewMode === "calendar" ? "bg-white text-slate-900 shadow-sm" : "text-slate-400 hover:text-slate-600"}`}
              title="Calendar view"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded-md transition ${viewMode === "list" ? "bg-white text-slate-900 shadow-sm" : "text-slate-400 hover:text-slate-600"}`}
              title="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={() => setShowBooking(!showBooking)}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors"
          >
            {showBooking ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {showBooking ? "Cancel" : "Log Appointment"}
          </button>
        </div>
      </div>

      {/* Booking Form */}
      {showBooking && (
        <div className="bg-white rounded-xl border border-emerald-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-emerald-600" /> New Appointment
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Patient Name *</label>
              <input
                type="text"
                value={form.patient_name}
                onChange={(e) => setForm({ ...form, patient_name: e.target.value })}
                placeholder="e.g. Rahul Sharma"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Phone Number *</label>
              <input
                type="tel"
                value={form.patient_phone}
                onChange={(e) => setForm({ ...form, patient_phone: e.target.value })}
                placeholder="e.g. 9876543210"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Treatment *</label>
              <select
                value={form.treatment}
                onChange={(e) => setForm({ ...form, treatment: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 bg-white"
              >
                {services.length > 0 ? (
                  services.map((s) => <option key={s} value={s}>{s}</option>)
                ) : (
                  <>
                    <option value="General Consultation">General Consultation</option>
                    <option value="Follow-up">Follow-up</option>
                  </>
                )}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Date</label>
              <input
                type="date"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Time</label>
              <input
                type="time"
                value={form.time}
                onChange={(e) => setForm({ ...form, time: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Source</label>
              <select
                value={form.source}
                onChange={(e) => setForm({ ...form, source: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 bg-white"
              >
                {SOURCE_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div className="flex justify-end mt-4">
            <button
              onClick={handleBook}
              disabled={booking || !form.patient_name.trim() || !form.patient_phone.trim()}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
            >
              {booking ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              {booking ? "Saving…" : "Book Appointment"}
            </button>
          </div>
        </div>
      )}

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <StatCard label="Total" value={stats.total_booked} />
          <StatCard label="Attended" value={stats.attended} color="text-emerald-600" />
          <StatCard label="No-Show" value={stats.no_show} color="text-red-600" />
          <StatCard label="Cancelled" value={stats.cancelled} color="text-slate-500" />
          <StatCard label="Rate" value={`${stats.attendance_rate}%`} color="text-cyan-600" />
        </div>
      )}

      {/* Walk-in Queue */}
      <WalkInQueue services={services} onPatientAdded={load} />

      {/* Calendar View */}
      {viewMode === "calendar" && (
        <CalendarView
          appointments={appointments}
          onSelectAppointment={(apt) => {
            const found = appointments.find((a) => a.id === apt.id);
            if (found) {
              setSelectedAppt(found);
              setTreatmentDoneInput(found.treatment);
            }
          }}
        />
      )}

      {/* Filter — only in list mode */}
      {viewMode === "list" && <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-400" />
        {STATUS_OPTIONS.map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === s
                ? "bg-emerald-50 text-emerald-600 border border-emerald-300"
                : "text-slate-500 border border-slate-200 hover:border-slate-300 hover:text-slate-700"
            }`}>
            {s === "ALL" ? "All" : s.replace("_", " ")}
          </button>
        ))}
      </div>}

      {/* Appointments List — only in list mode */}
      {viewMode === "list" && (loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
        </div>
      ) : appointments.length === 0 ? (
        <div className="bg-white rounded-xl p-8 text-center border border-slate-200">
          <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-slate-500 text-sm">No appointments found.</p>
          {!showBooking && (
            <button onClick={() => setShowBooking(true)} className="mt-3 text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              + Log your first appointment
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((a) => (
            <div key={a.id} className="bg-white rounded-xl border border-slate-200 p-4 cursor-pointer hover:border-emerald-200 hover:shadow-sm transition" onClick={() => { setSelectedAppt(a); setTreatmentDoneInput(a.treatment); }}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <User className="w-5 h-5 text-slate-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">{a.patient_name}</div>
                    <div className="text-sm text-slate-500">{a.treatment}</div>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                      <Calendar className="w-3 h-3" /> {a.date}
                      <Clock className="w-3 h-3 ml-1" /> {a.time}
                      <Phone className="w-3 h-3 ml-1" /> {a.patient_phone}
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(a.status)}`}>
                        {a.status.replace("_", " ")}
                      </span>
                      {a.reminder_24h_sent && <span className="text-[10px] text-slate-400">24h ✓</span>}
                      {a.reminder_2h_sent && <span className="text-[10px] text-slate-400">2h ✓</span>}
                      {a.notes && <span className="text-[10px] text-slate-400">📝 {a.notes}</span>}
                    </div>
                  </div>
                </div>

                {/* Status Action Buttons */}
                <div className="flex gap-2 shrink-0">
                  {(a.status === "CONFIRMED" || a.status === "REMINDED") && (
                    <>
                      <button
                        onClick={() => markStatus(a.id, "ATTENDED")}
                        disabled={updating === a.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white transition-colors disabled:opacity-50"
                      >
                        {updating === a.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                        Attended
                      </button>
                      <button
                        onClick={() => markStatus(a.id, "NO_SHOW")}
                        disabled={updating === a.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 hover:border-red-300 text-slate-500 hover:text-red-600 transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" /> No-Show
                      </button>
                      <button
                        onClick={() => markStatus(a.id, "CANCELLED")}
                        disabled={updating === a.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 hover:border-slate-300 text-slate-400 hover:text-slate-600 transition-colors disabled:opacity-50"
                      >
                        <X className="w-3.5 h-3.5" /> Cancel
                      </button>
                    </>
                  )}
                  {a.status === "ATTENDED" && (
                    <span className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-emerald-600">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Done
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ))}

      {/* Appointment Detail Modal */}
      {selectedAppt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setSelectedAppt(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900">Appointment Details</h3>
              <button onClick={() => setSelectedAppt(null)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-50 rounded-lg">
                  <User className="w-5 h-5 text-slate-400" />
                </div>
                <div>
                  <div className="font-medium text-slate-900">{selectedAppt.patient_name}</div>
                  <div className="text-sm text-slate-500 flex items-center gap-2">
                    <Phone className="w-3 h-3" /> {selectedAppt.patient_phone}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-0.5">Treatment</div>
                  <div className="font-medium text-slate-900">{selectedAppt.treatment}</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-0.5">Date & Time</div>
                  <div className="font-medium text-slate-900">{selectedAppt.date} · {selectedAppt.time}</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-0.5">Status</div>
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(selectedAppt.status)}`}>
                    {selectedAppt.status.replace("_", " ")}
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-0.5">Duration</div>
                  <div className="font-medium text-slate-900">{selectedAppt.duration_minutes} min</div>
                </div>
              </div>

              {selectedAppt.notes && (
                <div className="text-sm text-slate-600 bg-slate-50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-0.5">Notes</div>
                  {selectedAppt.notes}
                </div>
              )}

              {/* Revenue Input — shows when marking as Attended */}
              {(selectedAppt.status === "CONFIRMED" || selectedAppt.status === "REMINDED") && (
                <div className="border-t border-slate-100 pt-4 space-y-3">
                  <p className="text-sm font-medium text-slate-700">Complete this appointment:</p>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Treatment Done</label>
                    <input
                      type="text"
                      value={treatmentDoneInput}
                      onChange={(e) => setTreatmentDoneInput(e.target.value)}
                      placeholder="e.g. Root Canal + Crown"
                      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Amount Charged (₹)</label>
                    <div className="relative">
                      <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                      <input
                        type="number"
                        value={revenueInput}
                        onChange={(e) => setRevenueInput(e.target.value)}
                        placeholder="e.g. 5000"
                        className="w-full pl-8 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => markStatus(selectedAppt.id, "ATTENDED", {
                        revenue_amount: revenueInput ? parseFloat(revenueInput) : undefined,
                        treatment_done: treatmentDoneInput || undefined,
                      })}
                      disabled={updating === selectedAppt.id}
                      className="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-sm font-medium rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white transition-colors disabled:opacity-50"
                    >
                      {updating === selectedAppt.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                      Mark Attended
                    </button>
                    <button
                      onClick={() => markStatus(selectedAppt.id, "NO_SHOW")}
                      disabled={updating === selectedAppt.id}
                      className="px-4 py-2.5 text-sm font-medium rounded-lg border border-slate-200 hover:border-red-300 text-slate-500 hover:text-red-600 transition-colors disabled:opacity-50"
                    >
                      No-Show
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="bg-white rounded-xl p-3 border border-slate-200 text-center">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-xl font-bold ${color || "text-slate-900"}`}>{value}</div>
    </div>
  );
}
