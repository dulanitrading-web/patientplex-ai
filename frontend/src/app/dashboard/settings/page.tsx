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
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
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
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-[#0B2545]">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage your clinic profile, integrations, and subscription.</p>
      </div>

      {/* Profile Section */}
      <Card>
        <SectionHeader icon={<User className="w-5 h-5" />} title="Profile" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <InfoField label="Full Name" value={doctor?.full_name} />
          <InfoField label="Email" value={doctor?.email} />
          <InfoField label="Phone" value={doctor?.phone} />
          <InfoField label="Member Since" value={doctor?.created_at ? new Date(doctor.created_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" }) : undefined} />
        </div>
        <p className="text-xs text-gray-400 mt-4">Profile editing is not available yet. Contact support to update your details.</p>
      </Card>

      {/* Clinic Details */}
      <Card>
        <SectionHeader icon={<Building2 className="w-5 h-5" />} title="Clinic Details" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <InfoField label="Clinic Name" value={doctor?.clinic_name} />
          <InfoField label="Specialty" value={doctor?.specialty ? formatSpecialty(doctor.specialty) : undefined} />
          <InfoField label="City" value={doctor?.city} />
          <InfoField label="State" value={doctor?.state} />
          <InfoField label="Address" value={doctor?.clinic_address} className="sm:col-span-2" />
        </div>
        {doctor?.services && doctor.services.length > 0 && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-500 mb-2">Services</label>
            <div className="flex flex-wrap gap-2">
              {doctor.services.map((s) => (
                <span key={s} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Integration Status */}
      <Card>
        <SectionHeader icon={<Link2 className="w-5 h-5" />} title="Integration Status" />
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
      </Card>

      {/* Subscription */}
      <Card>
        <SectionHeader icon={<CreditCard className="w-5 h-5" />} title="Subscription" />
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
            <p className="text-sm text-gray-500">No active subscription. Start a free trial from the <a href="/dashboard/billing" className="text-blue-600 hover:underline">Billing</a> page.</p>
          </div>
        )}
      </Card>

      {/* Danger Zone */}
      <Card className="!border-red-200">
        <SectionHeader icon={<AlertTriangle className="w-5 h-5 text-red-500" />} title="Danger Zone" className="text-red-600" />
        <p className="text-sm text-gray-500 mt-2">Once you delete your account, there is no going back. All data will be permanently removed.</p>
        <div className="mt-4">
          <Button variant="danger" size="sm" disabled>
            Delete Account
          </Button>
          <p className="text-xs text-gray-400 mt-2">Account deletion is currently disabled. Contact support at support@patientplex.ai.</p>
        </div>
      </Card>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function SectionHeader({ icon, title, className }: { icon: React.ReactNode; title: string; className?: string }) {
  return (
    <h3 className={`font-semibold text-[#0B2545] flex items-center gap-2 ${className || ""}`}>
      {icon} {title}
    </h3>
  );
}

function InfoField({ label, value, className }: { label: string; value?: string | null; className?: string }) {
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-500">{label}</label>
      <p className="mt-0.5 text-sm text-gray-900">{value || <span className="text-gray-300">Not set</span>}</p>
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
    connected: { icon: <CheckCircle2 className="w-4 h-4 text-green-500" />, label: "Connected", cls: "bg-green-50 text-green-700" },
    pending: { icon: <Clock className="w-4 h-4 text-yellow-500" />, label: "Pending", cls: "bg-yellow-50 text-yellow-700" },
    not_connected: { icon: <XCircle className="w-4 h-4 text-gray-400" />, label: "Not Connected", cls: "bg-gray-100 text-gray-500" },
    coming_soon: { icon: <Clock className="w-4 h-4 text-blue-400" />, label: "Coming Soon", cls: "bg-blue-50 text-blue-600" },
  };
  const cfg = statusConfig[status];

  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-3">
        <div className="text-gray-400">{icon}</div>
        <div>
          <div className="text-sm font-medium text-gray-900">{name}</div>
          <div className="text-xs text-gray-500">{detail}</div>
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
