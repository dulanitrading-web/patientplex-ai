"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import clsx from "clsx";
import {
  Stethoscope,
  Smile,
  Bone,
  Eye,
  Baby,
  Brain,
  Heart,
  Ear,
  Scissors,
  Activity,
  Check,
  Plus,
  X,
  MapPin,
  IndianRupee,
  Zap,
  MessageCircle,
  Calendar,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
} from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import {
  getSpecialties,
  updateStep1,
  updateStep2,
  updateStep3,
  updateStep4,
  getGoogleCalendarUrl,
  completeOnboarding,
  getOnboardingStatus,
  ApiError,
} from "@/lib/api";

// ---------- Types ----------

interface Specialty {
  id: string;
  name: string;
  icon: string;
  default_services: string[];
}

interface Service {
  name: string;
  enabled: boolean;
}

// ---------- Fallback specialties ----------

const FALLBACK_SPECIALTIES: Specialty[] = [
  { id: "dentist", name: "Dentist", icon: "smile", default_services: ["Teeth Cleaning", "Root Canal", "Teeth Whitening", "Dental Implants", "Braces / Orthodontics", "Cavity Filling"] },
  { id: "dermatologist", name: "Dermatologist", icon: "sparkle", default_services: ["Acne Treatment", "Skin Whitening", "Hair Loss Treatment", "Laser Treatment", "Anti-Aging Therapy", "Scar Removal"] },
  { id: "orthopedic", name: "Orthopedic", icon: "bone", default_services: ["Joint Replacement", "Fracture Treatment", "Sports Injury", "Spine Treatment", "Arthroscopy", "Physiotherapy Referral"] },
  { id: "ophthalmologist", name: "Eye Specialist", icon: "eye", default_services: ["Cataract Surgery", "LASIK", "Glaucoma Treatment", "Retina Treatment", "Eye Check-up", "Contact Lens Fitting"] },
  { id: "pediatrician", name: "Pediatrician", icon: "baby", default_services: ["Vaccination", "Growth Monitoring", "Newborn Care", "Child Nutrition", "Fever / Infection", "Developmental Screening"] },
  { id: "neurologist", name: "Neurologist", icon: "brain", default_services: ["Migraine Treatment", "Epilepsy Management", "Stroke Rehab", "Nerve Conduction", "Memory Clinic", "Back Pain"] },
  { id: "cardiologist", name: "Cardiologist", icon: "heart", default_services: ["ECG / Echo", "Blood Pressure", "Angiography", "Heart Check-up", "Cholesterol Management", "Pacemaker"] },
  { id: "ent", name: "ENT Specialist", icon: "ear", default_services: ["Sinus Treatment", "Hearing Test", "Tonsil Surgery", "Ear Cleaning", "Snoring / Sleep Apnea", "Voice Disorders"] },
  { id: "plastic_surgeon", name: "Plastic Surgeon", icon: "scissors", default_services: ["Rhinoplasty", "Liposuction", "Hair Transplant", "Facelift", "Scar Revision", "Botox / Fillers"] },
  { id: "general", name: "General Physician", icon: "activity", default_services: ["General Check-up", "Fever / Cold", "Diabetes Management", "Thyroid Treatment", "Blood Tests", "Health Screening"] },
];

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  smile: Smile,
  sparkle: Stethoscope,
  bone: Bone,
  eye: Eye,
  baby: Baby,
  brain: Brain,
  heart: Heart,
  ear: Ear,
  scissors: Scissors,
  activity: Activity,
};

// ---------- Toast component ----------

function Toast({ message, type, onClose }: { message: string; type: "error" | "success"; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div className={clsx("toast", type === "error" ? "bg-coral" : "bg-teal")}>
      <div className="flex items-center gap-2">
        {type === "error" ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
        {message}
        <button onClick={onClose} className="ml-2 hover:opacity-80">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ---------- Step labels ----------

const STEPS = [
  { num: 1, label: "Specialty", icon: Stethoscope },
  { num: 2, label: "Location", icon: MapPin },
  { num: 3, label: "Budget", icon: IndianRupee },
  { num: 4, label: "Connect", icon: Zap },
];

// ---------- Main component ----------

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "error" | "success" } | null>(null);

  // Step 1
  const [specialties, setSpecialties] = useState<Specialty[]>(FALLBACK_SPECIALTIES);
  const [selectedSpecialty, setSelectedSpecialty] = useState<string | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [newService, setNewService] = useState("");

  // Step 2
  const [clinicName, setClinicName] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [geoRadius, setGeoRadius] = useState(5);

  // Step 3
  const [budget, setBudget] = useState(15000);

  // Step 4
  const [whatsappNumber, setWhatsappNumber] = useState("");
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [connectingCalendar, setConnectingCalendar] = useState(false);

  // Load specialties from API
  useEffect(() => {
    getSpecialties()
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setSpecialties(data);
        }
      })
      .catch(() => {
        // Use fallback
      });
  }, []);

  // Load onboarding status
  useEffect(() => {
    getOnboardingStatus()
      .then((data) => {
        if (data.current_step) {
          setCurrentStep(data.current_step);
        }
        if (data.completed) {
          router.push("/dashboard");
        }
      })
      .catch(() => {
        // Not authenticated or no status — stay on step 1
      });
  }, [router]);

  // When specialty selected, populate services
  useEffect(() => {
    if (selectedSpecialty) {
      const spec = specialties.find((s) => s.id === selectedSpecialty);
      if (spec) {
        setServices(spec.default_services.map((s) => ({ name: s, enabled: true })));
      }
    }
  }, [selectedSpecialty, specialties]);

  function showToast(message: string, type: "error" | "success" = "error") {
    setToast({ message, type });
  }

  function toggleService(index: number) {
    setServices((prev) =>
      prev.map((s, i) => (i === index ? { ...s, enabled: !s.enabled } : s))
    );
  }

  function addCustomService() {
    const trimmed = newService.trim();
    if (!trimmed) return;
    if (services.some((s) => s.name.toLowerCase() === trimmed.toLowerCase())) {
      showToast("This service already exists");
      return;
    }
    setServices((prev) => [...prev, { name: trimmed, enabled: true }]);
    setNewService("");
  }

  // Budget estimates
  const estimatedClicks = Math.round(budget / 90);
  const estimatedEnquiries = Math.round(estimatedClicks * 0.08);
  const estimatedAppointments = Math.round(estimatedEnquiries * 0.35);

  // Format currency
  function formatINR(n: number): string {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
  }

  // Validation
  function validateStep(): boolean {
    switch (currentStep) {
      case 1:
        if (!selectedSpecialty) { showToast("Please select a specialty"); return false; }
        if (!services.some((s) => s.enabled)) { showToast("Please enable at least one service"); return false; }
        return true;
      case 2:
        if (!clinicName.trim()) { showToast("Please enter your clinic name"); return false; }
        if (!address.trim()) { showToast("Please enter your address"); return false; }
        if (!city.trim()) { showToast("Please enter your city"); return false; }
        if (!state.trim()) { showToast("Please enter your state"); return false; }
        if (!pincode.trim() || !/^\d{6}$/.test(pincode.trim())) { showToast("Please enter a valid 6-digit pincode"); return false; }
        return true;
      case 3:
        if (budget < 5000) { showToast("Minimum budget is Rs. 5,000"); return false; }
        return true;
      case 4:
        if (!whatsappNumber.trim() || whatsappNumber.replace(/\D/g, "").length < 10) {
          showToast("Please enter a valid WhatsApp number");
          return false;
        }
        return true;
      default:
        return true;
    }
  }

  // Step submission
  const handleNext = useCallback(async () => {
    if (!validateStep()) return;

    setLoading(true);
    try {
      switch (currentStep) {
        case 1:
          await updateStep1({ specialty_id: selectedSpecialty!, services });
          break;
        case 2:
          await updateStep2({ clinic_name: clinicName, address, city, state, pincode, geo_radius_km: geoRadius });
          break;
        case 3:
          await updateStep3({ monthly_budget: budget });
          break;
        case 4:
          await updateStep4({ whatsapp_number: `+91${whatsappNumber.replace(/\D/g, "")}`, google_calendar_connected: calendarConnected });
          await completeOnboarding();
          showToast("Setup complete! Redirecting...", "success");
          setTimeout(() => router.push("/dashboard"), 1500);
          return;
      }
      setCurrentStep((s) => s + 1);
    } catch (err) {
      if (err instanceof ApiError) {
        showToast(err.message);
      } else {
        // If API is unavailable, allow navigation for demo
        showToast("API unavailable — continuing in demo mode", "success");
        if (currentStep === 4) {
          setTimeout(() => router.push("/dashboard"), 1500);
          return;
        }
        setCurrentStep((s) => s + 1);
      }
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep, selectedSpecialty, services, clinicName, address, city, state, pincode, geoRadius, budget, whatsappNumber, calendarConnected, router]);

  async function handleConnectCalendar() {
    setConnectingCalendar(true);
    try {
      const data = await getGoogleCalendarUrl();
      if (data.url) {
        window.open(data.url, "_blank");
        // After opening, we check periodically (simplified)
        setCalendarConnected(true);
        showToast("Calendar authorization started. Complete it in the new tab.", "success");
      }
    } catch {
      showToast("Could not get calendar link. You can connect later from the dashboard.");
    } finally {
      setConnectingCalendar(false);
    }
  }

  return (
    <div className="min-h-screen gradient-hero">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* Header */}
      <div className="pt-6 pb-4 px-4">
        <div className="flex items-center justify-center gap-2">
          <div className="w-8 h-8 bg-electric rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="text-white text-xl font-bold">PatientPlex AI</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="max-w-2xl mx-auto px-4 mb-8">
        <div className="flex items-center justify-between">
          {STEPS.map((step, i) => {
            const done = currentStep > step.num;
            const active = currentStep === step.num;
            return (
              <div key={step.num} className="flex items-center flex-1 last:flex-none">
                <div className="flex flex-col items-center">
                  <div
                    className={clsx(
                      "w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300",
                      done && "bg-green-500 text-white",
                      active && "bg-white text-navy shadow-lg scale-110",
                      !done && !active && "bg-white/20 text-white/60"
                    )}
                  >
                    {done ? <Check className="w-5 h-5" /> : step.num}
                  </div>
                  <span
                    className={clsx(
                      "text-xs mt-1.5 font-medium hidden sm:block",
                      active ? "text-white" : "text-white/50"
                    )}
                  >
                    {step.label}
                  </span>
                </div>
                {i < STEPS.length - 1 && (
                  <div className="flex-1 mx-2 sm:mx-4 mt-[-20px] sm:mt-0">
                    <div className="h-0.5 rounded-full bg-white/20">
                      <div
                        className="h-0.5 rounded-full bg-green-400 transition-all duration-500"
                        style={{ width: done ? "100%" : "0%" }}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step content card */}
      <div className="max-w-2xl mx-auto px-4 pb-12">
        <div className="card-elevated animate-fade-in">
          {/* ---------- STEP 1: Specialty ---------- */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-navy mb-1">What&apos;s your specialty?</h2>
              <p className="text-gray-500 mb-6">Select your medical specialty and the services you offer.</p>

              {/* Specialty grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                {specialties.map((spec) => {
                  const Icon = ICON_MAP[spec.icon] || Stethoscope;
                  const selected = selectedSpecialty === spec.id;
                  return (
                    <button
                      key={spec.id}
                      onClick={() => setSelectedSpecialty(spec.id)}
                      className={clsx(
                        "flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md",
                        selected
                          ? "border-electric bg-electric/5 shadow-md"
                          : "border-gray-200 hover:border-gray-300 bg-white"
                      )}
                    >
                      <div className={clsx("w-10 h-10 rounded-lg flex items-center justify-center", selected ? "bg-electric/10" : "bg-gray-100")}>
                        <Icon className={clsx("w-5 h-5", selected ? "text-electric" : "text-gray-500")} />
                      </div>
                      <span className={clsx("text-sm font-medium", selected ? "text-electric" : "text-gray-700")}>
                        {spec.name}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Services checklist */}
              {selectedSpecialty && services.length > 0 && (
                <div className="border border-gray-200 rounded-xl p-4 animate-fade-in">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    Services you offer
                  </h3>
                  <div className="space-y-2 mb-4">
                    {services.map((svc, i) => (
                      <label
                        key={svc.name}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <button
                          type="button"
                          onClick={() => toggleService(i)}
                          className={clsx(
                            "w-5 h-5 rounded flex items-center justify-center border-2 transition-all",
                            svc.enabled
                              ? "bg-electric border-electric"
                              : "border-gray-300 bg-white"
                          )}
                        >
                          {svc.enabled && <Check className="w-3 h-3 text-white" />}
                        </button>
                        <span className={clsx("text-sm", svc.enabled ? "text-gray-900" : "text-gray-400")}>
                          {svc.name}
                        </span>
                      </label>
                    ))}
                  </div>

                  {/* Add custom service */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newService}
                      onChange={(e) => setNewService(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustomService())}
                      placeholder="Add custom service..."
                      className="input-base flex-1 text-sm"
                    />
                    <button
                      type="button"
                      onClick={addCustomService}
                      className="p-2.5 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <Plus className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ---------- STEP 2: Location ---------- */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-navy mb-1">Where&apos;s your clinic?</h2>
              <p className="text-gray-500 mb-6">We&apos;ll target patients near your location.</p>

              <div className="space-y-4">
                <Input
                  label="Clinic Name"
                  placeholder="Sharma Dental Clinic"
                  value={clinicName}
                  onChange={(e) => setClinicName(e.target.value)}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Full Address
                  </label>
                  <textarea
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="123, MG Road, Near City Mall..."
                    rows={2}
                    className="input-base resize-none"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <Input
                    label="City"
                    placeholder="Hyderabad"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                  <Input
                    label="State"
                    placeholder="Telangana"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                  />
                  <Input
                    label="Pincode"
                    placeholder="500032"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  />
                </div>

                {/* Geo-radius slider */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">
                      Ad targeting radius
                    </label>
                    <span className="text-sm font-bold text-electric">
                      {geoRadius} km
                    </span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={20}
                    value={geoRadius}
                    onChange={(e) => setGeoRadius(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer accent-electric"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>1 km</span>
                    <span>20 km</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-electric" />
                    Patients within {geoRadius} km will see your ads
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ---------- STEP 3: Budget ---------- */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-navy mb-1">Set your monthly budget</h2>
              <p className="text-gray-500 mb-6">How much would you like to spend on patient acquisition?</p>

              {/* Budget display */}
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-navy">{formatINR(budget)}</div>
                <div className="text-sm text-gray-500 mt-1">per month</div>
              </div>

              {/* Slider */}
              <div className="mb-8">
                <input
                  type="range"
                  min={5000}
                  max={100000}
                  step={1000}
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer accent-electric"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>{formatINR(5000)}</span>
                  <span>{formatINR(100000)}</span>
                </div>
              </div>

              {/* Estimates */}
              <div className="bg-gradient-to-br from-navy/5 to-teal/5 rounded-xl p-5 border border-gray-100">
                <h3 className="text-sm font-semibold text-navy mb-4">
                  At {formatINR(budget)}/month, you can expect approximately:
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-electric">~{estimatedClicks}</div>
                    <div className="text-xs text-gray-500 mt-1">clicks/month</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-teal">~{estimatedEnquiries}</div>
                    <div className="text-xs text-gray-500 mt-1">enquiries</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-amber">~{estimatedAppointments}</div>
                    <div className="text-xs text-gray-500 mt-1">appointments</div>
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-4 leading-relaxed border-t border-gray-200 pt-3">
                  Actual results vary. These are planning estimates based on market averages (avg. CPC of Rs. 90, 8% conversion to enquiry, 35% booking rate).
                </p>
              </div>
            </div>
          )}

          {/* ---------- STEP 4: Connect ---------- */}
          {currentStep === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-navy mb-1">Connect your channels</h2>
              <p className="text-gray-500 mb-6">Link your WhatsApp and calendar for seamless patient booking.</p>

              <div className="space-y-5">
                {/* WhatsApp */}
                <div className="border border-gray-200 rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <MessageCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-navy">WhatsApp Business</h3>
                      <p className="text-xs text-gray-500">Patients will reach you here</p>
                    </div>
                    {whatsappNumber.replace(/\D/g, "").length >= 10 && (
                      <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
                    )}
                  </div>
                  <div className="flex gap-2">
                    <div className="flex items-center bg-gray-100 rounded-lg px-3 text-sm text-gray-600 font-medium">
                      +91
                    </div>
                    <input
                      type="tel"
                      value={whatsappNumber}
                      onChange={(e) => setWhatsappNumber(e.target.value.replace(/\D/g, "").slice(0, 10))}
                      placeholder="9876543210"
                      className="input-base flex-1"
                    />
                  </div>
                </div>

                {/* Google Calendar */}
                <div className="border border-gray-200 rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={clsx("w-10 h-10 rounded-lg flex items-center justify-center", calendarConnected ? "bg-green-100" : "bg-blue-100")}>
                      <Calendar className={clsx("w-5 h-5", calendarConnected ? "text-green-600" : "text-blue-600")} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-navy">Google Calendar</h3>
                      <p className="text-xs text-gray-500">Auto-book appointments into your schedule</p>
                    </div>
                    {calendarConnected ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-300 ml-auto" />
                    )}
                  </div>

                  {calendarConnected ? (
                    <div className="bg-green-50 rounded-lg px-4 py-2.5 text-sm text-green-700 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      Calendar connected
                    </div>
                  ) : (
                    <div>
                      <Button
                        variant="ghost"
                        onClick={handleConnectCalendar}
                        loading={connectingCalendar}
                        className="w-full border border-gray-200 hover:bg-gray-50"
                      >
                        <Calendar className="w-4 h-4 mr-2" />
                        Connect Google Calendar
                      </Button>
                      <p className="text-xs text-gray-400 mt-2 text-center">
                        Optional — you can connect this later from the dashboard
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ---------- Navigation buttons ---------- */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
            {currentStep > 1 ? (
              <Button
                variant="ghost"
                onClick={() => setCurrentStep((s) => s - 1)}
                disabled={loading}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            ) : (
              <div />
            )}

            <Button onClick={handleNext} loading={loading} size="lg">
              {currentStep === 4 ? (
                <>
                  Complete Setup
                  <CheckCircle2 className="w-5 h-5 ml-2" />
                </>
              ) : (
                <>
                  Continue
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
