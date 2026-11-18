"use client";

import { useState } from "react";
import {
  UserPlus, Loader2, CheckCircle2, Clock, User, Phone,
  Stethoscope, IndianRupee, ArrowRight,
} from "lucide-react";
import { bookAppointment, updateAppointmentStatus } from "@/lib/api";

interface WalkInPatient {
  id: string;
  name: string;
  phone: string;
  treatment: string;
  status: "waiting" | "in_consultation" | "done";
  addedAt: Date;
  revenue?: number;
}

interface WalkInQueueProps {
  services: string[];
  onPatientAdded?: () => void;
}

export default function WalkInQueue({ services, onPatientAdded }: WalkInQueueProps) {
  const [queue, setQueue] = useState<WalkInPatient[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [treatment, setTreatment] = useState(services[0] || "General Consultation");
  const [revenueInput, setRevenueInput] = useState("");

  async function addToQueue() {
    if (!name.trim() || !phone.trim()) return;
    setSaving(true);
    try {
      const today = new Date().toISOString().split("T")[0];
      const now = new Date();
      const time = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;

      const result = await bookAppointment({
        patient_name: name,
        patient_phone: phone,
        treatment,
        date: today,
        time,
        source: "Walk-in",
        notes: "Walk-in patient",
      });

      const newPatient: WalkInPatient = {
        id: result.appointment?.id || `local-${Date.now()}`,
        name,
        phone,
        treatment,
        status: "waiting",
        addedAt: new Date(),
      };
      setQueue((prev) => [...prev, newPatient]);
      setName("");
      setPhone("");
      setTreatment(services[0] || "General Consultation");
      setShowAdd(false);
      onPatientAdded?.();
    } catch (err) {
      console.error("Failed to add walk-in:", err);
    } finally {
      setSaving(false);
    }
  }

  function markConsulting(id: string) {
    setQueue((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: "in_consultation" as const } : p))
    );
  }

  async function markDone(id: string) {
    const revenue = revenueInput ? parseFloat(revenueInput) : undefined;
    setQueue((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: "done" as const, revenue } : p))
    );
    // Update in backend
    try {
      await updateAppointmentStatus(id, "ATTENDED", {
        revenue_amount: revenue,
      });
    } catch {
      // silent
    }
    setRevenueInput("");
    onPatientAdded?.();
  }

  const waiting = queue.filter((p) => p.status === "waiting");
  const inConsultation = queue.filter((p) => p.status === "in_consultation");
  const done = queue.filter((p) => p.status === "done");

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <h3 className="text-sm font-semibold text-slate-900">Walk-in Queue</h3>
          {waiting.length > 0 && (
            <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-medium">
              {waiting.length} waiting
            </span>
          )}
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white transition"
        >
          <UserPlus className="w-3.5 h-3.5" /> Walk-in
        </button>
      </div>

      {/* Quick Add Form */}
      {showAdd && (
        <div className="p-4 bg-emerald-50/50 border-b border-emerald-100">
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Patient name"
              className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-emerald-400 bg-white"
              autoFocus
            />
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Phone"
              className="w-32 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-emerald-400 bg-white"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={treatment}
              onChange={(e) => setTreatment(e.target.value)}
              className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:border-emerald-400"
            >
              {services.length > 0 ? (
                services.map((s) => <option key={s} value={s}>{s}</option>)
              ) : (
                <option value="General Consultation">General Consultation</option>
              )}
            </select>
            <button
              onClick={addToQueue}
              disabled={saving || !name.trim() || !phone.trim()}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white transition disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add"}
            </button>
          </div>
        </div>
      )}

      {/* Queue */}
      <div className="divide-y divide-slate-50">
        {queue.length === 0 && !showAdd && (
          <div className="px-4 py-6 text-center text-sm text-slate-400">
            No walk-ins yet today. Tap &ldquo;Walk-in&rdquo; to add a patient.
          </div>
        )}

        {/* In Consultation (top priority) */}
        {inConsultation.map((p) => (
          <div key={p.id} className="px-4 py-3 bg-blue-50/50 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center">
                <Stethoscope className="w-3.5 h-3.5 text-blue-600" />
              </div>
              <div>
                <div className="text-sm font-medium text-slate-900">{p.name}</div>
                <div className="text-xs text-slate-500">{p.treatment}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number"
                placeholder="₹ Revenue"
                value={revenueInput}
                onChange={(e) => setRevenueInput(e.target.value)}
                className="w-24 px-2 py-1.5 text-xs border border-slate-200 rounded-lg text-right"
              />
              <button
                onClick={() => markDone(p.id)}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition"
              >
                Done ₹
              </button>
            </div>
          </div>
        ))}

        {/* Waiting */}
        {waiting.map((p, i) => (
          <div key={p.id} className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-amber-100 flex items-center justify-center text-xs font-bold text-amber-700">
                {i + 1}
              </div>
              <div>
                <div className="text-sm font-medium text-slate-900">{p.name}</div>
                <div className="text-xs text-slate-500">{p.treatment} · {p.phone}</div>
              </div>
            </div>
            <button
              onClick={() => markConsulting(p.id)}
              className="px-3 py-1.5 text-xs font-medium rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 transition"
            >
              Start <ArrowRight className="w-3 h-3 inline ml-0.5" />
            </button>
          </div>
        ))}

        {/* Done */}
        {done.length > 0 && (
          <div className="px-4 py-2 bg-slate-50">
            <div className="text-[10px] text-slate-400 font-medium uppercase mb-1">Completed Today</div>
            {done.map((p) => (
              <div key={p.id} className="flex items-center justify-between py-1.5 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  {p.name} — {p.treatment}
                </div>
                {p.revenue && <span className="text-emerald-600 font-medium">₹{p.revenue.toLocaleString()}</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
