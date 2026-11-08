"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Loader2,
  Search,
  User,
  Phone,
  MessageCircle,
  Calendar,
  ChevronRight,
  ArrowLeft,
  Clock,
  CheckCircle2,
  XCircle,
  Tag,
} from "lucide-react";
import { getConversations, getConversation, getAppointments } from "@/lib/api";

type PatientStatus = "New" | "Active" | "Booked" | "Attended" | "Lost";

interface ConversationSummary {
  id: string;
  patient_phone: string;
  patient_name: string | null;
  treatment_interest: string | null;
  status: string;
  source: string;
  message_count: number;
  appointment_datetime: string | null;
  created_at: string;
  updated_at: string;
}

interface Message {
  role: string;
  content: string;
  timestamp: string;
}

interface ConversationDetail {
  id: string;
  patient_phone: string;
  patient_name: string | null;
  treatment_interest: string | null;
  status: string;
  messages: Message[];
  source: string;
  created_at: string;
}

interface AppointmentRecord {
  id: string;
  patient_name: string;
  patient_phone: string;
  treatment: string;
  date: string;
  time: string;
  status: string;
}

interface Patient {
  phone: string;
  name: string;
  status: PatientStatus;
  source: string;
  treatment: string | null;
  lastMessageDate: string;
  conversationId: string;
  conversationStatus: string;
  messageCount: number;
}

function derivePatientStatus(convStatus: string): PatientStatus {
  switch (convStatus) {
    case "ACTIVE":
    case "BOOKING_IN_PROGRESS":
      return "Active";
    case "BOOKED":
      return "Booked";
    case "COMPLETED":
      return "Attended";
    case "ABANDONED":
      return "Lost";
    default:
      return "New";
  }
}

function maskPhone(phone: string): string {
  if (phone.length <= 6) return phone;
  return phone.slice(0, 3) + "****" + phone.slice(-3);
}

const STATUS_CONFIG: Record<PatientStatus, { cls: string; icon: React.ReactNode }> = {
  New: { cls: "bg-blue-50 text-blue-600", icon: <User className="w-3 h-3" /> },
  Active: { cls: "bg-yellow-50 text-yellow-600", icon: <MessageCircle className="w-3 h-3" /> },
  Booked: { cls: "bg-purple-50 text-purple-600", icon: <Calendar className="w-3 h-3" /> },
  Attended: { cls: "bg-green-50 text-green-600", icon: <CheckCircle2 className="w-3 h-3" /> },
  Lost: { cls: "bg-red-50 text-red-600", icon: <XCircle className="w-3 h-3" /> },
};

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<PatientStatus | "All">("All");
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [patientAppointments, setPatientAppointments] = useState<AppointmentRecord[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadPatients();
  }, []);

  async function loadPatients() {
    try {
      const data = await getConversations();
      const convos: ConversationSummary[] = data.conversations || [];
      const patientMap = new Map<string, Patient>();

      for (const c of convos) {
        const existing = patientMap.get(c.patient_phone);
        if (!existing || new Date(c.updated_at) > new Date(existing.lastMessageDate)) {
          patientMap.set(c.patient_phone, {
            phone: c.patient_phone,
            name: c.patient_name || c.patient_phone,
            status: derivePatientStatus(c.status),
            source: c.source,
            treatment: c.treatment_interest,
            lastMessageDate: c.updated_at,
            conversationId: c.id,
            conversationStatus: c.status,
            messageCount: c.message_count,
          });
        }
      }

      setPatients(Array.from(patientMap.values()).sort(
        (a, b) => new Date(b.lastMessageDate).getTime() - new Date(a.lastMessageDate).getTime()
      ));
    } catch {
      /* use defaults */
    } finally {
      setLoading(false);
    }
  }

  async function openPatient(patient: Patient) {
    setSelectedPatient(patient);
    setDetailLoading(true);
    try {
      const [convoRes, apptsRes] = await Promise.allSettled([
        getConversation(patient.conversationId),
        getAppointments(),
      ]);
      if (convoRes.status === "fulfilled") setConversation(convoRes.value);
      if (apptsRes.status === "fulfilled") {
        const all: AppointmentRecord[] = apptsRes.value.appointments || [];
        setPatientAppointments(all.filter((a) => a.patient_phone === patient.phone));
      }
    } finally {
      setDetailLoading(false);
    }
  }

  const filtered = useMemo(() => {
    return patients.filter((p) => {
      const matchesSearch =
        !search ||
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.phone.includes(search);
      const matchesStatus = statusFilter === "All" || p.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [patients, search, statusFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-[#0B2545]">Patient CRM</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {patients.length} patients from WhatsApp conversations
          </p>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
          />
        </div>
        <div className="flex bg-white border border-gray-200 rounded-lg overflow-hidden">
          {(["All", "New", "Active", "Booked", "Attended", "Lost"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-2 text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-[#0B2545] text-white"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Patient List */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-medium text-gray-500">{filtered.length} patients</span>
          </div>
          <div className="max-h-[calc(100vh-320px)] overflow-y-auto divide-y divide-gray-50">
            {filtered.length === 0 ? (
              <div className="p-8 text-center">
                <User className="w-10 h-10 text-gray-200 mx-auto mb-2" />
                <p className="text-gray-400 text-sm">No patients found.</p>
              </div>
            ) : (
              filtered.map((p) => {
                const cfg = STATUS_CONFIG[p.status];
                return (
                  <button
                    key={p.phone}
                    onClick={() => openPatient(p)}
                    className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                      selectedPatient?.phone === p.phone ? "bg-blue-50" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center shrink-0">
                          <User className="w-5 h-5 text-gray-400" />
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium text-sm text-[#0B2545] truncate">
                            {p.name}
                          </div>
                          <div className="text-xs text-gray-400 flex items-center gap-1">
                            <Phone className="w-3 h-3" /> {maskPhone(p.phone)}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium ${cfg.cls}`}>
                              {cfg.icon} {p.status}
                            </span>
                            <span className="text-[10px] text-gray-400">
                              {timeAgo(p.lastMessageDate)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-300 shrink-0" />
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Patient Detail */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 flex flex-col">
          {detailLoading ? (
            <div className="flex-1 flex items-center justify-center py-20">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
            </div>
          ) : !selectedPatient ? (
            <div className="flex-1 flex items-center justify-center py-20">
              <div className="text-center">
                <User className="w-12 h-12 text-gray-200 mx-auto mb-2" />
                <p className="text-gray-400">Select a patient to view details</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              {/* Patient Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-[#0B2545] text-lg">
                      {selectedPatient.name}
                    </h3>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                      <span className="flex items-center gap-1">
                        <Phone className="w-3 h-3" /> {selectedPatient.phone}
                      </span>
                      <span className="flex items-center gap-1">
                        <Tag className="w-3 h-3" /> {selectedPatient.source}
                      </span>
                      {selectedPatient.treatment && (
                        <span>{selectedPatient.treatment}</span>
                      )}
                    </div>
                  </div>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[selectedPatient.status].cls}`}>
                    {STATUS_CONFIG[selectedPatient.status].icon}
                    {selectedPatient.status}
                  </span>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto">
                {/* Appointments Section */}
                <div className="p-4 border-b border-gray-100">
                  <h4 className="font-medium text-sm text-[#0B2545] flex items-center gap-2 mb-3">
                    <Calendar className="w-4 h-4" /> Appointments
                  </h4>
                  {patientAppointments.length === 0 ? (
                    <p className="text-sm text-gray-400">No appointments recorded.</p>
                  ) : (
                    <div className="space-y-2">
                      {patientAppointments.map((appt) => (
                        <div
                          key={appt.id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <div className="text-sm font-medium text-gray-700">
                              {appt.treatment}
                            </div>
                            <div className="text-xs text-gray-400 flex items-center gap-1">
                              <Clock className="w-3 h-3" /> {appt.date} at {appt.time}
                            </div>
                          </div>
                          <ApptStatusBadge status={appt.status} />
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Conversation History */}
                <div className="p-4">
                  <h4 className="font-medium text-sm text-[#0B2545] flex items-center gap-2 mb-3">
                    <MessageCircle className="w-4 h-4" /> Conversation History
                    {conversation && (
                      <span className="text-xs text-gray-400 font-normal">
                        ({(conversation.messages || []).length} messages)
                      </span>
                    )}
                  </h4>
                  {!conversation || (conversation.messages || []).length === 0 ? (
                    <p className="text-sm text-gray-400">No messages yet.</p>
                  ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto">
                      {(conversation.messages || []).map((msg, i) => (
                        <div
                          key={i}
                          className={`flex ${msg.role === "assistant" ? "justify-start" : "justify-end"}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${
                              msg.role === "assistant"
                                ? "bg-gray-100 text-gray-800"
                                : "bg-[#0B2545] text-white"
                            }`}
                          >
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                            <div
                              className={`text-[10px] mt-1 ${
                                msg.role === "assistant" ? "text-gray-400" : "text-white/60"
                              }`}
                            >
                              {msg.timestamp
                                ? new Date(msg.timestamp).toLocaleString([], {
                                    month: "short",
                                    day: "numeric",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })
                                : ""}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function ApptStatusBadge({ status }: { status: string }) {
  const config: Record<string, { cls: string; icon: React.ReactNode }> = {
    CONFIRMED: { cls: "bg-blue-50 text-blue-600", icon: <Clock className="w-3 h-3" /> },
    REMINDED: { cls: "bg-yellow-50 text-yellow-600", icon: <Clock className="w-3 h-3" /> },
    ATTENDED: { cls: "bg-green-50 text-green-600", icon: <CheckCircle2 className="w-3 h-3" /> },
    NO_SHOW: { cls: "bg-red-50 text-red-600", icon: <XCircle className="w-3 h-3" /> },
    CANCELLED: { cls: "bg-gray-100 text-gray-500", icon: <XCircle className="w-3 h-3" /> },
  };
  const cfg = config[status] || config.CONFIRMED;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
      {cfg.icon} {status}
    </span>
  );
}

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString([], { month: "short", day: "numeric" });
}
