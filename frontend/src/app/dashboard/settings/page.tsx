"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
  User,
  Building2,
  Link2,
  CreditCard,
  AlertTriangle,
  Calendar,
  MessageCircle,
  BarChart3,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import { getMe, getSubscription } from "@/lib/api";

interface DoctorProfile {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  clinic_name: string | null;
  specialty: string | null;
  services: string[] | null;
  clinic_address: string | null;
  city: string | null;
  state: string | null;
  pincode: string | null;
  monthly_budget: number;
  currency: string;
  google_calendar_connected: boolean;
  whatsapp_number: string | null;
  whatsapp_verified: boolean;
  onboarding_completed: boolean;
  created_at: string;
}

interface SubscriptionData {
  id: string;
  plan: string;
  status: string;
  price_inr: number;
  trial_ends_at: string | null;
  current_period_end: string | null;
  conversations_used: number;
  conversations_limit: number;
  campaigns_used: number;
  campaigns_limit: number;
}

export default function SettingsPage() {
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [profile, subRes] = await Promise.allSettled([
          getMe(),
          getSubscription(),
        ]);
        if (profile.status === "fulfilled") setDoctor(profile.value);
        if (subRes.status === "fulfilled") setSubscription(subRes.value.subscription);
      } catch {
        /* use defaults */
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-slate-900" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600 text-sm mt-1">Manage your clinic profile, integrations, and subscription.</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <SectionHeader icon={<User className="w-5 h-5 text-black" />} title="Profile" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <InfoField label="Full Name" value={doctor?.full_name} />
          <InfoField label="Email" value={doctor?.email} />
          <InfoField label="Phone" value={doctor?.phone} />
          <InfoField label="Member Since" value={doctor?.created_at ? new Date(doctor.created_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" }) : undefined} />
        </div>
        <p className="text-xs text-slate-600 mt-4">Profile editing is not available yet. Contact support to update your details.</p>
      </div>

      {/* Clinic Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <SectionHeader icon={<Building2 className="w-5 h-5 text-slate-700" />} title="Clinic Details" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <InfoField label="Clinic Name" value={doctor?.clinic_name} />
          <InfoField label="Specialty" value={doctor?.specialty ? formatSpecialty(doctor.specialty) : undefined} />
          <InfoField label="City" value={doctor?.city} />
          <InfoField label="State" value={doctor?.state} />
          <InfoField label="Address" value={doctor?.clinic_address} className="sm:col-span-2" />
        </div>
        {doctor?.services && doctor.services.length > 0 && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-600 mb-2">Services</label>
            <div className="flex flex-wrap gap-2">
              {doctor.services.map((s) => (
                <span key={s} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-50 text-black">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Integration Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <SectionHeader icon={<Link2 className="w-5 h-5 text-slate-700" />} title="Integration Status" />
        <div className="space-y-3 mt-4">
          <IntegrationRow
            icon={<Calendar className="w-4 h-4" />}
            name="Google Calendar"
            status={doctor?.google_calendar_connected ? "connected" : "not_connected"}
            detail={doctor?.google_calendar_connected ? "Syncing appointments" : "Connect to sync appointments"}
          />
          <IntegrationRow
            icon={<MessageCircle className="w-4 h-4" />}
            name="WhatsApp"
            status={doctor?.whatsapp_number ? (doctor?.whatsapp_verified ? "connected" : "pending") : "not_connected"}
            detail={doctor?.whatsapp_number ? `${doctor.whatsapp_number}${doctor.whatsapp_verified ? "" : " (verification pending)"}` : "No number configured"}
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="Google Ads"
            status="coming_soon"
            detail="Direct account linking coming soon"
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="Meta Ads"
            status="coming_soon"
            detail="Direct account linking coming soon"
          />
        </div>
      </div>

      {/* Subscription */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <SectionHeader icon={<CreditCard className="w-5 h-5 text-amber-600" />} title="Subscription" />
        {subscription ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <InfoField label="Plan" value={formatPlanName(subscription.plan)} />
            <InfoField label="Status" value={formatStatus(subscription.status)} />
            <InfoField label="Price" value={subscription.price_inr === 0 ? "Free" : `₹${subscription.price_inr.toLocaleString("en-IN")}/mo`} />
            {subscription.trial_ends_at && (
              <InfoField label="Trial Ends" value={new Date(subscription.trial_ends_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" })} />
            )}
          </div>
        ) : (
          <div className="mt-4">
            <p className="text-sm text-slate-600">No active subscription. Start a free trial from the <a href="/dashboard/billing" className="text-black hover:text-slate-600">Billing</a> page.</p>
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-xl border border-red-500/20 p-5">
        <SectionHeader icon={<AlertTriangle className="w-5 h-5 text-red-600" />} title="Danger Zone" className="text-red-600" />
        <p className="text-sm text-slate-600 mt-2">Once you delete your account, there is no going back. All data will be permanently removed.</p>
        <div className="mt-4">
          <button disabled className="px-4 py-2 rounded-lg text-sm font-medium bg-red-50 text-red-600 cursor-not-allowed opacity-50">
            Delete Account
          </button>
          <p className="text-xs text-slate-600 mt-2">Account deletion is currently disabled. Contact support at support@patientplex.ai.</p>
        </div>
      </div>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function SectionHeader({ icon, title, className }: { icon: React.ReactNode; title: string; className?: string }) {
  return (
    <h3 className={`font-semibold text-slate-900 flex items-center gap-2 ${className || ""}`}>
      {icon} {title}
    </h3>
  );
}

function InfoField({ label, value, className }: { label: string; value?: string | null; className?: string }) {
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-slate-600">{label}</label>
      <p className="mt-0.5 text-sm text-slate-800">{value || <span className="text-slate-600">Not set</span>}</p>
    </div>
  );
}

function IntegrationRow({ icon, name, status, detail }: {
  icon: React.ReactNode;
  name: string;
  status: "connected" | "pending" | "not_connected" | "coming_soon";
  detail: string;
}) {
  const statusConfig = {
    connected: { icon: <CheckCircle2 className="w-4 h-4 text-black" />, label: "Connected", cls: "bg-slate-50 text-black" },
    pending: { icon: <Clock className="w-4 h-4 text-amber-600" />, label: "Pending", cls: "bg-amber-50 text-amber-600" },
    not_connected: { icon: <XCircle className="w-4 h-4 text-slate-600" />, label: "Not Connected", cls: "bg-white/5 text-slate-600" },
    coming_soon: { icon: <Clock className="w-4 h-4 text-slate-700" />, label: "Coming Soon", cls: "bg-slate-50 text-slate-700" },
  };
  const cfg = statusConfig[status];

  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-200 last:border-0">
      <div className="flex items-center gap-3">
        <div className="text-slate-600">{icon}</div>
        <div>
          <div className="text-sm font-medium text-slate-800">{name}</div>
          <div className="text-xs text-slate-600">{detail}</div>
        </div>
      </div>
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
        {cfg.icon} {cfg.label}
      </span>
    </div>
  );
}

function formatSpecialty(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatPlanName(plan: string): string {
  return plan.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
