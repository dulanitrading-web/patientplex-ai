"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  Calendar, Clock, MapPin, Phone, CheckCircle2, Loader2,
  ArrowLeft, ArrowRight, User, Stethoscope, Mail, ChevronLeft, ChevronRight,
} from "lucide-react";
import Logo from "@/components/Logo";
import {
  trackBookingPageView, trackTreatmentSelected, trackDateSelected,
  trackSlotSelected, trackBookingCompleted, trackFormStarted, trackBookingWhatsAppClick,
} from "@/lib/analytics";

const API = process.env.NEXT_PUBLIC_API_URL || "https://patientplex-ai-g7ce.onrender.com/api/v1";

interface DoctorProfile {
  slug: string;
  doctor_name: string;
  clinic_name: string;
  specialty: string;
  city: string;
  address: string;
  services: string[];
  logo: string | null;
  phone: string;
}

interface Slot {
  time: string;
  display: string;
  available: boolean;
}

type Step = "info" | "date" | "time" | "details" | "confirm" | "success";

export default function PublicBookingPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Booking flow
  const [step, setStep] = useState<Step>("info");
  const [selectedTreatment, setSelectedTreatment] = useState("");
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [patientName, setPatientName] = useState("");
  const [honeypot, setHoneypot] = useState(""); // Anti-bot: hidden field that bots fill
  const [patientPhone, setPatientPhone] = useState("");
  const [patientEmail, setPatientEmail] = useState("");
  const [booking, setBooking] = useState(false);
  const [bookingResult, setBookingResult] = useState<any>(null);

  // Date navigation
  const [weekStart, setWeekStart] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay() + 1); // Monday
    return d;
  });

  useEffect(() => {
    fetchDoctor();
  }, [slug]);

  async function fetchDoctor() {
    try {
      const res = await fetch(`${API}/public/book/${slug}`);
      if (!res.ok) throw new Error("Clinic not found");
      const data = await res.json();
      setDoctor(data);
      if (data.services?.length > 0) setSelectedTreatment(data.services[0]);
      trackBookingPageView(slug);
    } catch {
      setError("This booking page doesn't exist or has been removed.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchSlots(dateStr: string) {
    setLoadingSlots(true);
    try {
      const res = await fetch(`${API}/public/book/${slug}/availability?date=${dateStr}`);
      const data = await res.json();
      setSlots(data.slots || []);
    } catch {
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }

  async function handleBook() {
    if (!patientName.trim() || !patientPhone.trim()) return;
    if (honeypot) return; // Bot detected — silently reject
    setBooking(true);
    try {
      // Get UTM params from URL
      const urlParams = new URLSearchParams(window.location.search);
      const res = await fetch(`${API}/public/book/${slug}/book`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_name: patientName,
          patient_phone: patientPhone,
          patient_email: patientEmail || undefined,
          treatment: selectedTreatment,
          date: selectedDate,
          time: selectedTime,
          source: "Online Booking",
          utm_source: urlParams.get("utm_source") || undefined,
          utm_campaign: urlParams.get("utm_campaign") || undefined,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setBookingResult(data.appointment);
        setStep("success");
        trackBookingCompleted(slug, selectedTreatment);
      } else {
        setError(data.detail || "Booking failed. Please try again.");
      }
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setBooking(false);
    }
  }

  function getWeekDates(): { date: Date; dateStr: string; dayName: string; dayNum: number; isToday: boolean; isPast: boolean }[] {
    const dates = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    for (let i = 0; i < 7; i++) {
      const d = new Date(weekStart);
      d.setDate(weekStart.getDate() + i);
      dates.push({
        date: d,
        dateStr: d.toISOString().split("T")[0],
        dayName: d.toLocaleDateString("en-IN", { weekday: "short" }),
        dayNum: d.getDate(),
        isToday: d.toISOString().split("T")[0] === today.toISOString().split("T")[0],
        isPast: d < today,
      });
    }
    return dates;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (error && !doctor) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <Logo size={40} />
          <h1 className="text-xl font-bold text-slate-900 mt-4">Page Not Found</h1>
          <p className="text-slate-500 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  if (!doctor) return null;

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-4 py-3">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          {doctor.logo ? (
            <img src={doctor.logo} alt="" className="w-10 h-10 rounded-full object-cover" />
          ) : (
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
              <Stethoscope className="w-5 h-5 text-emerald-600" />
            </div>
          )}
          <div>
            <div className="font-semibold text-slate-900 text-sm">{doctor.clinic_name || doctor.doctor_name}</div>
            <div className="text-xs text-slate-500">{doctor.specialty} · {doctor.city}</div>
          </div>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-6">
        {/* Step: Info */}
        {step === "info" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Book an Appointment</h1>
              <p className="text-slate-500 mt-1">with {doctor.doctor_name} at {doctor.clinic_name}</p>
            </div>

            {doctor.address && (
              <div className="flex items-start gap-2 text-sm text-slate-600">
                <MapPin className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                {doctor.address}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">What do you need?</label>
              <div className="grid grid-cols-2 gap-2">
                {doctor.services.map((s) => (
                  <button
                    key={s}
                    onClick={() => setSelectedTreatment(s)}
                    className={`px-3 py-3 rounded-xl text-sm font-medium text-left transition border ${
                      selectedTreatment === s
                        ? "bg-emerald-50 border-emerald-300 text-emerald-700"
                        : "bg-white border-slate-200 text-slate-700 hover:border-emerald-200"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => { trackTreatmentSelected(selectedTreatment, slug); setStep("date"); }}
              disabled={!selectedTreatment}
              className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              Choose Date <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Step: Date + Time */}
        {step === "date" && (
          <div className="space-y-5">
            <button onClick={() => setStep("info")} className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>

            <div>
              <h2 className="text-xl font-bold text-slate-900">Pick a date & time</h2>
              <p className="text-sm text-slate-500 mt-0.5">{selectedTreatment} with {doctor.doctor_name}</p>
            </div>

            {/* Week calendar */}
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center justify-between mb-3">
                <button
                  onClick={() => { const d = new Date(weekStart); d.setDate(d.getDate() - 7); setWeekStart(d); }}
                  className="p-1 rounded hover:bg-slate-100"
                >
                  <ChevronLeft className="w-4 h-4 text-slate-500" />
                </button>
                <span className="text-sm font-medium text-slate-700">
                  {weekStart.toLocaleDateString("en-IN", { month: "long", year: "numeric" })}
                </span>
                <button
                  onClick={() => { const d = new Date(weekStart); d.setDate(d.getDate() + 7); setWeekStart(d); }}
                  className="p-1 rounded hover:bg-slate-100"
                >
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </button>
              </div>

              <div className="grid grid-cols-7 gap-1.5">
                {getWeekDates().map((d) => (
                  <button
                    key={d.dateStr}
                    onClick={() => {
                      if (!d.isPast && d.date.getDay() !== 0) {
                        setSelectedDate(d.dateStr);
                        setSelectedTime("");
                        fetchSlots(d.dateStr);
                      }
                    }}
                    disabled={d.isPast || d.date.getDay() === 0}
                    className={`flex flex-col items-center py-2 rounded-lg text-xs transition ${
                      selectedDate === d.dateStr
                        ? "bg-emerald-500 text-white"
                        : d.isToday
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : d.isPast || d.date.getDay() === 0
                        ? "text-slate-300 cursor-not-allowed"
                        : "text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    <span className="font-medium">{d.dayName}</span>
                    <span className={`text-lg font-bold mt-0.5 ${selectedDate === d.dateStr ? "text-white" : ""}`}>{d.dayNum}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Time slots */}
            {selectedDate && (
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">
                  Available times for {new Date(selectedDate + "T00:00").toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}
                </h3>
                {loadingSlots ? (
                  <div className="flex justify-center py-6">
                    <Loader2 className="w-5 h-5 animate-spin text-emerald-500" />
                  </div>
                ) : slots.filter((s) => s.available).length === 0 ? (
                  <p className="text-sm text-slate-400 py-4 text-center">No available slots on this date. Try another day.</p>
                ) : (
                  <div className="grid grid-cols-3 gap-2">
                    {slots.filter((s) => s.available).map((s) => (
                      <button
                        key={s.time}
                        onClick={() => { setSelectedTime(s.time); trackSlotSelected(s.time, slug); }}
                        className={`py-2.5 rounded-lg text-sm font-medium transition border ${
                          selectedTime === s.time
                            ? "bg-emerald-500 text-white border-emerald-500"
                            : "bg-white border-slate-200 text-slate-700 hover:border-emerald-300"
                        }`}
                      >
                        {s.display}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {selectedTime && (
              <button
                onClick={() => { trackFormStarted(slug); setStep("details"); }}
                className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition flex items-center justify-center gap-2"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        )}

        {/* Step: Patient details */}
        {step === "details" && (
          <div className="space-y-5">
            <button onClick={() => setStep("date")} className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>

            <div>
              <h2 className="text-xl font-bold text-slate-900">Your details</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                {selectedTreatment} · {new Date(selectedDate + "T00:00").toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" })} at {slots.find((s) => s.time === selectedTime)?.display}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Your Name *</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                    autoFocus
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number *</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="tel"
                    value={patientPhone}
                    onChange={(e) => setPatientPhone(e.target.value)}
                    placeholder="e.g. 9876543210"
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email (for confirmation)</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="email"
                    value={patientEmail}
                    onChange={(e) => setPatientEmail(e.target.value)}
                    placeholder="optional"
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>
              {/* Honeypot — invisible to humans, bots fill it */}
              <div className="absolute -left-[9999px]" aria-hidden="true">
                <input
                  type="text"
                  name="website_url"
                  tabIndex={-1}
                  autoComplete="off"
                  value={honeypot}
                  onChange={(e) => setHoneypot(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleBook}
              disabled={booking || !patientName.trim() || !patientPhone.trim()}
              className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {booking ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Booking...</>
              ) : (
                <><CheckCircle2 className="w-4 h-4" /> Confirm Booking</>
              )}
            </button>
          </div>
        )}

        {/* Step: Success */}
        {step === "success" && bookingResult && (
          <div className="text-center space-y-6 py-8">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Appointment Booked!</h2>
              <p className="text-slate-500 mt-1">You&apos;re all set. See you at the clinic.</p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 text-left space-y-3 max-w-sm mx-auto">
              <div className="flex items-center gap-2 text-sm">
                <Stethoscope className="w-4 h-4 text-emerald-500" />
                <span className="text-slate-500">Doctor:</span>
                <span className="font-medium text-slate-900">{bookingResult.doctor_name}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-emerald-500" />
                <span className="text-slate-500">Date:</span>
                <span className="font-medium text-slate-900">
                  {new Date(bookingResult.date + "T00:00").toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-emerald-500" />
                <span className="text-slate-500">Time:</span>
                <span className="font-medium text-slate-900">{bookingResult.time}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Stethoscope className="w-4 h-4 text-emerald-500" />
                <span className="text-slate-500">Treatment:</span>
                <span className="font-medium text-slate-900">{bookingResult.treatment}</span>
              </div>
              {bookingResult.address && (
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="w-4 h-4 text-emerald-500 mt-0.5" />
                  <span className="text-slate-500">Address:</span>
                  <span className="text-slate-700">{bookingResult.address}</span>
                </div>
              )}
              {bookingResult.phone && (
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="w-4 h-4 text-emerald-500" />
                  <span className="text-slate-500">Phone:</span>
                  <a href={`tel:${bookingResult.phone}`} className="text-emerald-600 font-medium">{bookingResult.phone}</a>
                </div>
              )}
            </div>

            {patientEmail && (
              <p className="text-sm text-slate-400">A confirmation email has been sent to {patientEmail}</p>
            )}

            <p className="text-xs text-slate-400 mt-4">Powered by PatientPlex AI</p>
          </div>
        )}

        {/* Trust signals — psychology-driven */}
        {step !== "success" && (
          <div className="mt-8 pt-6 border-t border-slate-200">
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1">🔒 Secure Booking</span>
              <span className="flex items-center gap-1">✅ Instant Confirmation</span>
              <span className="flex items-center gap-1">📱 Free Reminders</span>
            </div>
            <p className="text-center text-[10px] text-slate-300 mt-3">
              No charges for booking. Cancel or reschedule anytime.
            </p>
          </div>
        )}
      </div>

      {/* WhatsApp Floating Button — always visible */}
      {doctor.phone && step !== "success" && (
        <a
          href={`https://wa.me/91${doctor.phone.replace(/\D/g, "").slice(-10)}?text=${encodeURIComponent(`Hi, I'd like to book an appointment for ${selectedTreatment || "consultation"} with ${doctor.doctor_name}`)}`}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => trackBookingWhatsAppClick(slug)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-[#25D366] hover:bg-[#20BD5A] text-white shadow-lg shadow-green-500/30 flex items-center justify-center transition-all hover:scale-105 active:scale-95"
          aria-label="Chat on WhatsApp"
        >
          <svg viewBox="0 0 24 24" className="w-7 h-7 fill-current">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
          </svg>
        </a>
      )}
    </div>
  );
}
