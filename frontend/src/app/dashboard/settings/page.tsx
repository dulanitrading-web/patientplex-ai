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
import {
  getMe,
  getSubscription,
  getIntegrationStatus,
  getGoogleCalendarUrl,
  connectGoogleAds,
  disconnectGoogleAds,
  connectMetaAds,
  disconnectMetaAds,
  verifyWhatsApp,
  importGoogleAdsCampaigns,
  provisionTwilioNumber,
} from "@/lib/api";

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

interface IntegrationInfo {
  status: string;
  detail: string;
  has_campaigns?: boolean;
  credentials_configured?: boolean;
  number?: string;
  verified?: boolean;
}

export default function SettingsPage() {
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [integrations, setIntegrations] = useState<Record<string, IntegrationInfo> | null>(null);
  const [loading, setLoading] = useState(true);
  const [importingCampaigns, setImportingCampaigns] = useState(false);
  const [provisioningTwilio, setProvisioningTwilio] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [profile, subRes, intRes] = await Promise.allSettled([
          getMe(),
          getSubscription(),
          getIntegrationStatus(),
        ]);
        if (profile.status === "fulfilled") setDoctor(profile.value);
        if (subRes.status === "fulfilled") setSubscription(subRes.value.subscription);
        if (intRes.status === "fulfilled") setIntegrations(intRes.value);
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
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
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
        <SectionHeader icon={<User className="w-5 h-5 text-emerald-600" />} title="Profile" />
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
        <SectionHeader icon={<Building2 className="w-5 h-5 text-cyan-600" />} title="Clinic Details" />
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
                <span key={s} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-600">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Integration Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <SectionHeader icon={<Link2 className="w-5 h-5 text-violet-600" />} title="Integration Status" />
        <div className="space-y-3 mt-4">
          <IntegrationRow
            icon={<Calendar className="w-4 h-4" />}
            name="Google Calendar"
            status={mapIntegrationStatus(integrations?.google_calendar?.status)}
            detail={integrations?.google_calendar?.detail || "Connect to sync appointments"}
            onConnect={async () => {
              try {
                const data = await getGoogleCalendarUrl();
                if (data.auth_url) window.location.href = data.auth_url;
                else alert("Google Calendar OAuth not configured on server. Please ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in the backend environment.");
              } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : "Could not start Google Calendar connection";
                alert(msg);
              }
            }}
          />
          <IntegrationRow
            icon={<MessageCircle className="w-4 h-4" />}
            name="WhatsApp"
            status={mapIntegrationStatus(integrations?.whatsapp?.status)}
            detail={integrations?.whatsapp?.detail || "No number configured"}
            onConnect={async () => {
              try {
                const result = await verifyWhatsApp();
                alert(result.message || result.detail || "Verification sent!");
                window.location.reload();
              } catch { alert("WhatsApp verification failed"); }
            }}
            connectLabel="Verify"
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="Google Ads"
            status={mapIntegrationStatus(integrations?.google_ads?.status)}
            detail={integrations?.google_ads?.detail || "Connect your Google Ads account"}
            onConnect={async () => {
              try {
                const data = await connectGoogleAds();
                if (data.auth_url) window.location.href = data.auth_url;
              } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : "Could not start Google Ads connection";
                alert(msg);
              }
            }}
            onDisconnect={async () => {
              if (confirm("Disconnect Google Ads?")) {
                await disconnectGoogleAds();
                window.location.reload();
              }
            }}
            extraAction={["connected", "ready"].includes(mapIntegrationStatus(integrations?.google_ads?.status)) ? (
              <button
                onClick={async () => {
                  setImportingCampaigns(true);
                  try {
                    const result = await importGoogleAdsCampaigns();
                    alert(result.message || `Imported ${result.imported} campaigns`);
                    window.location.reload();
                  } catch (err: unknown) {
                    const msg = err instanceof Error ? err.message : "Failed to import campaigns";
                    alert(msg);
                  }
                  finally { setImportingCampaigns(false); }
                }}
                disabled={importingCampaigns}
                className="px-3 py-1 rounded-lg text-xs font-medium bg-cyan-500 text-white hover:bg-cyan-600 transition-colors disabled:opacity-50"
              >
                {importingCampaigns ? "Importing…" : "Import Campaigns"}
              </button>
            ) : undefined}
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="Meta Ads"
            status={mapIntegrationStatus(integrations?.meta_ads?.status)}
            detail={integrations?.meta_ads?.detail || "Connect your Meta Ads account"}
            onConnect={async () => {
              try {
                const data = await connectMetaAds();
                if (data.auth_url) window.location.href = data.auth_url;
              } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : "Could not start Meta Ads connection";
                alert(msg);
              }
            }}
            onDisconnect={async () => {
              if (confirm("Disconnect Meta Ads?")) {
                await disconnectMetaAds();
                window.location.reload();
              }
            }}
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="ChatGPT Ads"
            status={mapIntegrationStatus(integrations?.chatgpt_ads?.status)}
            detail={integrations?.chatgpt_ads?.detail || "Coming soon — OpenAI Ads API in beta"}
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="LinkedIn Ads"
            status={mapIntegrationStatus(integrations?.linkedin_ads?.status)}
            detail={integrations?.linkedin_ads?.detail || "Coming soon"}
          />
          <IntegrationRow
            icon={<MessageCircle className="w-4 h-4" />}
            name="WhatsApp Ads (CTWA)"
            status={mapIntegrationStatus(integrations?.whatsapp_ads?.status)}
            detail={integrations?.whatsapp_ads?.detail || "Click-to-WhatsApp ads via Meta"}
          />
          <IntegrationRow
            icon={<BarChart3 className="w-4 h-4" />}
            name="Twilio Call Tracking"
            status={mapIntegrationStatus(integrations?.twilio_calls?.status)}
            detail={integrations?.twilio_calls?.detail || "Call tracking & recording"}
            extraAction={mapIntegrationStatus(integrations?.twilio_calls?.status) === "connected" ? (
              <button
                onClick={async () => {
                  setProvisioningTwilio(true);
                  try {
                    const result = await provisionTwilioNumber();
                    alert(result.message || `Number: ${result.phone_number}`);
                    window.location.reload();
                  } catch (err: unknown) {
                    const msg = err instanceof Error ? err.message : "Failed to provision Twilio number";
                    alert(msg);
                  }
                  finally { setProvisioningTwilio(false); }
                }}
                disabled={provisioningTwilio}
                className="px-3 py-1 rounded-lg text-xs font-medium bg-cyan-500 text-white hover:bg-cyan-600 transition-colors disabled:opacity-50"
              >
                {provisioningTwilio ? "Provisioning…" : "Provision Number"}
              </button>
            ) : undefined}
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
            <p className="text-sm text-slate-600">No active subscription. Start a free trial from the <a href="/dashboard/billing" className="text-emerald-600 hover:text-emerald-300">Billing</a> page.</p>
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

function mapIntegrationStatus(s?: string): "connected" | "pending" | "not_connected" | "ready" | "active_draft" {
  if (!s) return "not_connected";
  if (s === "connected") return "connected";
  if (s === "pending") return "pending";
  if (s === "ready") return "ready";
  if (s === "active_draft") return "active_draft";
  return "not_connected";
}

function IntegrationRow({ icon, name, status, detail, onConnect, onDisconnect, connectLabel, extraAction }: {
  icon: React.ReactNode;
  name: string;
  status: "connected" | "pending" | "not_connected" | "ready" | "active_draft";
  detail: string;
  onConnect?: () => void;
  onDisconnect?: () => void;
  connectLabel?: string;
  extraAction?: React.ReactNode;
}) {
  const statusConfig = {
    connected: { icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" />, label: "Connected", cls: "bg-emerald-50 text-emerald-600" },
    ready: { icon: <CheckCircle2 className="w-4 h-4 text-cyan-600" />, label: "Ready", cls: "bg-cyan-50 text-cyan-600" },
    active_draft: { icon: <Clock className="w-4 h-4 text-amber-600" />, label: "Draft Mode", cls: "bg-amber-50 text-amber-600" },
    pending: { icon: <Clock className="w-4 h-4 text-amber-600" />, label: "Pending", cls: "bg-amber-50 text-amber-600" },
    not_connected: { icon: <XCircle className="w-4 h-4 text-slate-600" />, label: "Not Connected", cls: "bg-white/5 text-slate-600" },
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
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
          {cfg.icon} {cfg.label}
        </span>
        {extraAction}
        {status !== "connected" && onConnect && (
          <button
            onClick={onConnect}
            className="px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500 text-white hover:bg-emerald-600 transition-colors"
          >
            {connectLabel || "Connect"}
          </button>
        )}
        {status === "connected" && onDisconnect && (
          <button
            onClick={onDisconnect}
            className="px-3 py-1 rounded-lg text-xs font-medium text-slate-500 hover:text-red-500 hover:bg-red-50 transition-colors"
          >
            Disconnect
          </button>
        )}
      </div>
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
