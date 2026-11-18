"use client";

import { useState, useMemo } from "react";
import { ChevronLeft, ChevronRight, Clock, User } from "lucide-react";

interface CalendarAppointment {
  id: string;
  patient_name: string;
  patient_phone: string;
  treatment: string;
  date: string; // YYYY-MM-DD
  time: string; // HH:MM
  duration_minutes: number;
  status: string;
  notes: string | null;
}

interface CalendarViewProps {
  appointments: CalendarAppointment[];
  onSelectAppointment?: (apt: CalendarAppointment) => void;
  onDateChange?: (startDate: string, endDate: string) => void;
}

const HOURS = Array.from({ length: 13 }, (_, i) => i + 8); // 8AM - 8PM
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function getWeekDates(baseDate: Date): Date[] {
  const d = new Date(baseDate);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day; // Monday-based
  d.setDate(d.getDate() + diff);
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(d);
    date.setDate(d.getDate() + i);
    return date;
  });
}

function formatDate(d: Date): string {
  return d.toISOString().split("T")[0];
}

function isToday(d: Date): boolean {
  const now = new Date();
  return formatDate(d) === formatDate(now);
}

const STATUS_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  CONFIRMED: { bg: "bg-cyan-50", border: "border-l-cyan-500", text: "text-cyan-700" },
  REMINDED: { bg: "bg-amber-50", border: "border-l-amber-500", text: "text-amber-700" },
  ATTENDED: { bg: "bg-emerald-50", border: "border-l-emerald-500", text: "text-emerald-700" },
  NO_SHOW: { bg: "bg-red-50", border: "border-l-red-500", text: "text-red-700" },
  CANCELLED: { bg: "bg-slate-50", border: "border-l-slate-400", text: "text-slate-500" },
};

export default function CalendarView({ appointments, onSelectAppointment, onDateChange }: CalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<"week" | "day">("week");

  const weekDates = useMemo(() => getWeekDates(currentDate), [currentDate]);

  // Group appointments by date
  const appointmentsByDate = useMemo(() => {
    const map: Record<string, CalendarAppointment[]> = {};
    for (const apt of appointments) {
      if (!map[apt.date]) map[apt.date] = [];
      map[apt.date].push(apt);
    }
    return map;
  }, [appointments]);

  function navigate(direction: -1 | 1) {
    const d = new Date(currentDate);
    if (view === "week") {
      d.setDate(d.getDate() + direction * 7);
    } else {
      d.setDate(d.getDate() + direction);
    }
    setCurrentDate(d);
    if (onDateChange) {
      const week = getWeekDates(d);
      onDateChange(formatDate(week[0]), formatDate(week[6]));
    }
  }

  function goToToday() {
    setCurrentDate(new Date());
  }

  const displayDates = view === "week" ? weekDates : [currentDate];

  // Week label
  const weekLabel = view === "week"
    ? `${weekDates[0].toLocaleDateString("en-IN", { month: "short", day: "numeric" })} – ${weekDates[6].toLocaleDateString("en-IN", { month: "short", day: "numeric", year: "numeric" })}`
    : currentDate.toLocaleDateString("en-IN", { weekday: "long", month: "long", day: "numeric", year: "numeric" });

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Calendar Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <ChevronLeft className="w-4 h-4 text-slate-600" />
          </button>
          <button
            onClick={() => navigate(1)}
            className="p-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <ChevronRight className="w-4 h-4 text-slate-600" />
          </button>
          <h2 className="text-sm font-semibold text-slate-900">{weekLabel}</h2>
          <button
            onClick={goToToday}
            className="px-2.5 py-1 text-xs font-medium text-emerald-600 border border-emerald-200 rounded-md hover:bg-emerald-50 transition"
          >
            Today
          </button>
        </div>
        <div className="flex gap-1 bg-slate-100 rounded-lg p-0.5">
          <button
            onClick={() => setView("day")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition ${view === "day" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"}`}
          >
            Day
          </button>
          <button
            onClick={() => setView("week")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition ${view === "week" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"}`}
          >
            Week
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <div className={`min-w-[640px] ${view === "day" ? "max-w-2xl mx-auto" : ""}`}>
          {/* Day Headers */}
          <div className={`grid border-b border-slate-100 ${view === "week" ? "grid-cols-[60px_repeat(7,1fr)]" : "grid-cols-[60px_1fr]"}`}>
            <div className="p-2" /> {/* Time gutter */}
            {displayDates.map((d) => (
              <div
                key={formatDate(d)}
                className={`text-center py-2 ${isToday(d) ? "bg-emerald-50" : ""}`}
              >
                <div className="text-[10px] text-slate-400 uppercase font-medium">
                  {d.toLocaleDateString("en-IN", { weekday: "short" })}
                </div>
                <div className={`text-sm font-semibold ${isToday(d) ? "text-emerald-600" : "text-slate-900"}`}>
                  {d.getDate()}
                </div>
              </div>
            ))}
          </div>

          {/* Time Rows */}
          <div className={`relative grid ${view === "week" ? "grid-cols-[60px_repeat(7,1fr)]" : "grid-cols-[60px_1fr]"}`}>
            {HOURS.map((hour) => (
              <div key={hour} className="contents">
                {/* Time label */}
                <div className="text-[10px] text-slate-400 text-right pr-2 py-3 border-b border-slate-50 font-medium">
                  {hour > 12 ? `${hour - 12} PM` : hour === 12 ? "12 PM" : `${hour} AM`}
                </div>
                {/* Day columns */}
                {displayDates.map((d) => {
                  const dateKey = formatDate(d);
                  const hourAppts = (appointmentsByDate[dateKey] || []).filter((apt) => {
                    const h = parseInt(apt.time.split(":")[0], 10);
                    return h === hour;
                  });
                  return (
                    <div
                      key={`${dateKey}-${hour}`}
                      className={`min-h-[52px] border-b border-l border-slate-50 p-0.5 ${isToday(d) ? "bg-emerald-50/30" : ""}`}
                    >
                      {hourAppts.map((apt) => {
                        const colors = STATUS_COLORS[apt.status] || STATUS_COLORS.CONFIRMED;
                        return (
                          <button
                            key={apt.id}
                            onClick={() => onSelectAppointment?.(apt)}
                            className={`w-full text-left rounded-md p-1.5 mb-0.5 border-l-2 ${colors.bg} ${colors.border} hover:shadow-sm transition cursor-pointer`}
                          >
                            <div className={`text-[11px] font-medium ${colors.text} truncate`}>
                              {apt.time} · {apt.patient_name}
                            </div>
                            <div className="text-[10px] text-slate-500 truncate">
                              {apt.treatment}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
