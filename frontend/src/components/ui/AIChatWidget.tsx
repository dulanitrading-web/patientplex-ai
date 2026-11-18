"use client";

import { useState, useEffect, useRef } from "react";
import {
  MessageCircle, X, Send, Loader2, Sparkles, Calendar,
  TrendingUp, IndianRupee, HelpCircle, FileText, Users,
  Megaphone, ChevronDown,
} from "lucide-react";
import { sendChatMessage, getChatSuggestions } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  data?: Record<string, unknown>;
}

interface Suggestion {
  text: string;
  icon: string;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  calendar: <Calendar className="w-3.5 h-3.5" />,
  "trending-up": <TrendingUp className="w-3.5 h-3.5" />,
  "indian-rupee": <IndianRupee className="w-3.5 h-3.5" />,
  users: <Users className="w-3.5 h-3.5" />,
  "message-circle": <MessageCircle className="w-3.5 h-3.5" />,
  "file-text": <FileText className="w-3.5 h-3.5" />,
  "help-circle": <HelpCircle className="w-3.5 h-3.5" />,
  megaphone: <Megaphone className="w-3.5 h-3.5" />,
};

export default function AIChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load persisted messages from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("pp_chat_messages");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) })));
          return;
        }
      }
    } catch { /* ignore */ }
  }, []);

  // Save messages to localStorage when they change
  useEffect(() => {
    if (messages.length > 1) {
      try {
        // Keep last 20 messages to avoid localStorage bloat
        const toSave = messages.slice(-20);
        localStorage.setItem("pp_chat_messages", JSON.stringify(toSave));
      } catch { /* ignore */ }
    }
  }, [messages]);

  useEffect(() => {
    if (open && messages.length === 0) {
      // First time — show welcome and load suggestions
      loadSuggestions();
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content: "Hi! 👋 I'm your PatientPlex AI assistant. Ask me about appointments, ad performance, revenue — or anything about your clinic.",
          timestamp: new Date(),
        },
      ]);
    }
    if (open && messages.length > 0 && suggestions.length === 0) {
      loadSuggestions();
    }
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadSuggestions() {
    try {
      const data = await getChatSuggestions();
      setSuggestions(data.suggestions || []);
    } catch {
      // Use defaults
      setSuggestions([
        { text: "How many appointments today?", icon: "calendar" },
        { text: "How are my ads performing?", icon: "trending-up" },
        { text: "Generate a report", icon: "file-text" },
        { text: "What can you help with?", icon: "help-circle" },
      ]);
    }
  }

  async function handleSend(text?: string) {
    const msg = (text || input).trim();
    if (!msg || sending) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: msg,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      // Send conversation history for context
      const historyForApi = messages.slice(-8).map((m) => ({
        role: m.role === "user" ? "user" : "assistant",
        content: m.content,
      }));
      const data = await sendChatMessage(msg, historyForApi);
      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: data.reply || "Sorry, I couldn't process that. Please try again.",
        timestamp: new Date(),
        data: data.data,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I'm having trouble connecting. Please try again in a moment.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // Format markdown-lite: **bold**, bullet points, line breaks
  function formatContent(text: string) {
    return text.split("\n").map((line, i) => {
      // Bold
      let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Bullet points
      if (formatted.startsWith("• ") || formatted.startsWith("- ")) {
        formatted = `<span class="text-emerald-500 mr-1">•</span>${formatted.slice(2)}`;
        return <div key={i} className="flex items-start gap-0 pl-2 py-0.5" dangerouslySetInnerHTML={{ __html: formatted }} />;
      }
      if (formatted.trim() === "") return <div key={i} className="h-2" />;
      return <div key={i} className="py-0.5" dangerouslySetInnerHTML={{ __html: formatted }} />;
    });
  }

  return (
    <>
      {/* Floating button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/30 flex items-center justify-center transition-all hover:scale-105 active:scale-95"
          aria-label="Open AI assistant"
        >
          <Sparkles className="w-6 h-6" />
        </button>
      )}

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-32px)] h-[560px] max-h-[calc(100vh-100px)] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <div className="text-sm font-semibold">PatientPlex AI</div>
                <div className="text-[10px] text-emerald-100">Your clinic assistant</div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="p-1.5 rounded-lg hover:bg-white/10 transition"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-emerald-600 text-white rounded-br-sm"
                      : "bg-slate-100 text-slate-800 rounded-bl-sm"
                  }`}
                >
                  {msg.role === "assistant" ? formatContent(msg.content) : msg.content}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-slate-100 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions — show when few messages */}
          {messages.length <= 2 && suggestions.length > 0 && !sending && (
            <div className="px-4 pb-2 flex flex-wrap gap-1.5 shrink-0">
              {suggestions.slice(0, 4).map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(s.text)}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-full hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition"
                >
                  {ICON_MAP[s.icon] || <MessageCircle className="w-3.5 h-3.5" />}
                  {s.text.length > 35 ? s.text.slice(0, 35) + "…" : s.text}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="px-3 py-2.5 border-t border-slate-100 shrink-0">
            <div className="flex items-center gap-2 bg-slate-50 rounded-xl px-3 py-1.5 border border-slate-200 focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-500/20 transition">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about your clinic..."
                className="flex-1 bg-transparent text-sm text-slate-900 placeholder-slate-400 outline-none py-1.5"
                disabled={sending}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || sending}
                className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-100 disabled:opacity-30 disabled:hover:bg-transparent transition"
                aria-label="Send message"
              >
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
