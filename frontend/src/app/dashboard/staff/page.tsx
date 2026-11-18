"use client";

import { useState, useEffect } from "react";
import {
  ArrowLeft, Plus, Users, Loader2, User, Phone, Mail,
  Clock, Stethoscope, X, CheckCircle2, Palette, Calendar,
} from "lucide-react";
import Link from "next/link";
import { getClinicStaff, addClinicStaff } from "@/lib/api";

interface StaffMember {
  id: string;
  full_name: string;
  title: string;
  specialty: string;
  role: string;
  phone: string | null;
  email: string | null;
  services: string[];
  weekly_schedule: Record<string, { start: string; end: string }>;
  slot_duration_minutes: number;
  max_patients_per_day: number;
  calendar_color: string;
  is_active: boolean;
  google_calendar_connected: boolean;
}

const COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#ec4899", "#06b6d4", "#84cc16"];
const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

export default function StaffPage() {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    full_name: "",
    specialty: "",
    phone: "",
    email: "",
    services: "",
    calendar_color: COLORS[1],
  });

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await getClinicStaff();
      setStaff(data.staff || []);
    } catch (err) {
      console.error("Failed to load staff:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd() {
    if (!form.full_name.trim() || !form.specialty.trim()) return;
    setSaving(true);
    try {
      await addClinicStaff({
        full_name: form.full_name,
        specialty: form.specialty,
        phone: form.phone || undefined,
        email: form.email || undefined,
        services: form.services ? form.services.split(",").map((s) => s.trim()).filter(Boolean) : undefined,
        calendar_color: form.calendar_color,
      });
      setShowAdd(false);
      setForm({ full_name: "", specialty: "", phone: "", email: "", services: "", calendar_color: COLORS[staff.length % COLORS.length + 1] || COLORS[0] });
      await load();
    } catch (err) {
      console.error("Failed to add staff:", err);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/dashboard/settings" className="text-slate-400 hover:text-slate-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Clinic Staff</h1>
            <p className="text-sm text-slate-500">Manage doctors and practitioners at your clinic</p>
          </div>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors"
        >
          {showAdd ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showAdd ? "Cancel" : "Add Doctor"}
        </button>
      </div>

      {/* Add Form */}
      {showAdd && (
        <div className="bg-white rounded-xl border border-emerald-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-emerald-600" /> New Doctor / Practitioner
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Full Name *</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="e.g. Dr. Priya Sharma"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Specialty *</label>
              <input
                type="text"
                value={form.specialty}
                onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                placeholder="e.g. Orthodontist, Endodontist"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Phone</label>
              <input
                type="tel"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="e.g. 9876543210"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="e.g. priya@clinic.com"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Services (comma-separated)</label>
              <input
                type="text"
                value={form.services}
                onChange={(e) => setForm({ ...form, services: e.target.value })}
                placeholder="Root Canal, Implants, Braces"
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Calendar Color</label>
              <div className="flex items-center gap-2 mt-1">
                {COLORS.map((c) => (
                  <button
                    key={c}
                    onClick={() => setForm({ ...form, calendar_color: c })}
                    className={`w-7 h-7 rounded-full border-2 transition ${
                      form.calendar_color === c ? "border-slate-900 scale-110" : "border-transparent"
                    }`}
                    style={{ backgroundColor: c }}
                    aria-label={`Color ${c}`}
                  />
                ))}
              </div>
            </div>
          </div>
          <div className="flex justify-end mt-4">
            <button
              onClick={handleAdd}
              disabled={saving || !form.full_name.trim() || !form.specialty.trim()}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              {saving ? "Adding…" : "Add to Clinic"}
            </button>
          </div>
        </div>
      )}

      {/* Staff List */}
      {staff.length === 0 ? (
        <div className="bg-white rounded-xl p-10 text-center border border-slate-200">
          <Users className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm mb-1">No staff members yet</p>
          <p className="text-slate-400 text-xs mb-4">Add doctors and practitioners who see patients at your clinic</p>
          <button
            onClick={() => setShowAdd(true)}
            className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
          >
            + Add your first doctor
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {staff.map((s) => (
            <div
              key={s.id}
              className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-sm transition relative overflow-hidden"
            >
              {/* Color stripe */}
              <div className="absolute top-0 left-0 right-0 h-1" style={{ backgroundColor: s.calendar_color }} />

              <div className="flex items-start gap-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                  style={{ backgroundColor: s.calendar_color }}
                >
                  {s.full_name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-slate-900 text-sm">{s.title} {s.full_name}</div>
                  <div className="text-xs text-slate-500">{s.specialty}</div>
                  {s.role === "OWNER" && (
                    <span className="inline-block mt-1 px-2 py-0.5 text-[10px] font-medium bg-emerald-50 text-emerald-700 rounded-full">
                      Clinic Owner
                    </span>
                  )}
                </div>
                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${s.is_active ? "bg-green-500" : "bg-slate-300"}`} />
              </div>

              {/* Details */}
              <div className="mt-4 space-y-1.5 text-xs text-slate-500">
                {s.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3 h-3" /> {s.phone}
                  </div>
                )}
                {s.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-3 h-3" /> {s.email}
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Clock className="w-3 h-3" /> {s.slot_duration_minutes} min slots · Max {s.max_patients_per_day}/day
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-3 h-3" /> {s.google_calendar_connected ? "Calendar synced" : "No calendar linked"}
                </div>
              </div>

              {/* Services */}
              {s.services.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {s.services.slice(0, 4).map((svc) => (
                    <span key={svc} className="px-2 py-0.5 text-[10px] font-medium bg-slate-100 text-slate-600 rounded-full">
                      {svc}
                    </span>
                  ))}
                  {s.services.length > 4 && (
                    <span className="px-2 py-0.5 text-[10px] text-slate-400">+{s.services.length - 4} more</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
