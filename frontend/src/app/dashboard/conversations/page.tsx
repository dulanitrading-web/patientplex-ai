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
    ACTIVE: "bg-green-400",
    BOOKING_IN_PROGRESS: "bg-yellow-400",
    BOOKED: "bg-blue-400",
    COMPLETED: "bg-gray-400",
    ABANDONED: "bg-red-400",
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-3">
          <Link href="/dashboard" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-[#0B2545]">WhatsApp Conversations</h1>
          <span className="text-sm text-gray-400 ml-2">{conversations.length} total</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-140px)]">
          {/* Conversation List */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-y-auto">
            {loading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            ) : conversations.length === 0 ? (
              <div className="p-8 text-center">
                <MessageCircle className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No conversations yet.</p>
                <p className="text-gray-400 text-xs mt-1">Patient messages will appear here.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {conversations.map((c) => (
                  <button key={c.id} onClick={() => openChat(c.id)}
                    className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                      selected?.id === c.id ? "bg-blue-50" : ""
                    }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="relative">
                          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-gray-400" />
                          </div>
                          <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${statusColor[c.status] || "bg-gray-400"}`} />
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium text-sm text-[#0B2545] truncate">
                            {c.patient_name || c.patient_phone}
                          </div>
                          <div className="text-xs text-gray-500 truncate">
                            {c.treatment_interest || "New enquiry"}
                          </div>
                          <div className="text-xs text-gray-400 mt-0.5">
                            {c.message_count} msgs · {c.source}
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-300 shrink-0 mt-1" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Chat Viewer */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 flex flex-col">
            {chatLoading ? (
              <div className="flex-1 flex items-center justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            ) : !selected ? (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-200" />
                  <p>Select a conversation to view</p>
                </div>
              </div>
            ) : (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-[#0B2545]">
                      {selected.patient_name || selected.patient_phone}
                    </div>
                    <div className="text-xs text-gray-500 flex items-center gap-2">
                      <Phone className="w-3 h-3" /> {selected.patient_phone}
                      {selected.treatment_interest && (
                        <> · {selected.treatment_interest}</>
                      )}
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    selected.status === "BOOKED" ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-600"
                  }`}>
                    {selected.status === "BOOKED" && <CheckCircle2 className="w-3 h-3 mr-1" />}
                    {selected.status}
                  </span>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                  {(selected.messages || []).map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "assistant" ? "justify-start" : "justify-end"}`}>
                      <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                        msg.role === "assistant"
                          ? "bg-white border border-gray-200 text-gray-800"
                          : "bg-[#0B2545] text-white"
                      }`}>
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                        <div className={`text-[10px] mt-1 ${
                          msg.role === "assistant" ? "text-gray-400" : "text-white/60"
                        }`}>
                          {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Footer note */}
                <div className="p-3 border-t border-gray-100 text-center text-xs text-gray-400">
                  AI Receptionist handles this conversation automatically
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
