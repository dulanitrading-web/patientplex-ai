"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft, MessageCircle, User, Calendar, Loader2,
  ChevronRight, Clock, CheckCircle2, Phone,
} from "lucide-react";
import { getConversations, getConversation } from "@/lib/api";

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

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    try {
      const data = await getConversations();
      setConversations(data.conversations || []);
    } finally {
      setLoading(false);
    }
  }

  async function openChat(id: string) {
    setChatLoading(true);
    try {
      const data = await getConversation(id);
      setSelected(data);
    } finally {
      setChatLoading(false);
    }
  }

  const statusColor: Record<string, string> = {
    ACTIVE: "bg-emerald-400",
    BOOKING_IN_PROGRESS: "bg-amber-400",
    BOOKED: "bg-cyan-400",
    COMPLETED: "bg-slate-400",
    ABANDONED: "bg-red-400",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-slate-900">WhatsApp Conversations</h1>
        <span className="text-sm text-slate-600 ml-2">{conversations.length} total</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-200px)]">
        {/* Conversation List */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-600" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-8 text-center">
              <MessageCircle className="w-10 h-10 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500 text-sm">No conversations yet.</p>
              <p className="text-slate-600 text-xs mt-1">Patient messages will appear here.</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {conversations.map((c) => (
                <button key={c.id} onClick={() => openChat(c.id)}
                  className={`w-full text-left p-4 hover:bg-slate-100 transition-colors ${
                    selected?.id === c.id ? "bg-emerald-50" : ""
                  }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="relative">
                        <div className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center">
                          <User className="w-5 h-5 text-slate-600" />
                        </div>
                        <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${statusColor[c.status] || "bg-slate-400"}`} />
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-sm text-slate-900 truncate">
                          {c.patient_name || c.patient_phone}
                        </div>
                        <div className="text-xs text-slate-500 truncate">
                          {c.treatment_interest || "New enquiry"}
                        </div>
                        <div className="text-xs text-slate-600 mt-0.5">
                          {c.message_count} msgs · {c.source}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-600 shrink-0 mt-1" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Chat Viewer */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 flex flex-col">
          {chatLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-600" />
            </div>
          ) : !selected ? (
            <div className="flex-1 flex items-center justify-center text-slate-600">
              <div className="text-center">
                <MessageCircle className="w-12 h-12 mx-auto mb-2 text-slate-700" />
                <p>Select a conversation to view</p>
              </div>
            </div>
          ) : (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-900">
                    {selected.patient_name || selected.patient_phone}
                  </div>
                  <div className="text-xs text-slate-600 flex items-center gap-2">
                    <Phone className="w-3 h-3" /> {selected.patient_phone}
                    {selected.treatment_interest && (
                      <> · {selected.treatment_interest}</>
                    )}
                  </div>
                </div>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  selected.status === "BOOKED" ? "bg-emerald-50 text-emerald-600" : "bg-white/5 text-slate-500"
                }`}>
                  {selected.status === "BOOKED" && <CheckCircle2 className="w-3 h-3 mr-1" />}
                  {selected.status}
                </span>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#FAFAF8]">
                {(selected.messages || []).map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === "assistant" ? "justify-start" : "justify-end"}`}>
                    <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                      msg.role === "assistant"
                        ? "bg-white border border-slate-200 text-slate-800"
                        : "bg-emerald-600 text-white"
                    }`}>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      <div className={`text-[10px] mt-1 ${
                        msg.role === "assistant" ? "text-slate-600" : "text-slate-900/60"
                      }`}>
                        {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer note */}
              <div className="p-3 border-t border-slate-200 text-center text-xs text-slate-600">
                AI Receptionist handles this conversation automatically
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
